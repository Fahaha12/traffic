// 车辆相关类型定义
export interface Vehicle {
  id: string
  plateNumber?: string
  type: 'car' | 'truck' | 'bus' | 'motorcycle' | 'unknown'
  color: string
  brand?: string
  model?: string
  confidence: number
  timestamp: string
  cameraId: string
  position: {
    lat: number
    lng: number
  }
  speed?: number
  direction?: number
}

export interface VehicleReID {
  vehicleId: string
  features: number[]
  similarity: number
  timestamp: string
  cameraId: string
  imageUrl?: string
  bbox: {
    x: number
    y: number
    width: number
    height: number
  }
}

export interface VehicleTrajectory {
  vehicleId: string
  points: Array<{
    lat: number
    lng: number
    timestamp: string
    cameraId: string
    speed?: number
  }>
  startTime: string
  endTime: string
  totalDistance: number
  averageSpeed: number
}

export interface SuspiciousVehicle {
  vehicleId: string
  reason: 'speed_violation' | 'wrong_way' | 'stolen_vehicle' | 'wanted_person' | 'custom'
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  timestamp: string
  location: {
    lat: number
    lng: number
  }
  cameraId: string
  isActive: boolean
}

export interface VehicleAlert {
  id: string
  vehicleId: string
  type: 'suspicious' | 'violation' | 'emergency'
  message: string
  timestamp: string
  location: {
    lat: number
    lng: number
  }
  cameraId: string
  isRead: boolean
  isHandled: boolean
}
