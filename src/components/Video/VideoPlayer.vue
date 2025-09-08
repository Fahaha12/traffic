<template>
  <div class="video-player" :style="{ height: height + 'px' }">
    <video
      ref="videoElement"
      class="video-js vjs-default-skin"
      :poster="poster"
      :preload="preload"
      :data-setup="dataSetup"
      @loadstart="handleLoadStart"
      @loadeddata="handleLoadedData"
      @error="handleError"
    >
      <p class="vjs-no-js">
        要查看此视频，请启用JavaScript，并考虑升级到
        <a href="https://videojs.com/html5-video-support/" target="_blank">
          支持HTML5视频的Web浏览器
        </a>。
      </p>
    </video>
    
    <div v-if="isLoading" class="loading-overlay">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    
    <div v-if="hasError" class="error-overlay">
      <el-icon class="error-icon"><Warning /></el-icon>
      <div class="error-content">
        <div class="error-message">{{ errorMessage }}</div>
        <div v-if="errorMessage.includes('CORS')" class="error-detail">
          <p><strong>CORS错误说明：</strong></p>
          <p>浏览器阻止了跨域请求，因为：</p>
          <ul>
            <li>前端运行在 localhost:3000</li>
            <li>流媒体服务器在 ns8.indexforce.com</li>
            <li>服务器没有设置 Access-Control-Allow-Origin 头</li>
          </ul>
          <p><strong>解决方案：</strong></p>
          <ul>
            <li><strong>后端代理：</strong>在后端添加流媒体代理接口</li>
            <li><strong>Nginx代理：</strong>配置Nginx反向代理</li>
            <li><strong>CDN服务：</strong>使用支持CORS的CDN</li>
            <li><strong>服务器配置：</strong>在流媒体服务器添加CORS头</li>
          </ul>
        </div>
      </div>
      <el-button type="primary" size="small" @click="retry">重试</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'
import Hls from 'hls.js'
import type { VideoQuality } from '@/utils/videoUtils'
import { cameraAPI } from '@/api/backend'

interface Props {
  cameraId: string
  streamUrl: string
  autoPlay?: boolean
  height?: number
  poster?: string
  preload?: 'auto' | 'metadata' | 'none'
  quality?: VideoQuality
  controls?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoPlay: false,
  height: 300,
  poster: '',
  preload: 'metadata',
  quality: 'medium',
  controls: true
})

const emit = defineEmits<{
  ready: [player: any]
  error: [error: any]
  qualityChange: [quality: VideoQuality]
}>()

const videoElement = ref<HTMLVideoElement>()
const player = ref<any>(null)
const hls = ref<Hls | null>(null)
const isLoading = ref(false)
const hasError = ref(false)
const errorMessage = ref('')

const dataSetup = ref('{}')

// 初始化视频播放器
const initPlayer = async () => {
  if (!videoElement.value) return

  // 处理流媒体URL
  const processedUrl = await processStreamUrl(props.streamUrl, props.cameraId)
  const streamType = getStreamType(props.streamUrl)

  // 如果URL无效，显示占位符
  if (!processedUrl) {
    hasError.value = true
    errorMessage.value = '无效的视频流地址'
    return
  }

  const options = {
    controls: props.controls,
    fluid: true,
    responsive: true,
    autoplay: props.autoPlay,
    preload: props.preload,
    poster: props.poster,
    sources: [
      {
        src: processedUrl,
        type: streamType
      }
    ],
    techOrder: ['html5'],
    html5: {
      vhs: {
        overrideNative: true,
        enableLowInitialPlaylist: true,
        smoothQualityChange: true,
        overrideNative: !videojs.browser.IS_SAFARI
      }
    }
  }

  try {
    player.value = videojs(videoElement.value, options)
    
    player.value.ready(() => {
      emit('ready', player.value)
      
      // 如果是HLS流，使用HLS.js
      if (streamType === 'application/x-mpegURL' && Hls.isSupported()) {
        initHlsPlayer(processedUrl)
      }
    })

    player.value.on('error', (error: any) => {
      console.error('视频播放错误:', error)
      hasError.value = true
      errorMessage.value = getErrorMessage(error)
      emit('error', error)
    })

    player.value.on('loadstart', () => {
      isLoading.value = true
      hasError.value = false
    })

    player.value.on('loadeddata', () => {
      isLoading.value = false
    })

    player.value.on('waiting', () => {
      isLoading.value = true
    })

    player.value.on('canplay', () => {
      isLoading.value = false
    })

  } catch (error) {
    console.error('初始化视频播放器失败:', error)
    hasError.value = true
    errorMessage.value = '初始化播放器失败'
  }
}

// 获取流媒体类型
const getStreamType = (url: string): string => {
  if (url.includes('.m3u8')) {
    return 'application/x-mpegURL'
  } else if (url.includes('.mp4')) {
    return 'video/mp4'
  } else if (url.includes('.webm')) {
    return 'video/webm'
  } else if (url.includes('rtmp://')) {
    // RTMP流需要转换为HLS或通过WebRTC播放
    // 这里我们假设有后端服务将RTMP转换为HLS
    return 'application/x-mpegURL'
  } else {
    return 'video/mp4'
  }
}

