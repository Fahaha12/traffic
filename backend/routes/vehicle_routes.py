"""
车辆相关路由
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from core import db, Vehicle, VehicleDetection, VehicleAlert, generate_id, validate_required_fields

vehicle_bp = Blueprint('vehicle', __name__)
logger = logging.getLogger(__name__)

@vehicle_bp.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """获取车辆列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        vehicle_type = request.args.get('type')
        is_suspicious = request.args.get('is_suspicious')
        risk_level = request.args.get('risk_level')
        search = request.args.get('search')
        
        query = Vehicle.query
        
        if vehicle_type:
            query = query.filter_by(vehicle_type=vehicle_type)
        if is_suspicious is not None:
            query = query.filter_by(is_suspicious=is_suspicious.lower() == 'true')
        if risk_level:
            query = query.filter_by(risk_level=risk_level)
        if search:
            query = query.filter(Vehicle.plate_number.contains(search))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        vehicles = [vehicle.to_dict() for vehicle in pagination.items]
        
        return jsonify({
            'vehicles': vehicles,
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
        logger.error(f'获取车辆列表失败: {str(e)}')
        return jsonify({'error': '获取车辆列表失败'}), 500

@vehicle_bp.route('/api/vehicles/<vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """获取单个车辆详情"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        return jsonify(vehicle.to_dict()), 200
        
    except Exception as e:
        logger.error(f'获取车辆详情失败: {str(e)}')
        return jsonify({'error': '获取车辆详情失败'}), 500

@vehicle_bp.route('/api/vehicles', methods=['POST'])
def create_vehicle():
    """创建车辆"""
    try:
        data = request.get_json()
        
        # 字段名映射：前端驼峰命名 -> 后端下划线命名
        plate_number = data.get('plateNumber') or data.get('plate_number')
        vehicle_type = data.get('vehicleType') or data.get('vehicle_type')
        color = data.get('color')
        brand = data.get('brand')
        model = data.get('model')
        is_suspicious = data.get('isSuspicious', data.get('is_suspicious', False))
        risk_level = data.get('riskLevel', data.get('risk_level', 'low'))
        
        # 验证必填字段
        if not plate_number:
            return jsonify({'error': '缺少必填字段: plateNumber'}), 400
        if not vehicle_type:
            return jsonify({'error': '缺少必填字段: vehicleType'}), 400
        
        # 检查车牌号是否已存在
        existing_vehicle = Vehicle.query.filter_by(plate_number=plate_number).first()
        if existing_vehicle:
            return jsonify({'error': '车牌号已存在'}), 400
        
        # 创建车辆
        vehicle = Vehicle(
            id=generate_id(),
            plate_number=plate_number,
            vehicle_type=vehicle_type,
            color=color,
            brand=brand,
            model=model,
            is_suspicious=is_suspicious,
            risk_level=risk_level,
            created_at=datetime.utcnow()
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': '车辆创建成功',
            'vehicle': vehicle.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建车辆失败: {str(e)}')
        return jsonify({'error': '创建车辆失败'}), 500

@vehicle_bp.route('/api/vehicles/<vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    """更新车辆"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        data = request.get_json()
        
        # 字段名映射：前端驼峰命名 -> 后端下划线命名
        plate_number = data.get('plateNumber') or data.get('plate_number')
        vehicle_type = data.get('vehicleType') or data.get('vehicle_type')
        color = data.get('color')
        brand = data.get('brand')
        model = data.get('model')
        is_suspicious = data.get('isSuspicious')
        risk_level = data.get('riskLevel') or data.get('risk_level')
        
        # 更新字段
        if plate_number is not None:
            # 检查车牌号是否与其他车辆重复
            existing_vehicle = Vehicle.query.filter(
                Vehicle.plate_number == plate_number,
                Vehicle.id != vehicle_id
            ).first()
            if existing_vehicle:
                return jsonify({'error': '车牌号已存在'}), 400
            vehicle.plate_number = plate_number
        
        if vehicle_type is not None:
            vehicle.vehicle_type = vehicle_type
        if color is not None:
            vehicle.color = color
        if brand is not None:
            vehicle.brand = brand
        if model is not None:
            vehicle.model = model
        if is_suspicious is not None:
            vehicle.is_suspicious = is_suspicious
        if risk_level is not None:
            vehicle.risk_level = risk_level
        
        db.session.commit()
        
        return jsonify({
            'message': '车辆更新成功',
            'vehicle': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新车辆失败: {str(e)}')
        return jsonify({'error': '更新车辆失败'}), 500

@vehicle_bp.route('/api/vehicles/<vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """删除车辆"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({'message': '车辆删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除车辆失败: {str(e)}')
        return jsonify({'error': '删除车辆失败'}), 500

@vehicle_bp.route('/api/vehicles/suspicious', methods=['GET'])
def get_suspicious_vehicles():
    """获取可疑车辆列表"""
    try:
        suspicious_vehicles = Vehicle.query.filter_by(is_suspicious=True).all()
        vehicles = [vehicle.to_dict() for vehicle in suspicious_vehicles]
        
        return jsonify({
            'vehicles': vehicles,
            'count': len(vehicles)
        }), 200
        
    except Exception as e:
        logger.error(f'获取可疑车辆列表失败: {str(e)}')
        return jsonify({'error': '获取可疑车辆列表失败'}), 500

@vehicle_bp.route('/api/vehicles/<vehicle_id>/mark-suspicious', methods=['POST'])
def mark_vehicle_suspicious(vehicle_id):
    """标记车辆为可疑"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        data = request.get_json()
        is_suspicious = data.get('isSuspicious', data.get('is_suspicious', True))
        reason = data.get('reason', '')
        risk_level = data.get('riskLevel', data.get('risk_level', 'high'))
        
        vehicle.is_suspicious = is_suspicious
        if is_suspicious:
            vehicle.risk_level = risk_level
        
        db.session.commit()
        
        return jsonify({
            'message': f'车辆已{"标记为" if is_suspicious else "取消"}可疑',
            'vehicle': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'标记可疑车辆失败: {str(e)}')
        return jsonify({'error': '标记可疑车辆失败'}), 500

@vehicle_bp.route('/api/vehicles/stats', methods=['GET'])
def get_vehicle_stats():
    """获取车辆统计信息"""
    try:
        total_vehicles = Vehicle.query.count()
        suspicious_vehicles = Vehicle.query.filter_by(is_suspicious=True).count()
        
        # 按类型统计
        type_stats = {}
        for vehicle_type in ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'unknown']:
            count = Vehicle.query.filter_by(vehicle_type=vehicle_type).count()
            type_stats[vehicle_type] = count
        
        # 按风险等级统计
        risk_stats = {}
        for risk_level in ['low', 'medium', 'high', 'critical']:
            count = Vehicle.query.filter_by(risk_level=risk_level).count()
            risk_stats[risk_level] = count
        
        return jsonify({
            'total_vehicles': total_vehicles,
            'suspicious_vehicles': suspicious_vehicles,
            'type_stats': type_stats,
            'risk_stats': risk_stats
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆统计失败: {str(e)}')
        return jsonify({'error': '获取车辆统计失败'}), 500

@vehicle_bp.route('/api/vehicles/<vehicle_id>/tracks', methods=['GET'])
def get_vehicle_tracks(vehicle_id):
    """获取车辆轨迹"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = VehicleDetection.query.filter_by(vehicle_id=vehicle_id)
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        tracks = [track.to_dict() for track in pagination.items]
        
        return jsonify({
            'vehicle_id': vehicle_id,
            'tracks': tracks,
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
        logger.error(f'获取车辆轨迹失败: {str(e)}')
        return jsonify({'error': '获取车辆轨迹失败'}), 500

@vehicle_bp.route('/api/vehicles/tracks', methods=['POST'])
def create_vehicle_track():
    """创建车辆轨迹点"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['vehicle_id', 'camera_id', 'latitude', 'longitude']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        # 检查车辆是否存在
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 400
        
        # 创建轨迹点
        track = VehicleDetection(
            id=generate_id(),
            vehicle_id=data['vehicle_id'],
            camera_id=data['camera_id'],
            detected_at=datetime.fromisoformat(data.get('detectedAt', datetime.utcnow().isoformat())),
            latitude=data['latitude'],
            longitude=data['longitude'],
            confidence=data.get('confidence', 0.9),
            speed=data.get('speed', 0),
            direction=data.get('direction', 0),
            image_url=data.get('imageUrl'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(track)
        db.session.commit()
        
        return jsonify({
            'message': '轨迹点创建成功',
            'track': track.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建车辆轨迹失败: {str(e)}')
        return jsonify({'error': '创建车辆轨迹失败'}), 500

@vehicle_bp.route('/api/vehicles/<vehicle_id>/alerts', methods=['GET'])
def get_vehicle_alerts(vehicle_id):
    """获取车辆告警"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': '车辆不存在'}), 404
        
        alerts = VehicleAlert.query.filter_by(vehicle_id=vehicle_id).all()
        alert_list = [alert.to_dict() for alert in alerts]
        
        return jsonify({
            'vehicle_id': vehicle_id,
            'alerts': alert_list,
            'count': len(alert_list)
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆告警失败: {str(e)}')
        return jsonify({'error': '获取车辆告警失败'}), 500

@vehicle_bp.route('/api/vehicles/alerts/<alert_id>/read', methods=['POST'])
def mark_alert_read(alert_id):
    """标记告警为已读"""
    try:
        alert = VehicleAlert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        alert.is_read = True
        alert.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '告警已标记为已读',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'标记告警已读失败: {str(e)}')
        return jsonify({'error': '标记告警已读失败'}), 500

@vehicle_bp.route('/api/vehicles/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """解决告警"""
    try:
        alert = VehicleAlert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '告警已解决',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'解决告警失败: {str(e)}')
        return jsonify({'error': '解决告警失败'}), 500
