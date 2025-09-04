import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Camera, CameraStream, CameraEvent } from '@/types'

export const useCameraStore = defineStore('camera', () => {
  // 状态
  const cameras = ref<Camera[]>([])
  const activeStreams = ref<Map<string, CameraStream>>(new Map())
  const selectedCamera = ref<Camera | null>(null)
  const cameraEvents = ref<CameraEvent[]>([])
  const isStreaming = ref(false)

  // 计算属性
  const onlineCameras = computed(() => 
    cameras.value.filter(camera => camera.status === 'online')
  )
  
  const offlineCameras = computed(() => 
    cameras.value.filter(camera => camera.status === 'offline')
  )

  const maintenanceCameras = computed(() => 
    cameras.value.filter(camera => camera.status === 'maintenance')
  )

  const activeStreamCount = computed(() => activeStreams.value.size)

  const cameraById = computed(() => {
    const map = new Map<string, Camera>()
    cameras.value.forEach(camera => {
      map.set(camera.id, camera)
    })
    return map
  })

  // 方法
  const setCameras = (cameraList: Camera[]) => {
    cameras.value = cameraList
  }

  const addCamera = (camera: Camera) => {
    const index = cameras.value.findIndex(c => c.id === camera.id)
    if (index >= 0) {
      cameras.value[index] = camera
    } else {
      cameras.value.push(camera)
    }
  }

  const removeCamera = (cameraId: string) => {
    const index = cameras.value.findIndex(c => c.id === cameraId)
    if (index >= 0) {
      cameras.value.splice(index, 1)
      // 同时停止该摄像头的流
      stopStream(cameraId)
    }
  }

  const updateCameraStatus = (cameraId: string, status: Camera['status']) => {
    const camera = cameras.value.find(c => c.id === cameraId)
    if (camera) {
      camera.status = status
      camera.lastUpdate = new Date().toISOString()
    }
  }

  const selectCamera = (camera: Camera | null) => {
    selectedCamera.value = camera
  }

  const startStream = (cameraId: string, streamUrl: string) => {
    const stream: CameraStream = {
      cameraId,
      streamUrl,
      isPlaying: true,
      quality: 'medium',
      bitrate: 0,
      latency: 0
    }
    activeStreams.value.set(cameraId, stream)
    isStreaming.value = true
  }

  const stopStream = (cameraId: string) => {
    activeStreams.value.delete(cameraId)
    if (activeStreams.value.size === 0) {
      isStreaming.value = false
    }
  }

  const updateStreamQuality = (cameraId: string, quality: CameraStream['quality']) => {
    const stream = activeStreams.value.get(cameraId)
    if (stream) {
      stream.quality = quality
    }
  }

  const updateStreamStats = (cameraId: string, stats: Partial<CameraStream>) => {
    const stream = activeStreams.value.get(cameraId)
    if (stream) {
      Object.assign(stream, stats)
    }
  }

  const addCameraEvent = (event: CameraEvent) => {
    cameraEvents.value.unshift(event)
    // 只保留最近100个事件
    if (cameraEvents.value.length > 100) {
      cameraEvents.value = cameraEvents.value.slice(0, 100)
    }
  }

  const getCameraStream = (cameraId: string) => {
    return activeStreams.value.get(cameraId)
  }

  const isStreamActive = (cameraId: string) => {
    return activeStreams.value.has(cameraId)
  }

  const stopAllStreams = () => {
    activeStreams.value.clear()
    isStreaming.value = false
  }

  const refreshCameraData = async () => {
    // 这里可以调用API刷新摄像头数据
    // 实际实现时会调用相应的API
  }

  return {
    // 状态
    cameras,
    activeStreams,
    selectedCamera,
    cameraEvents,
    isStreaming,
    
    // 计算属性
    onlineCameras,
    offlineCameras,
    maintenanceCameras,
    activeStreamCount,
    cameraById,
    
    // 方法
    setCameras,
    addCamera,
    removeCamera,
    updateCameraStatus,
    selectCamera,
    startStream,
    stopStream,
    updateStreamQuality,
    updateStreamStats,
    addCameraEvent,
    getCameraStream,
    isStreamActive,
    stopAllStreams,
    refreshCameraData
  }
})
