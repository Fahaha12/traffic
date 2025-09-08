# 摄像头数据持久化修复说明

## 问题描述

用户反馈添加的摄像头刷新一下就没有了，这是因为当前系统只将数据保存在内存中，没有持久化存储。页面刷新后，所有数据都会丢失。

## 问题分析

### 1. 数据存储问题
- 摄像头数据只保存在Pinia store的内存中
- 页面刷新后store状态重置，数据丢失
- 没有本地存储或后端API支持

### 2. 初始化问题
- 页面初始化时没有加载保存的数据
- 缺少模拟数据的初始化逻辑
- 各页面之间数据不同步

## 解决方案

### 1. 添加本地存储支持 ✅

#### 1.1 创建存储工具 (`src/utils/storage.ts`)
```typescript
// 通用存储操作
export const storage = {
  set<T>(key: string, data: T): void,
  get<T>(key: string, defaultValue: T): T,
  remove(key: string): void,
  clear(): void
}

// 摄像头数据存储
export const cameraStorage = {
  saveCameras(cameras: any[]): void,
  loadCameras(): any[],
  addCamera(camera: any): void,
  removeCamera(cameraId: string): void,
  updateCamera(cameraId: string, updates: Partial<any>): void
}
```

#### 1.2 存储键常量
```typescript
const STORAGE_KEYS = {
  CAMERAS: 'traffic_monitor_cameras',
  VEHICLES: 'traffic_monitor_vehicles',
  USER_PREFERENCES: 'traffic_monitor_user_preferences'
} as const
```

### 2. 更新摄像头Store ✅

#### 2.1 集成本地存储
```typescript
import { cameraStorage } from '@/utils/storage'

const addCamera = (camera: Camera) => {
  // 更新内存中的数据
  const index = cameras.value.findIndex(c => c.id === camera.id)
  if (index >= 0) {
    cameras.value[index] = camera
  } else {
    cameras.value.push(camera)
  }
  
  // 保存到本地存储
  cameraStorage.addCamera(camera)
}
```

#### 2.2 数据同步
- **添加摄像头**: 同时更新内存和本地存储
- **删除摄像头**: 同时从内存和本地存储中删除
- **更新状态**: 同时更新内存和本地存储

#### 2.3 初始化逻辑
```typescript
// 从本地存储加载摄像头数据
const loadCamerasFromStorage = () => {
  const storedCameras = cameraStorage.loadCameras()
  if (storedCameras.length > 0) {
    cameras.value = storedCameras
  } else {
    // 如果没有存储的数据，初始化一些模拟数据
    initializeMockCameras()
  }
}
```

### 3. 添加模拟数据 ✅

#### 3.1 初始摄像头数据
```typescript
const initializeMockCameras = () => {
  const mockCameras: Camera[] = [
    {
      id: 'camera_001',
      name: '郑州市政府大门',
      type: 'traffic',
      position: { lat: 34.7466, lng: 113.6253 },
      status: 'online',
      streamUrl: 'rtmp://58.200.131.2:1935/livetv/hunantv',
      streamType: 'rtmp',
      resolution: { width: 1920, height: 1080 },
      fps: 25,
      direction: 90,
      lastUpdate: new Date().toISOString()
    },
    // ... 更多模拟数据
  ]

  cameras.value = mockCameras
  cameraStorage.saveCameras(mockCameras)
}
```

#### 3.2 模拟数据特性
- **地理位置**: 基于郑州市的真实坐标
- **流媒体**: 包含RTMP、HLS、HTTP等不同格式
- **状态多样**: 包含在线、离线等不同状态
- **类型丰富**: 交通监控、安防监控等不同类型

### 4. 页面初始化更新 ✅

#### 4.1 CameraView页面
```typescript
onMounted(() => {
  // 首先尝试从本地存储加载摄像头数据
  cameraStore.loadCamerasFromStorage()
  
  // 然后刷新数据（如果有API的话）
  refreshCameras()
})
```

#### 4.2 MapView页面
```typescript
onMounted(() => {
  // 加载摄像头数据
  cameraStore.loadCamerasFromStorage()
})
```

