-- 交通监控系统数据库导出文件
-- 适用于云端数据库导入调试
-- 生成时间: 2025-09-08

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS traffic_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE traffic_monitor;

-- 删除已存在的表（如果存在）
DROP TABLE IF EXISTS vehicle_detections;
DROP TABLE IF EXISTS vehicle_reid_features;
DROP TABLE IF EXISTS vehicle_tracks;
DROP TABLE IF EXISTS vehicle_track_segments;
DROP TABLE IF EXISTS model_predictions;
DROP TABLE IF EXISTS road_conditions;
DROP TABLE IF EXISTS danger_detections;
DROP TABLE IF EXISTS vehicle_alerts;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS operation_logs;
DROP TABLE IF EXISTS data_statistics;
DROP TABLE IF EXISTS system_configs;
DROP TABLE IF EXISTS ai_models;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS cameras;
DROP TABLE IF EXISTS users;

-- 1. 用户表
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

-- 3. 车辆表
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

-- 4. 车辆检测表
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
    position_lat DECIMAL(10, 8),
    position_lng DECIMAL(11, 8),
    image_path VARCHAR(500),
    model_id VARCHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    INDEX idx_camera_detection_time (camera_id, detection_time),
    INDEX idx_detection_time (detection_time),
    INDEX idx_vehicle_type (vehicle_type),
    INDEX idx_confidence (confidence)
);

-- 5. ReID特征表
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

-- 7. AI模型表
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

-- 8. 告警表
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

-- 9. 系统配置表
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

-- 插入示例数据

-- 插入管理员用户
INSERT INTO users (id, username, email, password_hash, is_admin, is_active, created_at) VALUES
('user_001', 'admin', 'admin@traffic-monitor.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.2.', TRUE, TRUE, NOW()),
('user_002', 'operator', 'operator@traffic-monitor.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.2.', FALSE, TRUE, NOW());

-- 插入示例摄像头
INSERT INTO cameras (id, name, type, position_lat, position_lng, status, stream_url, stream_type, resolution_width, resolution_height, fps, direction, created_at) VALUES
('camera_001', '郑州市政府大门', 'traffic', 34.7466, 113.6253, 'online', 'rtmp://58.200.131.2:1935/livetv/hunantv', 'rtmp', 1920, 1080, 25, 90, NOW()),
('camera_002', '中原路与建设路交叉口', 'traffic', 34.7500, 113.6300, 'online', 'http://example.com/camera2.m3u8', 'hls', 1280, 720, 30, 180, NOW()),
('camera_003', '金水区花园路', 'surveillance', 34.7600, 113.6400, 'offline', 'http://example.com/camera3.mp4', 'http', 1920, 1080, 25, 270, NOW()),
('camera_004', 'ReID检测点1', 'reid', 34.7650, 113.6350, 'online', 'rtmp://example.com/reid1', 'rtmp', 1920, 1080, 25, 0, NOW()),
('camera_005', '二七广场', 'traffic', 34.7400, 113.6500, 'online', 'http://example.com/erqi.m3u8', 'hls', 1280, 720, 30, 45, NOW());

-- 插入示例车辆
INSERT INTO vehicles (id, plate_number, vehicle_type, color, brand, model, year, is_suspicious, risk_level, last_seen, created_at) VALUES
('vehicle_001', '豫A12345', 'car', '白色', '大众', '朗逸', 2020, FALSE, 'low', NOW(), NOW()),
('vehicle_002', '豫B67890', 'truck', '蓝色', '解放', 'J6', 2019, TRUE, 'high', NOW(), NOW()),
('vehicle_003', '豫C11111', 'bus', '黄色', '宇通', 'ZK6120', 2021, FALSE, 'low', NOW(), NOW()),
('vehicle_004', '豫D22222', 'car', '黑色', '奥迪', 'A6L', 2022, FALSE, 'low', NOW(), NOW()),
('vehicle_005', '豫E33333', 'motorcycle', '红色', '本田', 'CBR600', 2020, TRUE, 'medium', NOW(), NOW());

