"""
MySQL数据库初始化脚本
支持车辆检测、ReID检测、轨迹记录、深度学习应用、路面信息检测
"""

import mysql.connector
from mysql.connector import Error
import os
import json
from datetime import datetime, timedelta
import uuid

def create_database_connection():
    """创建数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def create_database():
    """创建数据库"""
    connection = create_database_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS traffic_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("数据库创建成功")
        
        # 使用数据库
        cursor.execute("USE traffic_monitor")
        
        # 读取并执行SQL文件
        with open('database/schema.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # 分割SQL语句并执行
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in sql_statements:
            if statement.upper().startswith('CREATE DATABASE'):
                continue  # 跳过创建数据库的语句
            cursor.execute(statement)
        
        print("数据表创建成功")
        return True
        
    except Error as e:
        print(f"创建数据库失败: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_sample_data():
    """插入示例数据"""
    connection = create_database_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("USE traffic_monitor")
        
        # 插入管理员用户
        admin_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, is_admin, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (admin_id, 'admin', 'admin@traffic-monitor.com', 
              '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.2.', True, True))
        
        # 插入示例摄像头
        cameras_data = [
            (str(uuid.uuid4()), '郑州市政府大门', 'traffic', 34.7466, 113.6253, 'online',
             'rtmp://58.200.131.2:1935/livetv/hunantv', 'rtmp', 1920, 1080, 25, 90),
            (str(uuid.uuid4()), '中原路与建设路交叉口', 'traffic', 34.7500, 113.6300, 'online',
             'http://example.com/camera2.m3u8', 'hls', 1280, 720, 30, 180),
            (str(uuid.uuid4()), '金水区花园路', 'surveillance', 34.7600, 113.6400, 'offline',
             'http://example.com/camera3.mp4', 'http', 1920, 1080, 25, 270),
            (str(uuid.uuid4()), 'ReID检测点1', 'reid', 34.7650, 113.6350, 'online',
             'rtmp://example.com/reid1', 'rtmp', 1920, 1080, 25, 0)
        ]
        
        for camera in cameras_data:
            cursor.execute("""
                INSERT INTO cameras (id, name, type, position_lat, position_lng, status,
                                   stream_url, stream_type, resolution_width, resolution_height, fps, direction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, camera)
        
        # 插入示例车辆
        vehicles_data = [
            (str(uuid.uuid4()), '豫A12345', 'car', '白色', '大众', '朗逸', 2020, False, 'low'),
            (str(uuid.uuid4()), '豫B67890', 'truck', '蓝色', '解放', 'J6', 2019, True, 'high'),
            (str(uuid.uuid4()), '豫C11111', 'bus', '黄色', '宇通', 'ZK6120', 2021, False, 'low')
        ]
        
        for vehicle in vehicles_data:
            cursor.execute("""
                INSERT INTO vehicles (id, plate_number, vehicle_type, color, brand, model, year, is_suspicious, risk_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, vehicle)
        
        # 插入AI模型
        models_data = [
            (str(uuid.uuid4()), 'YOLOv8 车辆检测', 'detection', 'pytorch', '1.0.0', 
             'models/yolov8_vehicle.pt', 'models/yolov8_config.yaml', True, 0.5, '640x640',
             json.dumps(['car', 'truck', 'bus', 'motorcycle', 'bicycle']), '基于YOLOv8的车辆检测模型'),
            (str(uuid.uuid4()), 'DeepSORT 目标跟踪', 'tracking', 'tensorflow', '1.0.0',
             'models/deepsort.pb', 'models/deepsort_config.json', True, 0.7, '128x64',
             json.dumps(['person', 'car']), '基于DeepSORT的目标跟踪模型'),
            (str(uuid.uuid4()), 'ReID网络', 'reid', 'pytorch', '1.0.0',
             'models/reid_network.pth', 'models/reid_config.yaml', True, 0.8, '256x128',
             json.dumps(['vehicle']), '车辆ReID特征提取网络'),
            (str(uuid.uuid4()), '路面检测网络', 'road_analysis', 'onnx', '1.0.0',
             'models/road_detection.onnx', 'models/road_config.json', True, 0.6, '512x512',
             json.dumps(['dry', 'wet', 'icy', 'snowy']), '路面状况检测网络'),
            (str(uuid.uuid4()), '危险感知网络', 'danger_detection', 'pytorch', '1.0.0',
             'models/danger_detection.pth', 'models/danger_config.yaml', True, 0.7, '640x640',
             json.dumps(['accident', 'fire', 'flood', 'debris']), '危险事件检测网络')
        ]
        
        for model in models_data:
            cursor.execute("""
                INSERT INTO ai_models (id, name, model_type, framework, version, model_path, 
                                     config_path, is_active, confidence_threshold, input_size, classes, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, model)
        
        # 插入系统配置
        configs_data = [
            ('system_name', '交通监控系统', 'string', '系统名称', True),
            ('max_cameras', '100', 'number', '最大摄像头数量', True),
            ('detection_confidence', '0.5', 'number', '检测置信度阈值', True),
            ('reid_similarity_threshold', '0.8', 'number', 'ReID相似度阈值', True),
            ('alert_retention_days', '30', 'number', '告警保留天数', True),
            ('video_retention_days', '7', 'number', '视频保留天数', True),
            ('auto_cleanup', 'true', 'boolean', '自动清理过期数据', True)
        ]
        
        for config in configs_data:
            cursor.execute("""
                INSERT INTO system_configs (id, config_key, config_value, config_type, description, is_editable)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (str(uuid.uuid4()), config[0], config[1], config[2], config[3], config[4]))
        
        connection.commit()
        print("示例数据插入成功")
        return True
        
    except Error as e:
        print(f"插入示例数据失败: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_indexes():
    """创建额外的索引以优化查询性能"""
    connection = create_database_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("USE traffic_monitor")
        
        # 为车辆检测表创建复合索引
        indexes = [
            "CREATE INDEX idx_vehicle_detections_camera_time_type ON vehicle_detections(camera_id, detection_time, vehicle_type)",
            "CREATE INDEX idx_vehicle_tracks_vehicle_camera_time ON vehicle_tracks(vehicle_id, camera_id, timestamp)",
            "CREATE INDEX idx_vehicle_reid_features_vehicle_created ON vehicle_reid_features(vehicle_id, created_at)",
            "CREATE INDEX idx_road_conditions_camera_time_type ON road_conditions(camera_id, detection_time, road_type)",
            "CREATE INDEX idx_danger_detections_camera_time_type ON danger_detections(camera_id, detection_time, danger_type)",
            "CREATE INDEX idx_model_predictions_model_camera_time ON model_predictions(model_id, camera_id, timestamp)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Error as e:
                print(f"创建索引失败: {e}")
        
        connection.commit()
        print("索引创建完成")
        return True
        
    except Error as e:
        print(f"创建索引失败: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    """主函数"""
    print("开始初始化MySQL数据库...")
    
    # 创建数据库和表
    if not create_database():
        print("数据库创建失败")
        return
    
    # 插入示例数据
    if not insert_sample_data():
        print("示例数据插入失败")
        return
    
    # 创建索引
    if not create_indexes():
        print("索引创建失败")
        return
    
    print("MySQL数据库初始化完成！")
    print("数据库名称: traffic_monitor")
    print("默认管理员账号: admin / admin123")

if __name__ == '__main__':
    main()