// 处理流媒体URL，使用后端转换服务
const processStreamUrl = async (url: string, cameraId?: string): Promise<string> => {
  // 检查是否为无效的测试URL
  if (url.includes('example.com') || url.includes('test.com') || !url || url === '') {
    console.warn('检测到无效的测试URL，跳过播放:', url)
    return ''
  }
  
  if (url.includes('rtmp://') && cameraId) {
    // RTMP流，使用后端转换服务
    try {
      console.log('使用后端转换RTMP流:', url)
      
      // 首先检查是否已经有转换的流
      const streamResponse = await cameraAPI.getCameraStream(cameraId)
      if (streamResponse.data) {
        if (streamResponse.data.status === 'converting' && streamResponse.data.hls_url) {
          console.log('找到后端转换的HLS流:', streamResponse.data.hls_url)
          // 将相对路径转换为正确的API路径
          const hlsUrl = streamResponse.data.hls_url.startsWith('http') 
            ? streamResponse.data.hls_url 
            : `http://localhost:5000/api/stream/play/${cameraId}`
          return hlsUrl
        } else if (streamResponse.data.status === 'not_converted') {
          console.log('RTMP流需要转换，启动转换...')
          // 启动转换
          const convertResponse = await cameraAPI.convertStream(cameraId)
          if (convertResponse.data && convertResponse.data.hls_url) {
            console.log('已启动后端转换，HLS流:', convertResponse.data.hls_url)
            // 将相对路径转换为正确的API路径
            const hlsUrl = convertResponse.data.hls_url.startsWith('http') 
              ? convertResponse.data.hls_url 
              : `http://localhost:5000/api/stream/play/${cameraId}`
            return hlsUrl
          }
        } else if (streamResponse.data.status === 'ready' && streamResponse.data.hls_url) {
          console.log('流媒体可直接播放:', streamResponse.data.hls_url)
          return streamResponse.data.hls_url
        }
      }
      
    } catch (error) {
      console.error('后端转换失败:', error)
      return ''
    }
    
    return ''
  }
  
  return url
}

// 初始化HLS播放器
const initHlsPlayer = (url: string) => {
  if (!videoElement.value || !url) return

  // 清理之前的HLS实例
  if (hls.value) {
    hls.value.destroy()
    hls.value = null
  }

  console.log('初始化HLS播放器，URL:', url)

  try {
    hls.value = new Hls({
      debug: false,
      enableWorker: false,    // 禁用Worker，避免兼容性问题
      lowLatencyMode: false,  // 禁用低延迟模式
      backBufferLength: 10,   // 减少缓冲长度
      maxBufferLength: 10,    // 限制最大缓冲长度
      maxMaxBufferLength: 20, // 限制最大缓冲长度上限
      liveSyncDurationCount: 2, // 直播同步片段数
      liveMaxLatencyDurationCount: 3, // 最大延迟片段数
      maxLiveSyncPlaybackRate: 1.1, // 最大播放速率
      liveDurationInfinity: true, // 直播持续时间无限
      liveBackBufferLength: 0, // 直播后缓冲长度
      manifestLoadingTimeOut: 5000, // 清单加载超时
      manifestLoadingMaxRetry: 2, // 清单加载最大重试次数
      levelLoadingTimeOut: 5000, // 级别加载超时
      levelLoadingMaxRetry: 2, // 级别加载最大重试次数
      fragLoadingTimeOut: 10000, // 片段加载超时
      fragLoadingMaxRetry: 2 // 片段加载最大重试次数
    })

    hls.value.loadSource(url)
    hls.value.attachMedia(videoElement.value)

    hls.value.on(Hls.Events.MANIFEST_PARSED, () => {
      console.log('HLS manifest解析完成')
      isLoading.value = false
      hasError.value = false
      errorMessage.value = ''
    })

    hls.value.on(Hls.Events.ERROR, (event, data) => {
      console.error('HLS播放错误:', data)
      
      if (data.fatal) {
        switch (data.type) {
          case Hls.ErrorTypes.NETWORK_ERROR:
            console.log('网络错误，尝试恢复...')
            hls.value.startLoad()
            break
          case Hls.ErrorTypes.MEDIA_ERROR:
            console.log('媒体错误，尝试恢复...')
            hls.value.recoverMediaError()
            break
          default:
            console.log('无法恢复的错误，销毁HLS实例')
            hasError.value = true
            errorMessage.value = '视频播放失败'
            break
        }
      } else {
        console.warn('非致命HLS错误:', data)
      }
    })

    hls.value.on(Hls.Events.FRAG_LOADED, () => {
      isLoading.value = false
    })

  } catch (error) {
    console.error('初始化HLS播放器失败:', error)
    hasError.value = true
    errorMessage.value = '无法初始化视频播放器'
  }
}

// 获取错误信息
const getErrorMessage = (error: any): string => {
  if (error.code === 1) {
    return '视频加载被中止'
  } else if (error.code === 2) {
    return '网络错误导致视频下载失败'
  } else if (error.code === 3) {
    return '视频解码错误'
  } else if (error.code === 4) {
    return '不支持的视频格式'
  } else {
    return '视频播放错误'
  }
}

