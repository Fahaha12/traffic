-- 交通监控系统MySQL数据库设计
-- 支持车辆检测、ReID检测、轨迹记录、深度学习应用、路面信息检测

-- 创建数据库
CREATE DATABASE IF NOT EXISTS traffic_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE traffic_monitor;

-- 1. 用户管理表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar VARCHAR(255),
    department VARCHAR(100),
    position VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_is_active (is_active)
);

-- 2. 摄像头表
CREATE TABLE cameras (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('traffic', 'surveillance', 'speed', 'reid') NOT NULL,
    position_lat DECIMAL(10, 8) NOT NULL,
    position_lng DECIMAL(11, 8) NOT NULL,
    status ENUM('online', 'offline', 'maintenance') DEFAULT 'offline',
    stream_url VARCHAR(500) NOT NULL,
    stream_type ENUM('rtmp', 'hls', 'http', 'webrtc') NOT NULL,
    resolution_width INT DEFAULT 1920,
    resolution_height INT DEFAULT 1080,
    fps INT DEFAULT 25,
    direction DECIMAL(5, 2) DEFAULT 0,
    is_recording BOOLEAN DEFAULT FALSE,
    last_heartbeat DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_type (type),
    INDEX idx_position (position_lat, position_lng),
    INDEX idx_last_heartbeat (last_heartbeat)
);

-- 3. 车辆基础信息表
CREATE TABLE vehicles (
    id VARCHAR(36) PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL,
    vehicle_type ENUM('car', 'truck', 'bus', 'motorcycle', 'bicycle', 'unknown') NOT NULL,
    color VARCHAR(20),
    brand VARCHAR(50),
    model VARCHAR(50),
    year INT,
    is_suspicious BOOLEAN DEFAULT FALSE,
    risk_level ENUM('low', 'medium', 'high', 'critical') DEFAULT 'low',
    last_seen DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_plate_number (plate_number),
    INDEX idx_vehicle_type (vehicle_type),
    INDEX idx_is_suspicious (is_suspicious),
    INDEX idx_risk_level (risk_level),
    INDEX idx_last_seen (last_seen)
);

-- 4. 车辆检测记录表
CREATE TABLE vehicle_detections (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) NOT NULL,
    detection_time DATETIME NOT NULL,
    bbox_x1 DECIMAL(8, 2) NOT NULL,
    bbox_y1 DECIMAL(8, 2) NOT NULL,
    bbox_x2 DECIMAL(8, 2) NOT NULL,
    bbox_y2 DECIMAL(8, 2) NOT NULL,
    confidence DECIMAL(4, 3) NOT NULL,
    vehicle_type ENUM('car', 'truck', 'bus', 'motorcycle', 'bicycle', 'unknown') NOT NULL,
    color VARCHAR(20),
    speed DECIMAL(6, 2),
    direction DECIMAL(5, 2),
    image_path VARCHAR(500),
    model_id VARCHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES ai_models(id) ON DELETE SET NULL,
    INDEX idx_camera_detection_time (camera_id, detection_time),
    INDEX idx_detection_time (detection_time),
    INDEX idx_vehicle_type (vehicle_type),
    INDEX idx_confidence (confidence)
);

-- 5. 车辆ReID特征表
CREATE TABLE vehicle_reid_features (
    id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36),
    detection_id VARCHAR(36) NOT NULL,
    feature_vector JSON NOT NULL,
    feature_dimension INT NOT NULL,
    similarity_threshold DECIMAL(4, 3) DEFAULT 0.8,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (detection_id) REFERENCES vehicle_detections(id) ON DELETE CASCADE,
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_detection_id (detection_id),
    INDEX idx_created_at (created_at)
);

-- 6. 车辆轨迹表
CREATE TABLE vehicle_tracks (
    id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    camera_id VARCHAR(36) NOT NULL,
    detection_id VARCHAR(36) NOT NULL,
    position_lat DECIMAL(10, 8) NOT NULL,
    position_lng DECIMAL(11, 8) NOT NULL,
    speed DECIMAL(6, 2),
    direction DECIMAL(5, 2),
    location_name VARCHAR(200),
    timestamp DATETIME NOT NULL,
    image_path VARCHAR(500),
    confidence DECIMAL(4, 3),
    track_sequence INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    FOREIGN KEY (detection_id) REFERENCES vehicle_detections(id) ON DELETE CASCADE,
    INDEX idx_vehicle_timestamp (vehicle_id, timestamp),
    INDEX idx_camera_timestamp (camera_id, timestamp),
    INDEX idx_timestamp (timestamp),
    INDEX idx_track_sequence (track_sequence)
);

