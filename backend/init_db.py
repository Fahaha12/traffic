"""
数据库初始化脚本
"""

from app import create_app, db
from app.models.user import User
from app.models.camera import Camera
from app.models.vehicle import Vehicle
from app.models.alert import Alert
from app.models.ai_model import AIModel
import os

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")
        
        # 创建管理员用户
        admin = User.create_admin_user()
        print(f"管理员用户创建完成: {admin.username}")
        
        # 创建示例摄像头
        create_sample_cameras()
        print("示例摄像头创建完成")
        
        # 创建示例车辆
        create_sample_vehicles()
        print("示例车辆创建完成")
        
        # 创建示例AI模型
        create_sample_ai_models()
        print("示例AI模型创建完成")
        
        # 创建示例告警
        create_sample_alerts()
        print("示例告警创建完成")
        
        print("数据库初始化完成！")

def create_sample_cameras():
    """创建示例摄像头"""
    cameras_data = [
        {
            'name': '郑州市政府大门',
            'type': 'traffic',
            'position': {'lat': 34.7466, 'lng': 113.6253},
            'status': 'online',
            'stream_url': 'rtmp://58.200.131.2:1935/livetv/hunantv',
            'stream_type': 'rtmp',
            'resolution': {'width': 1920, 'height': 1080},
            'fps': 25,
            'direction': 90
        },
        {
            'name': '中原路与建设路交叉口',
            'type': 'traffic',
            'position': {'lat': 34.7500, 'lng': 113.6300},
            'status': 'online',
            'stream_url': 'http://example.com/camera2.m3u8',
            'stream_type': 'hls',
            'resolution': {'width': 1280, 'height': 720},
            'fps': 30,
            'direction': 180
        },
        {
            'name': '金水区花园路',
            'type': 'surveillance',
            'position': {'lat': 34.7600, 'lng': 113.6400},
            'status': 'offline',
            'stream_url': 'http://example.com/camera3.mp4',
            'stream_type': 'http',
            'resolution': {'width': 1920, 'height': 1080},
            'fps': 25,
            'direction': 270
        }
    ]
    
    for camera_data in cameras_data:
        camera = Camera(
            name=camera_data['name'],
            type=camera_data['type'],
            stream_url=camera_data['stream_url'],
            stream_type=camera_data['stream_type'],
            fps=camera_data['fps'],
            direction=camera_data['direction']
        )
        camera.position = camera_data['position']
        camera.resolution = camera_data['resolution']
        camera.status = camera_data['status']
        
        db.session.add(camera)
    
    db.session.commit()

def create_sample_vehicles():
    """创建示例车辆"""
    vehicles_data = [
        {
            'plate_number': '豫A12345',
            'vehicle_type': 'car',
            'color': '白色',
            'brand': '大众',
            'model': '朗逸',
            'year': 2020,
            'is_suspicious': False,
            'risk_level': 'low'
        },
        {
            'plate_number': '豫B67890',
            'vehicle_type': 'truck',
            'color': '蓝色',
            'brand': '解放',
            'model': 'J6',
            'year': 2019,
            'is_suspicious': True,
            'risk_level': 'high'
        },
        {
            'plate_number': '豫C11111',
            'vehicle_type': 'bus',
            'color': '黄色',
            'brand': '宇通',
            'model': 'ZK6120',
            'year': 2021,
            'is_suspicious': False,
            'risk_level': 'low'
        }
    ]
    
    for vehicle_data in vehicles_data:
        vehicle = Vehicle(**vehicle_data)
        db.session.add(vehicle)
    
    db.session.commit()

def create_sample_ai_models():
    """创建示例AI模型"""
    models_data = [
        {
            'name': 'YOLOv8 车辆检测模型',
            'model_type': 'detection',
            'framework': 'pytorch',
            'model_path': 'models/yolov8_vehicle.pt',
            'version': '1.0.0',
            'confidence_threshold': 0.5,
            'input_size': '640x640',
            'classes': ['car', 'truck', 'bus', 'motorcycle'],
            'description': '基于YOLOv8的车辆检测模型',
            'is_active': True
        },
        {
            'name': 'DeepSORT 目标跟踪模型',
            'model_type': 'tracking',
            'framework': 'tensorflow',
            'model_path': 'models/deepsort.pb',
            'version': '1.0.0',
            'confidence_threshold': 0.7,
            'input_size': '128x64',
            'classes': ['person', 'car'],
            'description': '基于DeepSORT的目标跟踪模型',
            'is_active': True
        },
        {
            'name': 'ResNet 车辆分类模型',
            'model_type': 'classification',
            'framework': 'onnx',
            'model_path': 'models/resnet_vehicle.onnx',
            'version': '1.0.0',
            'confidence_threshold': 0.8,
            'input_size': '224x224',
            'classes': ['sedan', 'suv', 'truck', 'bus'],
            'description': '基于ResNet的车辆分类模型',
            'is_active': False
        }
    ]
    
    for model_data in models_data:
        model = AIModel(
            name=model_data['name'],
            model_type=model_data['model_type'],
            framework=model_data['framework'],
            model_path=model_data['model_path'],
            version=model_data['version'],
            confidence_threshold=model_data['confidence_threshold'],
            input_size=model_data['input_size'],
            description=model_data['description'],
            is_active=model_data['is_active']
        )
        model.set_classes(model_data['classes'])
        
        db.session.add(model)
    
    db.session.commit()

def create_sample_alerts():
    """创建示例告警"""
    alerts_data = [
        {
            'title': '摄像头离线告警',
            'description': '摄像头"金水区花园路"已离线超过5分钟',
            'alert_type': 'camera',
            'severity': 'warning',
            'status': 'active',
            'source': 'system'
        },
        {
            'title': '检测到可疑车辆',
            'description': '车牌号豫B67890的车辆行为异常',
            'alert_type': 'vehicle',
            'severity': 'high',
            'status': 'active',
            'source': 'ai_detection'
        },
        {
            'title': '系统启动完成',
            'description': '交通监控系统启动完成，所有服务正常运行',
            'alert_type': 'system',
            'severity': 'info',
            'status': 'resolved',
            'source': 'system'
        }
    ]
    
    for alert_data in alerts_data:
        alert = Alert(**alert_data)
        db.session.add(alert)
    
    db.session.commit()

if __name__ == '__main__':
    init_database()
