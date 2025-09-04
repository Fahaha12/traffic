// 地图相关类型定义
export interface MapConfig {
  center: [number, number]
  zoom: number
  minZoom: number
  maxZoom: number
}

export interface CameraPosition {
  id: string
  name: string
  lat: number
  lng: number
  status: 'online' | 'offline'
  type: 'traffic' | 'surveillance' | 'speed'
  direction?: number // 摄像头朝向角度
}

export interface MapBounds {
  north: number
  south: number
  east: number
  west: number
}

export interface MapEvent {
  type: 'click' | 'move' | 'zoom'
  latlng?: [number, number]
  bounds?: MapBounds
  zoom?: number
}
