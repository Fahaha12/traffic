import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Vehicle, VehicleReID, VehicleTrajectory, SuspiciousVehicle, VehicleAlert } from '@/types'

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
    
    // 方法
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
    getSuspiciousVehiclesBySeverity
  }
})
