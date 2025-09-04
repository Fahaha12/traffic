// 摄像头相关类型定义
export interface Camera {
  id: string
  name: string
  position: {
    lat: number
    lng: number
  }
  status: 'online' | 'offline' | 'maintenance'
  type: 'traffic' | 'surveillance' | 'speed'
  streamUrl: string
  streamType: 'rtmp' | 'hls' | 'webrtc'
  resolution: {
    width: number
    height: number
  }
  fps: number
  lastUpdate: string
  direction?: number
  coverage?: {
    radius: number
    angle: number
  }
}

export interface CameraStream {
  cameraId: string
  streamUrl: string
  isPlaying: boolean
  quality: 'low' | 'medium' | 'high'
  bitrate: number
  latency: number
}

export interface CameraEvent {
  type: 'status_change' | 'stream_error' | 'quality_change'
  cameraId: string
  timestamp: string
  data?: any
}
