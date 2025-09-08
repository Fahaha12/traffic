# 流媒体转换服务设置说明

## 功能概述

现在系统已经实现了**后端代理 + HLS**方案，可以真正播放RTMP流：

1. **后端FFmpeg服务**：将RTMP流实时转换为HLS流
2. **流媒体代理API**：提供转换、播放、管理接口
3. **前端智能播放**：优先使用后端转换，备用本地转换

## 安装依赖

### 1. 安装FFmpeg

#### Windows:
```bash
# 下载FFmpeg: https://ffmpeg.org/download.html
# 解压到 C:\ffmpeg
# 添加 C:\ffmpeg\bin 到系统PATH
```

#### Linux/macOS:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# macOS
brew install ffmpeg
```

### 2. 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

## 使用方法

### 1. 启动后端服务

```bash
cd backend
python cloud_app.py
```

### 2. 测试流媒体转换

#### 转换RTMP流：
```bash
curl -X POST http://localhost:5000/api/cameras/{camera_id}/convert
```

#### 获取HLS流地址：
```bash
curl http://localhost:5000/api/cameras/{camera_id}/stream
```

#### 播放HLS流：
```bash
curl http://localhost:5000/api/stream/play/{camera_id}
```

### 3. 前端使用

前端会自动：
1. 检测RTMP流
2. 调用后端转换API
3. 获取HLS流地址
4. 使用HLS.js播放

## API接口

### 摄像头流媒体API

#### 转换RTMP流
```
POST /api/cameras/{camera_id}/convert
```

#### 获取流媒体地址
```
GET /api/cameras/{camera_id}/stream
```

### 流媒体管理API

#### 获取转换状态
```
GET /api/stream/status/{stream_id}
```

#### 停止转换
```
POST /api/stream/stop/{stream_id}
```

#### 播放HLS流
```
GET /api/stream/play/{stream_id}
```

#### 获取片段文件
```
GET /api/stream/segment/{stream_id}/{filename}
```

#### 列出所有流
```
GET /api/stream/list
```

#### 清理旧流
```
POST /api/stream/cleanup
```

## 工作流程

### 1. RTMP流转换流程

```
用户点击播放
    ↓
前端检测到RTMP流
    ↓
调用后端转换API
    ↓
后端启动FFmpeg转换
    ↓
返回HLS流地址
    ↓
前端使用HLS.js播放
```

### 2. 文件结构

```
backend/
├── stream_converter.py    # FFmpeg转换服务
├── stream_routes.py       # 流媒体API路由
├── cloud_app.py          # 主应用（已集成）
└── streams/              # HLS文件输出目录
    └── {stream_id}/
        ├── playlist.m3u8  # HLS播放列表
        └── segment_*.ts   # 视频片段
```

## 配置说明

### 1. FFmpeg参数

```python
# 在 stream_converter.py 中可调整：
cmd = [
    'ffmpeg',
    '-i', rtmp_url,           # 输入RTMP流
    '-c:v', 'libx264',        # 视频编码器
    '-c:a', 'aac',            # 音频编码器
    '-f', 'hls',              # 输出格式
    '-hls_time', '2',         # 每个片段2秒
    '-hls_list_size', '5',    # 保留5个片段
    '-hls_flags', 'delete_segments',  # 删除旧片段
    hls_path
]
```

### 2. 输出目录

```python
# 默认输出目录
output_dir = "streams"

# 可自定义
stream_converter = StreamConverter(output_dir="custom_streams")
```

## 故障排除

### 1. FFmpeg未找到

**错误**：`FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**解决**：
- 确保FFmpeg已安装
- 检查PATH环境变量
- 在代码中指定FFmpeg完整路径

### 2. RTMP连接失败

**错误**：`Connection refused` 或 `Network unreachable`

**解决**：
- 检查RTMP流地址是否正确
- 确认网络连接
- 验证流媒体服务器状态

### 3. 转换进程卡死

**解决**：
- 检查FFmpeg进程：`ps aux | grep ffmpeg`
- 手动停止：`pkill ffmpeg`
- 重启后端服务

### 4. HLS文件无法访问

**解决**：
- 检查文件权限
- 确认输出目录存在
- 查看后端日志

## 性能优化

### 1. 并发转换

```python
# 限制同时转换的流数量
MAX_CONCURRENT_STREAMS = 5

if len(active_conversions) >= MAX_CONCURRENT_STREAMS:
    return {'error': '转换队列已满'}
```

### 2. 资源清理

```python
# 定期清理旧文件
cleanup_old_streams(max_age_hours=24)
```

### 3. 监控日志

```python
# 启用详细日志
logging.basicConfig(level=logging.DEBUG)
```

## 注意事项

1. **FFmpeg依赖**：确保系统已安装FFmpeg
2. **磁盘空间**：HLS文件会占用磁盘空间
3. **网络带宽**：转换过程消耗网络带宽
4. **CPU使用**：视频转换是CPU密集型任务
5. **并发限制**：避免同时转换过多流

现在系统可以真正播放RTMP流了！🎉
