<template>
  <div class="vehicle-detail-panel">
    <div class="vehicle-header">
      <h3>{{ vehicle.plateNumber || '未知车牌' }}</h3>
      <el-tag :type="getVehicleTypeTag(vehicle.type)" size="small">
        {{ getVehicleTypeText(vehicle.type) }}
      </el-tag>
    </div>
    
    <div class="vehicle-image" v-if="vehicle.imageUrl">
      <img :src="vehicle.imageUrl" :alt="vehicle.plateNumber" />
    </div>
    
    <div class="vehicle-info">
      <el-descriptions :column="1" size="small">
        <el-descriptions-item label="车牌号">
          {{ vehicle.plateNumber || '未知' }}
        </el-descriptions-item>
        <el-descriptions-item label="车辆类型">
          {{ getVehicleTypeText(vehicle.type) }}
        </el-descriptions-item>
        <el-descriptions-item label="颜色">
          {{ vehicle.color }}
        </el-descriptions-item>
        <el-descriptions-item label="品牌" v-if="vehicle.brand">
          {{ vehicle.brand }}
        </el-descriptions-item>
        <el-descriptions-item label="型号" v-if="vehicle.model">
          {{ vehicle.model }}
        </el-descriptions-item>
        <el-descriptions-item label="置信度">
          {{ (vehicle.confidence * 100).toFixed(1) }}%
        </el-descriptions-item>
        <el-descriptions-item label="检测时间">
          {{ formatTime(vehicle.timestamp) }}
        </el-descriptions-item>
        <el-descriptions-item label="摄像头">
          {{ vehicle.cameraId }}
        </el-descriptions-item>
        <el-descriptions-item label="位置">
          {{ vehicle.position.lat.toFixed(6) }}, {{ vehicle.position.lng.toFixed(6) }}
        </el-descriptions-item>
        <el-descriptions-item label="速度" v-if="vehicle.speed">
          {{ vehicle.speed }} km/h
        </el-descriptions-item>
        <el-descriptions-item label="方向" v-if="vehicle.direction">
          {{ vehicle.direction }}°
        </el-descriptions-item>
      </el-descriptions>
    </div>
    
    <div class="vehicle-actions">
      <el-button type="primary" size="small" @click="viewTrajectory">
        查看轨迹
      </el-button>
      <el-button size="small" @click="viewReID">
        查看ReID
      </el-button>
      <el-button size="small" @click="markSuspicious">
        标记可疑
      </el-button>
    </div>
    
    <div class="vehicle-reid" v-if="reidData.length > 0">
      <h4>ReID信息</h4>
      <div class="reid-list">
        <div 
          v-for="reid in reidData" 
          :key="reid.id"
          class="reid-item"
        >
          <div class="reid-content">
            <div class="reid-similarity">
              相似度: {{ (reid.similarity * 100).toFixed(1) }}%
            </div>
            <div class="reid-time">{{ formatTime(reid.timestamp) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useVehicleStore } from '@/stores/vehicle'
import { dateUtils } from '@/utils/dateUtils'
import type { Vehicle } from '@/types'

interface Props {
  vehicle: Vehicle
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const vehicleStore = useVehicleStore()

const reidData = computed(() => {
  return vehicleStore.getVehicleReIDs(props.vehicle.id)
})

const getVehicleTypeText = (type: string) => {
  switch (type) {
    case 'car': return '轿车'
    case 'truck': return '卡车'
    case 'bus': return '公交车'
    case 'motorcycle': return '摩托车'
    default: return '未知'
  }
}

const getVehicleTypeTag = (type: string) => {
  switch (type) {
    case 'car': return 'primary'
    case 'truck': return 'warning'
    case 'bus': return 'success'
    case 'motorcycle': return 'danger'
    default: return 'info'
  }
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatTime(timestamp)
}

const viewTrajectory = () => {
  console.log('查看车辆轨迹:', props.vehicle.id)
}

const viewReID = () => {
  console.log('查看ReID信息:', props.vehicle.id)
}

const markSuspicious = () => {
  console.log('标记为可疑车辆:', props.vehicle.id)
}
</script>

<style scoped>
.vehicle-detail-panel {
  padding: 20px;
}

.vehicle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.vehicle-header h3 {
  margin: 0;
  color: var(--text-color);
}

.vehicle-image {
  margin-bottom: 20px;
  text-align: center;
}

.vehicle-image img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.vehicle-info {
  margin-bottom: 20px;
}

.vehicle-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.vehicle-actions .el-button {
  flex: 1;
}

.vehicle-reid h4 {
  color: var(--text-color);
  margin-bottom: 12px;
  font-size: 14px;
}

.reid-list {
  max-height: 200px;
  overflow-y: auto;
}

.reid-item {
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.reid-item:last-child {
  border-bottom: none;
}

.reid-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reid-similarity {
  color: var(--text-color);
  font-size: 12px;
}

.reid-time {
  color: var(--text-color-light);
  font-size: 11px;
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
