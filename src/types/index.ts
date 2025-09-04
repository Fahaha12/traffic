// 统一导出所有类型
export * from './map'
export * from './camera'
export * from './vehicle'

// 通用类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
}

export interface PaginationParams {
  page: number
  pageSize: number
  total?: number
}

export interface TimeRange {
  startTime: string
  endTime: string
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

// 用户相关类型
export interface User {
  id: string
  username: string
  role: 'admin' | 'operator' | 'viewer'
  permissions: string[]
  lastLogin?: string
}

// 系统配置类型
export interface SystemConfig {
  mapProvider: 'amap' | 'baidu' | 'leaflet'
  defaultZoom: number
  maxCameras: number
  videoQuality: 'low' | 'medium' | 'high'
  alertSound: boolean
  autoRefresh: boolean
  refreshInterval: number
  defaultCenter?: [number, number] // 默认地图中心坐标
}
