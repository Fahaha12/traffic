// 视频工具函数

// 视频流类型
export type StreamType = 'rtmp' | 'hls' | 'webrtc' | 'http'

// 视频质量类型
export type VideoQuality = 'low' | 'medium' | 'high' | 'ultra'

// 视频质量配置
export const VIDEO_QUALITY_CONFIG = {
  low: {
    width: 640,
    height: 480,
    bitrate: 500,
    fps: 15
  },
  medium: {
    width: 1280,
    height: 720,
    bitrate: 1500,
    fps: 25
  },
  high: {
    width: 1920,
    height: 1080,
    bitrate: 3000,
    fps: 30
  },
  ultra: {
    width: 2560,
    height: 1440,
    bitrate: 6000,
    fps: 30
  }
}

// 检测视频流类型
export const detectStreamType = (url: string): StreamType => {
  if (url.includes('rtmp://')) {
    return 'rtmp'
  } else if (url.includes('.m3u8')) {
    return 'hls'
  } else if (url.includes('webrtc://')) {
    return 'webrtc'
  } else {
    return 'http'
  }
}

// 生成不同质量的视频流URL
export const generateQualityUrls = (baseUrl: string, streamType: StreamType): Record<VideoQuality, string> => {
  const urls: Record<VideoQuality, string> = {
    low: '',
    medium: '',
    high: '',
    ultra: ''
  }

  switch (streamType) {
    case 'hls':
      urls.low = baseUrl.replace('.m3u8', '_low.m3u8')
      urls.medium = baseUrl.replace('.m3u8', '_medium.m3u8')
      urls.high = baseUrl.replace('.m3u8', '_high.m3u8')
      urls.ultra = baseUrl.replace('.m3u8', '_ultra.m3u8')
      break
    case 'rtmp':
      urls.low = baseUrl + '?quality=low'
      urls.medium = baseUrl + '?quality=medium'
      urls.high = baseUrl + '?quality=high'
      urls.ultra = baseUrl + '?quality=ultra'
      break
    case 'http':
      urls.low = baseUrl + '?quality=low'
      urls.medium = baseUrl + '?quality=medium'
      urls.high = baseUrl + '?quality=high'
      urls.ultra = baseUrl + '?quality=ultra'
      break
    default:
      urls.low = baseUrl
      urls.medium = baseUrl
      urls.high = baseUrl
      urls.ultra = baseUrl
  }

  return urls
}

// 格式化视频时长
export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  } else {
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
}

// 格式化文件大小
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化比特率
export const formatBitrate = (bitrate: number): string => {
  if (bitrate < 1000) {
    return `${bitrate} bps`
  } else if (bitrate < 1000000) {
    return `${(bitrate / 1000).toFixed(1)} Kbps`
  } else {
    return `${(bitrate / 1000000).toFixed(1)} Mbps`
  }
}

// 计算视频分辨率
export const calculateResolution = (width: number, height: number): string => {
  return `${width}x${height}`
}

// 获取宽高比
export const getAspectRatio = (width: number, height: number): string => {
  const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b)
  const divisor = gcd(width, height)
  return `${width / divisor}:${height / divisor}`
}

// 检测视频格式支持
export const checkVideoSupport = (): {
  h264: boolean
  h265: boolean
  vp8: boolean
  vp9: boolean
  av1: boolean
} => {
  const video = document.createElement('video')
  
  return {
    h264: video.canPlayType('video/mp4; codecs="avc1.42E01E"') !== '',
    h265: video.canPlayType('video/mp4; codecs="hev1.1.6.L93.B0"') !== '',
    vp8: video.canPlayType('video/webm; codecs="vp8"') !== '',
    vp9: video.canPlayType('video/webm; codecs="vp9"') !== '',
    av1: video.canPlayType('video/mp4; codecs="av01.0.05M.08"') !== ''
  }
}

// 获取视频元数据
export const getVideoMetadata = (videoElement: HTMLVideoElement): {
  duration: number
  currentTime: number
  buffered: TimeRanges
  readyState: number
  networkState: number
  videoWidth: number
  videoHeight: number
} => {
  return {
    duration: videoElement.duration || 0,
    currentTime: videoElement.currentTime || 0,
    buffered: videoElement.buffered,
    readyState: videoElement.readyState,
    networkState: videoElement.networkState,
    videoWidth: videoElement.videoWidth || 0,
    videoHeight: videoElement.videoHeight || 0
  }
}

