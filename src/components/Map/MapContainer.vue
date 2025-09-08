<template>
  <div class="map-container" ref="mapContainer">
    <div class="map-controls" v-if="showControls">
      <el-button-group>
        <el-button @click="fitBounds" size="small">
          <el-icon><FullScreen /></el-icon>
          适应范围
        </el-button>
        <el-button @click="resetView" size="small">
          <el-icon><Refresh /></el-icon>
          重置视图
        </el-button>
        <el-button @click="toggleTraffic" size="small" :type="showTraffic ? 'primary' : 'default'">
          <el-icon><Location /></el-icon>
          交通状况
        </el-button>
      </el-button-group>
    </div>
    
    <div class="map-legend" v-if="showLegend">
      <div class="legend-item">
        <div class="legend-color online"></div>
        <span>在线摄像头</span>
      </div>
      <div class="legend-item">
        <div class="legend-color offline"></div>
        <span>离线摄像头</span>
      </div>
      <div class="legend-item">
        <div class="legend-color suspicious"></div>
        <span>可疑车辆</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { FullScreen, Refresh, Location } from '@element-plus/icons-vue'
import L from 'leaflet'
import { useMapStore } from '@/stores/map'
import { useCameraStore } from '@/stores/camera'
import { useVehicleStore } from '@/stores/vehicle'
import type { Camera } from '@/types'

// 删除默认图标
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

interface Props {
  height?: number | string
  showControls?: boolean
  showLegend?: boolean
  center?: [number, number]
  zoom?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: '100%',
  showControls: true,
  showLegend: true,
  center: () => [34.7466, 113.6253], // 郑州市政府坐标
  zoom: 12
})

const emit = defineEmits<{
  mapReady: [map: L.Map]
  cameraClick: [camera: Camera]
  vehicleClick: [vehicle: any]
}>()

const mapContainer = ref<HTMLElement>()
const mapStore = useMapStore()
const cameraStore = useCameraStore()
const vehicleStore = useVehicleStore()

let map: L.Map | null = null
let cameraMarkers: Map<string, L.Marker> = new Map()
let vehicleMarkers: Map<string, L.Marker> = new Map()
let trajectoryLayers: Map<string, L.Polyline> = new Map()
let showTraffic = ref(false)

// 初始化地图
const initMap = async () => {
  if (!mapContainer.value) return

  map = L.map(mapContainer.value, {
    center: props.center,
    zoom: props.zoom,
    zoomControl: true,
    attributionControl: true
  })

  // 添加瓦片图层
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)

  // 设置地图实例到store
  mapStore.setMapInstance(map)

  // 监听地图事件
  map.on('moveend', () => {
    if (map) {
      const bounds = map.getBounds()
      mapStore.updateMapBounds({
        north: bounds.getNorth(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        west: bounds.getWest()
      })
    }
  })

  // 添加摄像头标记
  addCameraMarkers()
  
  // 添加车辆标记
  addVehicleMarkers()

  emit('mapReady', map)
}

// 添加摄像头标记
const addCameraMarkers = () => {
  if (!map) return

  // 清除现有标记
  cameraMarkers.forEach(marker => map!.removeLayer(marker))
  cameraMarkers.clear()

  // 添加新标记
  cameraStore.cameras.forEach(camera => {
    const marker = L.marker([camera.position.lat, camera.position.lng], {
      icon: createCameraIcon(camera.status)
    })

    marker.bindPopup(`
      <div class="camera-popup">
        <h4>${camera.name}</h4>
        <p>状态: ${getStatusText(camera.status)}</p>
        <p>类型: ${getTypeText(camera.type)}</p>
        <button onclick="viewCamera('${camera.id}')">查看详情</button>
      </div>
    `)

    marker.on('click', () => {
      emit('cameraClick', camera)
      mapStore.selectCamera(camera)
    })

    marker.addTo(map)
    cameraMarkers.set(camera.id, marker)
  })
}

// 添加车辆标记
const addVehicleMarkers = () => {
  if (!map) return

  // 清除现有车辆标记
  vehicleMarkers.forEach(marker => map!.removeLayer(marker))
  vehicleMarkers.clear()

  // 添加活跃车辆标记
  vehicleStore.activeVehicles.forEach(vehicle => {
    const marker = L.marker([vehicle.position.lat, vehicle.position.lng], {
      icon: createVehicleIcon(vehicle.type)
    })

    marker.bindPopup(`
      <div class="vehicle-popup">
        <h4>${vehicle.plateNumber || '未知车牌'}</h4>
        <p>类型: ${getVehicleTypeText(vehicle.type)}</p>
        <p>颜色: ${vehicle.color}</p>
        <p>置信度: ${(vehicle.confidence * 100).toFixed(1)}%</p>
      </div>
    `)

    marker.on('click', () => {
      emit('vehicleClick', vehicle)
      vehicleStore.selectVehicle(vehicle)
    })

    marker.addTo(map)
    vehicleMarkers.set(vehicle.id, marker)
  })

  // 添加可疑车辆高亮
  vehicleStore.suspiciousVehicles
    .filter(v => v.isActive)
    .forEach(vehicle => {
      const marker = L.marker([vehicle.location.lat, vehicle.location.lng], {
        icon: createSuspiciousVehicleIcon()
      })

      marker.bindPopup(`
        <div class="suspicious-vehicle-popup">
          <h4>可疑车辆</h4>
          <p>原因: ${vehicle.reason}</p>
          <p>严重程度: ${getSeverityText(vehicle.severity)}</p>
          <p>描述: ${vehicle.description}</p>
        </div>
      `)

      marker.addTo(map)
    })
}

