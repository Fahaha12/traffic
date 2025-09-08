"""
流媒体代理API路由
"""

from flask import Blueprint, request, jsonify, send_file, abort, make_response
import os
import logging
from stream_converter import stream_converter

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
        result = stream_converter.convert_rtmp_to_hls(rtmp_url, stream_id)
        
        if result['success']:
            return jsonify({
                'message': '流媒体转换已启动',
                'stream_id': result['stream_id'],
                'hls_url': result['hls_url'],
                'status': result['status']
            }), 200
        else:
            return jsonify({
                'error': '流媒体转换启动失败',
                'details': result.get('error', '未知错误')
            }), 500
            
    except Exception as e:
        logger.error(f"转换流媒体失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@stream_bp.route('/status/<stream_id>')
def get_stream_status(stream_id):
    """获取流媒体转换状态"""
    try:
        status = stream_converter.get_conversion_status(stream_id)
        
        if status:
            return jsonify({
                'stream_id': stream_id,
                'status': status['status'],
                'rtmp_url': status['rtmp_url'],
                'hls_url': f'/api/stream/play/{stream_id}',
                'start_time': status['start_time'].isoformat() if 'start_time' in status else None,
                'error': status.get('error')
            }), 200
        else:
            return jsonify({'error': '流媒体不存在'}), 404
            
    except Exception as e:
        logger.error(f"获取流媒体状态失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@stream_bp.route('/stop/<stream_id>', methods=['POST'])
def stop_stream(stream_id):
    """停止流媒体转换"""
    try:
        success = stream_converter.stop_conversion(stream_id)
        
        if success:
            return jsonify({'message': '流媒体转换已停止'}), 200
        else:
            return jsonify({'error': '流媒体不存在或已停止'}), 404
            
    except Exception as e:
        logger.error(f"停止流媒体失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@stream_bp.route('/play/<stream_id>')
def play_stream(stream_id):
    """播放HLS流"""
    try:
        # 检查流媒体是否存在
        status = stream_converter.get_conversion_status(stream_id)
        if not status:
            abort(404)
        
        # 构建HLS文件路径
        hls_path = status['hls_path']
        
        if not os.path.exists(hls_path):
            abort(404)
        
        # 返回HLS播放列表，添加CORS头
        response = make_response(send_file(
            hls_path,
            mimetype='application/vnd.apple.mpegurl',
            as_attachment=False
        ))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    except Exception as e:
        logger.error(f"播放流媒体失败: {str(e)}")
        abort(500)

@stream_bp.route('/segment/<stream_id>/<filename>')
def get_segment(stream_id, filename):
    """获取HLS片段文件"""
    try:
        # 构建片段文件路径
        segment_path = os.path.join('streams', stream_id, filename)
        
        if not os.path.exists(segment_path):
            abort(404)
        
        # 返回片段文件，添加CORS头
        response = make_response(send_file(
            segment_path,
            mimetype='video/mp2t',
            as_attachment=False
        ))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    except Exception as e:
        logger.error(f"获取片段文件失败: {str(e)}")
        abort(500)

@stream_bp.route('/list')
def list_streams():
    """获取所有活跃的流媒体"""
    try:
        active_streams = stream_converter.list_active_conversions()
        streams_info = []
        
        for stream_id in active_streams:
            status = stream_converter.get_conversion_status(stream_id)
            if status:
                streams_info.append({
                    'stream_id': stream_id,
                    'rtmp_url': status['rtmp_url'],
                    'hls_url': f'/api/stream/play/{stream_id}',
                    'status': status['status'],
                    'start_time': status['start_time'].isoformat() if 'start_time' in status else None
                })
        
        return jsonify({
            'streams': streams_info,
            'total': len(streams_info)
        }), 200
        
    except Exception as e:
        logger.error(f"获取流媒体列表失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@stream_bp.route('/cleanup', methods=['POST'])
def cleanup_streams():
    """清理旧的流媒体文件"""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        stream_converter.cleanup_old_streams(max_age_hours)
        
        return jsonify({'message': f'已清理超过{max_age_hours}小时的流媒体文件'}), 200
        
    except Exception as e:
        logger.error(f"清理流媒体失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500
