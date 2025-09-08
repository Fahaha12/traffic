"""
数据库模型包
"""

from .user import User
from .camera import Camera
from .vehicle import Vehicle, VehicleAlert, VehicleTrack
from .alert import Alert
from .ai_model import AIModel, ModelPrediction
from .detection import VehicleDetection
from .reid import VehicleReIDFeature

__all__ = [
    'User',
    'Camera', 
    'Vehicle',
    'VehicleAlert',
    'VehicleTrack',
    'Alert',
    'AIModel',
    'ModelPrediction',
    'VehicleDetection',
    'VehicleReIDFeature'
]