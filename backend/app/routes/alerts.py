"""
告警管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.alert import Alert
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """获取告警列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        severity = request.args.get('severity')
        alert_type = request.args.get('type')
        is_read = request.args.get('is_read')
        
        query = Alert.query
        
        if status:
            query = query.filter_by(status=status)
        if severity:
            query = query.filter_by(severity=severity)
        if alert_type:
            query = query.filter_by(alert_type=alert_type)
        if is_read is not None:
            query = query.filter_by(is_read=is_read.lower() == 'true')
        
        alerts = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts.items],
            'total': alerts.total,
            'page': page,
            'per_page': per_page,
            'pages': alerts.pages
        }), 200
        
    except Exception as e:
        logger.error(f'获取告警列表失败: {str(e)}')
        return jsonify({'error': '获取告警列表失败'}), 500

@alerts_bp.route('/<alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    """获取单个告警信息"""
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        return jsonify({
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'获取告警信息失败: {str(e)}')
        return jsonify({'error': '获取告警信息失败'}), 500

@alerts_bp.route('/<alert_id>/acknowledge', methods=['POST'])
@jwt_required()
def acknowledge_alert(alert_id):
    """确认告警"""
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        user_id = get_jwt_identity()
        alert.acknowledge(user_id)
        
        return jsonify({
            'message': '告警已确认',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'确认告警失败: {str(e)}')
        return jsonify({'error': '确认告警失败'}), 500

@alerts_bp.route('/<alert_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_alert(alert_id):
    """解决告警"""
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        user_id = get_jwt_identity()
        alert.resolve(user_id)
        
        return jsonify({
            'message': '告警已解决',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'解决告警失败: {str(e)}')
        return jsonify({'error': '解决告警失败'}), 500

@alerts_bp.route('/<alert_id>/read', methods=['POST'])
@jwt_required()
def mark_alert_read(alert_id):
    """标记告警为已读"""
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': '告警不存在'}), 404
        
        alert.mark_as_read()
        
        return jsonify({
            'message': '告警已标记为已读',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'标记告警已读失败: {str(e)}')
        return jsonify({'error': '标记告警已读失败'}), 500

@alerts_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_alerts():
    """获取活跃告警"""
    try:
        alerts = Alert.get_active_alerts()
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
        
    except Exception as e:
        logger.error(f'获取活跃告警失败: {str(e)}')
        return jsonify({'error': '获取活跃告警失败'}), 500

@alerts_bp.route('/unread', methods=['GET'])
@jwt_required()
def get_unread_alerts():
    """获取未读告警"""
    try:
        alerts = Alert.get_unread_alerts()
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
        
    except Exception as e:
        logger.error(f'获取未读告警失败: {str(e)}')
        return jsonify({'error': '获取未读告警失败'}), 500

@alerts_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_alert_stats():
    """获取告警统计信息"""
    try:
        # 总告警数
        total_alerts = Alert.query.count()
        
        # 活跃告警数
        active_alerts = Alert.query.filter_by(status='active').count()
        
        # 未读告警数
        unread_alerts = Alert.query.filter_by(is_read=False).count()
        
        # 按类型统计
        type_stats = db.session.query(
            Alert.alert_type,
            db.func.count(Alert.id)
        ).group_by(Alert.alert_type).all()
        
        # 按严重程度统计
        severity_stats = db.session.query(
            Alert.severity,
            db.func.count(Alert.id)
        ).group_by(Alert.severity).all()
        
        # 按状态统计
        status_stats = db.session.query(
            Alert.status,
            db.func.count(Alert.id)
        ).group_by(Alert.status).all()
        
        # 最近24小时的告警数
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_alerts = Alert.query.filter(
            Alert.created_at >= yesterday
        ).count()
        
        return jsonify({
            'totalAlerts': total_alerts,
            'activeAlerts': active_alerts,
            'unreadAlerts': unread_alerts,
            'typeStats': dict(type_stats),
            'severityStats': dict(severity_stats),
            'statusStats': dict(status_stats),
            'recentAlerts': recent_alerts
        }), 200
        
    except Exception as e:
        logger.error(f'获取告警统计失败: {str(e)}')
        return jsonify({'error': '获取告警统计失败'}), 500
