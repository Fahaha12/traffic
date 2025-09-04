# 交通监控系统前端

一个基于Vue 3 + TypeScript的智能交通监控系统前端项目，提供实时地图监控、摄像头管理、车辆追踪和数据分析功能。

## 🚀 功能特性

- **实时地图监控**: 基于Leaflet的高性能地图展示
- **摄像头管理**: 支持多路视频流播放和状态监控
- **车辆追踪**: 实时车辆检测和ReID识别
- **轨迹分析**: 可疑车辆轨迹追踪和告警
- **数据分析**: 交通流量统计和可视化图表
- **响应式设计**: 支持桌面端和移动端访问

## 🛠️ 技术栈

### 核心框架
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript超集
- **Vite** - 下一代前端构建工具

### UI组件
- **Element Plus** - Vue 3组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue状态管理库

### 地图和可视化
- **Leaflet** - 开源地图库
- **ECharts** - 数据可视化图表库
- **Video.js** - HTML5视频播放器

### 开发工具
- **ESLint** - 代码质量检查
- **Prettier** - 代码格式化
- **Auto Import** - 自动导入插件

## 📦 安装和运行

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装依赖
```bash
npm install
```

### 开发环境运行
```bash
npm run dev
```

### 生产环境构建
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 📁 项目结构

```
src/
├── api/                    # API接口
│   ├── map.ts             # 地图相关API
│   ├── camera.ts          # 摄像头API
│   ├── vehicle.ts         # 车辆API
│   └── websocket.ts       # WebSocket连接
├── assets/                # 静态资源
│   ├── images/           # 图片资源
│   └── styles/           # 样式文件
├── components/            # 组件
│   ├── Map/              # 地图组件
│   ├── Video/            # 视频组件
│   ├── Vehicle/          # 车辆组件
│   └── Layout/           # 布局组件
├── stores/               # Pinia状态管理
│   ├── map.ts           # 地图状态
│   ├── camera.ts        # 摄像头状态
│   ├── vehicle.ts       # 车辆状态
│   └── user.ts          # 用户状态
├── types/               # TypeScript类型定义
├── utils/               # 工具函数
├── views/               # 页面组件
└── router/              # 路由配置
```

## 🔧 配置说明

### 环境变量
创建 `.env.local` 文件配置环境变量：

```env
# API基础URL
VITE_API_BASE_URL=http://localhost:8080

# WebSocket URL
VITE_WS_URL=ws://localhost:8080/ws

# 地图配置
VITE_MAP_CENTER_LAT=39.9042
VITE_MAP_CENTER_LNG=116.4074
VITE_MAP_DEFAULT_ZOOM=12
```

### 代理配置
开发环境下的API代理配置在 `vite.config.ts` 中：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## 🎨 主题定制

项目支持暗色主题，可以通过以下方式切换：

```typescript
// 在组件中切换主题
const toggleTheme = () => {
  const html = document.documentElement
  html.classList.toggle('dark')
}
```

## 📱 响应式设计

项目采用响应式设计，支持以下断点：

- 桌面端: >= 1200px
- 平板端: 768px - 1199px
- 移动端: < 768px

## 🔌 API接口

### 地图API
- `GET /api/map/cameras` - 获取摄像头位置
- `POST /api/map/cameras` - 添加摄像头位置
- `PUT /api/map/cameras/:id` - 更新摄像头位置

### 摄像头API
- `GET /api/cameras` - 获取摄像头列表
- `GET /api/cameras/:id/stream` - 获取视频流
- `POST /api/cameras/:id/stream/start` - 开始视频流

### 车辆API
- `GET /api/vehicles` - 获取车辆列表
- `GET /api/vehicles/:id/trajectory` - 获取车辆轨迹
- `GET /api/vehicles/suspicious` - 获取可疑车辆

## 🌐 WebSocket事件

系统支持以下WebSocket事件：

- `camera_status_update` - 摄像头状态更新
- `vehicle_detection` - 车辆检测事件
- `vehicle_reid` - 车辆ReID识别
- `suspicious_vehicle` - 可疑车辆告警
- `vehicle_alert` - 车辆告警事件

## 🚀 部署

### Docker部署
```bash
# 构建镜像
docker build -t traffic-monitor-frontend .

# 运行容器
docker run -p 3000:80 traffic-monitor-frontend
```

### Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws {
        proxy_pass http://backend:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱: your-email@example.com
- 项目地址: https://github.com/your-username/traffic-monitor-frontend

## 🙏 致谢

感谢以下开源项目的支持：

- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [Leaflet](https://leafletjs.com/)
- [ECharts](https://echarts.apache.org/)
- [Vite](https://vitejs.dev/)
