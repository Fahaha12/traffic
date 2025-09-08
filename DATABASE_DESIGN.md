# 交通监控系统数据库设计

## 概述

本文档描述了交通监控系统的完整MySQL数据库设计，支持车辆检测、ReID检测、轨迹记录、深度学习应用以及路面信息检测等功能。

## 数据库特性

- **数据库类型**: MySQL 8.0+
- **字符集**: utf8mb4
- **排序规则**: utf8mb4_unicode_ci
- **存储引擎**: InnoDB
- **支持功能**: 车辆检测、ReID跟踪、轨迹记录、路面分析、危险感知

## 核心表结构

### 1. 用户管理

#### users - 用户表
```sql
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 2. 摄像头管理

#### cameras - 摄像头表
```sql
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 3. 车辆管理

#### vehicles - 车辆基础信息表
```sql
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 4. 车辆检测

#### vehicle_detections - 车辆检测记录表
```sql
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5. ReID特征管理

#### vehicle_reid_features - 车辆ReID特征表
```sql
CREATE TABLE vehicle_reid_features (
    id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36),
    detection_id VARCHAR(36) NOT NULL,
    feature_vector JSON NOT NULL,
    feature_dimension INT NOT NULL,
    similarity_threshold DECIMAL(4, 3) DEFAULT 0.8,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6. 轨迹记录

#### vehicle_tracks - 车辆轨迹表
```sql
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### vehicle_track_segments - 车辆轨迹段表
```sql
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 7. AI模型管理

#### ai_models - AI模型表
```sql
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### model_predictions - 模型预测结果表
```sql
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
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 8. 路面信息检测

#### road_conditions - 路面信息检测表
```sql
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 9. 危险感知检测

#### danger_detections - 危险感知检测表
```sql
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 10. 告警管理

#### vehicle_alerts - 车辆告警表
```sql
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
    resolved_at DATETIME
);
```

#### alerts - 系统告警表
```sql
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
    resolved_at DATETIME
);
```

### 11. 系统管理

#### system_configs - 系统配置表
```sql
CREATE TABLE system_configs (
    id VARCHAR(36) PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    is_editable BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### operation_logs - 操作日志表
```sql
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### data_statistics - 数据统计表
```sql
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 索引设计

### 主要索引

1. **用户表索引**
   - `idx_username` - 用户名索引
   - `idx_email` - 邮箱索引
   - `idx_is_active` - 活跃状态索引

2. **摄像头表索引**
   - `idx_status` - 状态索引
   - `idx_type` - 类型索引
   - `idx_position` - 位置复合索引
   - `idx_last_heartbeat` - 心跳时间索引

3. **车辆检测表索引**
   - `idx_camera_detection_time` - 摄像头和时间复合索引
   - `idx_detection_time` - 检测时间索引
   - `idx_vehicle_type` - 车辆类型索引
   - `idx_confidence` - 置信度索引

4. **轨迹表索引**
   - `idx_vehicle_timestamp` - 车辆和时间复合索引
   - `idx_camera_timestamp` - 摄像头和时间复合索引
   - `idx_timestamp` - 时间索引
   - `idx_track_sequence` - 轨迹序列索引

5. **ReID特征表索引**
   - `idx_vehicle_id` - 车辆ID索引
   - `idx_detection_id` - 检测ID索引
   - `idx_created_at` - 创建时间索引

## 数据关系

### 主要外键关系

1. **摄像头相关**
   - `vehicle_detections.camera_id` → `cameras.id`
   - `vehicle_tracks.camera_id` → `cameras.id`
   - `road_conditions.camera_id` → `cameras.id`
   - `danger_detections.camera_id` → `cameras.id`

2. **车辆相关**
   - `vehicle_tracks.vehicle_id` → `vehicles.id`
   - `vehicle_reid_features.vehicle_id` → `vehicles.id`
   - `vehicle_alerts.vehicle_id` → `vehicles.id`

3. **检测相关**
   - `vehicle_reid_features.detection_id` → `vehicle_detections.id`
   - `vehicle_tracks.detection_id` → `vehicle_detections.id`

4. **模型相关**
   - `vehicle_detections.model_id` → `ai_models.id`
   - `model_predictions.model_id` → `ai_models.id`
   - `road_conditions.model_id` → `ai_models.id`
   - `danger_detections.model_id` → `ai_models.id`

## 性能优化

### 查询优化

1. **时间范围查询**
   - 使用复合索引优化时间范围查询
   - 分区表按时间分区（可选）

2. **地理位置查询**
   - 使用空间索引优化地理位置查询
   - 考虑使用PostGIS扩展（可选）

3. **JSON字段查询**
   - 为JSON字段创建虚拟列索引
   - 使用MySQL 8.0的JSON函数优化查询

### 存储优化

1. **数据归档**
   - 定期归档历史数据
   - 使用分区表分离热数据和冷数据

2. **压缩存储**
   - 启用InnoDB压缩
   - 压缩大文本字段

3. **缓存策略**
   - 使用Redis缓存热点数据
   - 实现查询结果缓存

## 扩展性设计

### 水平扩展

1. **读写分离**
   - 主库处理写操作
   - 从库处理读操作

2. **分库分表**
   - 按摄像头ID分表
   - 按时间分表

3. **微服务架构**
   - 检测服务独立部署
   - ReID服务独立部署

### 垂直扩展

1. **硬件升级**
   - 增加CPU和内存
   - 使用SSD存储

2. **配置优化**
   - 调整MySQL参数
   - 优化查询计划

## 安全设计

### 数据安全

1. **访问控制**
   - 基于角色的权限控制
   - 数据库用户权限最小化

2. **数据加密**
   - 敏感数据加密存储
   - 传输过程加密

3. **审计日志**
   - 记录所有数据操作
   - 定期审计日志分析

### 备份恢复

1. **备份策略**
   - 全量备份 + 增量备份
   - 跨地域备份

2. **恢复测试**
   - 定期恢复测试
   - 灾难恢复预案

## 监控告警

### 性能监控

1. **数据库性能**
   - 慢查询监控
   - 连接数监控
   - 锁等待监控

2. **业务指标**
   - 检测准确率
   - 系统响应时间
   - 数据完整性

### 告警机制

1. **系统告警**
   - 数据库连接异常
   - 磁盘空间不足
   - 性能指标异常

2. **业务告警**
   - 检测异常
   - 数据异常
   - 服务异常

## 总结

本数据库设计支持完整的交通监控系统功能，包括：

- ✅ **车辆检测**: 实时车辆检测和记录
- ✅ **ReID跟踪**: 车辆重识别和轨迹跟踪
- ✅ **轨迹记录**: 多轨迹段记录和分析
- ✅ **深度学习**: AI模型管理和预测结果存储
- ✅ **路面分析**: 路面状况检测和分析
- ✅ **危险感知**: 危险事件检测和告警
- ✅ **系统管理**: 用户、配置、日志管理
- ✅ **性能优化**: 索引、缓存、分区优化
- ✅ **扩展性**: 支持水平和垂直扩展
- ✅ **安全性**: 权限控制、数据加密、审计日志

该设计为未来的功能扩展和性能优化提供了良好的基础。
