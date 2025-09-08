#!/bin/bash

echo "启动临时文件清理服务..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 安装依赖
echo "安装清理脚本依赖..."
pip3 install schedule

# 给脚本执行权限
chmod +x cleanup_temp_files.py

# 启动清理服务
echo "启动清理服务..."
python3 cleanup_temp_files.py --daemon
