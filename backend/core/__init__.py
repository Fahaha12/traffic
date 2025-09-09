"""
核心模块
包含数据库、模型、工具等核心组件
"""
from .database import db
from .models import Camera, Vehicle, VehicleDetection, VehicleAlert
from .stream_tools import stream_manager
from .stream_converter import stream_converter
from .cleanup_service import TempFileCleaner
from .stream_routes import stream_bp
from .utils import (
    generate_id, format_datetime, safe_get, validate_required_fields,
    validate_enum_value, sanitize_string, calculate_distance,
    format_file_size, is_valid_coordinate, create_response
)

__all__ = [
    'db', 'Camera', 'Vehicle', 'VehicleDetection', 'VehicleAlert',
    'stream_manager', 'stream_converter', 'TempFileCleaner', 'stream_bp',
    'generate_id', 'format_datetime', 'safe_get',
    'validate_required_fields', 'validate_enum_value', 'sanitize_string',
    'calculate_distance', 'format_file_size', 'is_valid_coordinate', 'create_response'
]
