"""
路由模块初始化
"""
from .auth_routes import auth_bp
from .system_routes import system_bp
from .camera_routes import camera_bp
from .vehicle_routes import vehicle_bp
from .detection_routes import detection_bp
from .analytics_routes import analytics_bp

__all__ = ['auth_bp', 'system_bp', 'camera_bp', 'vehicle_bp', 'detection_bp', 'analytics_bp']