-- 插入AI模型
INSERT INTO ai_models (id, name, model_type, framework, version, model_path, config_path, is_active, confidence_threshold, input_size, classes, description, created_at) VALUES
('model_001', 'YOLOv8 车辆检测', 'detection', 'pytorch', '1.0.0', 'models/yolov8_vehicle.pt', 'models/yolov8_config.yaml', TRUE, 0.5, '640x640', '["car", "truck", "bus", "motorcycle", "bicycle"]', '基于YOLOv8的车辆检测模型', NOW()),
('model_002', 'DeepSORT 目标跟踪', 'tracking', 'tensorflow', '1.0.0', 'models/deepsort.pb', 'models/deepsort_config.json', TRUE, 0.7, '128x64', '["person", "car"]', '基于DeepSORT的目标跟踪模型', NOW()),
('model_003', 'ReID网络', 'reid', 'pytorch', '1.0.0', 'models/reid_network.pth', 'models/reid_config.yaml', TRUE, 0.8, '256x128', '["vehicle"]', '车辆ReID特征提取网络', NOW()),
('model_004', '路面检测网络', 'road_analysis', 'onnx', '1.0.0', 'models/road_detection.onnx', 'models/road_config.json', TRUE, 0.6, '512x512', '["dry", "wet", "icy", "snowy"]', '路面状况检测网络', NOW()),
('model_005', '危险感知网络', 'danger_detection', 'pytorch', '1.0.0', 'models/danger_detection.pth', 'models/danger_config.yaml', TRUE, 0.7, '640x640', '["accident", "fire", "flood", "debris"]', '危险事件检测网络', NOW());

-- 插入示例车辆检测记录
INSERT INTO vehicle_detections (id, camera_id, detection_time, bbox_x1, bbox_y1, bbox_x2, bbox_y2, confidence, vehicle_type, color, speed, direction, position_lat, position_lng, image_path, model_id, created_at) VALUES
('detection_001', 'camera_001', NOW(), 100, 150, 300, 400, 0.95, 'car', '白色', 45.5, 90, 34.7466, 113.6253, 'images/detection_001.jpg', 'model_001', NOW()),
('detection_002', 'camera_002', NOW(), 200, 100, 450, 350, 0.88, 'truck', '蓝色', 35.2, 180, 34.7500, 113.6300, 'images/detection_002.jpg', 'model_001', NOW()),
('detection_003', 'camera_001', NOW(), 150, 200, 350, 450, 0.92, 'car', '黑色', 50.1, 90, 34.7466, 113.6253, 'images/detection_003.jpg', 'model_001', NOW()),
('detection_004', 'camera_003', NOW(), 80, 120, 280, 380, 0.85, 'bus', '黄色', 40.3, 270, 34.7600, 113.6400, 'images/detection_004.jpg', 'model_001', NOW()),
('detection_005', 'camera_004', NOW(), 120, 180, 320, 420, 0.90, 'car', '红色', 55.7, 0, 34.7650, 113.6350, 'images/detection_005.jpg', 'model_001', NOW());

-- 插入示例告警
INSERT INTO alerts (id, title, description, alert_type, severity, status, source, camera_id, user_id, is_read, created_at) VALUES
('alert_001', '摄像头离线告警', '摄像头camera_003已离线超过5分钟', 'camera', 'medium', 'active', 'system', 'camera_003', 'user_001', FALSE, NOW()),
('alert_002', '可疑车辆检测', '检测到可疑车辆豫B67890', 'vehicle', 'high', 'active', 'ai_model', 'camera_001', 'user_001', FALSE, NOW()),
('alert_003', '超速告警', '车辆豫A12345在camera_001处超速行驶', 'vehicle', 'medium', 'acknowledged', 'ai_model', 'camera_001', 'user_002', TRUE, NOW()),
('alert_004', '系统性能告警', 'AI模型处理延迟超过阈值', 'ai', 'low', 'resolved', 'system', NULL, 'user_001', TRUE, NOW()),
('alert_005', '存储空间告警', '视频存储空间不足', 'system', 'high', 'active', 'system', NULL, 'user_001', FALSE, NOW());

