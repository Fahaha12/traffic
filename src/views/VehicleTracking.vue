<template>
  <div class="vehicle-tracking-view">
    <LayoutHeader />
    <div class="vehicle-tracking-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="vehicle-tracking-header">
          <h1>轨迹追踪</h1>
          <div class="header-actions">
            <el-button type="primary" @click="refreshTracking">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="exportTrajectory">
              <el-icon><Download /></el-icon>
              导出轨迹
            </el-button>
          </div>
        </div>
        
        <div class="vehicle-tracking-content-wrapper">
          <!-- 车辆选择 -->
          <div class="vehicle-selector">
            <el-card>
              <el-form :model="searchForm" inline>
                <el-form-item label="车牌号">
                  <el-input 
                    v-model="searchForm.plateNumber" 
                    placeholder="请输入车牌号" 
                    @keyup.enter="searchVehicle"
                    style="width: 200px"
                  />
                </el-form-item>
                
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="searchForm.dateRange"
                    type="datetimerange"
                    range-separator="至"
                    start-placeholder="开始时间"
                    end-placeholder="结束时间"
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    style="width: 400px"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="searchVehicle">搜索</el-button>
                  <el-button @click="clearSearch">清空</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
          
          <!-- 地图和轨迹信息 -->
          <div class="tracking-main">
            <el-row :gutter="20">
              <!-- 地图区域 -->
              <el-col :span="16">
                <el-card class="map-card">
                  <template #header>
                    <div class="card-header">
                      <span>轨迹地图</span>
                      <div class="map-controls">
                        <el-button size="small" @click="fitBounds">适应范围</el-button>
                        <el-button size="small" @click="playTrajectory" :disabled="!selectedVehicle">
                          <el-icon><VideoPlay /></el-icon>
                          播放轨迹
                        </el-button>
                        <el-button size="small" @click="pauseTrajectory" :disabled="!isPlaying">
                          <el-icon><VideoPause /></el-icon>
                          暂停
                        </el-button>
                      </div>
                    </div>
                  </template>
                  
                  <div class="map-container" ref="mapContainer">
                    <div id="tracking-map" style="width: 100%; height: 500px;"></div>
                  </div>
                </el-card>
              </el-col>
              
              <!-- 轨迹信息 -->
              <el-col :span="8">
                <el-card class="info-card">
                  <template #header>
                    <span>轨迹信息</span>
                  </template>
                  
                  <div v-if="selectedVehicle" class="vehicle-info">
                    <el-descriptions :column="1" border>
                      <el-descriptions-item label="车牌号">
                        {{ selectedVehicle.plateNumber }}
                      </el-descriptions-item>
                      <el-descriptions-item label="车辆类型">
                        <el-tag :type="getVehicleTypeTagType(selectedVehicle.vehicleType)" size="small">
                          {{ getVehicleTypeText(selectedVehicle.vehicleType) }}
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="颜色">
                        {{ selectedVehicle.color }}
                      </el-descriptions-item>
                      <el-descriptions-item label="轨迹点数">
                        {{ trajectoryPoints.length }}
                      </el-descriptions-item>
                      <el-descriptions-item label="总距离">
                        {{ totalDistance.toFixed(2) }} 公里
                      </el-descriptions-item>
                      <el-descriptions-item label="平均速度">
                        {{ averageSpeed.toFixed(1) }} km/h
                      </el-descriptions-item>
                      <el-descriptions-item label="最大速度">
                        {{ maxSpeed.toFixed(1) }} km/h
                      </el-descriptions-item>
                      <el-descriptions-item label="追踪时长">
                        {{ trackingDuration }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                  
                  <div v-else class="no-vehicle">
                    <el-empty description="请选择车辆查看轨迹" />
                  </div>
                </el-card>
                
                <!-- 轨迹点列表 -->
                <el-card class="points-card" v-if="selectedVehicle">
                  <template #header>
                    <span>轨迹点列表</span>
                  </template>
                  
                  <div class="points-list">
                    <el-timeline>
                      <el-timeline-item
                        v-for="(point, index) in trajectoryPoints"
                        :key="index"
                        :timestamp="formatTime(point.timestamp)"
                        placement="top"
                      >
                        <div class="point-info">
                          <div class="point-location">{{ point.location }}</div>
                          <div class="point-details">
                            <span>速度: {{ point.speed }} km/h</span>
                            <span>方向: {{ point.direction }}°</span>
                          </div>
                        </div>
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useVehicleStore } from '@/stores/vehicle'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'
import { ElMessage } from 'element-plus'
import L from 'leaflet'

const route = useRoute()
const userStore = useUserStore()
const vehicleStore = useVehicleStore()

