"""
摄像头模型
"""

from app import db
from datetime import datetime
import uuid
import json

class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # traffic, surveillance, speed
    position_lat = db.Column(db.Float, nullable=False)
    position_lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='offline')  # online, offline, maintenance
    stream_url = db.Column(db.String(500), nullable=False)
    stream_type = db.Column(db.String(20), nullable=False)  # rtmp, hls, http
    resolution_width = db.Column(db.Integer, default=1920)
    resolution_height = db.Column(db.Integer, default=1080)
    fps = db.Column(db.Integer, default=25)
    direction = db.Column(db.Float, default=0)  # 朝向角度
    is_recording = db.Column(db.Boolean, default=False)
    last_heartbeat = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    alerts = db.relationship('Alert', backref='camera', lazy='dynamic')
    predictions = db.relationship('ModelPrediction', backref='camera', lazy='dynamic')
    
    def __repr__(self):
        return f'<Camera {self.name}>'
    
    @property
    def position(self):
        """获取位置信息"""
        return {
            'lat': self.position_lat,
            'lng': self.position_lng
        }
    
    @position.setter
    def position(self, value):
        """设置位置信息"""
        if isinstance(value, dict):
            self.position_lat = value.get('lat')
            self.position_lng = value.get('lng')
        elif isinstance(value, (list, tuple)) and len(value) >= 2:
            self.position_lat = value[0]
            self.position_lng = value[1]
    
    @property
    def resolution(self):
        """获取分辨率信息"""
        return {
            'width': self.resolution_width,
            'height': self.resolution_height
        }
    
    @resolution.setter
    def resolution(self, value):
        """设置分辨率信息"""
        if isinstance(value, dict):
            self.resolution_width = value.get('width', 1920)
            self.resolution_height = value.get('height', 1080)
        elif isinstance(value, (list, tuple)) and len(value) >= 2:
            self.resolution_width = value[0]
            self.resolution_height = value[1]
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'position': self.position,
            'status': self.status,
            'streamUrl': self.stream_url,
            'streamType': self.stream_type,
            'resolution': self.resolution,
            'fps': self.fps,
            'direction': self.direction,
            'isRecording': self.is_recording,
            'lastHeartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }
    
    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = datetime.utcnow()
        db.session.commit()
    
    def is_online(self):
        """检查是否在线"""
        if not self.last_heartbeat:
            return False
        # 如果超过5分钟没有心跳，认为离线
        return (datetime.utcnow() - self.last_heartbeat).total_seconds() < 300
    
    @classmethod
    def get_online_cameras(cls):
        """获取在线摄像头"""
        return cls.query.filter_by(status='online').all()
    
    @classmethod
    def get_by_location(cls, lat, lng, radius=0.01):
        """根据位置获取摄像头"""
        return cls.query.filter(
            db.and_(
                db.func.abs(cls.position_lat - lat) <= radius,
                db.func.abs(cls.position_lng - lng) <= radius
            )
        ).all()
