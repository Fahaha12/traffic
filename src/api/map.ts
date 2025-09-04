import request from '@/utils/request'
import type { CameraPosition, MapConfig } from '@/types'

// 地图相关API
export const mapApi = {
  // 获取地图配置
  getMapConfig: (): Promise<MapConfig> => {
    return request.get('/map/config')
  },

  // 更新地图配置
  updateMapConfig: (config: Partial<MapConfig>): Promise<void> => {
    return request.put('/map/config', config)
  },

  // 获取摄像头位置列表
  getCameraPositions: (): Promise<CameraPosition[]> => {
    return request.get('/map/cameras')
  },

  // 添加摄像头位置
  addCameraPosition: (camera: Omit<CameraPosition, 'id'>): Promise<CameraPosition> => {
    return request.post('/map/cameras', camera)
  },

  // 更新摄像头位置
  updateCameraPosition: (id: string, camera: Partial<CameraPosition>): Promise<CameraPosition> => {
    return request.put(`/map/cameras/${id}`, camera)
  },

  // 删除摄像头位置
  deleteCameraPosition: (id: string): Promise<void> => {
    return request.delete(`/map/cameras/${id}`)
  },

  // 获取摄像头状态
  getCameraStatus: (id: string): Promise<{ status: CameraPosition['status'] }> => {
    return request.get(`/map/cameras/${id}/status`)
  },

  // 批量更新摄像头状态
  updateCameraStatuses: (updates: Array<{ id: string; status: CameraPosition['status'] }>): Promise<void> => {
    return request.put('/map/cameras/status', { updates })
  }
}
