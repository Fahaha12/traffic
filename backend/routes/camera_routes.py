"""
摄像头相关路由
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from core import db, Camera, generate_id, validate_required_fields

camera_bp = Blueprint('camera', __name__)
logger = logging.getLogger(__name__)

@camera_bp.route('/api/cameras', methods=['GET'])
def get_cameras():
    """获取摄像头列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = Camera.query
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        cameras = []
        for camera in pagination.items:
            camera_dict = camera.to_dict()
            camera_dict['actual_status'] = camera.get_actual_status()
            cameras.append(camera_dict)
        
        return jsonify({
            'cameras': cameras,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f'获取摄像头列表失败: {str(e)}')
        return jsonify({'error': '获取摄像头列表失败'}), 500

@camera_bp.route('/api/cameras/<camera_id>', methods=['GET'])
def get_camera(camera_id):
    """获取单个摄像头详情"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        camera_dict = camera.to_dict()
        camera_dict['actual_status'] = camera.get_actual_status()
        
        return jsonify(camera_dict), 200
        
    except Exception as e:
        logger.error(f'获取摄像头详情失败: {str(e)}')
        return jsonify({'error': '获取摄像头详情失败'}), 500

@camera_bp.route('/api/cameras', methods=['POST'])
def create_camera():
    """创建摄像头"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'type', 'position_lat', 'position_lng', 'stream_url', 'stream_type']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        # 检查名称是否已存在
        existing_camera = Camera.query.filter_by(name=data['name']).first()
        if existing_camera:
            return jsonify({'error': '摄像头名称已存在'}), 400
        
        # 创建摄像头
        camera = Camera(
            id=generate_id(),
            name=data['name'],
            type=data['type'],
            position_lat=data['position_lat'],
            position_lng=data['position_lng'],
            status=data.get('status', 'offline'),
            stream_url=data['stream_url'],
            stream_type=data['stream_type'],
            resolution_width=data.get('resolution_width'),
            resolution_height=data.get('resolution_height'),
            fps=data.get('fps'),
            direction=data.get('direction'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(camera)
        db.session.commit()
        
        return jsonify({
            'message': '摄像头创建成功',
            'camera': camera.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建摄像头失败: {str(e)}')
        return jsonify({'error': '创建摄像头失败'}), 500

@camera_bp.route('/api/cameras/<camera_id>', methods=['PUT'])
def update_camera(camera_id):
    """更新摄像头"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否与其他摄像头重复
            existing_camera = Camera.query.filter(
                Camera.name == data['name'],
                Camera.id != camera_id
            ).first()
            if existing_camera:
                return jsonify({'error': '摄像头名称已存在'}), 400
            camera.name = data['name']
        
        if 'type' in data:
            camera.type = data['type']
        if 'position_lat' in data:
            camera.position_lat = data['position_lat']
        if 'position_lng' in data:
            camera.position_lng = data['position_lng']
        if 'status' in data:
            camera.status = data['status']
        if 'stream_url' in data:
            camera.stream_url = data['stream_url']
        if 'stream_type' in data:
            camera.stream_type = data['stream_type']
        if 'resolution_width' in data:
            camera.resolution_width = data['resolution_width']
        if 'resolution_height' in data:
            camera.resolution_height = data['resolution_height']
        if 'fps' in data:
            camera.fps = data['fps']
        if 'direction' in data:
            camera.direction = data['direction']
        
        camera.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '摄像头更新成功',
            'camera': camera.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新摄像头失败: {str(e)}')
        return jsonify({'error': '更新摄像头失败'}), 500

@camera_bp.route('/api/cameras/<camera_id>/convert', methods=['POST'])
def convert_stream(camera_id):
    """转换流媒体格式"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        # 这里应该调用实际的流媒体转换服务
        # 目前返回模拟结果
        return jsonify({
            'message': '流媒体转换已启动',
            'camera_id': camera_id,
            'status': 'converting'
        }), 200
        
    except Exception as e:
        logger.error(f'转换流媒体失败: {str(e)}')
        return jsonify({'error': '转换流媒体失败'}), 500

@camera_bp.route('/api/cameras/<camera_id>/stream')
def get_camera_stream(camera_id):
    """获取摄像头流媒体信息"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        # 模拟流媒体状态检查
        return jsonify({
            'camera_id': camera_id,
            'stream_url': camera.stream_url,
            'stream_type': camera.stream_type,
            'status': 'not_converted',  # 实际应该检查转换状态
            'hls_url': f'/streams/{camera_id}/playlist.m3u8'
        }), 200
        
    except Exception as e:
        logger.error(f'获取流媒体信息失败: {str(e)}')
        return jsonify({'error': '获取流媒体信息失败'}), 500

@camera_bp.route('/api/cameras/<camera_id>/status', methods=['GET'])
def get_camera_status(camera_id):
    """获取摄像头状态"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        actual_status = camera.get_actual_status()
        
        return jsonify({
            'camera_id': camera_id,
            'status': actual_status,
            'last_update': camera.updated_at.isoformat() if camera.updated_at else None
        }), 200
        
    except Exception as e:
        logger.error(f'获取摄像头状态失败: {str(e)}')
        return jsonify({'error': '获取摄像头状态失败'}), 500

@camera_bp.route('/api/cameras/<camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    """删除摄像头"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        db.session.delete(camera)
        db.session.commit()
        
        return jsonify({'message': '摄像头删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除摄像头失败: {str(e)}')
        return jsonify({'error': '删除摄像头失败'}), 500