#### 4.3 Dashboard页面
```typescript
onMounted(() => {
  // 首先加载摄像头数据
  cameraStore.loadCamerasFromStorage()
  // 然后刷新数据
  refreshData()
})
```

## 技术实现

### 1. 本地存储策略

#### 1.1 数据格式
- 使用JSON序列化存储复杂对象
- 支持类型安全的泛型操作
- 提供默认值处理

#### 1.2 错误处理
```typescript
try {
  const serialized = JSON.stringify(data)
  localStorage.setItem(key, serialized)
} catch (error) {
  console.error('存储数据失败:', error)
}
```

#### 1.3 数据恢复
```typescript
try {
  const item = localStorage.getItem(key)
  if (item === null) {
    return defaultValue
  }
  return JSON.parse(item) as T
} catch (error) {
  console.error('读取数据失败:', error)
  return defaultValue
}
```

### 2. 数据同步机制

#### 2.1 实时同步
- 每次数据变更都立即同步到本地存储
- 确保内存和存储数据的一致性
- 支持批量操作和单个操作

#### 2.2 状态管理
- 使用Pinia store管理全局状态
- 本地存储作为持久化层
- 页面初始化时自动加载数据

### 3. 模拟数据设计

#### 3.1 地理位置
- 基于郑州市政府坐标 (34.7466, 113.6253)
- 包含多个真实地点的坐标
- 覆盖不同区域和道路

#### 3.2 流媒体格式
- **RTMP流**: `rtmp://58.200.131.2:1935/livetv/hunantv`
- **HLS流**: `http://example.com/camera2.m3u8`
- **HTTP流**: `http://example.com/camera3.mp4`

#### 3.3 摄像头配置
- 不同的分辨率和帧率
- 不同的朝向角度
- 不同的状态和类型

## 功能特性

### 1. 数据持久化
- **自动保存**: 添加、编辑、删除摄像头时自动保存
- **自动加载**: 页面刷新后自动恢复数据
- **数据同步**: 内存和存储数据保持同步

### 2. 用户体验
- **无缝体验**: 用户操作后数据立即保存
- **数据恢复**: 刷新页面后数据不会丢失
- **状态保持**: 摄像头状态和配置都会保持

### 3. 开发友好
- **类型安全**: 使用TypeScript确保类型安全
- **错误处理**: 完善的错误处理机制
- **调试支持**: 控制台日志帮助调试

## 使用说明

### 1. 添加摄像头
1. 进入"摄像头管理"页面
2. 点击"添加摄像头"按钮
3. 填写摄像头信息
4. 点击"添加摄像头"
5. 数据会自动保存到本地存储

### 2. 编辑摄像头
1. 在摄像头列表中点击"编辑"
2. 修改摄像头信息
3. 点击"保存修改"
4. 数据会自动更新到本地存储

### 3. 删除摄像头
1. 在摄像头列表中点击"删除"
2. 确认删除操作
3. 摄像头会从内存和本地存储中删除

### 4. 数据恢复
- 刷新页面后，所有摄像头数据会自动恢复
- 新添加的摄像头会立即显示
- 编辑的摄像头信息会保持最新状态

## 注意事项

### 1. 浏览器兼容性
- 需要支持localStorage的现代浏览器
- 存储空间有限（通常5-10MB）
- 用户清除浏览器数据会丢失所有数据

### 2. 数据安全
- 数据存储在用户本地，不会上传到服务器
- 敏感信息应该避免存储在本地
- 建议定期备份重要数据

### 3. 性能考虑
- 大量数据可能影响页面加载速度
- 建议定期清理过期数据
- 可以考虑分页加载大量数据

## 后续优化建议

### 1. 后端集成
- 添加真实的后端API支持
- 实现数据同步和冲突解决
- 支持多用户数据隔离

### 2. 数据管理
- 添加数据导入/导出功能
- 实现数据备份和恢复
- 支持数据版本控制

### 3. 性能优化
- 实现数据懒加载
- 添加数据缓存机制
- 优化大量数据的处理

### 4. 用户体验
- 添加数据同步状态指示
- 实现离线模式支持
- 提供数据恢复选项

现在系统已经实现了完整的摄像头数据持久化功能，添加的摄像头在刷新页面后不会丢失！