-- 插入系统配置
INSERT INTO system_configs (id, config_key, config_value, config_type, description, is_editable, created_at) VALUES
('config_001', 'system_name', '交通监控系统', 'string', '系统名称', TRUE, NOW()),
('config_002', 'max_cameras', '100', 'number', '最大摄像头数量', TRUE, NOW()),
('config_003', 'detection_confidence', '0.5', 'number', '检测置信度阈值', TRUE, NOW()),
('config_004', 'reid_similarity_threshold', '0.8', 'number', 'ReID相似度阈值', TRUE, NOW()),
('config_005', 'alert_retention_days', '30', 'number', '告警保留天数', TRUE, NOW()),
('config_006', 'video_retention_days', '7', 'number', '视频保留天数', TRUE, NOW()),
('config_007', 'auto_cleanup', 'true', 'boolean', '自动清理过期数据', TRUE, NOW()),
('config_008', 'default_map_center', '{"lat": 34.7466, "lng": 113.6253}', 'json', '默认地图中心点', TRUE, NOW());

-- 插入示例ReID特征
INSERT INTO vehicle_reid_features (id, vehicle_id, detection_id, feature_vector, feature_dimension, similarity_threshold, created_at) VALUES
('reid_001', 'vehicle_001', 'detection_001', '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]', 10, 0.8, NOW()),
('reid_002', 'vehicle_002', 'detection_002', '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1]', 10, 0.8, NOW()),
('reid_003', 'vehicle_003', 'detection_004', '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2]', 10, 0.8, NOW()),
('reid_004', 'vehicle_004', 'detection_003', '[0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3]', 10, 0.8, NOW()),
('reid_005', 'vehicle_005', 'detection_005', '[0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4]', 10, 0.8, NOW());

-- 插入示例轨迹记录
INSERT INTO vehicle_tracks (id, vehicle_id, camera_id, detection_id, position_lat, position_lng, speed, direction, location_name, timestamp, image_path, confidence, track_sequence, created_at) VALUES
('track_001', 'vehicle_001', 'camera_001', 'detection_001', 34.7466, 113.6253, 45.5, 90, '郑州市政府大门', NOW(), 'images/track_001.jpg', 0.95, 1, NOW()),
('track_002', 'vehicle_002', 'camera_002', 'detection_002', 34.7500, 113.6300, 35.2, 180, '中原路与建设路交叉口', NOW(), 'images/track_002.jpg', 0.88, 1, NOW()),
('track_003', 'vehicle_003', 'camera_003', 'detection_004', 34.7600, 113.6400, 40.3, 270, '金水区花园路', NOW(), 'images/track_003.jpg', 0.85, 1, NOW()),
('track_004', 'vehicle_004', 'camera_001', 'detection_003', 34.7466, 113.6253, 50.1, 90, '郑州市政府大门', NOW(), 'images/track_004.jpg', 0.92, 1, NOW()),
('track_005', 'vehicle_005', 'camera_004', 'detection_005', 34.7650, 113.6350, 55.7, 0, 'ReID检测点1', NOW(), 'images/track_005.jpg', 0.90, 1, NOW());

-- 创建视图用于常用查询
CREATE VIEW camera_status_summary AS
SELECT 
    c.id,
    c.name,
    c.type,
    c.status,
    c.position_lat,
    c.position_lng,
    c.resolution_width,
    c.resolution_height,
    c.fps,
    c.direction,
    c.created_at,
    COUNT(vd.id) as detection_count,
    MAX(vd.detection_time) as last_detection
FROM cameras c
LEFT JOIN vehicle_detections vd ON c.id = vd.camera_id
GROUP BY c.id, c.name, c.type, c.status, c.position_lat, c.position_lng, c.resolution_width, c.resolution_height, c.fps, c.direction, c.created_at;

CREATE VIEW vehicle_summary AS
SELECT 
    v.id,
    v.plate_number,
    v.vehicle_type,
    v.color,
    v.brand,
    v.model,
    v.is_suspicious,
    v.risk_level,
    v.last_seen,
    v.created_at,
    COUNT(vt.id) as track_count,
    COUNT(vrf.id) as reid_feature_count
FROM vehicles v
LEFT JOIN vehicle_tracks vt ON v.id = vt.vehicle_id
LEFT JOIN vehicle_reid_features vrf ON v.id = vrf.vehicle_id
GROUP BY v.id, v.plate_number, v.vehicle_type, v.color, v.brand, v.model, v.is_suspicious, v.risk_level, v.last_seen, v.created_at;

