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
      <span>{{ errorMessage }}</span>
      <el-button type="primary" size="small" @click="retry">重试</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'
import type { VideoQuality } from '@/utils/videoUtils'

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
const isLoading = ref(false)
const hasError = ref(false)
const errorMessage = ref('')

const dataSetup = ref('{}')

// 初始化视频播放器
const initPlayer = () => {
  if (!videoElement.value) return

  const options = {
    controls: props.controls,
    fluid: true,
    responsive: true,
    autoplay: props.autoPlay,
    preload: props.preload,
    poster: props.poster,
    sources: [
      {
        src: props.streamUrl,
        type: getStreamType(props.streamUrl)
      }
    ],
    techOrder: ['html5'],
    html5: {
      vhs: {
        overrideNative: true
      }
    }
  }

  try {
    player.value = videojs(videoElement.value, options)
    
    player.value.ready(() => {
      emit('ready', player.value)
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
  } else {
    return 'video/mp4'
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
const retry = () => {
  hasError.value = false
  errorMessage.value = ''
  if (player.value) {
    player.value.src(props.streamUrl)
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
watch(() => props.streamUrl, (newUrl) => {
  if (player.value && newUrl) {
    player.value.src(newUrl)
    player.value.load()
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
onMounted(() => {
  nextTick(() => {
    initPlayer()
  })
})

onUnmounted(() => {
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
