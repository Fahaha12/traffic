"""
摄像头管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.camera import Camera
from app.models.alert import Alert
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

cameras_bp = Blueprint('cameras', __name__)

@cameras_bp.route('/', methods=['GET'])
@jwt_required()
def get_cameras():
    """获取摄像头列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        camera_type = request.args.get('type')
        
        query = Camera.query
        
        if status:
            query = query.filter_by(status=status)
        if camera_type:
            query = query.filter_by(type=camera_type)
        
        cameras = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'cameras': [camera.to_dict() for camera in cameras.items],
            'total': cameras.total,
            'page': page,
            'per_page': per_page,
            'pages': cameras.pages
        }), 200
        
    except Exception as e:
        logger.error(f'获取摄像头列表失败: {str(e)}')
        return jsonify({'error': '获取摄像头列表失败'}), 500

@cameras_bp.route('/<camera_id>', methods=['GET'])
@jwt_required()
def get_camera(camera_id):
    """获取单个摄像头信息"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        return jsonify({
            'camera': camera.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'获取摄像头信息失败: {str(e)}')
        return jsonify({'error': '获取摄像头信息失败'}), 500

@cameras_bp.route('/', methods=['POST'])
@jwt_required()
def create_camera():
    """创建摄像头"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'type', 'position', 'streamUrl', 'streamType']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 创建摄像头
        camera = Camera(
            name=data['name'],
            type=data['type'],
            stream_url=data['streamUrl'],
            stream_type=data['streamType'],
            fps=data.get('fps', 25),
            direction=data.get('direction', 0)
        )
        
        # 设置位置
        if 'position' in data:
            camera.position = data['position']
        
        # 设置分辨率
        if 'resolution' in data:
            camera.resolution = data['resolution']
        
        db.session.add(camera)
        db.session.commit()
        
        # 创建告警
        Alert.create_alert(
            title=f'新摄像头已添加: {camera.name}',
            description=f'摄像头 {camera.name} 已成功添加到系统中',
            alert_type='camera',
            severity='info',
            source='system',
            camera_id=camera.id
        )
        
        return jsonify({
            'message': '摄像头创建成功',
            'camera': camera.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'创建摄像头失败: {str(e)}')
        return jsonify({'error': '创建摄像头失败'}), 500

@cameras_bp.route('/<camera_id>', methods=['PUT'])
@jwt_required()
def update_camera(camera_id):
    """更新摄像头"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            camera.name = data['name']
        if 'type' in data:
            camera.type = data['type']
        if 'position' in data:
            camera.position = data['position']
        if 'streamUrl' in data:
            camera.stream_url = data['streamUrl']
        if 'streamType' in data:
            camera.stream_type = data['streamType']
        if 'resolution' in data:
            camera.resolution = data['resolution']
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
        logger.error(f'更新摄像头失败: {str(e)}')
        return jsonify({'error': '更新摄像头失败'}), 500

@cameras_bp.route('/<camera_id>', methods=['DELETE'])
@jwt_required()
def delete_camera(camera_id):
    """删除摄像头"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        camera_name = camera.name
        db.session.delete(camera)
        db.session.commit()
        
        # 创建告警
        Alert.create_alert(
            title=f'摄像头已删除: {camera_name}',
            description=f'摄像头 {camera_name} 已从系统中删除',
            alert_type='camera',
            severity='warning',
            source='system'
        )
        
        return jsonify({'message': '摄像头删除成功'}), 200
        
    except Exception as e:
        logger.error(f'删除摄像头失败: {str(e)}')
        return jsonify({'error': '删除摄像头失败'}), 500

@cameras_bp.route('/<camera_id>/status', methods=['PUT'])
@jwt_required()
def update_camera_status(camera_id):
    """更新摄像头状态"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['online', 'offline', 'maintenance']:
            return jsonify({'error': '无效的状态值'}), 400
        
        old_status = camera.status
        camera.status = status
        camera.updated_at = datetime.utcnow()
        
        if status == 'online':
            camera.update_heartbeat()
        
        db.session.commit()
        
        # 创建告警
        if old_status != status:
            Alert.create_alert(
                title=f'摄像头状态变更: {camera.name}',
                description=f'摄像头 {camera.name} 状态从 {old_status} 变更为 {status}',
                alert_type='camera',
                severity='info' if status == 'online' else 'warning',
                source='system',
                camera_id=camera.id
            )
        
        return jsonify({
            'message': '状态更新成功',
            'camera': camera.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'更新摄像头状态失败: {str(e)}')
        return jsonify({'error': '更新摄像头状态失败'}), 500

@cameras_bp.route('/<camera_id>/heartbeat', methods=['POST'])
@jwt_required()
def update_heartbeat(camera_id):
    """更新摄像头心跳"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        camera.update_heartbeat()
        
        return jsonify({'message': '心跳更新成功'}), 200
        
    except Exception as e:
        logger.error(f'更新心跳失败: {str(e)}')
        return jsonify({'error': '更新心跳失败'}), 500

@cameras_bp.route('/<camera_id>/test-connection', methods=['POST'])
@jwt_required()
def test_connection(camera_id):
    """测试摄像头连接"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        # 这里可以添加实际的连接测试逻辑
        # 例如：ping摄像头IP、测试流媒体连接等
        
        # 模拟测试结果
        import random
        is_online = random.choice([True, True, True, False])  # 75%成功率
        
        if is_online:
            camera.status = 'online'
            camera.update_heartbeat()
            message = '连接测试成功'
        else:
            camera.status = 'offline'
            message = '连接测试失败'
        
        db.session.commit()
        
        return jsonify({
            'success': is_online,
            'message': message,
            'camera': camera.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'测试连接失败: {str(e)}')
        return jsonify({'error': '测试连接失败'}), 500

@cameras_bp.route('/online', methods=['GET'])
@jwt_required()
def get_online_cameras():
    """获取在线摄像头"""
    try:
        cameras = Camera.get_online_cameras()
        return jsonify({
            'cameras': [camera.to_dict() for camera in cameras]
        }), 200
        
    except Exception as e:
        logger.error(f'获取在线摄像头失败: {str(e)}')
        return jsonify({'error': '获取在线摄像头失败'}), 500

@cameras_bp.route('/nearby', methods=['GET'])
@jwt_required()
def get_nearby_cameras():
    """获取附近摄像头"""
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', 0.01, type=float)
        
        if not lat or not lng:
            return jsonify({'error': '缺少经纬度参数'}), 400
        
        cameras = Camera.get_by_location(lat, lng, radius)
        return jsonify({
            'cameras': [camera.to_dict() for camera in cameras]
        }), 200
        
    except Exception as e:
        logger.error(f'获取附近摄像头失败: {str(e)}')
        return jsonify({'error': '获取附近摄像头失败'}), 500
