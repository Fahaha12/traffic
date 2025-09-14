<template>
  <div class="vehicle-tracking-view">
    <LayoutHeader />
    <div class="vehicle-tracking-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="tracking-header">
          <h1>车辆轨迹追踪</h1>
          <div class="header-actions">
            <el-button @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <el-button type="primary" @click="refreshTracks">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="exportTrajectory" v-if="tracks.length > 0">
              <el-icon><Download /></el-icon>
              导出轨迹
            </el-button>
          </div>
        </div>
        
        <div class="tracking-content">
          <!-- 车辆信息和轨迹控制并排 -->
          <el-row :gutter="20" class="info-controls-row">
            <!-- 车辆信息卡片 -->
            <el-col :span="12">
              <el-card class="vehicle-info-card" v-if="vehicleInfo">
                <template #header>
                  <div class="card-header">
                    <span>车辆信息</span>
                    <el-tag :type="vehicleInfo.isSuspicious ? 'warning' : 'success'" size="small">
                      {{ vehicleInfo.isSuspicious ? '可疑' : '正常' }}
                    </el-tag>
                  </div>
                </template>
                <div class="vehicle-info">
                  <div class="info-item">
                    <label>车牌号：</label>
                    <span>{{ vehicleInfo.plateNumber }}</span>
                  </div>
                  <div class="info-item">
                    <label>车辆类型：</label>
                    <el-tag :type="getVehicleTypeTagType(vehicleInfo.vehicleType)" size="small">
                      {{ getVehicleTypeText(vehicleInfo.vehicleType) }}
                    </el-tag>
                  </div>
                  <div class="info-item">
                    <label>颜色：</label>
                    <span>{{ vehicleInfo.color || '未知' }}</span>
                  </div>
                  <div class="info-item">
                    <label>品牌：</label>
                    <span>{{ vehicleInfo.brand || '未知' }}</span>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <!-- 轨迹控制面板 -->
            <el-col :span="12">
              <el-card class="tracking-controls">
                <template #header>
                  <span>轨迹控制</span>
                </template>
                <div class="controls-content">
                  <el-form :model="trackingParams" inline>
                    <el-form-item label="时间范围">
                      <el-date-picker
                        v-model="trackingParams.dateRange"
                        type="datetimerange"
                        range-separator="至"
                        start-placeholder="开始时间"
                        end-placeholder="结束时间"
                        format="YYYY-MM-DD HH:mm:ss"
                        value-format="YYYY-MM-DD HH:mm:ss"
                        style="width: 100%"
                      />
                    </el-form-item>
                    <el-form-item label="轨迹点数">
                      <el-input-number
                        v-model="trackingParams.limit"
                        :min="10"
                        :max="1000"
                        controls-position="right"
                        style="width: 100%"
                      />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="loadTracks" style="width: 100%">查询轨迹</el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
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
                        <el-button size="small" @click="playTrajectory" :disabled="!vehicleInfo || tracks.length === 0">
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
                  
                  <div v-if="vehicleInfo" class="vehicle-info">
                    <el-descriptions :column="1" border>
                      <el-descriptions-item label="车牌号">
                        {{ vehicleInfo.plateNumber }}
                      </el-descriptions-item>
                      <el-descriptions-item label="车辆类型">
                        <el-tag :type="getVehicleTypeTagType(vehicleInfo.vehicleType)" size="small">
                          {{ getVehicleTypeText(vehicleInfo.vehicleType) }}
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="颜色">
                        {{ vehicleInfo.color || '未知' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="轨迹点数">
                        {{ tracks.length }}
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
              </el-col>
            </el-row>
            
            <!-- 轨迹点列表 - 移到地图下面 -->
            <el-card class="points-card" v-if="vehicleInfo && tracks.length > 0">
              <template #header>
                <span>轨迹点列表 ({{ tracks.length }} 个点)</span>
              </template>
              
              <el-table :data="tracks" style="width: 100%" max-height="400">
                <el-table-column prop="detectedAt" label="检测时间" width="200">
                  <template #default="{ row }">
                    {{ formatTime(row.detectedAt) }}
                  </template>
                </el-table-column>
                <el-table-column prop="latitude" label="纬度" width="150" />
                <el-table-column prop="longitude" label="经度" width="150" />
                <el-table-column prop="speed" label="速度" width="120">
                  <template #default="{ row }">
                    {{ row.speed || 0 }} km/h
                  </template>
                </el-table-column>
                <el-table-column prop="direction" label="方向" width="120">
                  <template #default="{ row }">
                    {{ row.direction || 0 }}°
                  </template>
                </el-table-column>
                <el-table-column prop="confidence" label="置信度" width="150">
                  <template #default="{ row }">
                    <el-progress
                      :percentage="Math.round((row.confidence || 0) * 100)"
                      :stroke-width="6"
                      :show-text="false"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="cameraId" label="摄像头ID" width="180">
                  <template #default="{ row }">
                    {{ row.cameraId || '未知' }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row, $index }">
                    <el-button type="text" size="small" @click="goToTrack($index)">
                      定位
                    </el-button>
                    <el-button type="text" size="small" @click="viewImage(row)" v-if="row.imageUrl">
                      查看图片
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="showImageDialog"
      :title="`轨迹图片 - ${formatTime(selectedImage?.detectedAt)}`"
      width="800px"
    >
      <div class="image-preview">
        <img
          :src="selectedImage?.imageUrl"
          :alt="`轨迹图片 - ${formatTime(selectedImage?.detectedAt)}`"
          style="width: 100%; max-height: 400px"
        />
        <div class="image-info">
          <p><strong>检测时间：</strong>{{ formatTime(selectedImage.detectedAt) }}</p>
          <p><strong>位置：</strong>{{ selectedImage.latitude }}, {{ selectedImage.longitude }}</p>
          <p><strong>置信度：</strong>{{ Math.round((selectedImage.confidence || 0) * 100) }}%</p>
        </div>
      </div>
    </el-dialog>
    
    <!-- 车辆选择对话框 -->
    <el-dialog
      v-model="showVehicleSelector"
      title="选择车辆"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-loading="vehicleListLoading">
        <el-table :data="vehicleList" style="width: 100%" max-height="400">
          <el-table-column type="selection" width="55">
            <template #default="{ row }">
              <el-radio 
                v-model="selectedVehicleId" 
                :label="row.id"
                @change="selectedVehicleId = row.id"
              />
            </template>
          </el-table-column>
          <el-table-column prop="plateNumber" label="车牌号" width="120" />
          <el-table-column prop="vehicleType" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getVehicleTypeTagType(row.vehicleType)" size="small">
                {{ getVehicleTypeText(row.vehicleType) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="color" label="颜色" width="80" />
          <el-table-column prop="brand" label="品牌" width="100" />
          <el-table-column prop="model" label="型号" width="100" />
          <el-table-column prop="isSuspicious" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.isSuspicious ? 'warning' : 'success'" size="small">
                {{ row.isSuspicious ? '可疑' : '正常' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" @click="selectVehicle" :disabled="!selectedVehicleId">
          选择车辆
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useVehicleStore } from '@/stores/vehicle'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh, Download, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import L from 'leaflet'

const route = useRoute()
const router = useRouter()
const vehicleStore = useVehicleStore()

// 响应式数据
const vehicleInfo = ref<any>(null)
const tracks = ref<any[]>([])
const loading = ref(false)
const isPlaying = ref(false)
const currentTrackIndex = ref(0)
const showImageDialog = ref(false)
const selectedImage = ref<any>(null)
const mapContainer = ref<HTMLElement>()
const mapInstance = ref<any>(null)
const playbackTimer = ref<any>(null)

// 车辆选择相关
const showVehicleSelector = ref(false)
const vehicleList = ref<any[]>([])
const vehicleListLoading = ref(false)
const selectedVehicleId = ref('')

// 轨迹查询参数
const trackingParams = reactive({
  dateRange: null as any,
  limit: 100
})

// 计算属性
const totalDistance = computed(() => {
  if (tracks.value.length < 2) return 0
  
  let distance = 0
  for (let i = 1; i < tracks.value.length; i++) {
    const prev = tracks.value[i - 1]
    const curr = tracks.value[i]
    distance += calculateDistance(prev.latitude, prev.longitude, curr.latitude, curr.longitude)
  }
  return distance
})

const averageSpeed = computed(() => {
  if (tracks.value.length === 0) return 0
  
  const totalSpeed = tracks.value.reduce((sum, track) => sum + (track.speed || 0), 0)
  return totalSpeed / tracks.value.length
})

const maxSpeed = computed(() => {
  if (tracks.value.length === 0) return 0
  
  return Math.max(...tracks.value.map(track => track.speed || 0))
})

const trackingDuration = computed(() => {
  if (tracks.value.length < 2) return '0分钟'
  
  const start = new Date(tracks.value[0].detectedAt)
  const end = new Date(tracks.value[tracks.value.length - 1].detectedAt)
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
    bus: '公交车',
    bicycle: '自行车',
    other: '其他'
  }
  return typeMap[type] || type
}

const getVehicleTypeTagType = (type: string): 'primary' | 'success' | 'info' | 'warning' | 'danger' => {
  const typeMap: Record<string, 'primary' | 'success' | 'info' | 'warning' | 'danger'> = {
    car: 'primary',
    truck: 'warning',
    motorcycle: 'info',
    bus: 'success',
    bicycle: 'info',
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

const initMap = async () => {
  if (!mapInstance.value) {
    // 确保DOM元素存在
    await nextTick()
    
    const mapElement = document.getElementById('tracking-map')
    if (!mapElement) {
      console.error('地图容器不存在')
      return
    }
    
    // 如果地图已经存在，先移除
    if (mapInstance.value) {
      mapInstance.value.remove()
    }
    
    mapInstance.value = L.map('tracking-map').setView([34.7466, 113.6253], 12)
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(mapInstance.value)
    
    console.log('地图初始化完成')
  }
}

const loadVehicleInfo = async () => {
  const vehicleId = route.query.vehicleId as string
  const plateNumber = route.query.plateNumber as string
  
  // 检查参数是否存在且不为空字符串
  if ((!vehicleId || vehicleId.trim() === '') && (!plateNumber || plateNumber.trim() === '')) {
    ElMessage.error('缺少车辆参数')
    router.push('/vehicles')
    return
  }
  
  try {
    if (vehicleId) {
      // 根据车辆ID获取车辆信息
      const vehicle = await vehicleStore.fetchVehicle(vehicleId)
      vehicleInfo.value = vehicle
    } else if (plateNumber) {
      // 根据车牌号查找车辆信息
      const response = await vehicleStore.fetchVehicles({ search: plateNumber })
      if (response.vehicles && response.vehicles.length > 0) {
        vehicleInfo.value = response.vehicles[0]
      } else {
        ElMessage.error('未找到该车辆')
        router.push('/vehicles')
        return
      }
    }
  } catch (error) {
    console.error('加载车辆信息失败:', error)
    ElMessage.error('加载车辆信息失败')
    router.push('/vehicles')
  }
}

const loadTracks = async () => {
  // 获取车辆ID，优先使用vehicleInfo，否则使用路由参数
  const vehicleId = vehicleInfo.value?.id || route.query.vehicleId as string
  
  if (!vehicleId) {
    ElMessage.error('无法获取车辆ID')
    return
  }
  
  try {
    loading.value = true
    const params: any = {
      limit: trackingParams.limit
    }
    
    if (trackingParams.dateRange && trackingParams.dateRange.length === 2) {
      params.start_time = trackingParams.dateRange[0]
      params.end_time = trackingParams.dateRange[1]
    }
    
    const trackData = await vehicleStore.fetchVehicleTracks(vehicleId, params)
    tracks.value = trackData
    
    // 绘制轨迹
    drawTrajectory()
    
    ElMessage.success(`加载了 ${trackData.length} 个轨迹点`)
  } catch (error) {
    console.error('加载轨迹失败:', error)
    ElMessage.error('加载轨迹失败')
  } finally {
    loading.value = false
  }
}

const drawTrajectory = () => {
  if (!mapInstance.value || tracks.value.length === 0) return
  
  // 清除之前的轨迹
  mapInstance.value.eachLayer((layer: any) => {
    if (layer instanceof L.Marker || layer instanceof L.Polyline) {
      mapInstance.value.removeLayer(layer)
    }
  })
  
  // 绘制轨迹线
  const latlngs = tracks.value.map(track => [track.latitude, track.longitude])
  const polyline = L.polyline(latlngs, {
    color: '#409eff',
    weight: 4,
    opacity: 0.8
  }).addTo(mapInstance.value)
  
  // 添加起点和终点标记
  const startPoint = tracks.value[0]
  const endPoint = tracks.value[tracks.value.length - 1]
  
  L.marker([startPoint.latitude, startPoint.longitude], {
    icon: L.divIcon({
      className: 'start-marker',
      html: '<div style="background: #67c23a; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px;">起</div>',
      iconSize: [20, 20]
    })
  }).addTo(mapInstance.value)
  
  L.marker([endPoint.latitude, endPoint.longitude], {
    icon: L.divIcon({
      className: 'end-marker',
      html: '<div style="background: #f56c6c; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px;">终</div>',
      iconSize: [20, 20]
    })
  }).addTo(mapInstance.value)
  
  // 添加中间点标记
  tracks.value.forEach((track, index) => {
    if (index > 0 && index < tracks.value.length - 1) {
      L.marker([track.latitude, track.longitude], {
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
  if (mapInstance.value && tracks.value.length > 0) {
    const bounds = L.latLngBounds(tracks.value.map(track => [track.latitude, track.longitude]))
    mapInstance.value.fitBounds(bounds, { padding: [20, 20] })
  }
}

const playTrajectory = () => {
  if (tracks.value.length === 0) return
  
  isPlaying.value = true
  let currentIndex = 0
  
  playbackTimer.value = setInterval(() => {
    if (currentIndex < tracks.value.length) {
      const track = tracks.value[currentIndex]
      
      // 移动地图中心到当前点
      mapInstance.value.setView([track.latitude, track.longitude], 16)
      
      // 添加当前位置标记
      L.marker([track.latitude, track.longitude], {
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
  if (playbackTimer.value) {
    clearInterval(playbackTimer.value)
    playbackTimer.value = null
  }
}

const refreshTracks = async () => {
  if (vehicleInfo.value) {
    await loadTracks()
    ElMessage.success('轨迹已刷新')
  } else {
    ElMessage.info('请先选择车辆')
  }
}

const exportTrajectory = () => {
  if (vehicleInfo.value && tracks.value.length > 0) {
    // 导出轨迹数据为CSV
    const csvContent = [
      ['时间', '纬度', '经度', '速度(km/h)', '方向(度)', '置信度'],
      ...tracks.value.map(track => [
        formatTime(track.detectedAt),
        track.latitude,
        track.longitude,
        track.speed || 0,
        track.direction || 0,
        Math.round((track.confidence || 0) * 100)
      ])
    ].map(row => row.join(',')).join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `轨迹数据_${vehicleInfo.value.plateNumber}_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('轨迹数据已导出')
  } else {
    ElMessage.info('没有可导出的轨迹数据')
  }
}

const goToTrack = (index: number) => {
  if (mapInstance.value && tracks.value[index]) {
    const track = tracks.value[index]
    mapInstance.value.setView([track.latitude, track.longitude], 16)
    
    // 添加高亮标记
    L.marker([track.latitude, track.longitude], {
      icon: L.divIcon({
        className: 'highlight-marker',
        html: '<div style="background: #e6a23c; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; border: 2px solid #fff;">●</div>',
        iconSize: [24, 24]
      })
    }).addTo(mapInstance.value)
    
    ElMessage.success(`已定位到第 ${index + 1} 个轨迹点`)
  }
}

const viewImage = (track: any) => {
  if (track.imageUrl) {
    selectedImage.value = track
    showImageDialog.value = true
  } else {
    ElMessage.info('该轨迹点没有图片')
  }
}

const goBack = () => {
  router.push('/vehicles')
}

// 车辆选择相关方法
const loadVehicleList = async () => {
  try {
    vehicleListLoading.value = true
    const response = await vehicleStore.fetchVehicles({ page: 1, per_page: 50 })
    vehicleList.value = response.vehicles || []
  } catch (error) {
    console.error('加载车辆列表失败:', error)
    ElMessage.error('加载车辆列表失败')
  } finally {
    vehicleListLoading.value = false
  }
}

const selectVehicle = async () => {
  if (!selectedVehicleId.value) {
    ElMessage.warning('请选择车辆')
    return
  }
  
  try {
    // 更新URL参数
    await router.push({
      path: '/vehicles/tracking',
      query: {
        vehicleId: selectedVehicleId.value,
        plateNumber: vehicleList.value.find(v => v.id === selectedVehicleId.value)?.plateNumber || ''
      }
    })
    
    // 重新加载页面数据
    showVehicleSelector.value = false
    await loadVehicleInfo()
    
    // 确保地图初始化
    await nextTick()
    setTimeout(async () => {
      await initMap()
      
      // 延迟加载轨迹
      setTimeout(async () => {
        await loadTracks()
      }, 200)
    }, 100)
  } catch (error) {
    console.error('选择车辆失败:', error)
    ElMessage.error('选择车辆失败')
  }
}

onMounted(async () => {
  // 立即检查参数
  const vehicleId = route.query.vehicleId as string
  const plateNumber = route.query.plateNumber as string
  
  if (!vehicleId && !plateNumber) {
    // 没有车辆参数，显示车辆选择界面
    showVehicleSelector.value = true
    await loadVehicleList()
    return
  }
  
  await loadVehicleInfo()
  
  // 初始化地图 - 确保在DOM更新后
  await nextTick()
  setTimeout(async () => {
    await initMap()
    
    // 延迟加载轨迹，确保地图和vehicleInfo都已准备好
    setTimeout(async () => {
      await loadTracks()
    }, 200)
  }, 100)
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

.tracking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tracking-header h1 {
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.tracking-content {
  max-width: 1400px;
}

.info-controls-row {
  margin-bottom: 20px;
}

.vehicle-info-card,
.tracking-controls,
.map-card,
.info-card,
.points-card {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.info-controls-row .vehicle-info-card,
.info-controls-row .tracking-controls {
  margin-bottom: 0;
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

.info-item {
  display: flex;
  margin-bottom: 10px;
}

.info-item label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 80px;
}

.no-vehicle {
  text-align: center;
  padding: 40px 0;
}


.image-preview {
  text-align: center;
}

.image-info {
  margin-top: 15px;
  text-align: left;
}

.image-info p {
  margin: 5px 0;
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