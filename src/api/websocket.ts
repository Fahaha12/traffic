import type { WebSocketMessage } from '@/types'
import { useCameraStore } from '@/stores/camera'
import { useVehicleStore } from '@/stores/vehicle'
import { useMapStore } from '@/stores/map'

class WebSocketManager {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000
  private heartbeatInterval: number | null = null
  private isConnecting = false

  // 连接WebSocket
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      if (this.isConnecting) {
        reject(new Error('正在连接中...'))
        return
      }

      this.isConnecting = true
      const wsUrl = `ws://localhost:8080/ws`
      
      try {
        this.ws = new WebSocket(wsUrl)
        
        this.ws.onopen = () => {
          console.log('WebSocket连接已建立')
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('解析WebSocket消息失败:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭:', event.code, event.reason)
          this.isConnecting = false
          this.stopHeartbeat()
          
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket连接错误:', error)
          this.isConnecting = false
          reject(error)
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  // 断开连接
  disconnect(): void {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close(1000, '主动断开连接')
      this.ws = null
    }
  }

  // 发送消息
  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket未连接，无法发送消息')
    }
  }

  // 处理接收到的消息
  private handleMessage(message: WebSocketMessage): void {
    const { type, data } = message

    switch (type) {
      case 'camera_status_update':
        this.handleCameraStatusUpdate(data)
        break
      case 'camera_stream_event':
        this.handleCameraStreamEvent(data)
        break
      case 'vehicle_detection':
        this.handleVehicleDetection(data)
        break
      case 'vehicle_reid':
        this.handleVehicleReID(data)
        break
      case 'suspicious_vehicle':
        this.handleSuspiciousVehicle(data)
        break
      case 'vehicle_alert':
        this.handleVehicleAlert(data)
        break
      case 'vehicle_trajectory':
        this.handleVehicleTrajectory(data)
        break
      case 'pong':
        // 心跳响应
        break
      default:
        console.warn('未知的WebSocket消息类型:', type)
    }
  }

  // 处理摄像头状态更新
  private handleCameraStatusUpdate(data: any): void {
    const cameraStore = useCameraStore()
    cameraStore.updateCameraStatus(data.cameraId, data.status)
    
    const mapStore = useMapStore()
    mapStore.updateCameraStatus(data.cameraId, data.status)
  }

  // 处理摄像头流事件
  private handleCameraStreamEvent(data: any): void {
    const cameraStore = useCameraStore()
    cameraStore.addCameraEvent(data)
  }

  // 处理车辆检测
  private handleVehicleDetection(data: any): void {
    const vehicleStore = useVehicleStore()
    vehicleStore.addVehicle(data)
  }

  // 处理车辆ReID
  private handleVehicleReID(data: any): void {
    const vehicleStore = useVehicleStore()
    vehicleStore.addVehicleReID(data)
  }

  // 处理可疑车辆
  private handleSuspiciousVehicle(data: any): void {
    const vehicleStore = useVehicleStore()
    vehicleStore.addSuspiciousVehicle(data)
  }

  // 处理车辆告警
  private handleVehicleAlert(data: any): void {
    const vehicleStore = useVehicleStore()
    vehicleStore.addVehicleAlert(data)
  }

  // 处理车辆轨迹
  private handleVehicleTrajectory(data: any): void {
    const vehicleStore = useVehicleStore()
    vehicleStore.addTrajectory(data)
  }

  // 开始心跳
  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(() => {
      this.send({ type: 'ping', data: {}, timestamp: new Date().toISOString() })
    }, 30000) // 每30秒发送一次心跳
  }

  // 停止心跳
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  // 安排重连
  private scheduleReconnect(): void {
    this.reconnectAttempts++
    console.log(`准备第${this.reconnectAttempts}次重连...`)
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error('重连失败:', error)
      })
    }, this.reconnectInterval)
  }

  // 获取连接状态
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  // 获取连接状态文本
  get connectionState(): string {
    if (!this.ws) return '未连接'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return '连接中'
      case WebSocket.OPEN:
        return '已连接'
      case WebSocket.CLOSING:
        return '断开中'
      case WebSocket.CLOSED:
        return '已断开'
      default:
        return '未知状态'
    }
  }
}

// 创建单例实例
export const wsManager = new WebSocketManager()

// 导出类型
export type { WebSocketMessage }
