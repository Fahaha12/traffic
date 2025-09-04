import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MapConfig, CameraPosition, MapBounds, MapEvent, Camera } from '@/types'

export const useMapStore = defineStore('map', () => {
  // 状态
  const mapInstance = ref<any>(null)
  const mapConfig = ref<MapConfig>({
    center: [34.7466, 113.6253], // 郑州市政府
    zoom: 12,
    minZoom: 8,
    maxZoom: 18
  })
  const cameraPositions = ref<CameraPosition[]>([])
  const selectedCamera = ref<Camera | null>(null)
  const mapBounds = ref<MapBounds | null>(null)
  const isMapReady = ref(false)

  // 计算属性
  const onlineCameras = computed(() => 
    cameraPositions.value.filter(camera => camera.status === 'online')
  )
  
  const offlineCameras = computed(() => 
    cameraPositions.value.filter(camera => camera.status === 'offline')
  )

  const cameraCount = computed(() => cameraPositions.value.length)

  // 方法
  const setMapInstance = (instance: any) => {
    mapInstance.value = instance
    isMapReady.value = true
  }

  const updateMapConfig = (config: Partial<MapConfig>) => {
    mapConfig.value = { ...mapConfig.value, ...config }
  }

  const setCameraPositions = (cameras: CameraPosition[]) => {
    cameraPositions.value = cameras
  }

  const addCamera = (camera: CameraPosition) => {
    const index = cameraPositions.value.findIndex(c => c.id === camera.id)
    if (index >= 0) {
      cameraPositions.value[index] = camera
    } else {
      cameraPositions.value.push(camera)
    }
  }

  const removeCamera = (cameraId: string) => {
    const index = cameraPositions.value.findIndex(c => c.id === cameraId)
    if (index >= 0) {
      cameraPositions.value.splice(index, 1)
    }
  }

  const updateCameraStatus = (cameraId: string, status: CameraPosition['status']) => {
    const camera = cameraPositions.value.find(c => c.id === cameraId)
    if (camera) {
      camera.status = status
    }
  }

  const selectCamera = (camera: Camera | null) => {
    selectedCamera.value = camera
  }

  const updateMapBounds = (bounds: MapBounds) => {
    mapBounds.value = bounds
  }

  const centerOnCamera = (cameraId: string) => {
    const camera = cameraPositions.value.find(c => c.id === cameraId)
    if (camera && mapInstance.value) {
      mapInstance.value.setView([camera.lat, camera.lng], 16)
    }
  }

  const fitCameraBounds = () => {
    if (cameraPositions.value.length > 0 && mapInstance.value) {
      const bounds = cameraPositions.value.map(camera => [camera.lat, camera.lng])
      mapInstance.value.fitBounds(bounds)
    }
  }

  const resetMap = () => {
    mapInstance.value = null
    isMapReady.value = false
    selectedCamera.value = null
    mapBounds.value = null
  }

  return {
    // 状态
    mapInstance,
    mapConfig,
    cameraPositions,
    selectedCamera,
    mapBounds,
    isMapReady,
    
    // 计算属性
    onlineCameras,
    offlineCameras,
    cameraCount,
    
    // 方法
    setMapInstance,
    updateMapConfig,
    setCameraPositions,
    addCamera,
    removeCamera,
    updateCameraStatus,
    selectCamera,
    updateMapBounds,
    centerOnCamera,
    fitCameraBounds,
    resetMap
  }
})
