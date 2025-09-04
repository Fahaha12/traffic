import request from '@/utils/request'
import type { Camera, CameraStream, CameraEvent } from '@/types'

// 摄像头相关API
export const cameraApi = {
  // 获取摄像头列表
  getCameras: (): Promise<Camera[]> => {
    return request.get('/cameras')
  },

  // 获取单个摄像头信息
  getCamera: (id: string): Promise<Camera> => {
    return request.get(`/cameras/${id}`)
  },

  // 添加摄像头
  addCamera: (camera: Omit<Camera, 'id' | 'lastUpdate'>): Promise<Camera> => {
    return request.post('/cameras', camera)
  },

  // 更新摄像头信息
  updateCamera: (id: string, camera: Partial<Camera>): Promise<Camera> => {
    return request.put(`/cameras/${id}`, camera)
  },

  // 删除摄像头
  deleteCamera: (id: string): Promise<void> => {
    return request.delete(`/cameras/${id}`)
  },

  // 获取摄像头流信息
  getCameraStream: (id: string): Promise<CameraStream> => {
    return request.get(`/cameras/${id}/stream`)
  },

  // 开始摄像头流
  startCameraStream: (id: string): Promise<CameraStream> => {
    return request.post(`/cameras/${id}/stream/start`)
  },

  // 停止摄像头流
  stopCameraStream: (id: string): Promise<void> => {
    return request.post(`/cameras/${id}/stream/stop`)
  },

  // 更新流质量
  updateStreamQuality: (id: string, quality: CameraStream['quality']): Promise<void> => {
    return request.put(`/cameras/${id}/stream/quality`, { quality })
  },

  // 获取摄像头事件
  getCameraEvents: (id: string, limit = 50): Promise<CameraEvent[]> => {
    return request.get(`/cameras/${id}/events`, { params: { limit } })
  },

  // 获取所有摄像头事件
  getAllCameraEvents: (limit = 100): Promise<CameraEvent[]> => {
    return request.get('/cameras/events', { params: { limit } })
  },

  // 测试摄像头连接
  testCameraConnection: (id: string): Promise<{ success: boolean; message: string }> => {
    return request.post(`/cameras/${id}/test`)
  },

  // 重启摄像头
  restartCamera: (id: string): Promise<void> => {
    return request.post(`/cameras/${id}/restart`)
  }
}
