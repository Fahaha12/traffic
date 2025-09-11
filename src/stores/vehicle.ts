import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Vehicle, VehicleReID, VehicleTrajectory, SuspiciousVehicle, VehicleAlert } from '@/types'
import { vehicleAPI } from '@/api/backend'

export const useVehicleStore = defineStore('vehicle', () => {
  // 状态
  const vehicles = ref<Vehicle[]>([])
  const vehicleReIDs = ref<VehicleReID[]>([])
  const trajectories = ref<Map<string, VehicleTrajectory>>(new Map())
  const suspiciousVehicles = ref<SuspiciousVehicle[]>([])
  const vehicleAlerts = ref<VehicleAlert[]>([])
  const selectedVehicle = ref<Vehicle | null>(null)
  const isTracking = ref(false)

  // 计算属性
  const activeVehicles = computed(() => 
    vehicles.value.filter(vehicle => {
      const now = new Date()
      const vehicleTime = new Date(vehicle.timestamp)
      // 5分钟内的车辆认为是活跃的
      return (now.getTime() - vehicleTime.getTime()) < 5 * 60 * 1000
    })
  )

  const suspiciousCount = computed(() => 
    suspiciousVehicles.value.filter(v => v.isActive).length
  )

  const unreadAlerts = computed(() => 
    vehicleAlerts.value.filter(alert => !alert.isRead)
  )

  const criticalAlerts = computed(() => 
    vehicleAlerts.value.filter(alert => 
      !alert.isRead && !alert.isHandled
    )
  )

  const vehicleById = computed(() => {
    const map = new Map<string, Vehicle>()
    vehicles.value.forEach(vehicle => {
      map.set(vehicle.id, vehicle)
    })
    return map
  })

  // 方法
  const addVehicle = (vehicle: Vehicle) => {
    const index = vehicles.value.findIndex(v => v.id === vehicle.id)
    if (index >= 0) {
      vehicles.value[index] = vehicle
    } else {
      vehicles.value.push(vehicle)
    }
  }

  const removeVehicle = (vehicleId: string) => {
    const index = vehicles.value.findIndex(v => v.id === vehicleId)
    if (index >= 0) {
      vehicles.value.splice(index, 1)
    }
    // 同时移除相关数据
    removeTrajectory(vehicleId)
    removeSuspiciousVehicle(vehicleId)
  }

  // 后端API方法
  const fetchVehicles = async (params?: any) => {
    try {
      const response = await vehicleAPI.getVehicles(params)
      vehicles.value = response.data.vehicles || []
      return response.data
    } catch (error) {
      console.error('获取车辆列表失败:', error)
      throw error
    }
  }

  const fetchVehicle = async (vehicleId: string) => {
    try {
      const response = await vehicleAPI.getVehicle(vehicleId)
      addVehicle(response.data)
      return response.data
    } catch (error) {
      console.error('获取车辆信息失败:', error)
      throw error
    }
  }

  const createVehicle = async (vehicleData: any) => {
    try {
      const response = await vehicleAPI.createVehicle(vehicleData)
      const vehicle = response.data.vehicle || response.data
      addVehicle(vehicle)
      return vehicle
    } catch (error) {
      console.error('创建车辆失败:', error)
      throw error
    }
  }

  const updateVehicle = async (vehicleId: string, vehicleData: any) => {
    try {
      const response = await vehicleAPI.updateVehicle(vehicleId, vehicleData)
      const vehicle = response.data.vehicle || response.data
      addVehicle(vehicle)
      return vehicle
    } catch (error) {
      console.error('更新车辆失败:', error)
      throw error
    }
  }

  const deleteVehicle = async (vehicleId: string) => {
    try {
      await vehicleAPI.deleteVehicle(vehicleId)
      removeVehicle(vehicleId)
    } catch (error) {
      console.error('删除车辆失败:', error)
      throw error
    }
  }

  const fetchSuspiciousVehicles = async () => {
    try {
      const response = await vehicleAPI.getSuspiciousVehicles()
      suspiciousVehicles.value = response.data.map((vehicle: any) => ({
        vehicleId: vehicle.id,
        plateNumber: vehicle.plateNumber,
        vehicleType: vehicle.vehicleType,
        riskLevel: vehicle.riskLevel,
        severity: vehicle.riskLevel,
        reason: '标记为可疑',
        timestamp: vehicle.createdAt,
        isActive: true
      }))
      return response.data
    } catch (error) {
      console.error('获取可疑车辆失败:', error)
      throw error
    }
  }

  const markVehicleSuspicious = async (vehicleId: string, data: any) => {
    try {
      const response = await vehicleAPI.markSuspicious(vehicleId, data)
      const vehicle = response.data.vehicle || response.data
      addVehicle(vehicle)
      return vehicle
    } catch (error) {
      console.error('标记可疑车辆失败:', error)
      throw error
    }
  }

  const fetchVehicleStats = async () => {
    try {
      const response = await vehicleAPI.getVehicleStats()
      return response.data
    } catch (error) {
      console.error('获取车辆统计失败:', error)
      throw error
    }
  }

  const fetchVehicleTracks = async (vehicleId: string, params?: any) => {
    try {
      const response = await vehicleAPI.getVehicleTracks(vehicleId, params)
      return response.data.tracks || []
    } catch (error) {
      console.error('获取车辆轨迹失败:', error)
      throw error
    }
  }

  const addVehicleReID = (reid: VehicleReID) => {
    vehicleReIDs.value.push(reid)
    // 只保留最近1000个ReID记录
    if (vehicleReIDs.value.length > 1000) {
      vehicleReIDs.value = vehicleReIDs.value.slice(-1000)
    }
  }

  const getVehicleReIDs = (vehicleId: string) => {
    return vehicleReIDs.value.filter(reid => reid.vehicleId === vehicleId)
  }

  const addTrajectory = (trajectory: VehicleTrajectory) => {
    trajectories.value.set(trajectory.vehicleId, trajectory)
  }

  const removeTrajectory = (vehicleId: string) => {
    trajectories.value.delete(vehicleId)
  }

  const getTrajectory = (vehicleId: string) => {
    return trajectories.value.get(vehicleId)
  }

  const addSuspiciousVehicle = (vehicle: SuspiciousVehicle) => {
    const index = suspiciousVehicles.value.findIndex(v => v.vehicleId === vehicle.vehicleId)
    if (index >= 0) {
      suspiciousVehicles.value[index] = vehicle
    } else {
      suspiciousVehicles.value.push(vehicle)
    }
  }

  const removeSuspiciousVehicle = (vehicleId: string) => {
    const index = suspiciousVehicles.value.findIndex(v => v.vehicleId === vehicleId)
    if (index >= 0) {
      suspiciousVehicles.value.splice(index, 1)
    }
  }

  const updateSuspiciousVehicleStatus = (vehicleId: string, isActive: boolean) => {
    const vehicle = suspiciousVehicles.value.find(v => v.vehicleId === vehicleId)
    if (vehicle) {
      vehicle.isActive = isActive
    }
  }

  const addVehicleAlert = (alert: VehicleAlert) => {
    vehicleAlerts.value.unshift(alert)
    // 只保留最近200个告警
    if (vehicleAlerts.value.length > 200) {
      vehicleAlerts.value = vehicleAlerts.value.slice(0, 200)
    }
  }

  const markAlertAsRead = (alertId: string) => {
    const alert = vehicleAlerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.isRead = true
    }
  }

  const markAlertAsHandled = (alertId: string) => {
    const alert = vehicleAlerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.isHandled = true
    }
  }

  const selectVehicle = (vehicle: Vehicle | null) => {
    selectedVehicle.value = vehicle
  }

  const startTracking = () => {
    isTracking.value = true
  }

  const stopTracking = () => {
    isTracking.value = false
  }

  const clearOldData = () => {
    const now = new Date()
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)
    
    // 清理1小时前的车辆数据
    vehicles.value = vehicles.value.filter(vehicle => 
      new Date(vehicle.timestamp) > oneHourAgo
    )
    
    // 清理1小时前的ReID数据
    vehicleReIDs.value = vehicleReIDs.value.filter(reid => 
      new Date(reid.timestamp) > oneHourAgo
    )
  }

  const getVehiclesByCamera = (cameraId: string) => {
    return vehicles.value.filter(vehicle => vehicle.cameraId === cameraId)
  }

  const getSuspiciousVehiclesBySeverity = (severity: SuspiciousVehicle['severity']) => {
    return suspiciousVehicles.value.filter(vehicle => 
      vehicle.severity === severity && vehicle.isActive
    )
  }

  return {
    // 状态
    vehicles,
    vehicleReIDs,
    trajectories,
    suspiciousVehicles,
    vehicleAlerts,
    selectedVehicle,
    isTracking,
    
    // 计算属性
    activeVehicles,
    suspiciousCount,
    unreadAlerts,
    criticalAlerts,
    vehicleById,
    
    // 本地方法
    addVehicle,
    removeVehicle,
    addVehicleReID,
    getVehicleReIDs,
    addTrajectory,
    removeTrajectory,
    getTrajectory,
    addSuspiciousVehicle,
    removeSuspiciousVehicle,
    updateSuspiciousVehicleStatus,
    addVehicleAlert,
    markAlertAsRead,
    markAlertAsHandled,
    selectVehicle,
    startTracking,
    stopTracking,
    clearOldData,
    getVehiclesByCamera,
    getSuspiciousVehiclesBySeverity,
    
    // 后端API方法
    fetchVehicles,
    fetchVehicle,
    createVehicle,
    updateVehicle,
    deleteVehicle,
    fetchSuspiciousVehicles,
    markVehicleSuspicious,
    fetchVehicleStats,
    fetchVehicleTracks
  }
})