// 创建摄像头图标
const createCameraIcon = (status: string) => {
  const color = status === 'online' ? '#67c23a' : '#f56c6c'
  return L.divIcon({
    className: 'camera-marker',
    html: `<div style="background: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  })
}

// 创建车辆图标
const createVehicleIcon = (type: string) => {
  const colors = {
    car: '#409eff',
    truck: '#e6a23c',
    bus: '#67c23a',
    motorcycle: '#f56c6c',
    unknown: '#909399'
  }
  const color = colors[type as keyof typeof colors] || colors.unknown
  
  return L.divIcon({
    className: 'vehicle-marker',
    html: `<div style="background: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  })
}

// 创建可疑车辆图标
const createSuspiciousVehicleIcon = () => {
  return L.divIcon({
    className: 'suspicious-vehicle-marker',
    html: `<div style="background: #ff6b6b; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; animation: pulse 2s infinite;"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  })
}

// 工具函数
const getStatusText = (status: string) => {
  const statusMap = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中'
  }
  return statusMap[status as keyof typeof statusMap] || '未知'
}

const getTypeText = (type: string) => {
  const typeMap = {
    traffic: '交通监控',
    surveillance: '安防监控',
    speed: '测速监控'
  }
  return typeMap[type as keyof typeof typeMap] || '未知'
}

const getVehicleTypeText = (type: string) => {
  const typeMap = {
    car: '轿车',
    truck: '卡车',
    bus: '公交车',
    motorcycle: '摩托车',
    unknown: '未知'
  }
  return typeMap[type as keyof typeof typeMap] || '未知'
}

const getSeverityText = (severity: string) => {
  const severityMap = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '严重'
  }
  return severityMap[severity as keyof typeof severityMap] || '未知'
}

// 地图控制方法
const fitBounds = () => {
  if (map && cameraStore.cameras.length > 0) {
    const bounds = L.latLngBounds(
      cameraStore.cameras.map(camera => [camera.position.lat, camera.position.lng])
    )
    map.fitBounds(bounds)
  }
}

const resetView = () => {
  if (map) {
    map.setView(props.center, props.zoom)
  }
}

const toggleTraffic = () => {
  showTraffic.value = !showTraffic.value
  // 这里可以添加交通状况图层的显示/隐藏逻辑
}

// 监听数据变化
watch(() => cameraStore.cameras, () => {
  addCameraMarkers()
}, { deep: true })

watch(() => vehicleStore.activeVehicles, () => {
  addVehicleMarkers()
}, { deep: true })

watch(() => vehicleStore.suspiciousVehicles, () => {
  addVehicleMarkers()
}, { deep: true })

// 生命周期
onMounted(() => {
  nextTick(() => {
    initMap()
  })
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
  mapStore.resetMap()
})
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: v-bind(height);
  background: #f0f0f0;
}

.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  background: var(--bg-color);
  color: var(--text-color);
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.map-legend {
  position: absolute;
  bottom: 10px;
  left: 10px;
  z-index: 1000;
  background: var(--bg-color);
  color: var(--text-color);
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
  color: var(--text-color);
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-item span {
  color: var(--text-color);
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
}

.legend-color.online {
  background: #67c23a;
}

.legend-color.offline {
  background: #f56c6c;
}

.legend-color.suspicious {
  background: #ff6b6b;
}

:deep(.camera-marker),
:deep(.vehicle-marker),
:deep(.suspicious-vehicle-marker) {
  background: transparent !important;
  border: none !important;
}

:deep(.leaflet-popup-content) {
  margin: 8px 12px;
  line-height: 1.4;
}

:deep(.leaflet-popup-content h4) {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
}

:deep(.leaflet-popup-content p) {
  margin: 4px 0;
  font-size: 12px;
}

:deep(.leaflet-popup-content button) {
  margin-top: 8px;
  padding: 4px 8px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

:deep(.leaflet-popup-content button:hover) {
  background: #337ecc;
}
</style>
