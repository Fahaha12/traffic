// 系统常量定义

// 地图相关常量
export const MAP_CONSTANTS = {
  DEFAULT_CENTER: [39.9042, 116.4074] as [number, number], // 北京天安门
  DEFAULT_ZOOM: 12,
  MIN_ZOOM: 8,
  MAX_ZOOM: 18,
  TILE_URL: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  ATTRIBUTION: '© OpenStreetMap contributors'
}

// 摄像头相关常量
export const CAMERA_CONSTANTS = {
  MAX_CAMERAS: 50,
  STREAM_QUALITIES: ['low', 'medium', 'high'] as const,
  CAMERA_TYPES: ['traffic', 'surveillance', 'speed'] as const,
  STATUS_TYPES: ['online', 'offline', 'maintenance'] as const,
  DEFAULT_FPS: 25,
  DEFAULT_RESOLUTION: { width: 1920, height: 1080 }
}

// 车辆相关常量
export const VEHICLE_CONSTANTS = {
  VEHICLE_TYPES: ['car', 'truck', 'bus', 'motorcycle', 'unknown'] as const,
  SUSPICIOUS_REASONS: ['speed_violation', 'wrong_way', 'stolen_vehicle', 'wanted_person', 'custom'] as const,
  SEVERITY_LEVELS: ['low', 'medium', 'high', 'critical'] as const,
  ALERT_TYPES: ['suspicious', 'violation', 'emergency'] as const,
  MAX_TRAJECTORY_POINTS: 1000,
  TRAJECTORY_UPDATE_INTERVAL: 5000 // 5秒
}

// 用户相关常量
export const USER_CONSTANTS = {
  ROLES: ['admin', 'operator', 'viewer'] as const,
  PERMISSIONS: [
    'camera:view',
    'camera:manage',
    'vehicle:view',
    'vehicle:manage',
    'alert:view',
    'alert:manage',
    'system:view',
    'system:manage'
  ] as const,
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30分钟
  MAX_LOGIN_ATTEMPTS: 5
}

// 系统配置常量
export const SYSTEM_CONSTANTS = {
  REFRESH_INTERVALS: {
    CAMERA_STATUS: 10000, // 10秒
    VEHICLE_DATA: 5000,   // 5秒
    ALERT_DATA: 3000,     // 3秒
    MAP_DATA: 15000       // 15秒
  },
  CACHE_DURATION: {
    CAMERA_LIST: 5 * 60 * 1000,    // 5分钟
    VEHICLE_LIST: 2 * 60 * 1000,   // 2分钟
    USER_INFO: 30 * 60 * 1000,     // 30分钟
    SYSTEM_CONFIG: 60 * 60 * 1000  // 1小时
  },
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  WEBSOCKET_HEARTBEAT_INTERVAL: 30000, // 30秒
  WEBSOCKET_RECONNECT_DELAY: 3000      // 3秒
}

// 颜色常量
export const COLOR_CONSTANTS = {
  STATUS: {
    ONLINE: '#67c23a',
    OFFLINE: '#f56c6c',
    MAINTENANCE: '#e6a23c',
    UNKNOWN: '#909399'
  },
  VEHICLE: {
    CAR: '#409eff',
    TRUCK: '#e6a23c',
    BUS: '#67c23a',
    MOTORCYCLE: '#f56c6c',
    UNKNOWN: '#909399'
  },
  SEVERITY: {
    LOW: '#67c23a',
    MEDIUM: '#e6a23c',
    HIGH: '#f56c6c',
    CRITICAL: '#ff0000'
  },
  TRAJECTORY: {
    NORMAL: '#409eff',
    SUSPICIOUS: '#ff6b6b',
    ALERT: '#ff0000'
  }
}

// 图标常量
export const ICON_CONSTANTS = {
  CAMERA: 'VideoCamera',
  VEHICLE: 'Truck',
  ALERT: 'Bell',
  WARNING: 'Warning',
  SUCCESS: 'SuccessFilled',
  ERROR: 'CircleCloseFilled',
  INFO: 'InfoFilled',
  SETTING: 'Setting',
  USER: 'User',
  MAP: 'Location',
  CHART: 'DataAnalysis'
}

// 本地存储键名
export const STORAGE_KEYS = {
  USER_TOKEN: 'traffic_monitor_token',
  USER_INFO: 'traffic_monitor_user',
  SYSTEM_CONFIG: 'traffic_monitor_config',
  MAP_CONFIG: 'traffic_monitor_map_config',
  THEME: 'traffic_monitor_theme',
  LANGUAGE: 'traffic_monitor_language'
}

// 事件名称常量
export const EVENT_CONSTANTS = {
  // WebSocket事件
  WS_CAMERA_STATUS_UPDATE: 'camera_status_update',
  WS_CAMERA_STREAM_EVENT: 'camera_stream_event',
  WS_VEHICLE_DETECTION: 'vehicle_detection',
  WS_VEHICLE_REID: 'vehicle_reid',
  WS_SUSPICIOUS_VEHICLE: 'suspicious_vehicle',
  WS_VEHICLE_ALERT: 'vehicle_alert',
  WS_VEHICLE_TRAJECTORY: 'vehicle_trajectory',
  WS_PING: 'ping',
  WS_PONG: 'pong',
  
  // 应用事件
  APP_THEME_CHANGE: 'app_theme_change',
  APP_LANGUAGE_CHANGE: 'app_language_change',
  APP_USER_LOGIN: 'app_user_login',
  APP_USER_LOGOUT: 'app_user_logout',
  APP_DATA_REFRESH: 'app_data_refresh'
}

// 错误代码常量
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  PERMISSION_ERROR: 'PERMISSION_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
}

// 成功消息常量
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: '登录成功',
  LOGOUT_SUCCESS: '退出成功',
  SAVE_SUCCESS: '保存成功',
  DELETE_SUCCESS: '删除成功',
  UPDATE_SUCCESS: '更新成功',
  UPLOAD_SUCCESS: '上传成功',
  CONNECT_SUCCESS: '连接成功',
  DISCONNECT_SUCCESS: '断开连接成功'
}

// 错误消息常量
export const ERROR_MESSAGES = {
  LOGIN_FAILED: '登录失败',
  NETWORK_ERROR: '网络连接错误',
  PERMISSION_DENIED: '权限不足',
  VALIDATION_FAILED: '数据验证失败',
  SERVER_ERROR: '服务器错误',
  UNKNOWN_ERROR: '未知错误',
  CONNECTION_FAILED: '连接失败',
  DATA_LOAD_FAILED: '数据加载失败'
}
