# 临时文件清理指南

## 概述

本系统包含自动清理功能，用于清理HLS流媒体文件、临时文件、日志文件等，防止磁盘空间被临时文件占满。

## 功能特性

### 🗂️ 自动清理目录
- **streams/**: HLS流媒体文件（.m3u8, .ts, .mp4等）
- **temp/**: 临时文件（.tmp, .temp, .log等）
- **uploads/**: 上传文件（.mp4, .avi, .mov等）
- **logs/**: 日志文件（.log）
- **cache/**: 缓存文件（.cache, .tmp）

### ⏰ 清理策略
- **快速清理**: 每30分钟执行一次
- **每日清理**: 凌晨2点执行深度清理
- **每周清理**: 周日凌晨3点执行完整清理

### 🛡️ 安全设置
- 只清理指定扩展名的文件
- 排除配置文件（.config, .conf, .ini等）
- 设置最大文件大小限制
- 支持干运行模式（测试模式）

## 使用方法

### 1. 自动清理（推荐）

系统启动时会自动启动清理服务：

```bash
# 启动后端服务（自动包含清理服务）
cd backend
python cloud_app.py
```

### 2. 手动清理

#### 执行一次清理
```bash
cd backend
python cleanup_temp_files.py --once
```

#### 启动守护进程
```bash
cd backend
python cleanup_temp_files.py --daemon
```

#### 查看使用情况报告
```bash
cd backend
python cleanup_temp_files.py --report
```

### 3. 使用批处理脚本（Windows）

```bash
# 双击运行或在命令行执行
backend/start_cleanup.bat
```

### 4. 使用Shell脚本（Linux/Mac）

```bash
# 给脚本执行权限
chmod +x backend/start_cleanup.sh

# 运行脚本
./backend/start_cleanup.sh
```

## API接口

### 手动触发清理
```http
POST /api/system/cleanup
```

### 获取清理状态
```http
GET /api/system/cleanup/status
```

响应示例：
```json
{
  "status": "active",
  "usage_info": {
    "streams": {
      "size": 1048576,
      "files": 5,
      "path": "streams"
    },
    "temp": {
      "size": 512000,
      "files": 3,
      "path": "temp"
    }
  },
  "last_cleanup": "2025-09-08T15:30:00.000Z"
}
```

## 配置说明

### 清理配置文件 (cleanup_config.json)

```json
{
  "cleanup_settings": {
    "enabled": true,
    "base_directory": ".",
    "log_file": "cleanup.log"
  },
  "directories": {
    "streams": {
      "path": "streams",
      "enabled": true,
      "max_age_hours": 2,
      "extensions": [".m3u8", ".ts", ".mp4"]
    }
  },
  "schedules": {
    "quick_cleanup": {
      "interval_minutes": 30,
      "enabled": true
    }
  }
}
```

### 主要配置项

- **max_age_hours**: 文件最大保留时间（小时）
- **extensions**: 要清理的文件扩展名
- **enabled**: 是否启用该目录的清理
- **interval_minutes**: 清理间隔（分钟）

## 日志文件

清理操作会记录在以下位置：
- **cleanup.log**: 清理操作日志
- **控制台输出**: 实时清理状态

日志示例：
```
2025-09-08 15:30:00 - INFO - 开始执行定时清理任务...
2025-09-08 15:30:01 - INFO - 清理 streams 目录...
2025-09-08 15:30:02 - INFO - 已删除过期文件: streams/camera1/segment_001.ts (大小: 1024000 bytes)
2025-09-08 15:30:03 - INFO - 目录 streams 清理完成: 删除 5 个文件, 释放 5120000 bytes
2025-09-08 15:30:04 - INFO - 定时清理任务完成，耗时: 4.23 秒
```

## 故障排除

### 1. 清理服务未启动
```bash
# 检查Python依赖
pip install schedule

# 手动启动清理服务
python cleanup_temp_files.py --daemon
```

### 2. 权限问题
```bash
# Linux/Mac: 给脚本执行权限
chmod +x cleanup_temp_files.py
chmod +x start_cleanup.sh
```

### 3. 磁盘空间不足
```bash
# 立即执行清理
python cleanup_temp_files.py --once

# 查看磁盘使用情况
python cleanup_temp_files.py --report
```

### 4. 清理过于频繁
修改 `cleanup_config.json` 中的 `interval_minutes` 值，增加清理间隔。

## 安全注意事项

1. **备份重要文件**: 清理前确保重要文件已备份
2. **测试模式**: 首次使用建议开启 `dry_run` 模式
3. **监控日志**: 定期检查清理日志，确保清理正常
4. **权限控制**: 确保清理脚本有适当的文件系统权限

## 自定义清理规则

### 添加新的清理目录
在 `cleanup_config.json` 中添加新的目录配置：

```json
{
  "directories": {
    "custom_dir": {
      "path": "custom_directory",
      "enabled": true,
      "max_age_hours": 24,
      "extensions": [".custom", ".tmp"],
      "description": "自定义目录"
    }
  }
}
```

### 修改清理时间
```json
{
  "schedules": {
    "custom_cleanup": {
      "interval_minutes": 60,
      "enabled": true,
      "description": "每小时清理一次"
    }
  }
}
```

## 监控和维护

### 定期检查
- 每周检查清理日志
- 监控磁盘使用情况
- 验证清理效果

### 性能优化
- 根据实际使用情况调整清理频率
- 优化文件保留时间
- 监控清理服务的资源使用

## 联系支持

如果遇到问题，请：
1. 查看清理日志文件
2. 检查配置文件设置
3. 验证文件系统权限
4. 联系技术支持团队
