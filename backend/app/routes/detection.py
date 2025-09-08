"""
车辆检测API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.detection import VehicleDetection
from app.models.camera import Camera
from app.models.ai_model import AIModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

detection_bp = Blueprint('detection', __name__)

@detection_bp.route('/', methods=['GET'])
@jwt_required()
def get_detections():
    """获取车辆检测记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        camera_id = request.args.get('camera_id')
        vehicle_type = request.args.get('vehicle_type')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        min_confidence = request.args.get('min_confidence', 0.5, type=float)
        
        query = VehicleDetection.query
        
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        if vehicle_type:
            query = query.filter_by(vehicle_type=vehicle_type)
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(VehicleDetection.detection_time >= start_dt)
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(VehicleDetection.detection_time <= end_dt)
        if min_confidence:
            query = query.filter(VehicleDetection.confidence >= min_confidence)
        
        detections = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'detections': [detection.to_dict() for detection in detections.items],
            'total': detections.total,
            'page': page,
            'per_page': per_page,
            'pages': detections.pages
        }), 200
        
    except Exception as e:
        logger.error(f'获取检测记录失败: {str(e)}')
        return jsonify({'error': '获取检测记录失败'}), 500

@detection_bp.route('/<detection_id>', methods=['GET'])
@jwt_required()
def get_detection(detection_id):
    """获取单个检测记录"""
    try:
        detection = VehicleDetection.query.get(detection_id)
        if not detection:
            return jsonify({'error': '检测记录不存在'}), 404
        
        return jsonify({
            'detection': detection.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'获取检测记录失败: {str(e)}')
        return jsonify({'error': '获取检测记录失败'}), 500

@detection_bp.route('/', methods=['POST'])
@jwt_required()
def create_detection():
    """创建检测记录"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['cameraId', 'detectionTime', 'bbox', 'confidence', 'vehicleType']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 创建检测记录
        detection = VehicleDetection(
            camera_id=data['cameraId'],
            detection_time=datetime.fromisoformat(data['detectionTime'].replace('Z', '+00:00')),
            bbox_x1=data['bbox']['x1'],
            bbox_y1=data['bbox']['y1'],
            bbox_x2=data['bbox']['x2'],
            bbox_y2=data['bbox']['y2'],
            confidence=data['confidence'],
            vehicle_type=data['vehicleType'],
            color=data.get('color'),
            speed=data.get('speed'),
            direction=data.get('direction'),
            image_path=data.get('imagePath'),
            model_id=data.get('modelId')
        )
        
        db.session.add(detection)
        db.session.commit()
        
        return jsonify({
            'message': '检测记录创建成功',
            'detection': detection.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'创建检测记录失败: {str(e)}')
        return jsonify({'error': '创建检测记录失败'}), 500

@detection_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_detection_stats():
    """获取检测统计信息"""
    try:
        camera_id = request.args.get('camera_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        query = VehicleDetection.query
        
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(VehicleDetection.detection_time >= start_dt)
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(VehicleDetection.detection_time <= end_dt)
        
        # 总检测数
        total_detections = query.count()
        
        # 按车辆类型统计
        type_stats = db.session.query(
            VehicleDetection.vehicle_type,
            db.func.count(VehicleDetection.id)
        ).filter(
            query.whereclause
        ).group_by(VehicleDetection.vehicle_type).all()
        
        # 按摄像头统计
        camera_stats = db.session.query(
            VehicleDetection.camera_id,
            db.func.count(VehicleDetection.id)
        ).filter(
            query.whereclause
        ).group_by(VehicleDetection.camera_id).all()
        
        # 平均置信度
        avg_confidence = db.session.query(
            db.func.avg(VehicleDetection.confidence)
        ).filter(
            query.whereclause
        ).scalar() or 0
        
        # 最近24小时检测数
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_detections = query.filter(
            VehicleDetection.detection_time >= yesterday
        ).count()
        
        return jsonify({
            'totalDetections': total_detections,
            'typeStats': dict(type_stats),
            'cameraStats': dict(camera_stats),
            'avgConfidence': round(avg_confidence, 3),
            'recentDetections': recent_detections
        }), 200
        
    except Exception as e:
        logger.error(f'获取检测统计失败: {str(e)}')
        return jsonify({'error': '获取检测统计失败'}), 500

@detection_bp.route('/realtime', methods=['GET'])
@jwt_required()
def get_realtime_detections():
    """获取实时检测数据"""
    try:
        camera_id = request.args.get('camera_id')
        limit = request.args.get('limit', 50, type=int)
        
        query = VehicleDetection.query
        
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        
        # 获取最近的检测记录
        detections = query.order_by(
            VehicleDetection.detection_time.desc()
        ).limit(limit).all()
        
        return jsonify({
            'detections': [detection.to_dict() for detection in detections]
        }), 200
        
    except Exception as e:
        logger.error(f'获取实时检测数据失败: {str(e)}')
        return jsonify({'error': '获取实时检测数据失败'}), 500
