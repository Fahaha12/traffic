-- 简化的调试用SQL文件
-- 专门解决摄像头重复问题

-- 创建数据库
CREATE DATABASE IF NOT EXISTS traffic_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE traffic_monitor;

-- 删除现有表（如果存在）
DROP TABLE IF EXISTS vehicle_detections;
DROP TABLE IF EXISTS vehicle_reid_features;
DROP TABLE IF EXISTS vehicle_tracks;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS system_configs;
DROP TABLE IF EXISTS ai_models;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS cameras;
DROP TABLE IF EXISTS users;

-- 创建用户表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建摄像头表（添加唯一约束防止重复）
CREATE TABLE cameras (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_status (status),
    INDEX idx_type (type)
);

-- 创建车辆表
CREATE TABLE vehicles (
    id VARCHAR(36) PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL,
    vehicle_type ENUM('car', 'truck', 'bus', 'motorcycle', 'bicycle', 'unknown') NOT NULL,
    color VARCHAR(20),
    brand VARCHAR(50),
    model VARCHAR(50),
    is_suspicious BOOLEAN DEFAULT FALSE,
    risk_level ENUM('low', 'medium', 'high', 'critical') DEFAULT 'low',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建车辆检测表
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE,
    INDEX idx_camera_time (camera_id, detection_time)
);

-- 插入测试数据
INSERT INTO users (id, username, email, password_hash, is_admin, is_active) VALUES
('user_001', 'admin', 'admin@traffic-monitor.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.2.', TRUE, TRUE);

INSERT INTO cameras (id, name, type, position_lat, position_lng, status, stream_url, stream_type, resolution_width, resolution_height, fps, direction) VALUES
('camera_001', '郑州市政府大门', 'traffic', 34.7466, 113.6253, 'online', 'rtmp://58.200.131.2:1935/livetv/hunantv', 'rtmp', 1920, 1080, 25, 90),
('camera_002', '中原路与建设路交叉口', 'traffic', 34.7500, 113.6300, 'online', 'http://example.com/camera2.m3u8', 'hls', 1280, 720, 30, 180),
('camera_003', '金水区花园路', 'surveillance', 34.7600, 113.6400, 'offline', 'http://example.com/camera3.mp4', 'http', 1920, 1080, 25, 270);

INSERT INTO vehicles (id, plate_number, vehicle_type, color, brand, model, is_suspicious, risk_level) VALUES
('vehicle_001', '豫A12345', 'car', '白色', '大众', '朗逸', FALSE, 'low'),
('vehicle_002', '豫B67890', 'truck', '蓝色', '解放', 'J6', TRUE, 'high'),
('vehicle_003', '豫C11111', 'bus', '黄色', '宇通', 'ZK6120', FALSE, 'low');

-- 创建存储过程来安全地处理摄像头操作
DELIMITER //

-- 获取所有摄像头
CREATE PROCEDURE GetCameras()
BEGIN
    SELECT 
        id,
        name,
        type,
        position_lat,
        position_lng,
        status,
        stream_url,
        stream_type,
        resolution_width,
        resolution_height,
        fps,
        direction,
        created_at,
        updated_at
    FROM cameras 
    ORDER BY created_at DESC;
END //

-- 根据ID获取摄像头
CREATE PROCEDURE GetCameraById(IN p_id VARCHAR(36))
BEGIN
    SELECT 
        id,
        name,
        type,
        position_lat,
        position_lng,
        status,
        stream_url,
        stream_type,
        resolution_width,
        resolution_height,
        fps,
        direction,
        created_at,
        updated_at
    FROM cameras 
    WHERE id = p_id;
END //

