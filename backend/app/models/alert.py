"""
告警模型
"""

from app import db
from datetime import datetime
import uuid

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    alert_type = db.Column(db.String(50), nullable=False)  # system, camera, vehicle, ai
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
    source = db.Column(db.String(100))  # 告警来源
    camera_id = db.Column(db.String(36), db.ForeignKey('cameras.id'))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    metadata = db.Column(db.Text)  # JSON格式的额外数据
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Alert {self.title}>'
    
    def to_dict(self):
        """转换为字典"""
        metadata = None
        if self.metadata:
            try:
                import json
                metadata = json.loads(self.metadata)
            except:
                metadata = self.metadata
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'alertType': self.alert_type,
            'severity': self.severity,
            'status': self.status,
            'source': self.source,
            'cameraId': self.camera_id,
            'userId': self.user_id,
            'metadata': metadata,
            'isRead': self.is_read,
            'createdAt': self.created_at.isoformat(),
            'acknowledgedAt': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolvedAt': self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    def acknowledge(self, user_id=None):
        """确认告警"""
        self.status = 'acknowledged'
        self.acknowledged_at = datetime.utcnow()
        if user_id:
            self.user_id = user_id
        db.session.commit()
    
    def resolve(self, user_id=None):
        """解决告警"""
        self.status = 'resolved'
        self.resolved_at = datetime.utcnow()
        if user_id:
            self.user_id = user_id
        db.session.commit()
    
    def mark_as_read(self):
        """标记为已读"""
        self.is_read = True
        db.session.commit()
    
    @classmethod
    def get_active_alerts(cls):
        """获取活跃告警"""
        return cls.query.filter_by(status='active').order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_unread_alerts(cls):
        """获取未读告警"""
        return cls.query.filter_by(is_read=False).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def create_alert(cls, title, description, alert_type, severity='medium', 
                    source=None, camera_id=None, metadata=None):
        """创建告警"""
        alert = cls(
            title=title,
            description=description,
            alert_type=alert_type,
            severity=severity,
            source=source,
            camera_id=camera_id,
            metadata=metadata
        )
        db.session.add(alert)
        db.session.commit()
        return alert
