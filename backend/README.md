# 交通监控系统后端

基于Flask的交通监控系统后端API，支持摄像头管理、视频流处理、深度学习模型集成等功能。

## 功能特性

### 🎯 核心功能
- **摄像头管理**: 添加、编辑、删除摄像头，支持多种流媒体格式
- **视频流处理**: 实时视频流分析，支持RTMP、HLS、HTTP格式
- **车辆管理**: 车辆信息管理、轨迹跟踪、可疑车辆标记
- **告警系统**: 实时告警生成、分类、处理
- **数据分析**: 交通流量分析、车辆行为分析、告警统计

### 🤖 AI集成
- **深度学习模型管理**: 支持PyTorch、TensorFlow、ONNX模型
- **目标检测**: 基于YOLO的车辆和人员检测
- **目标跟踪**: DeepSORT算法实现车辆跟踪
- **行为分析**: 可疑行为检测和告警

### 🔧 技术栈
- **后端框架**: Flask + SQLAlchemy + Flask-Migrate
- **数据库**: SQLite/PostgreSQL/MySQL
- **AI框架**: PyTorch + TensorFlow + ONNX
- **视频处理**: OpenCV + FFmpeg
- **实时通信**: WebSocket + SocketIO
- **任务队列**: Celery + Redis

## 快速开始

### 1. 环境要求

- Python 3.8+
- Node.js 16+ (前端)
- Redis (可选，用于任务队列)
- PostgreSQL/MySQL (可选，生产环境推荐)

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd traffic-monitor/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 复制环境变量文件
cp env.example .env

# 编辑配置文件
# 修改数据库连接、Redis配置等
```

### 4. 初始化数据库

```bash
# 初始化数据库和示例数据
python init_db.py
```

### 5. 启动服务

```bash
# 开发模式
python run.py

# 或使用启动脚本
chmod +x start.sh
./start.sh
```

### 6. 访问API

- API文档: http://localhost:5000/api/health
- 健康检查: http://localhost:5000/api/health

## API文档

### 认证接口

```bash
# 用户登录
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# 获取用户信息
GET /api/auth/profile
Authorization: Bearer <token>
```

### 摄像头管理

```bash
# 获取摄像头列表
GET /api/cameras?page=1&per_page=20&status=online

# 创建摄像头
POST /api/cameras
{
  "name": "摄像头名称",
  "type": "traffic",
  "position": {"lat": 34.7466, "lng": 113.6253},
  "streamUrl": "rtmp://example.com/stream",
  "streamType": "rtmp"
}

# 测试摄像头连接
POST /api/cameras/{camera_id}/test-connection
```

### 车辆管理

```bash
# 获取车辆列表
GET /api/vehicles?page=1&per_page=20

# 获取车辆轨迹
GET /api/vehicles/{vehicle_id}/tracks?start_time=2024-01-01&end_time=2024-01-02

# 标记可疑车辆
POST /api/vehicles/{vehicle_id}/mark-suspicious
{
  "is_suspicious": true,
  "risk_level": "high",
  "reason": "超速行驶"
}
```

### AI模型管理

```bash
# 获取AI模型列表
GET /api/ai/models

# 创建AI模型
POST /api/ai/models
{
  "name": "YOLOv8 车辆检测",
  "modelType": "detection",
  "framework": "pytorch",
  "modelPath": "models/yolov8.pt",
  "confidenceThreshold": 0.5
}

# 执行AI预测
POST /api/ai/predict
{
  "modelId": "model_id",
  "cameraId": "camera_id",
  "imagePath": "path/to/image.jpg"
}
```

## 数据库设计

### 主要表结构

- **users**: 用户表
- **cameras**: 摄像头表
- **vehicles**: 车辆表
- **vehicle_tracks**: 车辆轨迹表
- **vehicle_alerts**: 车辆告警表
- **alerts**: 系统告警表
- **ai_models**: AI模型表
- **model_predictions**: 模型预测结果表

### 数据库迁移

```bash
# 创建迁移文件
flask db migrate -m "描述"

# 执行迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

## 深度学习集成

### 支持的模型类型

1. **目标检测**: YOLO系列、R-CNN系列
2. **目标跟踪**: DeepSORT、ByteTrack
3. **行为分析**: 动作识别、异常检测
4. **车辆分类**: 车型识别、颜色识别

### 模型部署

1. 将模型文件放入 `models/` 目录
2. 通过API创建模型记录
3. 激活模型开始使用

### 自定义模型

```python
# 在 app/ai/model_manager.py 中添加自定义模型加载逻辑
def _load_custom_model(self, model: AIModel):
    # 自定义模型加载逻辑
    pass
```

## 视频流处理

### 支持的流格式

- **RTMP**: 实时消息协议
- **HLS**: HTTP Live Streaming
- **HTTP**: 标准HTTP视频流

### 流处理流程

1. 接收视频流
2. 帧提取和分析
3. AI模型推理
4. 结果存储和告警

## 部署指南

### 开发环境

```bash
# 使用SQLite数据库
export DATABASE_URL=sqlite:///traffic_monitor.db

# 启动开发服务器
python run.py
```

### 生产环境

```bash
# 使用PostgreSQL数据库
export DATABASE_URL=postgresql://user:pass@localhost/traffic_monitor

# 使用Gunicorn启动
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 使用Docker
docker build -t traffic-monitor-backend .
docker run -p 5000:5000 traffic-monitor-backend
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 监控和日志

### 日志配置

```python
# 在 app.py 中配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 性能监控

- 使用Flask-MonitoringDashboard进行性能监控
- 集成Prometheus指标收集
- 配置告警规则

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接字符串配置

2. **AI模型加载失败**
   - 检查模型文件路径
   - 验证模型格式和依赖

3. **视频流处理失败**
   - 检查流地址是否可访问
   - 验证OpenCV和FFmpeg安装

### 调试模式

```bash
# 启用调试模式
export FLASK_DEBUG=True
export FLASK_ENV=development

# 查看详细日志
tail -f app.log
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

MIT License

## 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目地址: [GitHub Repository URL]