-- 7. 车辆轨迹段表（用于多轨迹记录）
CREATE TABLE vehicle_track_segments (
    id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    segment_name VARCHAR(100),
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    start_camera_id VARCHAR(36) NOT NULL,
    end_camera_id VARCHAR(36) NOT NULL,
    total_distance DECIMAL(10, 2),
    average_speed DECIMAL(6, 2),
    max_speed DECIMAL(6, 2),
    track_points JSON,
    is_complete BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (start_camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    FOREIGN KEY (end_camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    INDEX idx_vehicle_segment (vehicle_id, start_time),
    INDEX idx_time_range (start_time, end_time),
    INDEX idx_is_complete (is_complete)
);

-- 8. AI模型表
CREATE TABLE ai_models (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model_type ENUM('detection', 'tracking', 'classification', 'reid', 'road_analysis', 'danger_detection') NOT NULL,
    framework ENUM('pytorch', 'tensorflow', 'onnx', 'openvino') NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    model_path VARCHAR(500) NOT NULL,
    config_path VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    confidence_threshold DECIMAL(4, 3) DEFAULT 0.5,
    input_size VARCHAR(50),
    classes JSON,
    description TEXT,
    performance_metrics JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_model_type (model_type),
    INDEX idx_framework (framework),
    INDEX idx_is_active (is_active)
);

-- 9. 模型预测结果表
CREATE TABLE model_predictions (
    id VARCHAR(36) PRIMARY KEY,
    model_id VARCHAR(36) NOT NULL,
    camera_id VARCHAR(36) NOT NULL,
    prediction_type ENUM('detection', 'tracking', 'classification', 'reid', 'road_analysis', 'danger_detection') NOT NULL,
    input_image_path VARCHAR(500),
    output_image_path VARCHAR(500),
    predictions JSON NOT NULL,
    confidence DECIMAL(4, 3),
    processing_time DECIMAL(8, 4),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES ai_models(id) ON DELETE CASCADE,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    INDEX idx_model_timestamp (model_id, timestamp),
    INDEX idx_camera_timestamp (camera_id, timestamp),
    INDEX idx_prediction_type (prediction_type),
    INDEX idx_timestamp (timestamp)
);

-- 10. 路面信息检测表
CREATE TABLE road_conditions (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) NOT NULL,
    detection_time DATETIME NOT NULL,
    road_type ENUM('highway', 'urban', 'rural', 'bridge', 'tunnel') NOT NULL,
    surface_condition ENUM('dry', 'wet', 'icy', 'snowy', 'flooded') NOT NULL,
    traffic_density ENUM('low', 'medium', 'high', 'congested') NOT NULL,
    visibility_level ENUM('excellent', 'good', 'fair', 'poor', 'very_poor') NOT NULL,
    weather_condition ENUM('clear', 'cloudy', 'rainy', 'snowy', 'foggy', 'stormy') NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    wind_speed DECIMAL(6, 2),
    precipitation DECIMAL(6, 2),
    confidence DECIMAL(4, 3) NOT NULL,
    image_path VARCHAR(500),
    model_id VARCHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES ai_models(id) ON DELETE SET NULL,
    INDEX idx_camera_detection_time (camera_id, detection_time),
    INDEX idx_detection_time (detection_time),
    INDEX idx_road_type (road_type),
    INDEX idx_surface_condition (surface_condition)
);

-- 11. 危险感知检测表
CREATE TABLE danger_detections (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) NOT NULL,
    detection_time DATETIME NOT NULL,
    danger_type ENUM('accident', 'fire', 'flood', 'debris', 'construction', 'pedestrian', 'animal', 'other') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    position_lat DECIMAL(10, 8),
    position_lng DECIMAL(11, 8),
    bbox_x1 DECIMAL(8, 2),
    bbox_y1 DECIMAL(8, 2),
    bbox_x2 DECIMAL(8, 2),
    bbox_y2 DECIMAL(8, 2),
    confidence DECIMAL(4, 3) NOT NULL,
    description TEXT,
    image_path VARCHAR(500),
    video_path VARCHAR(500),
    model_id VARCHAR(36),
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(36),
    verified_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES ai_models(id) ON DELETE SET NULL,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_camera_detection_time (camera_id, detection_time),
    INDEX idx_danger_type (danger_type),
    INDEX idx_severity (severity),
    INDEX idx_is_verified (is_verified),
    INDEX idx_detection_time (detection_time)
);

-- 12. 车辆告警表
CREATE TABLE vehicle_alerts (
    id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    camera_id VARCHAR(36) NOT NULL,
    alert_type ENUM('speeding', 'red_light', 'wrong_lane', 'illegal_parking', 'suspicious_behavior', 'reckless_driving') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    description TEXT,
    position_lat DECIMAL(10, 8),
    position_lng DECIMAL(11, 8),
    speed DECIMAL(6, 2),
    speed_limit DECIMAL(6, 2),
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_camera_id (camera_id),
    INDEX idx_alert_type (alert_type),
    INDEX idx_severity (severity),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);

-- 13. 系统告警表
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    alert_type ENUM('system', 'camera', 'vehicle', 'ai', 'road', 'danger') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    status ENUM('active', 'acknowledged', 'resolved') DEFAULT 'active',
    source VARCHAR(100),
    camera_id VARCHAR(36),
    user_id VARCHAR(36),
    metadata JSON,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at DATETIME,
    resolved_at DATETIME,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_alert_type (alert_type),
    INDEX idx_severity (severity),
    INDEX idx_status (status),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);

-- 14. 系统配置表
CREATE TABLE system_configs (
    id VARCHAR(36) PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    is_editable BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key),
    INDEX idx_is_editable (is_editable)
);

-- 15. 操作日志表
CREATE TABLE operation_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    operation_type ENUM('create', 'update', 'delete', 'view', 'export', 'login', 'logout') NOT NULL,
    table_name VARCHAR(50),
    record_id VARCHAR(36),
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_table_name (table_name),
    INDEX idx_created_at (created_at)
);

-- 16. 数据统计表（用于缓存统计数据）
CREATE TABLE data_statistics (
    id VARCHAR(36) PRIMARY KEY,
    stat_type ENUM('daily', 'weekly', 'monthly', 'yearly') NOT NULL,
    stat_date DATE NOT NULL,
    camera_id VARCHAR(36),
    vehicle_count INT DEFAULT 0,
    detection_count INT DEFAULT 0,
    alert_count INT DEFAULT 0,
    avg_speed DECIMAL(6, 2),
    max_speed DECIMAL(6, 2),
    traffic_volume INT DEFAULT 0,
    suspicious_vehicles INT DEFAULT 0,
    danger_events INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    UNIQUE KEY unique_stat (stat_type, stat_date, camera_id),
    INDEX idx_stat_type_date (stat_type, stat_date),
    INDEX idx_camera_id (camera_id)
);
