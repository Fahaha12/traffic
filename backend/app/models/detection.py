"""
车辆检测模型
"""

from app import db
from datetime import datetime
import uuid

class VehicleDetection(db.Model):
    __tablename__ = 'vehicle_detections'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    camera_id = db.Column(db.String(36), db.ForeignKey('cameras.id'), nullable=False)
    detection_time = db.Column(db.DateTime, nullable=False, index=True)
    bbox_x1 = db.Column(db.Float, nullable=False)
    bbox_y1 = db.Column(db.Float, nullable=False)
    bbox_x2 = db.Column(db.Float, nullable=False)
    bbox_y2 = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    vehicle_type = db.Column(db.Enum('car', 'truck', 'bus', 'motorcycle', 'bicycle', 'unknown'), nullable=False)
    color = db.Column(db.String(20))
    speed = db.Column(db.Float)
    direction = db.Column(db.Float)
    position_lat = db.Column(db.Float)
    position_lng = db.Column(db.Float)
    image_path = db.Column(db.String(500))
    model_id = db.Column(db.String(36), db.ForeignKey('ai_models.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    camera = db.relationship('Camera', backref='detections')
    model = db.relationship('AIModel', backref='detections')
    reid_features = db.relationship('VehicleReIDFeature', backref='detection', lazy='dynamic')
    
    def __repr__(self):
        return f'<VehicleDetection {self.id}>'
    
    @property
    def bbox(self):
        """获取边界框信息"""
        return {
            'x1': self.bbox_x1,
            'y1': self.bbox_y1,
            'x2': self.bbox_x2,
            'y2': self.bbox_y2
        }
    
    @bbox.setter
    def bbox(self, value):
        """设置边界框信息"""
        if isinstance(value, dict):
            self.bbox_x1 = value.get('x1', 0)
            self.bbox_y1 = value.get('y1', 0)
            self.bbox_x2 = value.get('x2', 0)
            self.bbox_y2 = value.get('y2', 0)
        elif isinstance(value, (list, tuple)) and len(value) >= 4:
            self.bbox_x1 = value[0]
            self.bbox_y1 = value[1]
            self.bbox_x2 = value[2]
            self.bbox_y2 = value[3]
    
    @property
    def position(self):
        """获取位置信息"""
        if self.position_lat and self.position_lng:
            return {
                'lat': self.position_lat,
                'lng': self.position_lng
            }
        return None
    
    @position.setter
    def position(self, value):
        """设置位置信息"""
        if isinstance(value, dict):
            self.position_lat = value.get('lat')
            self.position_lng = value.get('lng')
        elif isinstance(value, (list, tuple)) and len(value) >= 2:
            self.position_lat = value[0]
            self.position_lng = value[1]
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'cameraId': self.camera_id,
            'detectionTime': self.detection_time.isoformat(),
            'bbox': self.bbox,
            'confidence': self.confidence,
            'vehicleType': self.vehicle_type,
            'color': self.color,
            'speed': self.speed,
            'direction': self.direction,
            'position': self.position,
            'imagePath': self.image_path,
            'modelId': self.model_id,
            'createdAt': self.created_at.isoformat()
        }
    
    @classmethod
    def get_recent_detections(cls, camera_id=None, limit=100):
        """获取最近的检测记录"""
        query = cls.query
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        return query.order_by(cls.detection_time.desc()).limit(limit).all()
    
    @classmethod
    def get_detections_by_time_range(cls, start_time, end_time, camera_id=None):
        """根据时间范围获取检测记录"""
        query = cls.query.filter(
            cls.detection_time >= start_time,
            cls.detection_time <= end_time
        )
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        return query.order_by(cls.detection_time).all()
    
    @classmethod
    def get_detections_by_vehicle_type(cls, vehicle_type, limit=100):
        """根据车辆类型获取检测记录"""
        return cls.query.filter_by(vehicle_type=vehicle_type)\
                       .order_by(cls.detection_time.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_high_confidence_detections(cls, min_confidence=0.8, limit=100):
        """获取高置信度检测记录"""
        return cls.query.filter(cls.confidence >= min_confidence)\
                       .order_by(cls.detection_time.desc())\
                       .limit(limit).all()
