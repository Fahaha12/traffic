import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Camera, CameraStream, CameraEvent } from '@/types'
import { cameraStorage } from '@/utils/storage'
import { cameraAPI } from '@/api/backend'

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

  const addCamera = async (camera: Camera) => {
    try {
      // 首先尝试通过API添加到后端
      console.log('DEBUG: cameraStore.addCamera called with:', camera)
      const response = await cameraAPI.createCamera(camera)
      if (response.data && response.data.camera) {
        const newCamera = response.data.camera
        const index = cameras.value.findIndex(c => c.id === newCamera.id)
        if (index >= 0) {
          cameras.value[index] = newCamera
        } else {
          cameras.value.push(newCamera)
        }
        // 同步到本地存储
        cameraStorage.addCamera(newCamera)
      } else {
        throw new Error('API返回数据格式错误')
      }
    } catch (error) {
      console.error('通过API添加摄像头失败:', error)
      // 如果API失败，只添加到本地
      const index = cameras.value.findIndex(c => c.id === camera.id)
      if (index >= 0) {
        cameras.value[index] = camera
      } else {
        cameras.value.push(camera)
      }
      // 保存到本地存储
      cameraStorage.addCamera(camera)
    }
  }

  const updateCamera = async (camera: Camera) => {
    try {
      // 首先尝试通过API更新后端
      console.log('DEBUG: 发送更新摄像头数据:', camera)
      const response = await cameraAPI.updateCamera(camera.id, camera)
      if (response.data && response.data.camera) {
        const updatedCamera = response.data.camera
        const index = cameras.value.findIndex(c => c.id === updatedCamera.id)
        if (index >= 0) {
          cameras.value[index] = updatedCamera
        }
        // 同步到本地存储
        cameraStorage.addCamera(updatedCamera)
      } else {
        throw new Error('API返回数据格式错误')
      }
    } catch (error) {
      console.error('通过API更新摄像头失败:', error)
      // 如果API失败，只更新本地
      const index = cameras.value.findIndex(c => c.id === camera.id)
      if (index >= 0) {
        cameras.value[index] = camera
        // 保存到本地存储
        cameraStorage.addCamera(camera)
      }
    }
  }

  const removeCamera = async (cameraId: string) => {
    try {
      // 首先尝试通过API从后端删除
      console.log('DEBUG: 删除摄像头:', cameraId)
      await cameraAPI.deleteCamera(cameraId)
      
      // 从本地状态中删除
      const index = cameras.value.findIndex(c => c.id === cameraId)
      if (index >= 0) {
        cameras.value.splice(index, 1)
      }
      // 同时停止该摄像头的流
      stopStream(cameraId)
      // 从本地存储中删除
      cameraStorage.removeCamera(cameraId)
    } catch (error) {
      console.error('通过API删除摄像头失败:', error)
      // 如果API失败，只删除本地
      const index = cameras.value.findIndex(c => c.id === cameraId)
      if (index >= 0) {
        cameras.value.splice(index, 1)
      }
      stopStream(cameraId)
      cameraStorage.removeCamera(cameraId)
    }
  }

  const updateCameraStatus = (cameraId: string, status: Camera['status']) => {
    const camera = cameras.value.find(c => c.id === cameraId)
    if (camera) {
      camera.status = status
      camera.lastUpdate = new Date().toISOString()
      // 更新本地存储
      cameraStorage.updateCamera(cameraId, { status, lastUpdate: camera.lastUpdate })
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
    try {
      // 首先尝试从后端API获取数据
      const response = await cameraAPI.getCameras()
      if (response.data && response.data.cameras) {
        cameras.value = response.data.cameras
        // 同步到本地存储
        cameraStorage.saveCameras(cameras.value)
      } else {
        // 如果API失败，从本地存储加载
        loadCamerasFromStorage()
      }
    } catch (error) {
      console.error('从后端获取摄像头数据失败:', error)
      // 从本地存储加载
      loadCamerasFromStorage()
    }
  }

  // 从本地存储加载摄像头数据
  const loadCamerasFromStorage = () => {
    const storedCameras = cameraStorage.loadCameras()
    if (storedCameras.length > 0) {
      cameras.value = storedCameras
    } else {
      // 如果没有存储的数据，初始化一些模拟数据
      initializeMockCameras()
    }
  }

  // 检测摄像头状态
  const checkCameraStatus = async (cameraId: string) => {
    try {
      const response = await cameraAPI.getCameraStatus(cameraId)
      if (response.data && response.data.status) {
        // 更新摄像头状态
        const camera = cameras.value.find(c => c.id === cameraId)
        if (camera) {
          camera.status = response.data.status
          console.log(`摄像头 ${camera.name} 状态更新为: ${camera.status}`)
        }
        return response.data.status
      }
    } catch (error) {
      console.error('检测摄像头状态失败:', error)
      return 'offline'
    }
  }

  // 批量检测所有摄像头状态
  const checkAllCameraStatus = async () => {
    const promises = cameras.value.map(camera => 
      checkCameraStatus(camera.id).catch(() => 'offline')
    )
    await Promise.all(promises)
    console.log('所有摄像头状态检测完成')
  }

  // 清除本地存储并重新从云端加载
  const clearLocalStorageAndRefresh = async () => {
    try {
      // 清除本地存储
      cameraStorage.clearCameras()
      // 从云端重新加载数据
      await refreshCameraData()
    } catch (error) {
      console.error('清除本地存储并刷新数据失败:', error)
    }
  }

  // 初始化模拟摄像头数据
  const initializeMockCameras = () => {
    const mockCameras: Camera[] = [
      {
        id: 'camera_001',
        name: '郑州市政府大门',
        type: 'traffic',
        position: {
          lat: 34.7466,
          lng: 113.6253
        },
        status: 'online',
        streamUrl: 'rtmp://58.200.131.2:1935/livetv/hunantv',
        streamType: 'rtmp',
        resolution: {
          width: 1920,
          height: 1080
        },
        fps: 25,
        direction: 90,
        lastUpdate: new Date().toISOString()
      },
      {
        id: 'camera_002',
        name: '中原路与建设路交叉口',
        type: 'traffic',
        position: {
          lat: 34.7500,
          lng: 113.6300
        },
        status: 'online',
        streamUrl: 'http://example.com/camera2.m3u8',
        streamType: 'hls',
        resolution: {
          width: 1280,
          height: 720
        },
        fps: 30,
        direction: 180,
        lastUpdate: new Date().toISOString()
      },
      {
        id: 'camera_003',
        name: '金水区花园路',
        type: 'surveillance',
        position: {
          lat: 34.7600,
          lng: 113.6400
        },
        status: 'offline',
        streamUrl: 'http://example.com/camera3.mp4',
        streamType: 'http',
        resolution: {
          width: 1920,
          height: 1080
        },
        fps: 25,
        direction: 270,
        lastUpdate: new Date(Date.now() - 3600000).toISOString()
      }
    ]

    cameras.value = mockCameras
    // 保存到本地存储
    cameraStorage.saveCameras(mockCameras)
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
    updateCamera,
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
    refreshCameraData,
    loadCamerasFromStorage,
    initializeMockCameras,
    clearLocalStorageAndRefresh,
    checkCameraStatus,
    checkAllCameraStatus
  }
})
