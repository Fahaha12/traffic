<template>
  <div class="dashboard">
    <LayoutHeader />
    <div class="dashboard-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="dashboard-header">
          <h1>交通监控控制台</h1>
          <div class="header-actions">
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </div>
        
        <div class="dashboard-stats">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon online">
                    <el-icon><VideoCamera /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ onlineCameraCount }}</div>
                    <div class="stat-label">在线摄像头</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon active">
                    <el-icon><Truck /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ activeVehicleCount }}</div>
                    <div class="stat-label">活跃车辆</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon suspicious">
                    <el-icon><Warning /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ suspiciousVehicleCount }}</div>
                    <div class="stat-label">可疑车辆</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon alert">
                    <el-icon><Bell /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ unreadAlertCount }}</div>
                    <div class="stat-label">未读告警</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div class="dashboard-main">
          <el-row :gutter="20">
            <el-col :span="16">
              <el-card class="map-card">
                <template #header>
                  <div class="card-header">
                    <span>实时地图</span>
                    <el-button type="text" @click="goToMapView">查看详情</el-button>
                  </div>
                </template>
                <MapContainer :height="400" :show-controls="false" />
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="alerts-card">
                <template #header>
                  <div class="card-header">
                    <span>最新告警</span>
                    <el-button type="text" @click="goToAlerts">查看全部</el-button>
                  </div>
                </template>
                <div class="alerts-list">
                  <div 
                    v-for="alert in recentAlerts" 
                    :key="alert.id"
                    class="alert-item"
                    :class="alert.type"
                  >
                    <div class="alert-content">
                      <div class="alert-message">{{ alert.message }}</div>
                      <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
                    </div>
                    <el-button 
                      type="text" 
                      size="small"
                      @click="markAlertAsRead(alert.id)"
                    >
                      标记已读
                    </el-button>
                  </div>
                  <div v-if="recentAlerts.length === 0" class="no-alerts">
                    暂无告警
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div class="dashboard-bottom">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="cameras-card">
                <template #header>
                  <div class="card-header">
                    <span>摄像头状态</span>
                    <el-button type="text" @click="goToCameras">管理摄像头</el-button>
                  </div>
                </template>
                <div class="cameras-list">
                  <div 
                    v-for="camera in recentCameras" 
                    :key="camera.id"
                    class="camera-item"
                    :class="camera.status"
                  >
                    <div class="camera-info">
                      <div class="camera-name">{{ camera.name }}</div>
                      <div class="camera-status">
                        <el-tag :type="getStatusType(camera.status)" size="small">
                          {{ getStatusText(camera.status) }}
                        </el-tag>
                      </div>
                    </div>
                    <el-button 
                      type="text" 
                      size="small"
                      @click="viewCamera(camera.id)"
                    >
                      查看
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="vehicles-card">
                <template #header>
                  <div class="card-header">
                    <span>最近检测车辆</span>
                    <el-button type="text" @click="goToVehicles">查看全部</el-button>
                  </div>
                </template>
                <div class="vehicles-list">
                  <div 
                    v-for="vehicle in recentVehicles" 
                    :key="vehicle.id"
                    class="vehicle-item"
                  >
                    <div class="vehicle-info">
                      <div class="vehicle-plate">{{ vehicle.plateNumber || '未知车牌' }}</div>
                      <div class="vehicle-type">{{ getVehicleTypeText(vehicle.type) }}</div>
                    </div>
                    <div class="vehicle-time">{{ formatTime(vehicle.timestamp) }}</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCameraStore } from '@/stores/camera'
import { useVehicleStore } from '@/stores/vehicle'
import { useMapStore } from '@/stores/map'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import MapContainer from '@/components/Map/MapContainer.vue'
import dayjs from 'dayjs'

const router = useRouter()
const cameraStore = useCameraStore()
const vehicleStore = useVehicleStore()
const mapStore = useMapStore()

// 计算属性
const onlineCameraCount = computed(() => cameraStore.onlineCameras.length)
const activeVehicleCount = computed(() => vehicleStore.activeVehicles.length)
const suspiciousVehicleCount = computed(() => vehicleStore.suspiciousCount)
const unreadAlertCount = computed(() => vehicleStore.unreadAlerts.length)

const recentAlerts = computed(() => vehicleStore.vehicleAlerts.slice(0, 5))
const recentCameras = computed(() => cameraStore.cameras.slice(0, 5))
const recentVehicles = computed(() => vehicleStore.activeVehicles.slice(0, 5))

// 方法
const refreshData = async () => {
  try {
    await Promise.all([
      cameraStore.refreshCameraData(),
      // 这里可以添加其他数据刷新逻辑
    ])
  } catch (error) {
    console.error('刷新数据失败:', error)
  }
}

const goToMapView = () => {
  router.push('/map')
}

const goToAlerts = () => {
  router.push('/analytics')
}

const goToCameras = () => {
  router.push('/cameras')
}

const goToVehicles = () => {
  router.push('/analytics')
}

const markAlertAsRead = (alertId: string) => {
  vehicleStore.markAlertAsRead(alertId)
}

const viewCamera = (cameraId: string) => {
  router.push(`/cameras?camera=${cameraId}`)
}

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

const getVehicleTypeText = (type: string) => {
  switch (type) {
    case 'car': return '轿车'
    case 'truck': return '卡车'
    case 'bus': return '公交车'
    case 'motorcycle': return '摩托车'
    default: return '未知'
  }
}

const formatTime = (timestamp: string) => {
  return dayjs(timestamp).format('HH:mm:ss')
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: var(--bg-color);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-header h1 {
  color: var(--text-color);
  margin: 0;
}

.dashboard-stats {
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.online {
  background: var(--success-color);
}

.stat-icon.active {
  background: var(--primary-color);
}

.stat-icon.suspicious {
  background: var(--warning-color);
}

.stat-icon.alert {
  background: var(--danger-color);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-color-light);
  margin-top: 5px;
}

.dashboard-main {
  margin-bottom: 20px;
}

.dashboard-bottom {
  margin-bottom: 20px;
}

.map-card,
.alerts-card,
.cameras-card,
.vehicles-card {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alerts-list,
.cameras-list,
.vehicles-list {
  max-height: 300px;
  overflow-y: auto;
}

.alert-item,
.camera-item,
.vehicle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.alert-item:last-child,
.camera-item:last-child,
.vehicle-item:last-child {
  border-bottom: none;
}

.alert-content {
  flex: 1;
}

.alert-message {
  color: var(--text-color);
  font-size: 14px;
}

.alert-time {
  color: var(--text-color-light);
  font-size: 12px;
  margin-top: 2px;
}

.camera-info,
.vehicle-info {
  flex: 1;
}

.camera-name,
.vehicle-plate {
  color: var(--text-color);
  font-size: 14px;
  font-weight: 500;
}

.camera-status,
.vehicle-type {
  margin-top: 2px;
}

.vehicle-time {
  color: var(--text-color-light);
  font-size: 12px;
}

.no-alerts {
  text-align: center;
  color: var(--text-color-light);
  padding: 20px;
}
</style>
