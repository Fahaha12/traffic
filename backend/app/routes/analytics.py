"""
数据分析API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.camera import Camera
from app.models.vehicle import Vehicle, VehicleTrack, VehicleAlert
from app.models.alert import Alert
from app.models.ai_model import ModelPrediction
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)

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
        total_alerts = Alert.query.count()
        active_alerts = Alert.query.filter_by(status='active').count()
        unread_alerts = Alert.query.filter_by(is_read=False).count()
        
        # 最近24小时的活动
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_tracks = VehicleTrack.query.filter(
            VehicleTrack.timestamp >= yesterday
        ).count()
        recent_predictions = ModelPrediction.query.filter(
            ModelPrediction.timestamp >= yesterday
        ).count()
        
        # 最近告警
        recent_alerts = Alert.query.filter(
            Alert.created_at >= yesterday
        ).order_by(Alert.created_at.desc()).limit(5).all()
        
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
                'active': active_alerts,
                'unread': unread_alerts
            },
            'activity': {
                'recentTracks': recent_tracks,
                'recentPredictions': recent_predictions
            },
            'recentAlerts': [alert.to_dict() for alert in recent_alerts],
            'recentCameras': [camera.to_dict() for camera in recent_cameras]
        }), 200
        
    except Exception as e:
        logger.error(f'获取仪表板数据失败: {str(e)}')
        return jsonify({'error': '获取仪表板数据失败'}), 500

@analytics_bp.route('/traffic-flow', methods=['GET'])
@jwt_required()
def get_traffic_flow():
    """获取交通流量数据"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        camera_id = request.args.get('camera_id')
        
        # 默认查询最近7天
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        if not end_date:
            end_date = datetime.utcnow().isoformat()
        
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        query = VehicleTrack.query.filter(
            VehicleTrack.timestamp >= start_dt,
            VehicleTrack.timestamp <= end_dt
        )
        
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        
        tracks = query.all()
        
        # 按小时统计流量
        hourly_flow = {}
        for track in tracks:
            hour = track.timestamp.hour
            if hour not in hourly_flow:
                hourly_flow[hour] = 0
            hourly_flow[hour] += 1
        
        # 按日期统计流量
        daily_flow = {}
        for track in tracks:
            date = track.timestamp.date().isoformat()
            if date not in daily_flow:
                daily_flow[date] = 0
            daily_flow[date] += 1
        
        # 按摄像头统计流量
        camera_flow = {}
        for track in tracks:
            if track.camera_id not in camera_flow:
                camera_flow[track.camera_id] = 0
            camera_flow[track.camera_id] += 1
        
        return jsonify({
            'hourlyFlow': hourly_flow,
            'dailyFlow': daily_flow,
            'cameraFlow': camera_flow,
            'totalTracks': len(tracks)
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
            db.func.count(Vehicle.id)
        ).group_by(Vehicle.vehicle_type).all()
        
        # 按颜色统计车辆
        color_stats = db.session.query(
            Vehicle.color,
            db.func.count(Vehicle.id)
        ).group_by(Vehicle.color).all()
        
        # 按风险等级统计
        risk_stats = db.session.query(
            Vehicle.risk_level,
            db.func.count(Vehicle.id)
        ).group_by(Vehicle.risk_level).all()
        
        # 可疑车辆趋势（最近30天）
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        suspicious_trend = db.session.query(
            db.func.date(Vehicle.updated_at),
            db.func.count(Vehicle.id)
        ).filter(
            Vehicle.is_suspicious == True,
            Vehicle.updated_at >= thirty_days_ago
        ).group_by(
            db.func.date(Vehicle.updated_at)
        ).all()
        
        return jsonify({
            'typeStats': dict(type_stats),
            'colorStats': dict(color_stats),
            'riskStats': dict(risk_stats),
            'suspiciousTrend': dict(suspicious_trend)
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
            Alert.alert_type,
            db.func.count(Alert.id)
        ).group_by(Alert.alert_type).all()
        
        # 按严重程度统计告警
        severity_stats = db.session.query(
            Alert.severity,
            db.func.count(Alert.id)
        ).group_by(Alert.severity).all()
        
        # 按状态统计告警
        status_stats = db.session.query(
            Alert.status,
            db.func.count(Alert.id)
        ).group_by(Alert.status).all()
        
        # 告警趋势（最近30天）
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        alert_trend = db.session.query(
            db.func.date(Alert.created_at),
            db.func.count(Alert.id)
        ).filter(
            Alert.created_at >= thirty_days_ago
        ).group_by(
            db.func.date(Alert.created_at)
        ).all()
        
        # 按摄像头统计告警
        camera_alert_stats = db.session.query(
            Alert.camera_id,
            db.func.count(Alert.id)
        ).filter(
            Alert.camera_id.isnot(None)
        ).group_by(Alert.camera_id).all()
        
        return jsonify({
            'typeStats': dict(type_stats),
            'severityStats': dict(severity_stats),
            'statusStats': dict(status_stats),
            'alertTrend': dict(alert_trend),
            'cameraAlertStats': dict(camera_alert_stats)
        }), 200
        
    except Exception as e:
        logger.error(f'获取告警分析数据失败: {str(e)}')
        return jsonify({'error': '获取告警分析数据失败'}), 500

@analytics_bp.route('/ai-performance', methods=['GET'])
@jwt_required()
def get_ai_performance():
    """获取AI性能数据"""
    try:
        # 按模型统计预测次数
        model_stats = db.session.query(
            ModelPrediction.model_id,
            db.func.count(ModelPrediction.id)
        ).group_by(ModelPrediction.model_id).all()
        
        # 按类型统计预测次数
        type_stats = db.session.query(
            ModelPrediction.prediction_type,
            db.func.count(ModelPrediction.id)
        ).group_by(ModelPrediction.prediction_type).all()
        
        # 平均处理时间
        avg_processing_time = db.session.query(
            db.func.avg(ModelPrediction.processing_time)
        ).scalar() or 0
        
        # 平均置信度
        avg_confidence = db.session.query(
            db.func.avg(ModelPrediction.confidence)
        ).scalar() or 0
        
        # 预测趋势（最近30天）
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        prediction_trend = db.session.query(
            db.func.date(ModelPrediction.timestamp),
            db.func.count(ModelPrediction.id)
        ).filter(
            ModelPrediction.timestamp >= thirty_days_ago
        ).group_by(
            db.func.date(ModelPrediction.timestamp)
        ).all()
        
        return jsonify({
            'modelStats': dict(model_stats),
            'typeStats': dict(type_stats),
            'avgProcessingTime': round(avg_processing_time, 3),
            'avgConfidence': round(avg_confidence, 3),
            'predictionTrend': dict(prediction_trend)
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
        export_type = data.get('type')  # cameras, vehicles, alerts, tracks
        format_type = data.get('format', 'json')  # json, csv, excel
        filters = data.get('filters', {})
        
        # 这里应该实现实际的数据导出逻辑
        # 现在返回模拟响应
        
        return jsonify({
            'message': '数据导出功能开发中',
            'exportType': export_type,
            'format': format_type,
            'filters': filters
        }), 200
        
    except Exception as e:
        logger.error(f'导出数据失败: {str(e)}')
        return jsonify({'error': '导出数据失败'}), 500
