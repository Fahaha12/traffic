<template>
  <div class="vehicle-list-view">
    <LayoutHeader />
    <div class="vehicle-list-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="vehicle-list-header">
          <h1>车辆列表</h1>
          <div class="header-actions">
            <el-button type="primary" @click="refreshVehicles">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="exportVehicles">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>
        
        <div class="vehicle-list-content-wrapper">
          <!-- 车辆筛选 -->
          <div class="vehicle-filters">
            <el-card>
              <el-form :model="filters" inline>
                <el-form-item label="车牌号">
                  <el-input v-model="filters.plateNumber" placeholder="请输入车牌号" clearable />
                </el-form-item>
                
                <el-form-item label="车辆类型">
                  <el-select v-model="filters.vehicleType" placeholder="全部类型" clearable>
                    <el-option label="小型汽车" value="car" />
                    <el-option label="大型汽车" value="truck" />
                    <el-option label="摩托车" value="motorcycle" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="状态">
                  <el-select v-model="filters.status" placeholder="全部状态" clearable>
                    <el-option label="正常" value="normal" />
                    <el-option label="可疑" value="suspicious" />
                    <el-option label="黑名单" value="blacklist" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="filters.dateRange"
                    type="datetimerange"
                    range-separator="至"
                    start-placeholder="开始时间"
                    end-placeholder="结束时间"
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DD HH:mm:ss"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="applyFilters">筛选</el-button>
                  <el-button @click="resetFilters">重置</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
          
          <!-- 车辆列表 -->
          <div class="vehicle-list">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>车辆列表 ({{ totalVehicles }} 辆)</span>
                </div>
              </template>
              
              <el-table 
                :data="filteredVehicles" 
                style="width: 100%"
                @row-click="handleVehicleClick"
              >
                <el-table-column prop="plateNumber" label="车牌号" width="120" />
                
                <el-table-column prop="vehicleType" label="车辆类型" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getVehicleTypeTagType(row.vehicleType)" size="small">
                      {{ getVehicleTypeText(row.vehicleType) }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column prop="color" label="颜色" width="80" />
                
                <el-table-column prop="brand" label="品牌" width="100" />
                
                <el-table-column prop="model" label="型号" width="120" />
                
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getStatusTagType(row.status)" size="small">
                      {{ getStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column prop="lastSeen" label="最后出现" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.lastSeen) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="location" label="最后位置" min-width="200" show-overflow-tooltip />
                
                <el-table-column prop="detectionCount" label="检测次数" width="100" />
                
                <el-table-column label="操作" width="200" fixed="right">
                  <template #default="{ row }">
                    <el-button type="text" size="small" @click.stop="viewTrajectory(row)">
                      轨迹
                    </el-button>
                    <el-button type="text" size="small" @click.stop="viewDetails(row)">
                      详情
                    </el-button>
                    <el-button 
                      type="text" 
                      size="small" 
                      @click.stop="toggleSuspicious(row)"
                      :class="{ 'danger': row.status === 'suspicious' }"
                    >
                      {{ row.status === 'suspicious' ? '取消标记' : '标记可疑' }}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 分页 -->
              <div class="pagination-wrapper">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[10, 20, 50, 100]"
                  :total="totalVehicles"
                  layout="total, sizes, prev, pager, next, jumper"
                  @size-change="handleSizeChange"
                  @current-change="handleCurrentChange"
                />
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 车辆详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`车辆详情 - ${selectedVehicle?.plateNumber}`"
      width="800px"
    >
      <div v-if="selectedVehicle" class="vehicle-detail">
        <el-descriptions :column="2" border>
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
          <el-descriptions-item label="品牌">
            {{ selectedVehicle.brand }}
          </el-descriptions-item>
          <el-descriptions-item label="型号">
            {{ selectedVehicle.model }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedVehicle.status)" size="small">
              {{ getStatusText(selectedVehicle.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最后出现时间">
            {{ formatTime(selectedVehicle.lastSeen) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后位置">
            {{ selectedVehicle.location }}
          </el-descriptions-item>
          <el-descriptions-item label="检测次数">
            {{ selectedVehicle.detectionCount }}
          </el-descriptions-item>
          <el-descriptions-item label="首次检测">
            {{ formatTime(selectedVehicle.firstSeen) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="vehicle-images" v-if="selectedVehicle.images && selectedVehicle.images.length > 0">
          <h4>车辆图片</h4>
          <div class="image-grid">
            <div v-for="image in selectedVehicle.images" :key="image.id" class="image-item">
              <el-image
                :src="image.url"
                :preview-src-list="selectedVehicle.images.map(img => img.url)"
                fit="cover"
                style="width: 100px; height: 100px"
              />
              <div class="image-info">
                <span>{{ formatTime(image.timestamp) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="viewTrajectory(selectedVehicle)">
          查看轨迹
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const vehicles = ref([
  {
    id: '1',
    plateNumber: '豫A12345',
    vehicleType: 'car',
    color: '白色',
    brand: '大众',
    model: '朗逸',
    status: 'normal',
    lastSeen: new Date().toISOString(),
    location: '郑州市中原路与建设路交叉口',
    detectionCount: 15,
    firstSeen: new Date(Date.now() - 86400000).toISOString(),
    images: [
      {
        id: '1',
        url: 'https://via.placeholder.com/300x200?text=Vehicle+Image',
        timestamp: new Date().toISOString()
      }
    ]
  },
  {
    id: '2',
    plateNumber: '豫B67890',
    vehicleType: 'truck',
    color: '蓝色',
    brand: '解放',
    model: 'J6P',
    status: 'suspicious',
    lastSeen: new Date(Date.now() - 1800000).toISOString(),
    location: '郑州市金水区花园路',
    detectionCount: 8,
    firstSeen: new Date(Date.now() - 172800000).toISOString(),
    images: []
  },
  {
    id: '3',
    plateNumber: '豫C11111',
    vehicleType: 'car',
    color: '黑色',
    brand: '奔驰',
    model: 'E300L',
    status: 'blacklist',
    lastSeen: new Date(Date.now() - 3600000).toISOString(),
    location: '郑州市二七区大学路',
    detectionCount: 3,
    firstSeen: new Date(Date.now() - 259200000).toISOString(),
    images: []
  }
])

const filters = reactive({
  plateNumber: '',
  vehicleType: '',
  status: '',
  dateRange: null as any
})

const currentPage = ref(1)
const pageSize = ref(20)
const showDetailDialog = ref(false)
const selectedVehicle = ref<any>(null)

// 计算属性
const totalVehicles = computed(() => filteredVehicles.value.length)

const filteredVehicles = computed(() => {
  let result = vehicles.value
  
  if (filters.plateNumber) {
    result = result.filter(vehicle => 
      vehicle.plateNumber.toLowerCase().includes(filters.plateNumber.toLowerCase())
    )
  }
  
  if (filters.vehicleType) {
    result = result.filter(vehicle => vehicle.vehicleType === filters.vehicleType)
  }
  
  if (filters.status) {
    result = result.filter(vehicle => vehicle.status === filters.status)
  }
  
  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    result = result.filter(vehicle => {
      const vehicleTime = new Date(vehicle.lastSeen)
      return vehicleTime >= new Date(start) && vehicleTime <= new Date(end)
    })
  }
  
  return result
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

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    normal: '正常',
    suspicious: '可疑',
    blacklist: '黑名单'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    normal: 'success',
    suspicious: 'warning',
    blacklist: 'danger'
  }
  return typeMap[status] || 'info'
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatDateTime(timestamp)
}

const applyFilters = () => {
  currentPage.value = 1
  ElMessage.success('筛选条件已应用')
}

const resetFilters = () => {
  Object.assign(filters, {
    plateNumber: '',
    vehicleType: '',
    status: '',
    dateRange: null
  })
  currentPage.value = 1
  ElMessage.success('筛选条件已重置')
}

const refreshVehicles = () => {
  ElMessage.success('车辆列表已刷新')
}

const exportVehicles = () => {
  ElMessage.info('导出功能开发中...')
}

const handleVehicleClick = (row: any) => {
  selectedVehicle.value = row
  showDetailDialog.value = true
}

const viewDetails = (vehicle: any) => {
  selectedVehicle.value = vehicle
  showDetailDialog.value = true
}

const viewTrajectory = (vehicle: any) => {
  if (vehicle) {
    router.push(`/vehicles/tracking?plateNumber=${vehicle.plateNumber}`)
  }
}

const toggleSuspicious = (vehicle: any) => {
  if (vehicle.status === 'suspicious') {
    vehicle.status = 'normal'
    ElMessage.success('已取消可疑标记')
  } else {
    vehicle.status = 'suspicious'
    ElMessage.success('已标记为可疑车辆')
  }
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.vehicle-list-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.vehicle-list-content {
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

.vehicle-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.vehicle-list-header h1 {
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.vehicle-list-content-wrapper {
  max-width: 1400px;
}

.vehicle-filters {
  margin-bottom: 20px;
}

.vehicle-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vehicle-detail {
  padding: 10px 0;
}

.vehicle-images {
  margin-top: 20px;
}

.vehicle-images h4 {
  color: var(--text-color);
  margin-bottom: 10px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}

.image-item {
  text-align: center;
}

.image-info {
  margin-top: 5px;
  font-size: 12px;
  color: var(--text-color-light);
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.danger {
  color: var(--danger-color);
}

:deep(.el-table th),
:deep(.el-table td) {
  background: var(--bg-color-light);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-table__header-wrapper) {
  background: var(--bg-color-light);
}

:deep(.el-card) {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
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
</style>
