"""
数据库模型定义
"""
from datetime import datetime
import logging
from .database import db

logger = logging.getLogger(__name__)

class Camera(db.Model):
    """摄像头模型"""
    __tablename__ = 'cameras'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.Enum('traffic', 'surveillance', 'speed', 'reid'), nullable=False)
    position_lat = db.Column(db.Float, nullable=False)
    position_lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('online', 'offline', 'maintenance'), nullable=True)
    stream_url = db.Column(db.String(500), nullable=False)
    stream_type = db.Column(db.Enum('rtmp', 'hls', 'http', 'webrtc'), nullable=False)
    resolution_width = db.Column(db.Integer, nullable=True)
    resolution_height = db.Column(db.Integer, nullable=True)
    fps = db.Column(db.Integer, nullable=True)
    direction = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'position': {
                'lat': self.position_lat,
                'lng': self.position_lng
            },
            'status': self.status,
            'streamUrl': self.stream_url,
            'streamType': self.stream_type,
            'resolution': {
                'width': self.resolution_width,
                'height': self.resolution_height
            },
            'fps': self.fps,
            'direction': self.direction,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'lastUpdate': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_actual_status(self):
        """获取实际状态（检查真实的连接状态）"""
        try:
            # 如果数据库状态是online，直接返回
            if self.status == 'online':
                return 'online'
            
            # 如果数据库状态是maintenance，直接返回
            if self.status == 'maintenance':
                return 'maintenance'
            
            # 对于offline状态，进行实际的连接检测
            if self.stream_type == 'hls':
                return self._check_hls_connection()
            elif self.stream_type == 'rtmp':
                return self._check_rtmp_connection()
            elif self.stream_type == 'http':
                return self._check_http_connection()
            elif self.stream_type == 'webrtc':
                return self._check_webrtc_connection()
            else:
                return 'offline'
                
        except Exception as e:
            logger.error(f'检测摄像头 {self.name} 状态失败: {str(e)}')
            return 'offline'
    
    def _check_hls_connection(self):
        """检查HLS流连接"""
        try:
            import requests
            response = requests.get(self.stream_url, timeout=5)
            if response.status_code == 200:
                # 检查是否包含HLS相关内容
                content_type = response.headers.get('content-type', '')
                if 'application/vnd.apple.mpegurl' in content_type or 'm3u8' in self.stream_url:
                    return 'online'
            return 'offline'
        except Exception:
            return 'offline'
    
    def _check_rtmp_connection(self):
        """检查RTMP流连接"""
        try:
            # 对于RTMP流，检查是否有对应的HLS转换
            from .stream_tools import stream_manager
            status = stream_manager.get_conversion_status(self.id)
            if status and status.get('status') == 'converting':
                return 'online'
            return 'offline'
        except Exception:
            return 'offline'
    
    def _check_http_connection(self):
        """检查HTTP流连接"""
        try:
            import requests
            response = requests.head(self.stream_url, timeout=5)
            if response.status_code == 200:
                return 'online'
            return 'offline'
        except Exception:
            return 'offline'
    
    def _check_webrtc_connection(self):
        """检查WebRTC连接"""
        # WebRTC连接检测比较复杂，这里暂时返回offline
        # 在实际应用中，可以通过WebRTC API进行检测
        return 'offline'

class Vehicle(db.Model):
    """车辆模型"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.String(36), primary_key=True)
    plate_number = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False)  # car, truck, bus, motorcycle, bicycle, unknown
    color = db.Column(db.String(20), nullable=True)
    brand = db.Column(db.String(50), nullable=True)
    model = db.Column(db.String(50), nullable=True)
    is_suspicious = db.Column(db.Boolean, nullable=True, default=False)
    risk_level = db.Column(db.String(20), nullable=True)  # low, medium, high, critical
    created_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plateNumber': self.plate_number,
            'vehicleType': self.vehicle_type,
            'color': self.color,
            'brand': self.brand,
            'model': self.model,
            'isSuspicious': self.is_suspicious,
            'riskLevel': self.risk_level,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

class VehicleDetection(db.Model):
    """车辆检测记录模型"""
    __tablename__ = 'vehicle_detections'
    
    id = db.Column(db.String(36), primary_key=True)
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicles.id'), nullable=False)
    camera_id = db.Column(db.String(36), nullable=False)
    detected_at = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=True, default=0.9)
    speed = db.Column(db.Float, nullable=True, default=0)
    direction = db.Column(db.Float, nullable=True, default=0)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicleId': self.vehicle_id,
            'cameraId': self.camera_id,
            'detectedAt': self.detected_at.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'confidence': self.confidence,
            'speed': self.speed,
            'direction': self.direction,
            'imageUrl': self.image_url,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

class VehicleAlert(db.Model):
    """车辆告警模型"""
    __tablename__ = 'vehicle_alerts'
    
    id = db.Column(db.String(36), primary_key=True)
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicles.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), nullable=True, default='medium')
    is_read = db.Column(db.Boolean, nullable=True, default=False)
    is_resolved = db.Column(db.Boolean, nullable=True, default=False)
    created_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicleId': self.vehicle_id,
            'alertType': self.alert_type,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'isRead': self.is_read,
            'isResolved': self.is_resolved,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'readAt': self.read_at.isoformat() if self.read_at else None,
            'resolvedAt': self.resolved_at.isoformat() if self.resolved_at else None
        }