// 计算视频缓冲进度
export const calculateBufferProgress = (videoElement: HTMLVideoElement): number => {
  if (!videoElement.buffered.length) {
    return 0
  }

  const currentTime = videoElement.currentTime
  const duration = videoElement.duration

  if (duration === 0) {
    return 0
  }

  let bufferedEnd = 0
  for (let i = 0; i < videoElement.buffered.length; i++) {
    if (videoElement.buffered.start(i) <= currentTime) {
      bufferedEnd = Math.max(bufferedEnd, videoElement.buffered.end(i))
    }
  }

  return (bufferedEnd / duration) * 100
}

// 视频截图
export const captureVideoFrame = (videoElement: HTMLVideoElement): string | null => {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')

  if (!ctx) {
    return null
  }

  canvas.width = videoElement.videoWidth
  canvas.height = videoElement.videoHeight

  ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height)

  return canvas.toDataURL('image/png')
}

// 检测视频流状态
export const checkStreamStatus = async (url: string): Promise<{
  isOnline: boolean
  latency: number
  error?: string
}> => {
  try {
    const startTime = Date.now()
    
    // 尝试获取视频流信息
    const response = await fetch(url, {
      method: 'HEAD',
      mode: 'no-cors'
    })
    
    const latency = Date.now() - startTime
    
    return {
      isOnline: true,
      latency
    }
  } catch (error) {
    return {
      isOnline: false,
      latency: 0,
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}

// 视频流重连逻辑
export const createReconnectManager = (
  connectFn: () => Promise<void>,
  maxRetries: number = 5,
  retryDelay: number = 3000
) => {
  let retryCount = 0
  let isReconnecting = false

  const reconnect = async (): Promise<void> => {
    if (isReconnecting || retryCount >= maxRetries) {
      return
    }

    isReconnecting = true
    retryCount++

    try {
      await new Promise(resolve => setTimeout(resolve, retryDelay))
      await connectFn()
      retryCount = 0 // 重置重试计数
    } catch (error) {
      console.error(`重连失败 (${retryCount}/${maxRetries}):`, error)
      if (retryCount < maxRetries) {
        await reconnect()
      }
    } finally {
      isReconnecting = false
    }
  }

  return {
    reconnect,
    reset: () => {
      retryCount = 0
      isReconnecting = false
    }
  }
}

// 视频质量自适应
export const createAdaptiveQuality = (
  videoElement: HTMLVideoElement,
  qualityUrls: Record<VideoQuality, string>
) => {
  let currentQuality: VideoQuality = 'medium'
  let lastCheckTime = 0
  const checkInterval = 5000 // 5秒检查一次

  const checkAndAdjustQuality = () => {
    const now = Date.now()
    if (now - lastCheckTime < checkInterval) {
      return
    }
    lastCheckTime = now

    const metadata = getVideoMetadata(videoElement)
    const bufferProgress = calculateBufferProgress(videoElement)

    // 根据缓冲进度调整质量
    if (bufferProgress < 20 && currentQuality !== 'low') {
      currentQuality = 'low'
      videoElement.src = qualityUrls.low
    } else if (bufferProgress > 80 && currentQuality !== 'high') {
      currentQuality = 'high'
      videoElement.src = qualityUrls.high
    }
  }

  return {
    checkAndAdjustQuality,
    setQuality: (quality: VideoQuality) => {
      currentQuality = quality
      videoElement.src = qualityUrls[quality]
    },
    getCurrentQuality: () => currentQuality
  }
}

export default {
  detectStreamType,
  generateQualityUrls,
  formatDuration,
  formatFileSize,
  formatBitrate,
  calculateResolution,
  getAspectRatio,
  checkVideoSupport,
  getVideoMetadata,
  calculateBufferProgress,
  captureVideoFrame,
  checkStreamStatus,
  createReconnectManager,
  createAdaptiveQuality
}