// 重试播放
const retry = async () => {
  hasError.value = false
  errorMessage.value = ''
  
  const processedUrl = await processStreamUrl(props.streamUrl, props.cameraId)
  const streamType = getStreamType(props.streamUrl)
  
  if (streamType === 'application/x-mpegURL' && Hls.isSupported()) {
    initHlsPlayer(processedUrl)
  } else if (player.value) {
    player.value.src({
      src: processedUrl,
      type: streamType
    })
    player.value.load()
  }
}

// 播放
const play = () => {
  if (player.value) {
    player.value.play()
  }
}

// 暂停
const pause = () => {
  if (player.value) {
    player.value.pause()
  }
}

// 停止
const stop = () => {
  if (player.value) {
    player.value.pause()
    player.value.currentTime(0)
  }
}

// 设置音量
const setVolume = (volume: number) => {
  if (player.value) {
    player.value.volume(volume)
  }
}

// 设置播放速度
const setPlaybackRate = (rate: number) => {
  if (player.value) {
    player.value.playbackRate(rate)
  }
}

// 跳转到指定时间
const seekTo = (time: number) => {
  if (player.value) {
    player.value.currentTime(time)
  }
}

// 全屏
const requestFullscreen = () => {
  if (player.value) {
    player.value.requestFullscreen()
  }
}

// 退出全屏
const exitFullscreen = () => {
  if (player.value) {
    player.value.exitFullscreen()
  }
}

// 获取播放器状态
const getPlayerState = () => {
  if (!player.value) return null

  return {
    paused: player.value.paused(),
    currentTime: player.value.currentTime(),
    duration: player.value.duration(),
    volume: player.value.volume(),
    playbackRate: player.value.playbackRate(),
    buffered: player.value.buffered(),
    readyState: player.value.readyState(),
    networkState: player.value.networkState()
  }
}

// 事件处理
const handleLoadStart = () => {
  isLoading.value = true
  hasError.value = false
}

const handleLoadedData = () => {
  isLoading.value = false
}

const handleError = (event: any) => {
  isLoading.value = false
  hasError.value = true
  errorMessage.value = '视频加载失败'
}

// 监听属性变化
watch(() => props.streamUrl, async (newUrl) => {
  if (newUrl) {
    const processedUrl = await processStreamUrl(newUrl, props.cameraId)
    const streamType = getStreamType(newUrl)
    
    if (streamType === 'application/x-mpegURL' && Hls.isSupported()) {
      initHlsPlayer(processedUrl)
    } else if (player.value) {
      player.value.src({
        src: processedUrl,
        type: streamType
      })
      player.value.load()
    }
  }
})

watch(() => props.autoPlay, (newAutoPlay) => {
  if (player.value) {
    if (newAutoPlay) {
      player.value.play()
    } else {
      player.value.pause()
    }
  }
})

// 生命周期
onMounted(async () => {
  await nextTick()
  await initPlayer()
})

onUnmounted(() => {
  if (hls.value) {
    hls.value.destroy()
    hls.value = null
  }
  
  if (player.value) {
    player.value.dispose()
    player.value = null
  }
})

// 暴露方法给父组件
defineExpose({
  play,
  pause,
  stop,
  setVolume,
  setPlaybackRate,
  seekTo,
  requestFullscreen,
  exitFullscreen,
  getPlayerState
})
</script>

<style scoped>
.video-player {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  z-index: 10;
}

.loading-icon {
  font-size: 32px;
  margin-bottom: 10px;
  animation: spin 1s linear infinite;
}

.error-icon {
  font-size: 32px;
  margin-bottom: 10px;
  color: #f56c6c;
}

.error-content {
  text-align: center;
  max-width: 400px;
  margin-bottom: 15px;
}

.error-message {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 10px;
}

.error-detail {
  font-size: 12px;
  text-align: left;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.error-detail p {
  margin: 5px 0;
}

.error-detail ul {
  margin: 5px 0;
  padding-left: 20px;
}

.error-detail li {
  margin: 3px 0;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

:deep(.video-js) {
  width: 100%;
  height: 100%;
}

:deep(.video-js .vjs-big-play-button) {
  background-color: rgba(64, 158, 255, 0.8);
  border: none;
  border-radius: 50%;
}

:deep(.video-js .vjs-big-play-button:hover) {
  background-color: rgba(64, 158, 255, 1);
}

:deep(.video-js .vjs-control-bar) {
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
}

:deep(.video-js .vjs-progress-control) {
  height: 6px;
}

:deep(.video-js .vjs-progress-holder) {
  height: 6px;
}

:deep(.video-js .vjs-play-progress) {
  background-color: #409eff;
}

:deep(.video-js .vjs-load-progress) {
  background-color: rgba(255, 255, 255, 0.3);
}

:deep(.video-js .vjs-volume-bar) {
  background-color: rgba(255, 255, 255, 0.3);
}

:deep(.video-js .vjs-volume-level) {
  background-color: #409eff;
}
</style>
