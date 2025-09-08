@echo off
echo 启动临时文件清理服务...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 安装依赖
echo 安装清理脚本依赖...
pip install schedule

REM 启动清理服务
echo 启动清理服务...
python cleanup_temp_files.py --daemon

pause
