"""
车辆管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.vehicle import Vehicle, VehicleTrack, VehicleAlert
from app.models.alert import Alert
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/', methods=['GET'])
@jwt_required()
def get_vehicles():
    """获取车辆列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        vehicle_type = request.args.get('type')
        is_suspicious = request.args.get('is_suspicious')
        risk_level = request.args.get('risk_level')
        
        query = Vehicle.query
        
        if vehicle_type:
            query = query.filter_by(vehicle_type=vehicle_type)
        if is_suspicious is not None:
            query = query.filter_by(is_suspicious=is_suspicious.lower() == 'true')
        if risk_level:
            query = query.filter_by(risk_level=risk_level)
        
        vehicles = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'vehicles': [vehicle.to_dict() for vehicle in vehicles.items],
            'total': vehicles.total,
            'page': page,
            'per_page': per_page,
            'pages': vehicles.pages
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆列表失败: {str(e)}')
        return jsonify({'error': '获取车辆列表失败'}), 500

@vehicles_bp.route('/<vehicle_id>', methods=['GET'])
@jwt_required()
def get_vehicle(vehicle_id):
    """获取单个车辆信息"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        return jsonify({
            'vehicle': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆信息失败: {str(e)}')
        return jsonify({'error': '获取车辆信息失败'}), 500

@vehicles_bp.route('/<vehicle_id>/tracks', methods=['GET'])
@jwt_required()
def get_vehicle_tracks(vehicle_id):
    """获取车辆轨迹"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', 100, type=int)
        
        # 解析时间参数
        start_dt = None
        end_dt = None
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        tracks = VehicleTrack.get_vehicle_trajectory(
            vehicle_id, 
            start_dt, 
            end_dt
        )[:limit]
        
        return jsonify({
            'tracks': [track.to_dict() for track in tracks]
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆轨迹失败: {str(e)}')
        return jsonify({'error': '获取车辆轨迹失败'}), 500

@vehicles_bp.route('/<vehicle_id>/alerts', methods=['GET'])
@jwt_required()
def get_vehicle_alerts(vehicle_id):
    """获取车辆告警"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        alerts = VehicleAlert.get_by_vehicle(vehicle_id)
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆告警失败: {str(e)}')
        return jsonify({'error': '获取车辆告警失败'}), 500

@vehicles_bp.route('/suspicious', methods=['GET'])
@jwt_required()
def get_suspicious_vehicles():
    """获取可疑车辆"""
    try:
        vehicles = Vehicle.get_suspicious_vehicles()
        return jsonify({
            'vehicles': [vehicle.to_dict() for vehicle in vehicles]
        }), 200
        
    except Exception as e:
        logger.error(f'获取可疑车辆失败: {str(e)}')
        return jsonify({'error': '获取可疑车辆失败'}), 500

@vehicles_bp.route('/<vehicle_id>/mark-suspicious', methods=['POST'])
@jwt_required()
def mark_suspicious(vehicle_id):
    """标记车辆为可疑"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        data = request.get_json()
        is_suspicious = data.get('is_suspicious', True)
        risk_level = data.get('risk_level', 'medium')
        reason = data.get('reason', '')
        
        vehicle.is_suspicious = is_suspicious
        vehicle.risk_level = risk_level
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 创建告警
        if is_suspicious:
            Alert.create_alert(
                title=f'车辆标记为可疑: {vehicle.plate_number}',
                description=f'车辆 {vehicle.plate_number} 被标记为可疑车辆。原因: {reason}',
                alert_type='vehicle',
                severity=risk_level,
                source='manual',
                metadata={'vehicle_id': vehicle_id, 'reason': reason}
            )
        
        return jsonify({
            'message': '标记成功',
            'vehicle': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'标记可疑车辆失败: {str(e)}')
        return jsonify({'error': '标记可疑车辆失败'}), 500

@vehicles_bp.route('/tracks', methods=['POST'])
@jwt_required()
def create_track():
    """创建车辆轨迹点"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['vehicleId', 'cameraId', 'position', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 检查车辆是否存在
        vehicle = Vehicle.query.get(data['vehicleId'])
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        # 创建轨迹点
        track = VehicleTrack(
            vehicle_id=data['vehicleId'],
            camera_id=data['cameraId'],
            position_lat=data['position']['lat'],
            position_lng=data['position']['lng'],
            speed=data.get('speed'),
            direction=data.get('direction'),
            location_name=data.get('locationName'),
            confidence=data.get('confidence'),
            image_url=data.get('imageUrl')
        )
        
        # 设置时间戳
        if 'timestamp' in data:
            track.timestamp = datetime.fromisoformat(
                data['timestamp'].replace('Z', '+00:00')
            )
        
        db.session.add(track)
        
        # 更新车辆最后出现时间
        vehicle.update_last_seen()
        
        db.session.commit()
        
        return jsonify({
            'message': '轨迹点创建成功',
            'track': track.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'创建轨迹点失败: {str(e)}')
        return jsonify({'error': '创建轨迹点失败'}), 500

@vehicles_bp.route('/alerts/<alert_id>/read', methods=['POST'])
@jwt_required()
def mark_alert_read(alert_id):
    """标记告警为已读"""
    try:
        alert = VehicleAlert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        alert.mark_as_read()
        
        return jsonify({'message': '告警已标记为已读'}), 200
        
    except Exception as e:
        logger.error(f'标记告警已读失败: {str(e)}')
        return jsonify({'error': '标记告警已读失败'}), 500

@vehicles_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    """解决告警"""
    try:
        alert = VehicleAlert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        alert.mark_as_resolved()
        
        return jsonify({'message': '告警已解决'}), 200
        
    except Exception as e:
        logger.error(f'解决告警失败: {str(e)}')
        return jsonify({'error': '解决告警失败'}), 500

@vehicles_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_vehicle_stats():
    """获取车辆统计信息"""
    try:
        # 总车辆数
        total_vehicles = Vehicle.query.count()
        
        # 可疑车辆数
        suspicious_vehicles = Vehicle.query.filter_by(is_suspicious=True).count()
        
        # 按类型统计
        type_stats = db.session.query(
            Vehicle.vehicle_type, 
            db.func.count(Vehicle.id)
        ).group_by(Vehicle.vehicle_type).all()
        
        # 按风险等级统计
        risk_stats = db.session.query(
            Vehicle.risk_level,
            db.func.count(Vehicle.id)
        ).group_by(Vehicle.risk_level).all()
        
        # 最近24小时的轨迹数
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_tracks = VehicleTrack.query.filter(
            VehicleTrack.timestamp >= yesterday
        ).count()
        
        return jsonify({
            'totalVehicles': total_vehicles,
            'suspiciousVehicles': suspicious_vehicles,
            'typeStats': dict(type_stats),
            'riskStats': dict(risk_stats),
            'recentTracks': recent_tracks
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆统计失败: {str(e)}')
        return jsonify({'error': '获取车辆统计失败'}), 500
