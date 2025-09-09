"""
工具函数模块
包含通用的工具函数和辅助方法
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def generate_id() -> str:
    """生成UUID字符串"""
    return str(uuid.uuid4())

def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """格式化日期时间为ISO字符串"""
    if dt is None:
        return None
    return dt.isoformat()

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """安全获取字典值"""
    try:
        return data.get(key, default)
    except (AttributeError, TypeError):
        return default

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Optional[str]:
    """验证必填字段"""
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            return f"缺少必填字段: {field}"
    return None

def validate_enum_value(value: Any, valid_values: list) -> bool:
    """验证枚举值"""
    return value in valid_values

def sanitize_string(value: str, max_length: int = 255) -> str:
    """清理字符串，移除危险字符并限制长度"""
    if not isinstance(value, str):
        return str(value)
    
    # 移除潜在的危险字符
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    # 限制长度
    if len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间距离（公里）"""
    from math import radians, cos, sin, asin, sqrt
    
    # 将十进制度数转化为弧度
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # 地球半径（公里）
    r = 6371
    return c * r

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def is_valid_coordinate(lat: float, lng: float) -> bool:
    """验证坐标是否有效"""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def create_response(success: bool, message: str, data: Any = None, status_code: int = 200) -> Dict[str, Any]:
    """创建标准API响应"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    return response, status_code
