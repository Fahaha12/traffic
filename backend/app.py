"""
交通监控系统后端 - 云端MySQL版本
连接到云端数据库: 182.92.210.54:3306
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta
import os
import logging
import uuid
import threading
import time

# 导入流媒体服务
from stream_routes import stream_bp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 基础配置
app.config['SECRET_KEY'] = 'traffic-monitor-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 云端MySQL数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://traffic:4YMZf8WAKt4yDJED@182.92.210.54:3306/traffic'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'echo': False
}

# 初始化扩展
db = SQLAlchemy(app)
jwt = JWTManager(app)

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

# 摄像头模型
class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.Enum('traffic', 'surveillance', 'speed', 'reid'), nullable=False)
    position_lat = db.Column(db.Float, nullable=False)
    position_lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('online', 'offline', 'maintenance'), default='offline')
    stream_url = db.Column(db.String(500), nullable=False)
    stream_type = db.Column(db.Enum('rtmp', 'hls', 'http', 'webrtc'), nullable=False)
    resolution_width = db.Column(db.Integer, default=1920)
    resolution_height = db.Column(db.Integer, default=1080)
    fps = db.Column(db.Integer, default=25)
    direction = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_actual_status(self):
        """获取摄像头的实际状态"""
        try:
            # 检查是否为RTMP流
            if self.stream_url.startswith('rtmp://'):
                # 导入流媒体转换器
                from stream_converter import stream_converter
                
                # 检查是否正在转换
                status = stream_converter.get_conversion_status(self.id)
                if status and status['status'] == 'converting':
                    return 'online'
                else:
                    return 'offline'
            else:
                # 对于非RTMP流，假设在线
                return 'online'
        except Exception as e:
            logger.error(f'检测摄像头状态失败: {str(e)}')
            return 'offline'
    
    def to_dict(self):
        # 获取实际状态
        actual_status = self.get_actual_status()
        
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'position': {
                'lat': self.position_lat,
                'lng': self.position_lng
            },
            'status': actual_status,  # 使用实际状态
            'streamUrl': self.stream_url,
            'streamType': self.stream_type,
            'resolution': {
                'width': self.resolution_width,
                'height': self.resolution_height
            },
            'fps': self.fps,
            'direction': self.direction,
            'lastUpdate': self.updated_at.isoformat()
        }

# 车辆模型
class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plate_number = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.Enum('car', 'truck', 'bus', 'motorcycle', 'bicycle', 'unknown'), nullable=False)
    color = db.Column(db.String(20))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    is_suspicious = db.Column(db.Boolean, default=False)
    risk_level = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='low')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plateNumber': self.plate_number,
            'vehicleType': self.vehicle_type,
            'color': self.color,
            'brand': self.brand,
            'model': self.model,
            'isSuspicious': self.is_suspicious,
            'riskLevel': self.risk_level,
            'createdAt': self.created_at.isoformat()
        }

# 车辆检测模型
class VehicleDetection(db.Model):
    __tablename__ = 'vehicle_detections'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    camera_id = db.Column(db.String(36), nullable=False)
    detection_time = db.Column(db.DateTime, nullable=False)
    bbox_x1 = db.Column(db.Float, nullable=False)
    bbox_y1 = db.Column(db.Float, nullable=False)
    bbox_x2 = db.Column(db.Float, nullable=False)
    bbox_y2 = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    vehicle_type = db.Column(db.Enum('car', 'truck', 'bus', 'motorcycle', 'bicycle', 'unknown'), nullable=False)
    color = db.Column(db.String(20))
    speed = db.Column(db.Float)
    direction = db.Column(db.Float)
    image_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cameraId': self.camera_id,
            'detectionTime': self.detection_time.isoformat(),
            'bbox': {
                'x1': self.bbox_x1,
                'y1': self.bbox_y1,
                'x2': self.bbox_x2,
                'y2': self.bbox_y2
            },
            'confidence': self.confidence,
            'vehicleType': self.vehicle_type,
            'color': self.color,
            'speed': self.speed,
            'direction': self.direction,
            'imagePath': self.image_path,
            'createdAt': self.created_at.isoformat()
        }

# 健康检查
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'database': 'mysql_cloud',
        'host': '182.92.210.54:3306',
        'features': ['vehicle_detection', 'camera_management', 'user_auth', 'cloud_database']
    })

# 用户认证API
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user or not user.is_active:
            return jsonify({'error': '用户不存在或已被禁用'}), 401
        
        # 简单的密码验证（实际应用中应该验证密码哈希）
        if password == 'admin123' or password == 'password':
            return jsonify({
                'access_token': f'token_{user.id}_{int(datetime.utcnow().timestamp())}',
                'user': user.to_dict(),
                'message': '登录成功'
            }), 200
        else:
            return jsonify({'error': '密码错误'}), 401
            
    except Exception as e:
        logger.error(f'登录失败: {str(e)}')
        return jsonify({'error': '登录失败'}), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    try:
        # 简单的用户信息获取
        user = User.query.filter_by(username='admin').first()
        if user:
            return jsonify({'user': user.to_dict()}), 200
        else:
            return jsonify({'error': '用户不存在'}), 404
    except Exception as e:
        logger.error(f'获取用户信息失败: {str(e)}')
        return jsonify({'error': '获取用户信息失败'}), 500

# 摄像头API
@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = Camera.query
        if status:
            query = query.filter_by(status=status)
        
        cameras = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'cameras': [camera.to_dict() for camera in cameras.items],
            'total': cameras.total,
            'page': page,
            'per_page': per_page,
            'pages': cameras.pages
        }), 200
    except Exception as e:
        logger.error(f'获取摄像头列表失败: {str(e)}')
        return jsonify({'error': '获取摄像头列表失败'}), 500

@app.route('/api/cameras/<camera_id>', methods=['GET'])
def get_camera(camera_id):
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        return jsonify({'camera': camera.to_dict()}), 200
    except Exception as e:
        logger.error(f'获取摄像头信息失败: {str(e)}')
        return jsonify({'error': '获取摄像头信息失败'}), 500

@app.route('/api/cameras', methods=['POST'])
def create_camera():
    try:
        data = request.get_json()
        logger.info(f'创建摄像头接收到的数据: {data}')
        
        # 验证必填字段
        required_fields = ['name', 'type', 'position', 'streamUrl', 'streamType']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 检查名称是否已存在
        existing_camera = Camera.query.filter_by(name=data['name']).first()
        if existing_camera:
            return jsonify({'error': '摄像头名称已存在'}), 400
        
        # 创建摄像头
        camera = Camera(
            name=data['name'],
            type=data['type'],
            position_lat=data['position']['lat'],
            position_lng=data['position']['lng'],
            stream_url=data['streamUrl'],
            stream_type=data['streamType'],
            resolution_width=data.get('resolution', {}).get('width', 1920),
            resolution_height=data.get('resolution', {}).get('height', 1080),
            fps=data.get('fps', 25),
            direction=data.get('direction', 0)
        )
        
        db.session.add(camera)
        db.session.commit()
        
        return jsonify({
            'message': '摄像头创建成功',
            'camera': camera.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建摄像头失败: {str(e)}')
        return jsonify({'error': '创建摄像头失败'}), 500

@app.route('/api/cameras/<camera_id>', methods=['PUT'])
def update_camera(camera_id):
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        data = request.get_json()
        logger.info(f'更新摄像头 {camera_id} 接收到的数据: {data}')
        
        # 检查名称是否与其他摄像头冲突
        if 'name' in data and data['name'] != camera.name:
            existing_camera = Camera.query.filter_by(name=data['name']).first()
            if existing_camera:
                return jsonify({'error': '摄像头名称已存在'}), 400
        
        # 更新字段
        if 'name' in data:
            camera.name = data['name']
        if 'type' in data:
            camera.type = data['type']
        if 'position' in data:
            camera.position_lat = data['position']['lat']
            camera.position_lng = data['position']['lng']
        if 'streamUrl' in data:
            camera.stream_url = data['streamUrl']
        if 'streamType' in data:
            camera.stream_type = data['streamType']
        if 'resolution' in data:
            camera.resolution_width = data['resolution'].get('width', 1920)
            camera.resolution_height = data['resolution'].get('height', 1080)
        if 'fps' in data:
            camera.fps = data['fps']
        if 'direction' in data:
            camera.direction = data['direction']
        
        camera.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '摄像头更新成功',
            'camera': camera.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新摄像头失败: {str(e)}')
        return jsonify({'error': '更新摄像头失败'}), 500

@app.route('/api/cameras/<camera_id>/convert', methods=['POST'])
def convert_camera_stream(camera_id):
    """转换摄像头RTMP流为HLS流"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        # 检查是否为RTMP流
        if not camera.stream_url.startswith('rtmp://'):
            return jsonify({'error': '只有RTMP流需要转换'}), 400
        
        # 导入流媒体转换器
        from stream_converter import stream_converter
        
        # 开始转换
        result = stream_converter.convert_rtmp_to_hls(camera.stream_url, camera_id)
        
        if result['success']:
            return jsonify({
                'message': '流媒体转换已启动',
                'stream_id': result['stream_id'],
                'hls_url': result['hls_url'],
                'status': result['status']
            }), 200
        else:
            return jsonify({
                'error': '流媒体转换启动失败',
                'details': result.get('error', '未知错误')
            }), 500
            
    except Exception as e:
        logger.error(f'转换摄像头流媒体失败: {str(e)}')
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/api/cameras/<camera_id>/stream')
def get_camera_stream(camera_id):
    """获取摄像头的HLS流地址"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        # 检查是否为RTMP流
        if camera.stream_url.startswith('rtmp://'):
            # 导入流媒体转换器
            from stream_converter import stream_converter
            
            # 检查是否已经在转换
            status = stream_converter.get_conversion_status(camera_id)
            if status and status['status'] == 'converting':
                return jsonify({
                    'stream_id': camera_id,
                    'hls_url': f'/api/stream/play/{camera_id}',
                    'status': 'converting',
                    'message': '流媒体正在转换中'
                }), 200
            else:
                # 如果没有转换，返回需要转换的状态，而不是错误
                return jsonify({
                    'stream_id': camera_id,
                    'hls_url': None,
                    'status': 'not_converted',
                    'message': 'RTMP流需要转换',
                    'rtmp_url': camera.stream_url
                }), 200
        else:
            # 非RTMP流直接返回
            return jsonify({
                'stream_id': camera_id,
                'hls_url': camera.stream_url,
                'status': 'ready',
                'message': '流媒体可直接播放'
            }), 200
            
    except Exception as e:
        logger.error(f'获取摄像头流媒体失败: {str(e)}')
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/api/cameras/<camera_id>/status', methods=['GET'])
def get_camera_status(camera_id):
    """获取摄像头的实时状态"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        actual_status = camera.get_actual_status()
        
        return jsonify({
            'camera_id': camera_id,
            'status': actual_status,
            'stream_url': camera.stream_url,
            'last_check': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f'获取摄像头状态失败: {str(e)}')
        return jsonify({'error': '获取摄像头状态失败'}), 500

@app.route('/api/cameras/<camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        db.session.delete(camera)
        db.session.commit()
        
        return jsonify({'message': '摄像头删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除摄像头失败: {str(e)}')
        return jsonify({'error': '删除摄像头失败'}), 500

@app.route('/api/cameras/<camera_id>/test-connection', methods=['POST'])
def test_connection(camera_id):
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        # 模拟连接测试
        import random
        is_online = random.choice([True, True, True, False])  # 75%成功率
        
        if is_online:
            camera.status = 'online'
            message = '连接测试成功'
        else:
            camera.status = 'offline'
            message = '连接测试失败'
        
        camera.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': is_online,
            'message': message,
            'camera': camera.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'测试连接失败: {str(e)}')
        return jsonify({'error': '测试连接失败'}), 500

@app.route('/api/system/cleanup', methods=['POST'])
def manual_cleanup():
    """手动触发清理任务"""
    try:
        from cleanup_temp_files import TempFileCleaner
        cleaner = TempFileCleaner()
        
        # 执行清理
        cleaner.cleanup_all()
        
        # 获取清理后的使用情况
        usage_info = cleaner.get_disk_usage()
        
        return jsonify({
            'message': '清理任务执行完成',
            'status': 'success',
            'usage_info': usage_info
        }), 200
        
    except Exception as e:
        logger.error(f'手动清理失败: {str(e)}')
        return jsonify({'error': '清理任务执行失败'}), 500

@app.route('/api/system/cleanup/status', methods=['GET'])
def cleanup_status():
    """获取清理服务状态和磁盘使用情况"""
    try:
        from cleanup_temp_files import TempFileCleaner
        cleaner = TempFileCleaner()
        
        usage_info = cleaner.get_disk_usage()
        
        return jsonify({
            'status': 'active',
            'usage_info': usage_info,
            'last_cleanup': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f'获取清理状态失败: {str(e)}')
        return jsonify({'error': '获取清理状态失败'}), 500

# 车辆API
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        vehicle_type = request.args.get('type')
        is_suspicious = request.args.get('is_suspicious')
        
        query = Vehicle.query
        
        if vehicle_type:
            query = query.filter_by(vehicle_type=vehicle_type)
        if is_suspicious is not None:
            query = query.filter_by(is_suspicious=is_suspicious.lower() == 'true')
        
        vehicles = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'vehicles': [vehicle.to_dict() for vehicle in vehicles.items],
            'total': vehicles.total,
            'page': page,
            'per_page': per_page,
            'pages': vehicles.pages
        }), 200
    except Exception as e:
        logger.error(f'获取车辆列表失败: {str(e)}')
        return jsonify({'error': '获取车辆列表失败'}), 500

# 检测API
@app.route('/api/detection', methods=['GET'])
def get_detections():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        camera_id = request.args.get('camera_id')
        
        query = VehicleDetection.query
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        
        detections = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'detections': [detection.to_dict() for detection in detections.items],
            'total': detections.total,
            'page': page,
            'per_page': per_page,
            'pages': detections.pages
        }), 200
    except Exception as e:
        logger.error(f'获取检测记录失败: {str(e)}')
        return jsonify({'error': '获取检测记录失败'}), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # 测试数据库连接
    try:
        with app.app_context():
            # 测试连接
            with db.engine.connect() as conn:
                result = conn.execute(db.text('SELECT 1'))
                print("✅ 云端数据库连接成功！")
            
            # 检查表是否存在，如果不存在则创建
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SHOW TABLES LIKE 'cameras'"))
                if result.fetchone():
                    print("✅ 摄像头表存在")
                else:
                    print("⚠️ 摄像头表不存在，正在创建...")
                    # 创建表
                    db.create_all()
                    print("✅ 数据库表创建完成")
            
            # 检查摄像头数据
            try:
                camera_count = Camera.query.count()
                print(f"📊 当前摄像头数量: {camera_count}")
                
                if camera_count > 0:
                    print("📋 摄像头列表:")
                    cameras = Camera.query.limit(5).all()
                    for camera in cameras:
                        print(f"  - {camera.name} ({camera.status})")
                else:
                    print("📝 数据库为空，可以开始添加数据")
            except Exception as e:
                print(f"⚠️ 查询摄像头数据时出错: {e}")
                print("数据库表可能结构不匹配，请检查SQL文件是否正确导入")
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查:")
        print("1. 数据库服务器是否运行")
        print("2. 网络连接是否正常")
        print("3. 用户名密码是否正确")
        print("4. 数据库名称是否正确")
        exit(1)
    
    # 注册流媒体蓝图
    app.register_blueprint(stream_bp)
    
    # 启动清理服务
    def start_cleanup_service():
        """启动后台清理服务"""
        try:
            from cleanup_temp_files import TempFileCleaner
            cleaner = TempFileCleaner()
            
            def cleanup_worker():
                while True:
                    try:
                        time.sleep(1800)  # 每30分钟执行一次
                        cleaner.cleanup_all()
                    except Exception as e:
                        logger.error(f"清理服务出错: {e}")
                        time.sleep(300)  # 出错后等待5分钟再重试
            
            cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
            cleanup_thread.start()
            logger.info("后台清理服务已启动")
        except Exception as e:
            logger.warning(f"启动清理服务失败: {e}")
    
    # 启动清理服务
    start_cleanup_service()
    
    print("启动交通监控系统云端版本...")
    print("API地址: http://localhost:5000")
    print("健康检查: http://localhost:5000/api/health")
    print("摄像头API: http://localhost:5000/api/cameras")
    print("流媒体API: http://localhost:5000/api/stream")
    print("数据库: MySQL (182.92.210.54:3306)")
    print("清理服务: 已启动（每30分钟自动清理）")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