CREATE VIEW alert_summary AS
SELECT 
    a.id,
    a.title,
    a.description,
    a.alert_type,
    a.severity,
    a.status,
    a.source,
    a.is_read,
    a.created_at,
    c.name as camera_name,
    u.username as user_name
FROM alerts a
LEFT JOIN cameras c ON a.camera_id = c.id
LEFT JOIN users u ON a.user_id = u.id;

-- 创建存储过程
DELIMITER //

CREATE PROCEDURE GetCameraDetections(IN camera_id VARCHAR(36), IN start_time DATETIME, IN end_time DATETIME)
BEGIN
    SELECT 
        vd.*,
        c.name as camera_name,
        c.position_lat,
        c.position_lng
    FROM vehicle_detections vd
    JOIN cameras c ON vd.camera_id = c.id
    WHERE vd.camera_id = camera_id
    AND vd.detection_time BETWEEN start_time AND end_time
    ORDER BY vd.detection_time DESC;
END //

CREATE PROCEDURE GetVehicleTrajectory(IN vehicle_id VARCHAR(36), IN start_time DATETIME, IN end_time DATETIME)
BEGIN
    SELECT 
        vt.*,
        c.name as camera_name,
        c.position_lat,
        c.position_lng
    FROM vehicle_tracks vt
    JOIN cameras c ON vt.camera_id = c.id
    WHERE vt.vehicle_id = vehicle_id
    AND vt.timestamp BETWEEN start_time AND end_time
    ORDER BY vt.timestamp ASC;
END //

CREATE PROCEDURE GetSystemStats()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM cameras WHERE status = 'online') as online_cameras,
        (SELECT COUNT(*) FROM cameras WHERE status = 'offline') as offline_cameras,
        (SELECT COUNT(*) FROM vehicles) as total_vehicles,
        (SELECT COUNT(*) FROM vehicles WHERE is_suspicious = TRUE) as suspicious_vehicles,
        (SELECT COUNT(*) FROM alerts WHERE status = 'active') as active_alerts,
        (SELECT COUNT(*) FROM vehicle_detections WHERE DATE(created_at) = CURDATE()) as today_detections;
END //

DELIMITER ;

-- 创建触发器
DELIMITER //

CREATE TRIGGER update_camera_last_heartbeat
AFTER INSERT ON vehicle_detections
FOR EACH ROW
BEGIN
    UPDATE cameras 
    SET last_heartbeat = NEW.detection_time 
    WHERE id = NEW.camera_id;
END //

CREATE TRIGGER update_vehicle_last_seen
AFTER INSERT ON vehicle_tracks
FOR EACH ROW
BEGIN
    UPDATE vehicles 
    SET last_seen = NEW.timestamp 
    WHERE id = NEW.vehicle_id;
END //

DELIMITER ;

-- 创建索引优化查询性能
CREATE INDEX idx_vehicle_detections_camera_time_type ON vehicle_detections(camera_id, detection_time, vehicle_type);
CREATE INDEX idx_vehicle_tracks_vehicle_camera_time ON vehicle_tracks(vehicle_id, camera_id, timestamp);
CREATE INDEX idx_vehicle_reid_features_vehicle_created ON vehicle_reid_features(vehicle_id, created_at);
CREATE INDEX idx_alerts_type_status_created ON alerts(alert_type, status, created_at);
CREATE INDEX idx_cameras_status_type ON cameras(status, type);

-- 完成
SELECT '数据库导入完成！' as message;
SELECT '包含以下数据:' as info;
SELECT '  - 2个用户 (admin, operator)' as users;
SELECT '  - 5个摄像头' as cameras;
SELECT '  - 5个车辆' as vehicles;
SELECT '  - 5个检测记录' as detections;
SELECT '  - 5个ReID特征' as reid_features;
SELECT '  - 5个轨迹记录' as tracks;
SELECT '  - 5个AI模型' as models;
SELECT '  - 5个告警' as alerts;
SELECT '  - 8个系统配置' as configs;
SELECT '  - 3个视图' as views;
SELECT '  - 3个存储过程' as procedures;
SELECT '  - 2个触发器' as triggers;
