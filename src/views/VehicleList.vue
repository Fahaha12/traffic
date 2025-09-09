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
                
                <el-form-item label="风险等级">
                  <el-select v-model="filters.riskLevel" placeholder="全部等级" clearable>
                    <el-option label="低风险" value="low" />
                    <el-option label="中风险" value="medium" />
                    <el-option label="高风险" value="high" />
                    <el-option label="严重" value="critical" />
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
                :loading="loading"
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
                
                <el-table-column prop="isSuspicious" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.isSuspicious ? 'warning' : 'success'" size="small">
                      {{ row.isSuspicious ? '可疑' : '正常' }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column prop="riskLevel" label="风险等级" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getRiskLevelType(row.riskLevel)" size="small">
                      {{ getRiskLevelText(row.riskLevel) }}
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
                
                <el-table-column label="操作" width="250" fixed="right">
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
                      :class="{ 'danger': row.isSuspicious }"
                    >
                      {{ row.isSuspicious ? '取消标记' : '标记可疑' }}
                    </el-button>
                    <el-button 
                      type="text" 
                      size="small" 
                      @click.stop="deleteVehicle(row)"
                      class="danger"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 分页 -->
              <div class="pagination-wrapper">
                <el-pagination
                  v-model:current-page="pagination.page"
                  v-model:page-size="pagination.pageSize"
                  :page-sizes="[10, 20, 50, 100]"
                  :total="pagination.total"
                  layout="total, sizes, prev, pager, next, jumper"
                  @size-change="handleSizeChange"
                  @current-change="handlePageChange"
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
import { useVehicleStore } from '@/stores/vehicle'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const vehicleStore = useVehicleStore()

// 响应式数据
const vehicles = ref([])
const loading = ref(false)
const pagination = ref({
  total: 0,
  page: 1,
  pageSize: 20,
  pages: 0
})

const filters = reactive({
  plateNumber: '',
  vehicleType: '',
  status: '',
  riskLevel: '',
  dateRange: null as any
})

const showDetailDialog = ref(false)
const selectedVehicle = ref<any>(null)

// 计算属性
const totalVehicles = computed(() => pagination.value.total)

const filteredVehicles = computed(() => {
  return vehicles.value
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

const getVehicleTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    car: 'primary',
    truck: 'warning',
    motorcycle: 'info',
    bus: 'success',
    bicycle: 'info',
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

const getRiskLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    low: '低风险',
    medium: '中风险',
    high: '高风险',
    critical: '严重'
  }
  return levelMap[level] || level
}

const getRiskLevelType = (level: string) => {
  const typeMap: Record<string, string> = {
    low: 'success',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return typeMap[level] || 'info'
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatDateTime(timestamp)
}

const loadVehicles = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.value.page,
      per_page: pagination.value.pageSize,
      search: filters.plateNumber,
      type: filters.vehicleType,
      is_suspicious: filters.status === 'suspicious' ? 'true' : filters.status === 'normal' ? 'false' : undefined,
      risk_level: filters.riskLevel
    }
    
    const response = await vehicleStore.fetchVehicles(params)
    vehicles.value = response.vehicles || []
    pagination.value = {
      total: response.total || 0,
      page: response.page || 1,
      pageSize: response.per_page || 20,
      pages: response.pages || 0
    }
  } catch (error) {
    console.error('加载车辆列表失败:', error)
    ElMessage.error('加载车辆列表失败')
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  pagination.value.page = 1
  loadVehicles()
}

const resetFilters = () => {
  Object.assign(filters, {
    plateNumber: '',
    vehicleType: '',
    status: '',
    riskLevel: '',
    dateRange: null
  })
  pagination.value.page = 1
  loadVehicles()
  ElMessage.success('筛选条件已重置')
}

const refreshVehicles = async () => {
  await loadVehicles()
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

const toggleSuspicious = async (vehicle: any) => {
  try {
    if (vehicle.isSuspicious) {
      await vehicleStore.markVehicleSuspicious(vehicle.id, {
        isSuspicious: false,
        riskLevel: 'low'
      })
      ElMessage.success('已取消可疑标记')
    } else {
      await vehicleStore.markVehicleSuspicious(vehicle.id, {
        isSuspicious: true,
        riskLevel: 'medium'
      })
      ElMessage.success('已标记为可疑车辆')
    }
    await loadVehicles()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

const deleteVehicle = async (vehicle: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除车辆 ${vehicle.plateNumber} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await vehicleStore.deleteVehicle(vehicle.id)
    ElMessage.success('车辆删除成功')
    await loadVehicles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除车辆失败:', error)
      ElMessage.error('删除车辆失败')
    }
  }
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  loadVehicles()
}

const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadVehicles()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

onMounted(() => {
  loadVehicles()
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
