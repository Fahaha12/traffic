"""
数据分析API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core import db, Camera, Vehicle, VehicleDetection, VehicleAlert
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """获取仪表板数据"""
    try:
        # 摄像头统计
        total_cameras = Camera.query.count()
        online_cameras = Camera.query.filter_by(status='online').count()
        offline_cameras = Camera.query.filter_by(status='offline').count()
        maintenance_cameras = Camera.query.filter_by(status='maintenance').count()
        
        # 车辆统计
        total_vehicles = Vehicle.query.count()
        suspicious_vehicles = Vehicle.query.filter_by(is_suspicious=True).count()
        
        # 告警统计
        total_alerts = VehicleAlert.query.count()
        unread_alerts = VehicleAlert.query.filter_by(is_read=False).count()
        
        # 最近24小时的活动
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_detections = VehicleDetection.query.filter(
            VehicleDetection.detected_at >= yesterday
        ).count()
        
        # 最近告警
        recent_alerts = VehicleAlert.query.filter(
            VehicleAlert.created_at >= yesterday
        ).order_by(VehicleAlert.created_at.desc()).limit(5).all()
        
        # 最近摄像头
        recent_cameras = Camera.query.order_by(
            Camera.updated_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'cameras': {
                'total': total_cameras,
                'online': online_cameras,
                'offline': offline_cameras,
                'maintenance': maintenance_cameras
            },
            'vehicles': {
                'total': total_vehicles,
                'suspicious': suspicious_vehicles
            },
            'alerts': {
                'total': total_alerts,
                'unread': unread_alerts
            },
            'activity': {
                'recentDetections': recent_detections
            },
            'recentAlerts': [
                {
                    'id': alert.id,
                    'message': alert.title,  # 使用title字段而不是message
                    'type': alert.alert_type,
                    'timestamp': alert.created_at.isoformat() if alert.created_at else None,
                    'isRead': alert.is_read
                } for alert in recent_alerts
            ],
            'recentCameras': [
                {
                    'id': camera.id,
                    'name': camera.name,
                    'type': camera.type,  # 使用type字段而不是camera_type
                    'status': camera.status,
                    'updatedAt': camera.updated_at.isoformat() if camera.updated_at else None
                } for camera in recent_cameras
            ]
        }), 200
        
    except Exception as e:
        logger.error(f'获取仪表板数据失败: {str(e)}')
        return jsonify({'error': '获取仪表板数据失败'}), 500

@analytics_bp.route('/traffic-flow', methods=['GET'])
@jwt_required()
def get_traffic_flow():
    """获取交通流量数据"""
    try:
        # 获取时间范围参数
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if not start_time or not end_time:
            # 默认最近24小时
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
        else:
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # 按小时统计检测数量
        hourly_stats = db.session.query(
            db.func.hour(VehicleDetection.detected_at).label('hour'),
            db.func.count(VehicleDetection.id).label('count')
        ).filter(
            VehicleDetection.detected_at >= start_time,
            VehicleDetection.detected_at <= end_time
        ).group_by(
            db.func.hour(VehicleDetection.detected_at)
        ).all()
        
        # 生成24小时数据
        hours = list(range(24))
        counts = [0] * 24
        
        for stat in hourly_stats:
            hour = stat.hour
            count = stat.count
            if 0 <= hour < 24:
                counts[hour] = count
        
        # 格式化时间标签
        time_labels = [f"{h:02d}:00" for h in hours]
        
        return jsonify({
            'timeLabels': time_labels,
            'data': counts
        }), 200
        
    except Exception as e:
        logger.error(f'获取交通流量数据失败: {str(e)}')
        return jsonify({'error': '获取交通流量数据失败'}), 500

@analytics_bp.route('/vehicle-analysis', methods=['GET'])
@jwt_required()
def get_vehicle_analysis():
    """获取车辆分析数据"""
    try:
        # 按类型统计车辆
        type_stats = db.session.query(
            Vehicle.vehicle_type,
            db.func.count(Vehicle.id).label('count')
        ).group_by(Vehicle.vehicle_type).all()
        
        # 按颜色统计车辆
        color_stats = db.session.query(
            Vehicle.color,
            db.func.count(Vehicle.id).label('count')
        ).group_by(Vehicle.color).all()
        
        # 按风险等级统计
        risk_stats = db.session.query(
            Vehicle.risk_level,
            db.func.count(Vehicle.id).label('count')
        ).group_by(Vehicle.risk_level).all()
        
        # 可疑车辆趋势（最近7天）
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        suspicious_trend = db.session.query(
            db.func.date(Vehicle.created_at).label('date'),
            db.func.count(Vehicle.id).label('count')
        ).filter(
            Vehicle.is_suspicious == True,
            Vehicle.created_at >= seven_days_ago
        ).group_by(
            db.func.date(Vehicle.created_at)
        ).all()
        
        # 告警数量趋势（最近7天）
        alert_trend = db.session.query(
            db.func.date(VehicleAlert.created_at).label('date'),
            db.func.count(VehicleAlert.id).label('count')
        ).filter(
            VehicleAlert.created_at >= seven_days_ago
        ).group_by(
            db.func.date(VehicleAlert.created_at)
        ).all()
        
        return jsonify({
            'typeStats': [
                {'name': stat.vehicle_type or '未知', 'value': stat.count}
                for stat in type_stats
            ],
            'colorStats': [
                {'name': stat.color or '未知', 'value': stat.count}
                for stat in color_stats
            ],
            'riskStats': [
                {'name': stat.risk_level or '未知', 'value': stat.count}
                for stat in risk_stats
            ],
            'suspiciousTrend': {
                'dates': [stat.date.strftime('%Y-%m-%d') for stat in suspicious_trend],
                'data': [stat.count for stat in suspicious_trend]
            },
            'alertTrend': {
                'dates': [stat.date.strftime('%Y-%m-%d') for stat in alert_trend],
                'data': [stat.count for stat in alert_trend]
            }
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆分析数据失败: {str(e)}')
        return jsonify({'error': '获取车辆分析数据失败'}), 500

@analytics_bp.route('/alert-analysis', methods=['GET'])
@jwt_required()
def get_alert_analysis():
    """获取告警分析数据"""
    try:
        # 按类型统计告警
        type_stats = db.session.query(
            VehicleAlert.alert_type,
            db.func.count(VehicleAlert.id).label('count')
        ).group_by(VehicleAlert.alert_type).all()
        
        # 按严重程度统计告警
        severity_stats = db.session.query(
            VehicleAlert.severity,
            db.func.count(VehicleAlert.id).label('count')
        ).group_by(VehicleAlert.severity).all()
        
        # 按状态统计告警
        status_stats = db.session.query(
            VehicleAlert.is_read,
            db.func.count(VehicleAlert.id).label('count')
        ).group_by(VehicleAlert.is_read).all()
        
        # 告警趋势（最近7天）
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        alert_trend = db.session.query(
            db.func.date(VehicleAlert.created_at).label('date'),
            db.func.count(VehicleAlert.id).label('count')
        ).filter(
            VehicleAlert.created_at >= seven_days_ago
        ).group_by(
            db.func.date(VehicleAlert.created_at)
        ).all()
        
        # 按摄像头统计告警
        camera_alert_stats = db.session.query(
            VehicleAlert.camera_id,
            db.func.count(VehicleAlert.id).label('count')
        ).filter(
            VehicleAlert.camera_id.isnot(None)
        ).group_by(VehicleAlert.camera_id).all()
        
        return jsonify({
            'typeStats': [
                {'name': stat.alert_type or '未知', 'value': stat.count}
                for stat in type_stats
            ],
            'severityStats': [
                {'name': stat.severity or '未知', 'value': stat.count}
                for stat in severity_stats
            ],
            'statusStats': [
                {'name': '已读' if stat.is_read else '未读', 'value': stat.count}
                for stat in status_stats
            ],
            'alertTrend': {
                'dates': [stat.date.strftime('%Y-%m-%d') for stat in alert_trend],
                'data': [stat.count for stat in alert_trend]
            },
            'cameraAlertStats': [
                {'cameraId': stat.camera_id, 'count': stat.count}
                for stat in camera_alert_stats
            ]
        }), 200
        
    except Exception as e:
        logger.error(f'获取告警分析数据失败: {str(e)}')
        return jsonify({'error': '获取告警分析数据失败'}), 500

@analytics_bp.route('/ai-performance', methods=['GET'])
@jwt_required()
def get_ai_performance():
    """获取AI性能数据"""
    try:
        # 检测统计
        total_detections = VehicleDetection.query.count()
        
        # 按摄像头统计检测
        camera_detection_stats = db.session.query(
            VehicleDetection.camera_id,
            db.func.count(VehicleDetection.id).label('count')
        ).group_by(VehicleDetection.camera_id).all()
        
        # 平均置信度
        avg_confidence = db.session.query(
            db.func.avg(VehicleDetection.confidence)
        ).scalar() or 0
        
        # 检测趋势（最近7天）
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        detection_trend = db.session.query(
            db.func.date(VehicleDetection.detected_at).label('date'),
            db.func.count(VehicleDetection.id).label('count')
        ).filter(
            VehicleDetection.detected_at >= seven_days_ago
        ).group_by(
            db.func.date(VehicleDetection.detected_at)
        ).all()
        
        return jsonify({
            'totalDetections': total_detections,
            'avgConfidence': round(avg_confidence, 3),
            'cameraStats': [
                {'cameraId': stat.camera_id, 'count': stat.count}
                for stat in camera_detection_stats
            ],
            'detectionTrend': {
                'dates': [stat.date.strftime('%Y-%m-%d') for stat in detection_trend],
                'data': [stat.count for stat in detection_trend]
            }
        }), 200
        
    except Exception as e:
        logger.error(f'获取AI性能数据失败: {str(e)}')
        return jsonify({'error': '获取AI性能数据失败'}), 500

@analytics_bp.route('/export', methods=['POST'])
@jwt_required()
def export_data():
    """导出数据"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'vehicles')
        
        if export_type == 'vehicles':
            vehicles = Vehicle.query.all()
            export_data = [
                {
                    'id': v.id,
                    'plateNumber': v.plate_number,
                    'vehicleType': v.vehicle_type,
                    'color': v.color,
                    'riskLevel': v.risk_level,
                    'isSuspicious': v.is_suspicious,
                    'createdAt': v.created_at.isoformat()
                } for v in vehicles
            ]
        elif export_type == 'alerts':
            alerts = VehicleAlert.query.all()
            export_data = [
                {
                    'id': a.id,
                    'message': a.message,
                    'alertType': a.alert_type,
                    'severity': a.severity,
                    'isRead': a.is_read,
                    'createdAt': a.created_at.isoformat()
                } for a in alerts
            ]
        else:
            return jsonify({'error': '不支持的导出类型'}), 400
        
        return jsonify({
            'data': export_data,
            'count': len(export_data),
            'exportedAt': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f'导出数据失败: {str(e)}')
        return jsonify({'error': '导出数据失败'}), 500