-- 创建摄像头（防止重复）
CREATE PROCEDURE CreateCamera(
    IN p_name VARCHAR(100),
    IN p_type VARCHAR(20),
    IN p_lat DECIMAL(10, 8),
    IN p_lng DECIMAL(11, 8),
    IN p_status VARCHAR(20),
    IN p_stream_url VARCHAR(500),
    IN p_stream_type VARCHAR(20),
    IN p_resolution_width INT,
    IN p_resolution_height INT,
    IN p_fps INT,
    IN p_direction DECIMAL(5, 2)
)
BEGIN
    DECLARE camera_id VARCHAR(36);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- 检查名称是否已存在
    IF EXISTS (SELECT 1 FROM cameras WHERE name = p_name) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '摄像头名称已存在';
    END IF;
    
    -- 生成新的ID
    SET camera_id = UUID();
    
    -- 插入新摄像头
    INSERT INTO cameras (
        id, name, type, position_lat, position_lng, status,
        stream_url, stream_type, resolution_width, resolution_height,
        fps, direction, created_at, updated_at
    ) VALUES (
        camera_id, p_name, p_type, p_lat, p_lng, p_status,
        p_stream_url, p_stream_type, p_resolution_width, p_resolution_height,
        p_fps, p_direction, NOW(), NOW()
    );
    
    -- 返回创建的摄像头信息
    SELECT 
        id,
        name,
        type,
        position_lat,
        position_lng,
        status,
        stream_url,
        stream_type,
        resolution_width,
        resolution_height,
        fps,
        direction,
        created_at,
        updated_at
    FROM cameras 
    WHERE id = camera_id;
    
    COMMIT;
END //

-- 更新摄像头（防止重复）
CREATE PROCEDURE UpdateCamera(
    IN p_id VARCHAR(36),
    IN p_name VARCHAR(100),
    IN p_type VARCHAR(20),
    IN p_lat DECIMAL(10, 8),
    IN p_lng DECIMAL(11, 8),
    IN p_status VARCHAR(20),
    IN p_stream_url VARCHAR(500),
    IN p_stream_type VARCHAR(20),
    IN p_resolution_width INT,
    IN p_resolution_height INT,
    IN p_fps INT,
    IN p_direction DECIMAL(5, 2)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- 检查摄像头是否存在
    IF NOT EXISTS (SELECT 1 FROM cameras WHERE id = p_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '摄像头不存在';
    END IF;
    
    -- 检查名称是否与其他摄像头冲突
    IF EXISTS (SELECT 1 FROM cameras WHERE name = p_name AND id != p_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '摄像头名称已存在';
    END IF;
    
    -- 更新摄像头
    UPDATE cameras SET
        name = p_name,
        type = p_type,
        position_lat = p_lat,
        position_lng = p_lng,
        status = p_status,
        stream_url = p_stream_url,
        stream_type = p_stream_type,
        resolution_width = p_resolution_width,
        resolution_height = p_resolution_height,
        fps = p_fps,
        direction = p_direction,
        updated_at = NOW()
    WHERE id = p_id;
    
    -- 返回更新后的摄像头信息
    SELECT 
        id,
        name,
        type,
        position_lat,
        position_lng,
        status,
        stream_url,
        stream_type,
        resolution_width,
        resolution_height,
        fps,
        direction,
        created_at,
        updated_at
    FROM cameras 
    WHERE id = p_id;
    
    COMMIT;
END //

-- 删除摄像头
CREATE PROCEDURE DeleteCamera(IN p_id VARCHAR(36))
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- 检查摄像头是否存在
    IF NOT EXISTS (SELECT 1 FROM cameras WHERE id = p_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '摄像头不存在';
    END IF;
    
    -- 删除摄像头（级联删除相关数据）
    DELETE FROM cameras WHERE id = p_id;
    
    COMMIT;
END //

DELIMITER ;

-- 创建视图
CREATE VIEW camera_summary AS
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
    c.updated_at,
    COUNT(vd.id) as detection_count,
    MAX(vd.detection_time) as last_detection
FROM cameras c
LEFT JOIN vehicle_detections vd ON c.id = vd.camera_id
GROUP BY c.id, c.name, c.type, c.status, c.position_lat, c.position_lng, 
         c.resolution_width, c.resolution_height, c.fps, c.direction, c.created_at, c.updated_at;

-- 测试查询
SELECT '数据库创建完成！' as message;
SELECT '包含以下数据:' as info;
SELECT '  - 1个用户 (admin)' as users;
SELECT '  - 3个摄像头' as cameras;
SELECT '  - 3个车辆' as vehicles;
SELECT '  - 5个存储过程' as procedures;
SELECT '  - 1个视图' as views;

-- 显示当前摄像头数据
SELECT * FROM camera_summary ORDER BY created_at DESC;
