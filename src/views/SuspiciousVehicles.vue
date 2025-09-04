<template>
  <div class="suspicious-vehicles-view">
    <LayoutHeader />
    <div class="suspicious-vehicles-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="suspicious-vehicles-header">
          <h1>可疑车辆</h1>
          <div class="header-actions">
            <el-button type="primary" @click="refreshSuspiciousVehicles">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="exportSuspiciousVehicles">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>
        
        <div class="suspicious-vehicles-content-wrapper">
          <!-- 可疑车辆统计 -->
          <div class="suspicious-stats">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon high-risk">
                      <el-icon><Warning /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ highRiskCount }}</div>
                      <div class="stat-label">高风险</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon medium-risk">
                      <el-icon><InfoFilled /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ mediumRiskCount }}</div>
                      <div class="stat-label">中风险</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon low-risk">
                      <el-icon><Check /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ lowRiskCount }}</div>
                      <div class="stat-label">低风险</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon total">
                      <el-icon><Truck /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ totalSuspiciousCount }}</div>
                      <div class="stat-label">总计</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
          
          <!-- 可疑车辆筛选 -->
          <div class="suspicious-filters">
            <el-card>
              <el-form :model="filters" inline>
                <el-form-item label="车牌号">
                  <el-input v-model="filters.plateNumber" placeholder="请输入车牌号" clearable />
                </el-form-item>
                
                <el-form-item label="风险等级">
                  <el-select v-model="filters.riskLevel" placeholder="全部等级" clearable>
                    <el-option label="高风险" value="high" />
                    <el-option label="中风险" value="medium" />
                    <el-option label="低风险" value="low" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="可疑类型">
                  <el-select v-model="filters.suspiciousType" placeholder="全部类型" clearable>
                    <el-option label="长时间停留" value="long_stay" />
                    <el-option label="异常轨迹" value="abnormal_trajectory" />
                    <el-option label="频繁出现" value="frequent_appearance" />
                    <el-option label="黑名单车辆" value="blacklist" />
                    <el-option label="无牌车辆" value="no_plate" />
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
          
          <!-- 可疑车辆列表 -->
          <div class="suspicious-list">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>可疑车辆列表</span>
                </div>
              </template>
              
              <el-table 
                :data="filteredSuspiciousVehicles" 
                style="width: 100%"
                @row-click="handleVehicleClick"
              >
                <el-table-column width="50">
                  <template #default="{ row }">
                    <el-icon 
                      :class="getRiskIconClass(row.riskLevel)"
                      :style="{ color: getRiskColor(row.riskLevel) }"
                    >
                      <Warning v-if="row.riskLevel === 'high'" />
                      <InfoFilled v-else-if="row.riskLevel === 'medium'" />
                      <Check v-else />
                    </el-icon>
                  </template>
                </el-table-column>
                
                <el-table-column prop="plateNumber" label="车牌号" width="120" />
                
                <el-table-column prop="vehicleType" label="车辆类型" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getVehicleTypeTagType(row.vehicleType)" size="small">
                      {{ getVehicleTypeText(row.vehicleType) }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column prop="color" label="颜色" width="80" />
                
                <el-table-column prop="riskLevel" label="风险等级" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getRiskTagType(row.riskLevel)" size="small">
                      {{ getRiskText(row.riskLevel) }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column prop="suspiciousType" label="可疑类型" width="120">
                  <template #default="{ row }">
                    {{ getSuspiciousTypeText(row.suspiciousType) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
                
                <el-table-column prop="firstDetected" label="首次检测" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.firstDetected) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="lastDetected" label="最后检测" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.lastDetected) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="detectionCount" label="检测次数" width="100" />
                
                <el-table-column prop="location" label="最后位置" min-width="200" show-overflow-tooltip />
                
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
                      @click.stop="handleSuspicious(row)"
                      :class="{ 'danger': row.status === 'handled' }"
                    >
                      {{ row.status === 'handled' ? '已处理' : '处理' }}
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
                  :total="totalSuspiciousVehicles"
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
    
    <!-- 可疑车辆详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`可疑车辆详情 - ${selectedVehicle?.plateNumber}`"
      width="800px"
    >
      <div v-if="selectedVehicle" class="suspicious-detail">
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
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskTagType(selectedVehicle.riskLevel)" size="small">
              {{ getRiskText(selectedVehicle.riskLevel) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="可疑类型">
            {{ getSuspiciousTypeText(selectedVehicle.suspiciousType) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedVehicle.status)" size="small">
              {{ getStatusText(selectedVehicle.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="首次检测时间">
            {{ formatTime(selectedVehicle.firstDetected) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后检测时间">
            {{ formatTime(selectedVehicle.lastDetected) }}
          </el-descriptions-item>
          <el-descriptions-item label="检测次数">
            {{ selectedVehicle.detectionCount }}
          </el-descriptions-item>
          <el-descriptions-item label="最后位置">
            {{ selectedVehicle.location }}
          </el-descriptions-item>
          <el-descriptions-item label="详细描述" :span="2">
            {{ selectedVehicle.description }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="suspicious-images" v-if="selectedVehicle.images && selectedVehicle.images.length > 0">
          <h4>相关图片</h4>
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
        <el-button 
          type="success" 
          @click="handleSuspicious(selectedVehicle)"
          v-if="selectedVehicle && selectedVehicle.status !== 'handled'"
        >
          标记处理
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
const suspiciousVehicles = ref([
  {
    id: '1',
    plateNumber: '豫B67890',
    vehicleType: 'truck',
    color: '蓝色',
    brand: '解放',
    model: 'J6P',
    riskLevel: 'high',
    suspiciousType: 'long_stay',
    description: '该车辆在监控区域内停留超过2小时，行为异常',
    firstDetected: new Date(Date.now() - 7200000).toISOString(),
    lastDetected: new Date(Date.now() - 1800000).toISOString(),
    detectionCount: 8,
    location: '郑州市金水区花园路',
    status: 'pending',
    images: [
      {
        id: '1',
        url: 'https://via.placeholder.com/300x200?text=Suspicious+Vehicle',
        timestamp: new Date(Date.now() - 1800000).toISOString()
      }
    ]
  },
  {
    id: '2',
    plateNumber: '豫C11111',
    vehicleType: 'car',
    color: '黑色',
    brand: '奔驰',
    model: 'E300L',
    riskLevel: 'high',
    suspiciousType: 'blacklist',
    description: '该车辆在黑名单中，需要重点关注',
    firstDetected: new Date(Date.now() - 86400000).toISOString(),
    lastDetected: new Date(Date.now() - 3600000).toISOString(),
    detectionCount: 3,
    location: '郑州市二七区大学路',
    status: 'handled',
    images: []
  },
  {
    id: '3',
    plateNumber: '无牌车辆',
    vehicleType: 'car',
    color: '白色',
    brand: '未知',
    model: '未知',
    riskLevel: 'medium',
    suspiciousType: 'no_plate',
    description: '检测到无牌车辆，可能存在违法行为',
    firstDetected: new Date(Date.now() - 43200000).toISOString(),
    lastDetected: new Date(Date.now() - 7200000).toISOString(),
    detectionCount: 5,
    location: '郑州市管城区商城路',
    status: 'pending',
    images: []
  },
  {
    id: '4',
    plateNumber: '豫D22222',
    vehicleType: 'car',
    color: '红色',
    brand: '丰田',
    model: '凯美瑞',
    riskLevel: 'low',
    suspiciousType: 'frequent_appearance',
    description: '该车辆在短时间内频繁出现在同一区域',
    firstDetected: new Date(Date.now() - 172800000).toISOString(),
    lastDetected: new Date(Date.now() - 10800000).toISOString(),
    detectionCount: 12,
    location: '郑州市中原区建设路',
    status: 'pending',
    images: []
  }
])

const filters = reactive({
  plateNumber: '',
  riskLevel: '',
  suspiciousType: '',
  dateRange: null as any
})

const currentPage = ref(1)
const pageSize = ref(20)
const showDetailDialog = ref(false)
const selectedVehicle = ref<any>(null)

// 计算属性
const highRiskCount = computed(() => 
  suspiciousVehicles.value.filter(vehicle => vehicle.riskLevel === 'high').length
)

const mediumRiskCount = computed(() => 
  suspiciousVehicles.value.filter(vehicle => vehicle.riskLevel === 'medium').length
)

const lowRiskCount = computed(() => 
  suspiciousVehicles.value.filter(vehicle => vehicle.riskLevel === 'low').length
)

const totalSuspiciousCount = computed(() => suspiciousVehicles.value.length)

const totalSuspiciousVehicles = computed(() => filteredSuspiciousVehicles.value.length)

const filteredSuspiciousVehicles = computed(() => {
  let result = suspiciousVehicles.value
  
  if (filters.plateNumber) {
    result = result.filter(vehicle => 
      vehicle.plateNumber.toLowerCase().includes(filters.plateNumber.toLowerCase())
    )
  }
  
  if (filters.riskLevel) {
    result = result.filter(vehicle => vehicle.riskLevel === filters.riskLevel)
  }
  
  if (filters.suspiciousType) {
    result = result.filter(vehicle => vehicle.suspiciousType === filters.suspiciousType)
  }
  
  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    result = result.filter(vehicle => {
      const vehicleTime = new Date(vehicle.lastDetected)
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

const getRiskText = (level: string) => {
  const levelMap: Record<string, string> = {
    high: '高风险',
    medium: '中风险',
    low: '低风险'
  }
  return levelMap[level] || level
}

const getRiskTagType = (level: string) => {
  const typeMap: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return typeMap[level] || 'info'
}

const getRiskColor = (level: string) => {
  const colorMap: Record<string, string> = {
    high: '#f56c6c',
    medium: '#e6a23c',
    low: '#67c23a'
  }
  return colorMap[level] || '#909399'
}

const getRiskIconClass = (level: string) => {
  return `risk-icon risk-icon-${level}`
}

const getSuspiciousTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    long_stay: '长时间停留',
    abnormal_trajectory: '异常轨迹',
    frequent_appearance: '频繁出现',
    blacklist: '黑名单车辆',
    no_plate: '无牌车辆'
  }
  return typeMap[type] || type
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    handled: '已处理',
    investigating: '调查中'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    handled: 'success',
    investigating: 'info'
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
    riskLevel: '',
    suspiciousType: '',
    dateRange: null
  })
  currentPage.value = 1
  ElMessage.success('筛选条件已重置')
}

const refreshSuspiciousVehicles = () => {
  ElMessage.success('可疑车辆列表已刷新')
}

const exportSuspiciousVehicles = () => {
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

const handleSuspicious = (vehicle: any) => {
  if (vehicle) {
    if (vehicle.status === 'handled') {
      vehicle.status = 'pending'
      ElMessage.success('已取消处理状态')
    } else {
      vehicle.status = 'handled'
      ElMessage.success('已标记为已处理')
    }
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
.suspicious-vehicles-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.suspicious-vehicles-content {
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

.suspicious-vehicles-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.suspicious-vehicles-header h1 {
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.suspicious-vehicles-content-wrapper {
  max-width: 1400px;
}

.suspicious-stats {
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

.stat-icon.high-risk {
  background: var(--danger-color);
}

.stat-icon.medium-risk {
  background: var(--warning-color);
}

.stat-icon.low-risk {
  background: var(--success-color);
}

.stat-icon.total {
  background: var(--primary-color);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-color-light);
  margin-top: 5px;
}

.suspicious-filters {
  margin-bottom: 20px;
}

.suspicious-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suspicious-detail {
  padding: 10px 0;
}

.suspicious-images {
  margin-top: 20px;
}

.suspicious-images h4 {
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
