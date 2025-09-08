<template>
  <div class="camera-detail-panel">
    <div class="camera-header">
      <h3>{{ camera.name }}</h3>
      <el-tag :type="getStatusType(camera.status)" size="small">
        {{ getStatusText(camera.status) }}
      </el-tag>
    </div>
    
    <div class="camera-video">
      <VideoPlayer
        :camera-id="camera.id"
        :stream-url="camera.streamUrl"
        :auto-play="false"
        :height="200"
      />
    </div>
    
    <div class="camera-info">
      <el-descriptions :column="1" size="small">
        <el-descriptions-item label="类型">
          {{ getTypeText(camera.type) }}
        </el-descriptions-item>
        <el-descriptions-item label="分辨率">
          {{ camera.resolution.width }}x{{ camera.resolution.height }}
        </el-descriptions-item>
        <el-descriptions-item label="帧率">
          {{ camera.fps }} FPS
        </el-descriptions-item>
        <el-descriptions-item label="位置">
          {{ camera.position.lat.toFixed(6) }}, {{ camera.position.lng.toFixed(6) }}
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">
          {{ formatTime(camera.lastUpdate) }}
        </el-descriptions-item>
      </el-descriptions>
    </div>
    
    <div class="camera-actions">
      <el-button type="primary" size="small" @click="startStream">
        开始播放
      </el-button>
      <el-button size="small" @click="stopStream">
        停止播放
      </el-button>
      <el-button size="small" @click="testConnection">
        测试连接
      </el-button>
    </div>
    
    <div class="camera-events">
      <h4>最近事件</h4>
      <div class="events-list">
        <div 
          v-for="event in recentEvents" 
          :key="event.id"
          class="event-item"
        >
          <div class="event-content">
            <div class="event-message">{{ event.message }}</div>
            <div class="event-time">{{ formatTime(event.timestamp) }}</div>
          </div>
        </div>
        <div v-if="recentEvents.length === 0" class="no-events">
          暂无事件
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useCameraStore } from '@/stores/camera'
import VideoPlayer from '@/components/Video/VideoPlayer.vue'
import { dateUtils } from '@/utils/dateUtils'
import { testStreamConnection } from '@/utils/streamUtils'
import type { CameraPosition } from '@/types'

interface Props {
  camera: CameraPosition
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const cameraStore = useCameraStore()

const recentEvents = computed(() => {
  return cameraStore.cameraEvents
    .filter(event => event.cameraId === props.camera.id)
    .slice(0, 5)
})

const getStatusType = (status: string) => {
  switch (status) {
    case 'online': return 'success'
    case 'offline': return 'danger'
    case 'maintenance': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'online': return '在线'
    case 'offline': return '离线'
    case 'maintenance': return '维护中'
    default: return '未知'
  }
}

const getTypeText = (type: string) => {
  switch (type) {
    case 'traffic': return '交通监控'
    case 'surveillance': return '安防监控'
    case 'speed': return '测速监控'
    default: return '未知'
  }
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatTime(timestamp)
}

const startStream = () => {
  cameraStore.startStream(props.camera.id, '')
}

const stopStream = () => {
  cameraStore.stopStream(props.camera.id)
}

const testConnection = async () => {
  try {
    ElMessage.info('正在测试摄像头连接...')
    
    // 使用流媒体工具进行连接测试
    const result = await testStreamConnection(props.camera.streamUrl)
    
    if (result.success) {
      ElMessage.success(result.message)
      cameraStore.updateCameraStatus(props.camera.id, 'online')
    } else {
      ElMessage.error(result.message)
      cameraStore.updateCameraStatus(props.camera.id, 'offline')
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error('测试连接失败')
  }
}
</script>

<style scoped>
.camera-detail-panel {
  padding: 20px;
}

.camera-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.camera-header h3 {
  margin: 0;
  color: var(--text-color);
}

.camera-video {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.camera-info {
  margin-bottom: 20px;
}

.camera-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.camera-actions .el-button {
  flex: 1;
}

.camera-events h4 {
  color: var(--text-color);
  margin-bottom: 12px;
  font-size: 14px;
}

.events-list {
  max-height: 200px;
  overflow-y: auto;
}

.event-item {
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.event-item:last-child {
  border-bottom: none;
}

.event-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-message {
  color: var(--text-color);
  font-size: 12px;
}

.event-time {
  color: var(--text-color-light);
  font-size: 11px;
}

.no-events {
  text-align: center;
  color: var(--text-color-light);
  padding: 20px;
  font-size: 12px;
}

:deep(.el-descriptions__label) {
  color: var(--text-color-light);
  font-size: 12px;
}

:deep(.el-descriptions__content) {
  color: var(--text-color);
  font-size: 12px;
}
</style>
