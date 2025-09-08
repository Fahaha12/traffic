"""
车辆相关模型
"""

from app import db
from datetime import datetime
import uuid
import json

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    vehicle_type = db.Column(db.String(20), nullable=False)  # car, truck, bus, motorcycle
    color = db.Column(db.String(20))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    is_suspicious = db.Column(db.Boolean, default=False)
    risk_level = db.Column(db.String(20), default='low')  # low, medium, high
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    tracks = db.relationship('VehicleTrack', backref='vehicle', lazy='dynamic')
    alerts = db.relationship('VehicleAlert', backref='vehicle', lazy='dynamic')
    
    def __repr__(self):
        return f'<Vehicle {self.plate_number}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'plateNumber': self.plate_number,
            'vehicleType': self.vehicle_type,
            'color': self.color,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'isSuspicious': self.is_suspicious,
            'riskLevel': self.risk_level,
            'lastSeen': self.last_seen.isoformat() if self.last_seen else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }
    
    def update_last_seen(self):
        """更新最后出现时间"""
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_suspicious_vehicles(cls):
        """获取可疑车辆"""
        return cls.query.filter_by(is_suspicious=True).all()
    
    @classmethod
    def get_by_plate(cls, plate_number):
        """根据车牌号获取车辆"""
        return cls.query.filter_by(plate_number=plate_number).first()

class VehicleTrack(db.Model):
    __tablename__ = 'vehicle_tracks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicles.id'), nullable=False)
    camera_id = db.Column(db.String(36), db.ForeignKey('cameras.id'), nullable=False)
    position_lat = db.Column(db.Float, nullable=False)
    position_lng = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float)  # km/h
    direction = db.Column(db.Float)  # 角度
    location_name = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    image_url = db.Column(db.String(500))
    confidence = db.Column(db.Float)  # 检测置信度
    
    def __repr__(self):
        return f'<VehicleTrack {self.vehicle_id} at {self.timestamp}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'vehicleId': self.vehicle_id,
            'cameraId': self.camera_id,
            'position': {
                'lat': self.position_lat,
                'lng': self.position_lng
            },
            'speed': self.speed,
            'direction': self.direction,
            'locationName': self.location_name,
            'timestamp': self.timestamp.isoformat(),
            'imageUrl': self.image_url,
            'confidence': self.confidence
        }
    
    @classmethod
    def get_vehicle_trajectory(cls, vehicle_id, start_time=None, end_time=None):
        """获取车辆轨迹"""
        query = cls.query.filter_by(vehicle_id=vehicle_id)
        if start_time:
            query = query.filter(cls.timestamp >= start_time)
        if end_time:
            query = query.filter(cls.timestamp <= end_time)
        return query.order_by(cls.timestamp).all()

class VehicleAlert(db.Model):
    __tablename__ = 'vehicle_alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicles.id'), nullable=False)
    camera_id = db.Column(db.String(36), db.ForeignKey('cameras.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # speeding, red_light, wrong_lane, etc.
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    description = db.Column(db.Text)
    position_lat = db.Column(db.Float)
    position_lng = db.Column(db.Float)
    speed = db.Column(db.Float)
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<VehicleAlert {self.alert_type} for {self.vehicle_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'vehicleId': self.vehicle_id,
            'cameraId': self.camera_id,
            'alertType': self.alert_type,
            'severity': self.severity,
            'description': self.description,
            'position': {
                'lat': self.position_lat,
                'lng': self.position_lng
            } if self.position_lat and self.position_lng else None,
            'speed': self.speed,
            'isRead': self.is_read,
            'isResolved': self.is_resolved,
            'createdAt': self.created_at.isoformat(),
            'resolvedAt': self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    def mark_as_read(self):
        """标记为已读"""
        self.is_read = True
        db.session.commit()
    
    def mark_as_resolved(self):
        """标记为已解决"""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_unread_alerts(cls):
        """获取未读告警"""
        return cls.query.filter_by(is_read=False).all()
    
    @classmethod
    def get_by_vehicle(cls, vehicle_id):
        """获取车辆的告警"""
        return cls.query.filter_by(vehicle_id=vehicle_id).order_by(cls.created_at.desc()).all()
