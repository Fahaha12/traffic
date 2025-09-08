#!/bin/bash

# 交通监控系统MySQL版本启动脚本

echo "启动交通监控系统MySQL版本..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查MySQL连接
echo "检查MySQL连接..."
python3 -c "
import mysql.connector
import os
try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )
    print('MySQL连接成功')
    conn.close()
except Exception as e:
    print(f'MySQL连接失败: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "请确保MySQL服务正在运行，并检查数据库连接配置"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cat > .env << EOF
# Flask配置
SECRET_KEY=traffic-monitor-secret-key-2024
JWT_SECRET_KEY=jwt-secret-string

# MySQL数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=traffic_monitor

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=104857600

# AI模型配置
MODEL_PATH=models
DETECTION_CONFIDENCE=0.5
REID_SIMILARITY_THRESHOLD=0.8
TRACKING_MAX_DISAPPEARED=30

# 开发配置
FLASK_ENV=development
FLASK_DEBUG=True
DB_ECHO=False
EOF
    echo "请编辑 .env 文件配置数据库连接信息"
fi

# 初始化数据库
echo "初始化MySQL数据库..."
python database/init_mysql.py

# 启动应用
echo "启动Flask应用..."
python app_mysql.py