// 响应式数据
const mapContainer = ref<HTMLElement>()
const mapInstance = ref<any>(null)
const selectedVehicle = ref<any>(null)
const trajectoryPoints = ref<any[]>([])
const isPlaying = ref(false)
const playInterval = ref<any>(null)

const searchForm = reactive({
  plateNumber: '',
  dateRange: null as any
})

// 轨迹数据将从后端API获取

// 计算属性
const totalDistance = computed(() => {
  if (trajectoryPoints.value.length < 2) return 0
  
  let distance = 0
  for (let i = 1; i < trajectoryPoints.value.length; i++) {
    const prev = trajectoryPoints.value[i - 1]
    const curr = trajectoryPoints.value[i]
    distance += calculateDistance(prev.lat, prev.lng, curr.lat, curr.lng)
  }
  return distance
})

const averageSpeed = computed(() => {
  if (trajectoryPoints.value.length === 0) return 0
  
  const totalSpeed = trajectoryPoints.value.reduce((sum, point) => sum + point.speed, 0)
  return totalSpeed / trajectoryPoints.value.length
})

const maxSpeed = computed(() => {
  if (trajectoryPoints.value.length === 0) return 0
  
  return Math.max(...trajectoryPoints.value.map(point => point.speed))
})

const trackingDuration = computed(() => {
  if (trajectoryPoints.value.length < 2) return '0分钟'
  
  const start = new Date(trajectoryPoints.value[0].timestamp)
  const end = new Date(trajectoryPoints.value[trajectoryPoints.value.length - 1].timestamp)
  const duration = end.getTime() - start.getTime()
  
  const hours = Math.floor(duration / 3600000)
  const minutes = Math.floor((duration % 3600000) / 60000)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
})

// 方法
const getVehicleTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    car: '小型汽车',
    truck: '大型汽车',
    motorcycle: '摩托车',
    other: '其他'
  }
  return typeMap[type] || type
}

const getVehicleTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    car: 'primary',
    truck: 'warning',
    motorcycle: 'info',
    other: 'success'
  }
  return typeMap[type] || 'info'
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatDateTime(timestamp)
}

const calculateDistance = (lat1: number, lng1: number, lat2: number, lng2: number) => {
  const R = 6371 // 地球半径（公里）
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

const initMap = () => {
  if (!mapInstance.value) {
    mapInstance.value = L.map('tracking-map').setView([34.7466, 113.6253], 12)
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(mapInstance.value)
  }
}

const searchVehicle = async () => {
  if (!searchForm.plateNumber) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  try {
    // 从后端获取车辆信息
    const vehicles = await vehicleStore.fetchVehicles({ search: searchForm.plateNumber })
    if (vehicles.vehicles.length === 0) {
      ElMessage.error('未找到该车辆')
      return
    }
    
    const vehicle = vehicles.vehicles[0]
    selectedVehicle.value = vehicle
    
    // 获取车辆轨迹
    const tracks = await vehicleStore.fetchVehicleTracks(vehicle.id)
    trajectoryPoints.value = tracks.map(track => ({
      lat: track.latitude,
      lng: track.longitude,
      timestamp: track.detectedAt,
      speed: track.speed,
      direction: track.direction,
      location: track.cameraId
    }))
    
    drawTrajectory()
    ElMessage.success('找到车辆轨迹')
  } catch (error) {
    console.error('搜索车辆失败:', error)
    ElMessage.error('搜索车辆失败')
  }
}

const clearSearch = () => {
  searchForm.plateNumber = ''
  searchForm.dateRange = null
  selectedVehicle.value = null
  trajectoryPoints.value = []
  if (mapInstance.value) {
    mapInstance.value.eachLayer((layer: any) => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        mapInstance.value.removeLayer(layer)
      }
    })
  }
}

