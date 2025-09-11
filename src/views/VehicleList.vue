<template>
  <div class="vehicle-list-view">
    <LayoutHeader />
    <div class="vehicle-list-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="vehicle-list-header">
          <h1>车辆列表</h1>
          <div class="header-actions">
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              添加车辆
            </el-button>
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
                  <div class="batch-actions" v-if="selectedVehicles.length > 0">
                    <span class="selected-count">已选择 {{ selectedVehicles.length }} 项</span>
                    <el-button size="small" @click="batchMarkSuspicious">
                      批量标记可疑
                    </el-button>
                    <el-button size="small" @click="batchCancelSuspicious">
                      批量取消标记
                    </el-button>
                    <el-button size="small" type="danger" @click="batchDelete">
                      批量删除
                    </el-button>
                  </div>
                </div>
              </template>
              
              <el-table 
                :data="filteredVehicles" 
                :loading="loading"
                style="width: 100%"
                @row-click="handleVehicleClick"
                @selection-change="handleSelectionChange"
              >
                <el-table-column type="selection" width="55" />
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
                
                <el-table-column label="操作" width="300" fixed="right">
                  <template #default="{ row }">
                    <el-button type="text" size="small" @click.stop="editVehicle(row)">
                      编辑
                    </el-button>
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
    
    <!-- 车辆创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateEditDialog"
      :title="isEditMode ? `编辑车辆 - ${formData.plateNumber}` : '添加车辆'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        label-position="left"
      >
        <el-form-item label="车牌号" prop="plateNumber">
          <el-input
            v-model="formData.plateNumber"
            placeholder="请输入车牌号"
            :disabled="isEditMode"
          />
        </el-form-item>
        
        <el-form-item label="车辆类型" prop="vehicleType">
          <el-select v-model="formData.vehicleType" placeholder="请选择车辆类型" style="width: 100%">
            <el-option label="小型汽车" value="car" />
            <el-option label="大型汽车" value="truck" />
            <el-option label="公交车" value="bus" />
            <el-option label="摩托车" value="motorcycle" />
            <el-option label="自行车" value="bicycle" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="颜色" prop="color">
          <el-input v-model="formData.color" placeholder="请输入车辆颜色" />
        </el-form-item>
        
        <el-form-item label="品牌" prop="brand">
          <el-input v-model="formData.brand" placeholder="请输入车辆品牌" />
        </el-form-item>
        
        <el-form-item label="型号" prop="model">
          <el-input v-model="formData.model" placeholder="请输入车辆型号" />
        </el-form-item>
        
        <el-form-item label="状态" prop="isSuspicious">
          <el-radio-group v-model="formData.isSuspicious">
            <el-radio :label="false">正常</el-radio>
            <el-radio :label="true">可疑</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="风险等级" prop="riskLevel" v-if="formData.isSuspicious">
          <el-select v-model="formData.riskLevel" placeholder="请选择风险等级" style="width: 100%">
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
            <el-option label="严重" value="critical" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateEditDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="formLoading">
          {{ isEditMode ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
    
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
            {{ selectedVehicle.color || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="品牌">
            {{ selectedVehicle.brand || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="型号">
            {{ selectedVehicle.model || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedVehicle.isSuspicious ? 'warning' : 'success'" size="small">
              {{ selectedVehicle.isSuspicious ? '可疑' : '正常' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="风险等级" v-if="selectedVehicle.isSuspicious">
            <el-tag :type="getRiskLevelType(selectedVehicle.riskLevel)" size="small">
              {{ getRiskLevelText(selectedVehicle.riskLevel) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(selectedVehicle.createdAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后出现时间">
            {{ formatTime(selectedVehicle.lastSeen) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后位置">
            {{ selectedVehicle.location || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="检测次数">
            {{ selectedVehicle.detectionCount || 0 }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="vehicle-images" v-if="selectedVehicle.images && selectedVehicle.images.length > 0">
          <h4>车辆图片</h4>
          <div class="image-grid">
            <div v-for="image in selectedVehicle.images" :key="image.id" class="image-item">
              <el-image
                :src="image.url"
                :preview-src-list="selectedVehicle.images.map((img: any) => img.url)"
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
import { ElMessage, ElMessageBox, ElForm } from 'element-plus'
import { Plus, Refresh, Download } from '@element-plus/icons-vue'

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
const showCreateEditDialog = ref(false)
const selectedVehicle = ref<any>(null)
const selectedVehicles = ref<any[]>([])
const isEditMode = ref(false)
const formLoading = ref(false)
const formRef = ref<InstanceType<typeof ElForm>>()

// 表单数据
const formData = reactive({
  id: '',
  plateNumber: '',
  vehicleType: '',
  color: '',
  brand: '',
  model: '',
  isSuspicious: false,
  riskLevel: 'low'
})

// 表单验证规则
const formRules = {
  plateNumber: [
    { required: true, message: '请输入车牌号', trigger: 'blur' },
    { pattern: /^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1}$/, message: '请输入正确的车牌号格式', trigger: 'blur' }
  ],
  vehicleType: [
    { required: true, message: '请选择车辆类型', trigger: 'change' }
  ],
  riskLevel: [
    { required: true, message: '请选择风险等级', trigger: 'change' }
  ]
}

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

const getVehicleTypeTagType = (type: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const typeMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
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

const getRiskLevelType = (level: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const typeMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
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

const exportVehicles = async () => {
  try {
    const response = await vehicleStore.fetchVehicles({
      page: 1,
      per_page: 10000, // 导出所有数据
      search: filters.plateNumber,
      type: filters.vehicleType,
      is_suspicious: filters.status === 'suspicious' ? 'true' : filters.status === 'normal' ? 'false' : undefined,
      risk_level: filters.riskLevel
    })
    
    const vehicles = response.vehicles || []
    
    // 转换为CSV格式
    const headers = ['车牌号', '车辆类型', '颜色', '品牌', '型号', '状态', '风险等级', '创建时间']
    const csvContent = [
      headers.join(','),
      ...vehicles.map((vehicle: any) => [
        vehicle.plateNumber,
        getVehicleTypeText(vehicle.vehicleType),
        vehicle.color || '',
        vehicle.brand || '',
        vehicle.model || '',
        vehicle.isSuspicious ? '可疑' : '正常',
        vehicle.isSuspicious ? getRiskLevelText(vehicle.riskLevel) : '',
        formatTime(vehicle.createdAt)
      ].join(','))
    ].join('\n')
    
    // 创建下载链接
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `车辆列表_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success(`已导出 ${vehicles.length} 条车辆记录`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
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
  if (vehicle && vehicle.id) {
    router.push(`/vehicles/tracking?vehicleId=${vehicle.id}&plateNumber=${vehicle.plateNumber}`)
  } else {
    ElMessage.error('车辆数据无效')
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
  pagination.value.page = page
  loadVehicles()
}

// 批量操作相关方法
const handleSelectionChange = (selection: any[]) => {
  selectedVehicles.value = selection
}

const batchMarkSuspicious = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selectedVehicles.value.length} 辆车标记为可疑吗？`,
      '批量标记可疑',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const promises = selectedVehicles.value.map(vehicle => 
      vehicleStore.markVehicleSuspicious(vehicle.id, {
        isSuspicious: true,
        riskLevel: 'medium'
      })
    )
    
    await Promise.all(promises)
    ElMessage.success(`已成功标记 ${selectedVehicles.value.length} 辆车为可疑`)
    selectedVehicles.value = []
    await loadVehicles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量标记可疑失败:', error)
      ElMessage.error('批量标记可疑失败')
    }
  }
}

const batchCancelSuspicious = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要取消选中 ${selectedVehicles.value.length} 辆车的可疑标记吗？`,
      '批量取消标记',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const promises = selectedVehicles.value.map(vehicle => 
      vehicleStore.markVehicleSuspicious(vehicle.id, {
        isSuspicious: false,
        riskLevel: 'low'
      })
    )
    
    await Promise.all(promises)
    ElMessage.success(`已成功取消 ${selectedVehicles.value.length} 辆车的可疑标记`)
    selectedVehicles.value = []
    await loadVehicles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量取消标记失败:', error)
      ElMessage.error('批量取消标记失败')
    }
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedVehicles.value.length} 辆车吗？此操作不可恢复！`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const promises = selectedVehicles.value.map(vehicle => 
      vehicleStore.deleteVehicle(vehicle.id)
    )
    
    await Promise.all(promises)
    ElMessage.success(`已成功删除 ${selectedVehicles.value.length} 辆车`)
    selectedVehicles.value = []
    await loadVehicles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 表单相关方法
const showCreateDialog = () => {
  isEditMode.value = false
  resetForm()
  showCreateEditDialog.value = true
}

const editVehicle = (vehicle: any) => {
  isEditMode.value = true
  Object.assign(formData, {
    id: vehicle.id,
    plateNumber: vehicle.plateNumber,
    vehicleType: vehicle.vehicleType,
    color: vehicle.color || '',
    brand: vehicle.brand || '',
    model: vehicle.model || '',
    isSuspicious: vehicle.isSuspicious || false,
    riskLevel: vehicle.riskLevel || 'low'
  })
  showCreateEditDialog.value = true
}

const resetForm = () => {
  Object.assign(formData, {
    id: '',
    plateNumber: '',
    vehicleType: '',
    color: '',
    brand: '',
    model: '',
    isSuspicious: false,
    riskLevel: 'low'
  })
  formRef.value?.clearValidate()
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    formLoading.value = true
    
    const vehicleData = {
      plateNumber: formData.plateNumber,
      vehicleType: formData.vehicleType,
      color: formData.color,
      brand: formData.brand,
      model: formData.model,
      isSuspicious: formData.isSuspicious,
      riskLevel: formData.isSuspicious ? formData.riskLevel : 'low'
    }
    
    if (isEditMode.value) {
      await vehicleStore.updateVehicle(formData.id, vehicleData)
      ElMessage.success('车辆更新成功')
    } else {
      await vehicleStore.createVehicle(vehicleData)
      ElMessage.success('车辆创建成功')
    }
    
    showCreateEditDialog.value = false
    await loadVehicles()
  } catch (error) {
    console.error('提交表单失败:', error)
    ElMessage.error(isEditMode.value ? '更新车辆失败' : '创建车辆失败')
  } finally {
    formLoading.value = false
  }
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

.batch-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.selected-count {
  color: var(--text-color-light);
  font-size: 14px;
  margin-right: 10px;
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
