"""
流媒体代理API路由
"""

from flask import Blueprint, request, jsonify, send_file, abort, make_response
import os
import logging
from .stream_tools import stream_manager

logger = logging.getLogger(__name__)

# 创建蓝图
stream_bp = Blueprint('stream', __name__, url_prefix='/api/stream')

# 添加CORS支持
@stream_bp.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@stream_bp.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

@stream_bp.route('/convert', methods=['POST'])
def convert_stream():
    """转换RTMP流为HLS流"""
    try:
        data = request.get_json()
        rtmp_url = data.get('rtmp_url')
        stream_id = data.get('stream_id')
        
        if not rtmp_url:
            return jsonify({'error': '缺少rtmp_url参数'}), 400
        
        # 开始转换
        result = stream_manager.start_conversion(stream_id, rtmp_url)
        
        if result:
            return jsonify({
                'message': '流媒体转换已启动',
                'stream_id': stream_id,
                'hls_url': f'/streams/{stream_id}/playlist.m3u8',
                'status': 'converting'
            }), 200
        else:
            return jsonify({'error': '流媒体转换启动失败'}), 500
            
    except Exception as e:
        logger.error(f'流媒体转换失败: {str(e)}')
        return jsonify({'error': '流媒体转换失败'}), 500

@stream_bp.route('/status/<stream_id>', methods=['GET'])
def get_stream_status(stream_id):
    """获取流转换状态"""
    try:
        status = stream_manager.get_conversion_status(stream_id)
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f'获取流状态失败: {str(e)}')
        return jsonify({'error': '获取流状态失败'}), 500

@stream_bp.route('/stop/<stream_id>', methods=['POST'])
def stop_stream(stream_id):
    """停止流转换"""
    try:
        success = stream_manager.stop_conversion(stream_id)
        
        if success:
            return jsonify({
                'message': '流媒体转换已停止',
                'stream_id': stream_id
            }), 200
        else:
            return jsonify({'error': '停止流媒体转换失败'}), 500
            
    except Exception as e:
        logger.error(f'停止流转换失败: {str(e)}')
        return jsonify({'error': '停止流转换失败'}), 500

@stream_bp.route('/play/<stream_id>/<filename>')
def play_stream(stream_id, filename):
    """播放HLS流文件"""
    try:
        # 构建文件路径
        file_path = os.path.join('streams', stream_id, filename)
        
        if not os.path.exists(file_path):
            abort(404)
        
        # 根据文件类型设置MIME类型
        if filename.endswith('.m3u8'):
            mimetype = 'application/vnd.apple.mpegurl'
        elif filename.endswith('.ts'):
            mimetype = 'video/mp2t'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(file_path, mimetype=mimetype)
        
    except Exception as e:
        logger.error(f'播放流文件失败: {str(e)}')
        abort(500)

@stream_bp.route('/list', methods=['GET'])
def list_streams():
    """获取所有活跃的流"""
    try:
        active_streams = stream_manager.list_active_conversions()
        
        streams_info = []
        for stream_id in active_streams:
            status = stream_manager.get_conversion_status(stream_id)
            streams_info.append({
                'stream_id': stream_id,
                'status': status.get('status', 'unknown'),
                'hls_url': f'/streams/{stream_id}/playlist.m3u8'
            })
        
        return jsonify({
            'streams': streams_info,
            'count': len(streams_info)
        }), 200
        
    except Exception as e:
        logger.error(f'获取流列表失败: {str(e)}')
        return jsonify({'error': '获取流列表失败'}), 500

@stream_bp.route('/cleanup', methods=['POST'])
def cleanup_streams():
    """清理旧的流文件"""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        stream_manager.cleanup_old_streams(max_age_hours)
        
        return jsonify({
            'message': '流文件清理完成',
            'max_age_hours': max_age_hours
        }), 200
        
    except Exception as e:
        logger.error(f'清理流文件失败: {str(e)}')
        return jsonify({'error': '清理流文件失败'}), 500
