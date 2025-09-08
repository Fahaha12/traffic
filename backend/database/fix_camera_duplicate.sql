-- 修复摄像头重复问题的SQL文件
-- 适用于云端数据库导入调试

-- 使用数据库
USE traffic_monitor;

-- 删除可能存在的重复数据
DELETE FROM vehicle_detections WHERE camera_id IN (
    SELECT id FROM cameras WHERE name LIKE '%复制%' OR name LIKE '%copy%'
);

DELETE FROM vehicle_tracks WHERE camera_id IN (
    SELECT id FROM cameras WHERE name LIKE '%复制%' OR name LIKE '%copy%'
);

DELETE FROM alerts WHERE camera_id IN (
    SELECT id FROM cameras WHERE name LIKE '%复制%' OR name LIKE '%copy%'
);

DELETE FROM cameras WHERE name LIKE '%复制%' OR name LIKE '%copy%';

-- 确保摄像头表有唯一约束
ALTER TABLE cameras ADD CONSTRAINT unique_camera_name UNIQUE (name);

-- 插入测试数据（确保没有重复）
INSERT IGNORE INTO cameras (id, name, type, position_lat, position_lng, status, stream_url, stream_type, resolution_width, resolution_height, fps, direction, created_at) VALUES
('camera_001', '郑州市政府大门', 'traffic', 34.7466, 113.6253, 'online', 'rtmp://58.200.131.2:1935/livetv/hunantv', 'rtmp', 1920, 1080, 25, 90, NOW()),
('camera_002', '中原路与建设路交叉口', 'traffic', 34.7500, 113.6300, 'online', 'http://example.com/camera2.m3u8', 'hls', 1280, 720, 30, 180, NOW()),
('camera_003', '金水区花园路', 'surveillance', 34.7600, 113.6400, 'offline', 'http://example.com/camera3.mp4', 'http', 1920, 1080, 25, 270, NOW()),
('camera_004', 'ReID检测点1', 'reid', 34.7650, 113.6350, 'online', 'rtmp://example.com/reid1', 'rtmp', 1920, 1080, 25, 0, NOW()),
('camera_005', '二七广场', 'traffic', 34.7400, 113.6500, 'online', 'http://example.com/erqi.m3u8', 'hls', 1280, 720, 30, 45, NOW());

-- 创建存储过程来安全地更新摄像头
DELIMITER //

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
    
    -- 检查名称是否与其他摄像头冲突
    IF EXISTS (SELECT 1 FROM cameras WHERE name = p_name AND id != p_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '摄像头名称已存在';
    END IF;
    
    -- 更新摄像头信息
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
    
    -- 检查是否更新成功
    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '摄像头不存在';
    END IF;
    
    COMMIT;
END //

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
    
    -- 创建新摄像头
    INSERT INTO cameras (
        id, name, type, position_lat, position_lng, status, 
        stream_url, stream_type, resolution_width, resolution_height, 
        fps, direction, created_at, updated_at
    ) VALUES (
        UUID(), p_name, p_type, p_lat, p_lng, p_status,
        p_stream_url, p_stream_type, p_resolution_width, p_resolution_height,
        p_fps, p_direction, NOW(), NOW()
    );
    
    COMMIT;
END //

DELIMITER ;

-- 创建视图来检查重复数据
CREATE VIEW camera_duplicates AS
SELECT 
    name,
    COUNT(*) as count,
    GROUP_CONCAT(id) as camera_ids
FROM cameras 
GROUP BY name 
HAVING COUNT(*) > 1;

-- 创建触发器防止重复插入
DELIMITER //

CREATE TRIGGER prevent_duplicate_camera_name
BEFORE INSERT ON cameras
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM cameras WHERE name = NEW.name) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '摄像头名称已存在，无法创建重复的摄像头';
    END IF;
END //

DELIMITER ;

-- 查询当前摄像头数据
SELECT 
    id,
    name,
    type,
    status,
    position_lat,
    position_lng,
    resolution_width,
    resolution_height,
    fps,
    direction,
    created_at,
    updated_at
FROM cameras 
ORDER BY created_at DESC;

-- 检查是否有重复的摄像头名称
SELECT * FROM camera_duplicates;

-- 完成
SELECT '摄像头重复问题修复完成！' as message;
SELECT '现在可以安全地编辑摄像头，不会产生重复数据' as info;
