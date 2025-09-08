<template>
  <div class="camera-view">
    <LayoutHeader />
    <div class="camera-view-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="camera-header">
          <h1>摄像头管理</h1>
          <div class="camera-actions">
            <el-button type="primary" @click="showAddCameraDialog = true">
              <el-icon><Plus /></el-icon>
              添加摄像头
            </el-button>
            <el-button @click="refreshCameras">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="checkAllStatus" :loading="isCheckingStatus">
              <el-icon><Connection /></el-icon>
              检测状态
            </el-button>
          </div>
        </div>
        
        <div class="camera-content">
          <div class="camera-list">
            <el-card class="camera-list-card">
              <template #header>
                <div class="card-header">
                  <span>摄像头列表</span>
                  <el-input
                    v-model="searchKeyword"
                    placeholder="搜索摄像头"
                    size="small"
                    style="width: 200px"
                    clearable
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </div>
              </template>
              
              <div class="camera-grid">
                <div 
                  v-for="camera in filteredCameras" 
                  :key="camera.id"
                  class="camera-item"
                  :class="{ active: selectedCamera?.id === camera.id }"
                  @click="selectCamera(camera)"
                >
                  <div class="camera-preview">
                    <VideoPlayer 
                      :camera-id="camera.id"
                      :stream-url="camera.streamUrl"
                      :auto-play="false"
                      :height="120"
                    />
                    <div class="camera-status" :class="camera.status">
                      <el-icon>
                        <VideoCamera v-if="camera.status === 'online'" />
                        <VideoCameraFilled v-else />
                      </el-icon>
                    </div>
                  </div>
                  
                  <div class="camera-info">
                    <div class="camera-name">{{ camera.name }}</div>
                    <div class="camera-type">{{ getTypeText(camera.type) }}</div>
                    <div class="camera-resolution">{{ camera.resolution.width }}x{{ camera.resolution.height }}</div>
                  </div>
                  
                  <div class="camera-actions">
                    <el-button 
                      type="text" 
                      size="small"
                      @click.stop="viewCameraDetail(camera)"
                    >
                      详情
                    </el-button>
                    <el-button 
                      type="text" 
                      size="small"
                      @click.stop="editCamera(camera)"
                    >
                      编辑
                    </el-button>
                    <el-button 
                      type="text" 
                      size="small"
                      @click.stop="deleteCamera(camera)"
                      class="danger"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          
          <div class="camera-detail" v-if="selectedCamera">
            <el-card class="camera-detail-card">
              <template #header>
                <div class="card-header">
                  <span>{{ selectedCamera.name }}</span>
                  <el-button type="text" @click="selectedCamera = null">
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
              </template>
              
              <div class="camera-detail-content">
                <div class="detail-section">
                  <h4>基本信息</h4>
                  <div class="detail-item">
                    <span class="label">名称:</span>
                    <span class="value">{{ selectedCamera.name }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">类型:</span>
                    <span class="value">{{ getTypeText(selectedCamera.type) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">状态:</span>
                    <el-tag :type="getStatusType(selectedCamera.status)" size="small">
                      {{ getStatusText(selectedCamera.status) }}
                    </el-tag>
                  </div>
                  <div class="detail-item">
                    <span class="label">分辨率:</span>
                    <span class="value">{{ selectedCamera.resolution.width }}x{{ selectedCamera.resolution.height }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">帧率:</span>
                    <span class="value">{{ selectedCamera.fps }} FPS</span>
                  </div>
                </div>
                
                <div class="detail-section">
                  <h4>位置信息</h4>
                  <div class="detail-item">
                    <span class="label">纬度:</span>
                    <span class="value">{{ selectedCamera.position.lat.toFixed(6) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">经度:</span>
                    <span class="value">{{ selectedCamera.position.lng.toFixed(6) }}</span>
                  </div>
                  <div class="detail-item" v-if="selectedCamera.direction">
                    <span class="label">朝向:</span>
                    <span class="value">{{ selectedCamera.direction }}°</span>
                  </div>
                </div>
                
                <div class="detail-section">
                  <h4>操作</h4>
                  <div class="action-buttons">
                    <el-button type="primary" @click="startStream(selectedCamera.id)">
                      开始播放
                    </el-button>
                    <el-button @click="stopStream(selectedCamera.id)">
                      停止播放
                    </el-button>
                    <el-button @click="testConnection(selectedCamera.id)">
                      测试连接
                    </el-button>
                    <el-button @click="restartCamera(selectedCamera.id)">
                      重启摄像头
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加摄像头对话框 -->
    <el-dialog
      v-model="showAddCameraDialog"
      title="添加摄像头"
      width="600px"
    >
      <AddCameraForm @success="handleAddCameraSuccess" @cancel="showAddCameraDialog = false" />
    </el-dialog>
    
    <!-- 编辑摄像头对话框 -->
    <el-dialog
      v-model="showEditCameraDialog"
      title="编辑摄像头"
      width="600px"
    >
      <EditCameraForm 
        v-if="editingCamera"
        :camera="editingCamera"
        @success="handleEditCameraSuccess"
        @cancel="showEditCameraDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCameraStore } from '@/stores/camera'
import { testStreamConnection } from '@/utils/streamUtils'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import VideoPlayer from '@/components/Video/VideoPlayer.vue'
import AddCameraForm from '@/components/Camera/AddCameraForm.vue'
import EditCameraForm from '@/components/Camera/EditCameraForm.vue'
import type { Camera } from '@/types'

const cameraStore = useCameraStore()

const searchKeyword = ref('')
const selectedCamera = ref<Camera | null>(null)
const editingCamera = ref<Camera | null>(null)
const showAddCameraDialog = ref(false)
const showEditCameraDialog = ref(false)
const isCheckingStatus = ref(false)

const filteredCameras = computed(() => {
  if (!searchKeyword.value) {
    return cameraStore.cameras
  }
  
  return cameraStore.cameras.filter(camera =>
    camera.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    camera.type.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const selectCamera = (camera: Camera) => {
  selectedCamera.value = camera
}

const viewCameraDetail = (camera: Camera) => {
  selectedCamera.value = camera
}

const editCamera = (camera: Camera) => {
  editingCamera.value = camera
  showEditCameraDialog.value = true
}

const deleteCamera = async (camera: Camera) => {
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要删除摄像头 "${camera.name}" 吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await cameraStore.removeCamera(camera.id)
    if (selectedCamera.value?.id === camera.id) {
      selectedCamera.value = null
    }
    ElMessage.success('摄像头删除成功')
  } catch (error) {
    if (error === 'cancel') {
      ElMessage.info('已取消删除')
    } else {
      console.error('删除摄像头失败:', error)
      ElMessage.error('删除摄像头失败')
    }
  }
}

const startStream = (cameraId: string) => {
  cameraStore.startStream(cameraId, '')
}

const stopStream = (cameraId: string) => {
  cameraStore.stopStream(cameraId)
}

const testConnection = async (cameraId: string) => {
  try {
    const camera = cameraStore.cameras.find(c => c.id === cameraId)
    if (!camera) {
      ElMessage.error('摄像头不存在')
      return
    }
    
    ElMessage.info('正在测试摄像头连接...')
    
    // 使用流媒体工具进行连接测试
    const result = await testStreamConnection(camera.streamUrl)
    
    if (result.success) {
      ElMessage.success(result.message)
      cameraStore.updateCameraStatus(cameraId, 'online')
    } else {
      ElMessage.error(result.message)
      cameraStore.updateCameraStatus(cameraId, 'offline')
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error('测试连接失败')
  }
}

const restartCamera = async (cameraId: string) => {
  try {
    // 这里调用重启摄像头的API
    console.log('重启摄像头:', cameraId)
  } catch (error) {
    console.error('重启摄像头失败:', error)
  }
}

const refreshCameras = async () => {
  try {
    await cameraStore.refreshCameraData()
  } catch (error) {
    console.error('刷新摄像头数据失败:', error)
  }
}

const checkAllStatus = async () => {
  try {
    isCheckingStatus.value = true
    await cameraStore.checkAllCameraStatus()
    ElMessage.success('状态检测完成')
  } catch (error) {
    console.error('状态检测失败:', error)
    ElMessage.error('状态检测失败')
  } finally {
    isCheckingStatus.value = false
  }
}

const handleAddCameraSuccess = () => {
  showAddCameraDialog.value = false
  refreshCameras()
}

const handleEditCameraSuccess = () => {
  showEditCameraDialog.value = false
  editingCamera.value = null
  refreshCameras()
}

const getTypeText = (type: string) => {
  const typeMap = {
    traffic: '交通监控',
    surveillance: '安防监控',
    speed: '测速监控'
  }
  return typeMap[type as keyof typeof typeMap] || '未知'
}

const getStatusText = (status: string) => {
  const statusMap = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中'
  }
  return statusMap[status as keyof typeof statusMap] || '未知'
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'online': return 'success'
    case 'offline': return 'danger'
    case 'maintenance': return 'warning'
    default: return 'info'
  }
}

onMounted(async () => {
  // 清除本地存储并重新从云端加载数据
  await cameraStore.clearLocalStorageAndRefresh()
})
</script>

<style scoped>
.camera-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.camera-view-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow: hidden;
  background: var(--bg-color);
}

.camera-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.camera-header h1 {
  color: var(--text-color);
  margin: 0;
}

.camera-content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
}

.camera-list {
  flex: 1;
}

.camera-detail {
  width: 400px;
}

.camera-list-card,
.camera-detail-card {
  height: 100%;
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.camera-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.camera-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-color);
}

.camera-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.camera-item.active {
  border-color: var(--primary-color);
  background: rgba(64, 158, 255, 0.1);
}

.camera-preview {
  position: relative;
  margin-bottom: 12px;
  border-radius: 4px;
  overflow: hidden;
}

.camera-status {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
}

.camera-status.online {
  background: var(--success-color);
}

.camera-status.offline {
  background: var(--danger-color);
}

.camera-status.maintenance {
  background: var(--warning-color);
}

.camera-info {
  margin-bottom: 12px;
}

.camera-name {
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 4px;
}

.camera-type,
.camera-resolution {
  font-size: 12px;
  color: var(--text-color-light);
  margin-bottom: 2px;
}

.camera-actions {
  display: flex;
  gap: 8px;
}

.camera-actions .danger {
  color: var(--danger-color);
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  color: var(--text-color);
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item .label {
  color: var(--text-color-light);
}

.detail-item .value {
  color: var(--text-color);
  font-weight: 500;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-buttons .el-button {
  width: 100%;
}
</style>
