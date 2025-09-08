<template>
  <div class="map-view">
    <LayoutHeader />
    <div class="map-view-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="map-header">
          <h1>地图监控</h1>
          <div class="map-controls">
            <el-button-group>
              <el-button @click="fitCameraBounds" size="small">
                <el-icon><FullScreen /></el-icon>
                适应摄像头
              </el-button>
              <el-button @click="toggleTrafficLayer" size="small" :type="showTraffic ? 'primary' : 'default'">
                <el-icon><Location /></el-icon>
                交通状况
              </el-button>
              <el-button @click="toggleVehicleTracking" size="small" :type="isTracking ? 'primary' : 'default'">
                <el-icon><Location /></el-icon>
                车辆追踪
              </el-button>
            </el-button-group>
          </div>
        </div>
        
        <div class="map-container-wrapper">
          <MapContainer 
            :height="'calc(100vh - 140px)'"
            :show-controls="true"
            :show-legend="true"
            @camera-click="handleCameraClick"
            @vehicle-click="handleVehicleClick"
          />
        </div>
        
        <!-- 摄像头详情面板 -->
        <el-drawer
          v-model="showCameraPanel"
          title="摄像头详情"
          direction="rtl"
          size="400px"
        >
          <CameraDetailPanel 
            v-if="selectedCamera"
            :camera="selectedCamera"
            @close="showCameraPanel = false"
          />
        </el-drawer>
        
        <!-- 车辆详情面板 -->
        <el-drawer
          v-model="showVehiclePanel"
          title="车辆详情"
          direction="rtl"
          size="400px"
        >
          <VehicleDetailPanel 
            v-if="selectedVehicle"
            :vehicle="selectedVehicle"
            @close="showVehiclePanel = false"
          />
        </el-drawer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { FullScreen, Location } from '@element-plus/icons-vue'
import { useMapStore } from '@/stores/map'
import { useCameraStore } from '@/stores/camera'
import { useVehicleStore } from '@/stores/vehicle'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import MapContainer from '@/components/Map/MapContainer.vue'
import CameraDetailPanel from '@/components/Camera/CameraDetailPanel.vue'
import VehicleDetailPanel from '@/components/Vehicle/VehicleDetailPanel.vue'
import type { CameraPosition } from '@/types'

const mapStore = useMapStore()
const cameraStore = useCameraStore()
const vehicleStore = useVehicleStore()

const showTraffic = ref(false)
const showCameraPanel = ref(false)
const showVehiclePanel = ref(false)

const selectedCamera = computed(() => mapStore.selectedCamera)
const selectedVehicle = computed(() => vehicleStore.selectedVehicle)
const isTracking = computed(() => vehicleStore.isTracking)

const fitCameraBounds = () => {
  mapStore.fitCameraBounds()
}

const toggleTrafficLayer = () => {
  showTraffic.value = !showTraffic.value
  // 这里可以添加交通状况图层的显示/隐藏逻辑
}

const toggleVehicleTracking = () => {
  if (vehicleStore.isTracking) {
    vehicleStore.stopTracking()
  } else {
    vehicleStore.startTracking()
  }
}

const handleCameraClick = (camera: CameraPosition) => {
  showCameraPanel.value = true
}

const handleVehicleClick = (vehicle: any) => {
  showVehiclePanel.value = true
}

// 页面初始化
onMounted(() => {
  // 加载摄像头数据
  cameraStore.loadCamerasFromStorage()
})
</script>

<style scoped>
.map-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.map-view-content {
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

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.map-header h1 {
  color: var(--text-color);
  margin: 0;
}

.map-controls {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.map-container-wrapper {
  height: calc(100vh - 140px);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}
</style>
