import request from '@/utils/request'
import type { Vehicle, VehicleReID, VehicleTrajectory, SuspiciousVehicle, VehicleAlert } from '@/types'

// 车辆相关API
export const vehicleApi = {
  // 获取车辆列表
  getVehicles: (params?: { cameraId?: string; limit?: number }): Promise<Vehicle[]> => {
    return request.get('/vehicles', { params })
  },

  // 获取单个车辆信息
  getVehicle: (id: string): Promise<Vehicle> => {
    return request.get(`/vehicles/${id}`)
  },

  // 获取车辆ReID信息
  getVehicleReIDs: (vehicleId: string): Promise<VehicleReID[]> => {
    return request.get(`/vehicles/${vehicleId}/reids`)
  },

  // 添加车辆ReID
  addVehicleReID: (reid: Omit<VehicleReID, 'timestamp'>): Promise<VehicleReID> => {
    return request.post('/vehicles/reids', reid)
  },

  // 获取车辆轨迹
  getVehicleTrajectory: (vehicleId: string, timeRange?: { start: string; end: string }): Promise<VehicleTrajectory> => {
    return request.get(`/vehicles/${vehicleId}/trajectory`, { params: timeRange })
  },

  // 获取多个车辆轨迹
  getVehicleTrajectories: (vehicleIds: string[]): Promise<VehicleTrajectory[]> => {
    return request.post('/vehicles/trajectories', { vehicleIds })
  },

  // 获取可疑车辆列表
  getSuspiciousVehicles: (): Promise<SuspiciousVehicle[]> => {
    return request.get('/vehicles/suspicious')
  },

  // 添加可疑车辆
  addSuspiciousVehicle: (vehicle: Omit<SuspiciousVehicle, 'timestamp'>): Promise<SuspiciousVehicle> => {
    return request.post('/vehicles/suspicious', vehicle)
  },

  // 更新可疑车辆状态
  updateSuspiciousVehicle: (vehicleId: string, updates: Partial<SuspiciousVehicle>): Promise<SuspiciousVehicle> => {
    return request.put(`/vehicles/suspicious/${vehicleId}`, updates)
  },

  // 获取车辆告警
  getVehicleAlerts: (params?: { isRead?: boolean; limit?: number }): Promise<VehicleAlert[]> => {
    return request.get('/vehicles/alerts', { params })
  },

  // 标记告警为已读
  markAlertAsRead: (alertId: string): Promise<void> => {
    return request.put(`/vehicles/alerts/${alertId}/read`)
  },

  // 标记告警为已处理
  markAlertAsHandled: (alertId: string): Promise<void> => {
    return request.put(`/vehicles/alerts/${alertId}/handled`)
  },

  // 批量标记告警
  batchMarkAlerts: (alertIds: string[], action: 'read' | 'handled'): Promise<void> => {
    return request.put('/vehicles/alerts/batch', { alertIds, action })
  },

  // 搜索车辆
  searchVehicles: (query: { plateNumber?: string; type?: string; color?: string }): Promise<Vehicle[]> => {
    return request.post('/vehicles/search', query)
  },

  // 获取车辆统计信息
  getVehicleStats: (timeRange?: { start: string; end: string }): Promise<{
    total: number
    byType: Record<string, number>
    byCamera: Record<string, number>
    suspicious: number
  }> => {
    return request.get('/vehicles/stats', { params: timeRange })
  }
}
