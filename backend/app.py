"""
交通监控系统后端 - 云端MySQL版本
连接到云端数据库: 182.92.210.54:3306
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import logging
import threading
import time

# 导入核心模块
from core import db, Camera, Vehicle, VehicleDetection, VehicleAlert, stream_bp, TempFileCleaner

# 导入路由模块
from routes import auth_bp, system_bp, camera_bp, vehicle_bp, detection_bp, analytics_bp

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
db.init_app(app)
jwt = JWTManager(app)

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/streams/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(system_bp)
app.register_blueprint(camera_bp)
app.register_blueprint(vehicle_bp)
app.register_blueprint(detection_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(stream_bp)

def start_cleanup_service():
    """启动清理服务"""
    try:
        cleaner = TempFileCleaner()
        
        def cleanup_loop():
            while True:
                try:
                    cleaner.cleanup_files()
                    logger.info("自动清理任务执行完成")
                except Exception as e:
                    logger.error(f"自动清理任务执行失败: {str(e)}")
                
                # 每30分钟执行一次
                time.sleep(30 * 60)
        
        # 在后台线程中运行清理服务
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logger.info("清理服务已启动（每30分钟自动清理）")
        
    except Exception as e:
        logger.warning(f"启动清理服务失败: {str(e)}")

def check_database_connection():
    """检查数据库连接"""
    try:
        with app.app_context():
            # 测试数据库连接
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("✅ 云端数据库连接成功！")
            
            # 检查摄像头表是否存在
            try:
                camera_count = Camera.query.count()
                print("✅ 摄像头表存在")
                print(f"📊 当前摄像头数量: {camera_count}")
                
                # 显示摄像头列表
                cameras = Camera.query.limit(5).all()
                print("📋 摄像头列表:")
                for camera in cameras:
                    print(f"  - {camera.name} ({camera.status})")
                
            except Exception as e:
                print("⚠️ 摄像头表不存在，正在创建...")
                # 创建表
                db.create_all()
                print("✅ 数据库表创建完成")
            
            return True
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

if __name__ == '__main__':
    print("启动交通监控系统云端版本...")
    print("API地址: http://localhost:5000")
    print("健康检查: http://localhost:5000/api/health")
    print("摄像头API: http://localhost:5000/api/cameras")
    print("流媒体API: http://localhost:5000/api/stream")
    print("数据库: MySQL (182.92.210.54:3306)")
    
    # 检查数据库连接
    if check_database_connection():
        # 启动清理服务
        start_cleanup_service()
        print("清理服务: 已启动（每30分钟自动清理）")
        
        # 启动Flask应用
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ 数据库连接失败，无法启动服务")
