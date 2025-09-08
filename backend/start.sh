#!/bin/bash

# 交通监控系统后端启动脚本

echo "启动交通监控系统后端..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
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
    cp env.example .env
    echo "请编辑 .env 文件配置数据库和其他设置"
fi

# 初始化数据库
echo "初始化数据库..."
python init_db.py

# 启动应用
echo "启动Flask应用..."
python run.py
