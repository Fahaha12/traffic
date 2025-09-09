"""
车辆检测相关路由
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from core import db, VehicleDetection

detection_bp = Blueprint('detection', __name__)
logger = logging.getLogger(__name__)

@detection_bp.route('/api/detection', methods=['GET'])
def get_detections():
    """获取车辆检测记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        vehicle_id = request.args.get('vehicle_id')
        camera_id = request.args.get('camera_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        query = VehicleDetection.query
        
        if vehicle_id:
            query = query.filter_by(vehicle_id=vehicle_id)
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        if start_time:
            query = query.filter(VehicleDetection.detected_at >= datetime.fromisoformat(start_time))
        if end_time:
            query = query.filter(VehicleDetection.detected_at <= datetime.fromisoformat(end_time))
        
        # 按检测时间倒序排列
        query = query.order_by(VehicleDetection.detected_at.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        detections = [detection.to_dict() for detection in pagination.items]
        
        return jsonify({
            'detections': detections,
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
        logger.error(f'获取检测记录失败: {str(e)}')
        return jsonify({'error': '获取检测记录失败'}), 500