const drawTrajectory = () => {
  if (!mapInstance.value || trajectoryPoints.value.length === 0) return
  
  // 清除之前的轨迹
  mapInstance.value.eachLayer((layer: any) => {
    if (layer instanceof L.Marker || layer instanceof L.Polyline) {
      mapInstance.value.removeLayer(layer)
    }
  })
  
  // 绘制轨迹线
  const latlngs = trajectoryPoints.value.map(point => [point.lat, point.lng])
  const polyline = L.polyline(latlngs, {
    color: '#409eff',
    weight: 4,
    opacity: 0.8
  }).addTo(mapInstance.value)
  
  // 添加起点和终点标记
  const startPoint = trajectoryPoints.value[0]
  const endPoint = trajectoryPoints.value[trajectoryPoints.value.length - 1]
  
  L.marker([startPoint.lat, startPoint.lng], {
    icon: L.divIcon({
      className: 'start-marker',
      html: '<div style="background: #67c23a; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px;">起</div>',
      iconSize: [20, 20]
    })
  }).addTo(mapInstance.value)
  
  L.marker([endPoint.lat, endPoint.lng], {
    icon: L.divIcon({
      className: 'end-marker',
      html: '<div style="background: #f56c6c; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px;">终</div>',
      iconSize: [20, 20]
    })
  }).addTo(mapInstance.value)
  
  // 添加中间点标记
  trajectoryPoints.value.forEach((point, index) => {
    if (index > 0 && index < trajectoryPoints.value.length - 1) {
      L.marker([point.lat, point.lng], {
        icon: L.divIcon({
          className: 'waypoint-marker',
          html: `<div style="background: #409eff; color: white; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; font-size: 10px;">${index}</div>`,
          iconSize: [16, 16]
        })
      }).addTo(mapInstance.value)
    }
  })
  
  // 适应地图范围
  fitBounds()
}

const fitBounds = () => {
  if (mapInstance.value && trajectoryPoints.value.length > 0) {
    const bounds = L.latLngBounds(trajectoryPoints.value.map(point => [point.lat, point.lng]))
    mapInstance.value.fitBounds(bounds, { padding: [20, 20] })
  }
}

const playTrajectory = () => {
  if (trajectoryPoints.value.length === 0) return
  
  isPlaying.value = true
  let currentIndex = 0
  
  playInterval.value = setInterval(() => {
    if (currentIndex < trajectoryPoints.value.length) {
      const point = trajectoryPoints.value[currentIndex]
      
      // 移动地图中心到当前点
      mapInstance.value.setView([point.lat, point.lng], 16)
      
      // 添加当前位置标记
      L.marker([point.lat, point.lng], {
        icon: L.divIcon({
          className: 'current-marker',
          html: '<div style="background: #e6a23c; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; animation: pulse 1s infinite;">●</div>',
          iconSize: [24, 24]
        })
      }).addTo(mapInstance.value)
      
      currentIndex++
    } else {
      pauseTrajectory()
    }
  }, 1000)
}

const pauseTrajectory = () => {
  isPlaying.value = false
  if (playInterval.value) {
    clearInterval(playInterval.value)
    playInterval.value = null
  }
}

const refreshTracking = () => {
  if (selectedVehicle.value) {
    drawTrajectory()
    ElMessage.success('轨迹已刷新')
  } else {
    ElMessage.info('请先选择车辆')
  }
}

const exportTrajectory = () => {
  if (selectedVehicle.value) {
    ElMessage.info('导出功能开发中...')
  } else {
    ElMessage.info('请先选择车辆')
  }
}

onMounted(() => {
  nextTick(() => {
    initMap()
    
    // 从URL参数获取车牌号
    const plateNumber = route.query.plateNumber as string
    if (plateNumber) {
      searchForm.plateNumber = plateNumber
      searchVehicle()
    }
  })
})

onUnmounted(() => {
  pauseTrajectory()
  if (mapInstance.value) {
    mapInstance.value.remove()
  }
})
</script>

<style scoped>
.vehicle-tracking-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.vehicle-tracking-content {
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

.vehicle-tracking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.vehicle-tracking-header h1 {
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.vehicle-tracking-content-wrapper {
  max-width: 1400px;
}

.vehicle-selector {
  margin-bottom: 20px;
}

.tracking-main {
  margin-bottom: 20px;
}

.map-card,
.info-card,
.points-card {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.map-controls {
  display: flex;
  gap: 10px;
}

.vehicle-info {
  margin-bottom: 20px;
}

.no-vehicle {
  text-align: center;
  padding: 40px 0;
}

.points-list {
  max-height: 400px;
  overflow-y: auto;
}

.point-info {
  padding: 5px 0;
}

.point-location {
  font-weight: bold;
  color: var(--text-color);
  margin-bottom: 5px;
}

.point-details {
  font-size: 12px;
  color: var(--text-color-light);
  display: flex;
  gap: 15px;
}

:deep(.el-card__header) {
  background: var(--bg-color-lighter);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
}

:deep(.el-form-item__label) {
  color: var(--text-color);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  background: var(--bg-color);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-descriptions) {
  background: var(--bg-color-light);
}

:deep(.el-descriptions__label) {
  color: var(--text-color);
  background: var(--bg-color-lighter);
}

:deep(.el-descriptions__content) {
  color: var(--text-color);
  background: var(--bg-color-light);
}

:deep(.el-timeline-item__timestamp) {
  color: var(--text-color-light);
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}
</style>
