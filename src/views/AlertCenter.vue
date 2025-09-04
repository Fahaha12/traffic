<template>
  <div class="alert-center-view">
    <LayoutHeader />
    <div class="alert-center-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="alert-center-header">
          <h1>告警中心</h1>
          <div class="header-actions">
            <el-button type="primary" @click="markAllAsRead" :disabled="unreadCount === 0">
              <el-icon><Check /></el-icon>
              全部标记为已读
            </el-button>
            <el-button @click="clearAllAlerts" :disabled="alerts.length === 0">
              <el-icon><Delete /></el-icon>
              清空所有告警
            </el-button>
          </div>
        </div>
        
        <div class="alert-center-content-wrapper">
          <!-- 告警统计 -->
          <div class="alert-stats">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon critical">
                      <el-icon><Warning /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ criticalCount }}</div>
                      <div class="stat-label">严重告警</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon high">
                      <el-icon><Warning /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ highCount }}</div>
                      <div class="stat-label">高级告警</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon medium">
                      <el-icon><InfoFilled /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ mediumCount }}</div>
                      <div class="stat-label">中级告警</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon unread">
                      <el-icon><Bell /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ unreadCount }}</div>
                      <div class="stat-label">未读告警</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
          
          <!-- 告警筛选 -->
          <div class="alert-filters">
            <el-card>
              <el-form :model="filters" inline>
                <el-form-item label="告警级别">
                  <el-select v-model="filters.level" placeholder="全部级别" clearable>
                    <el-option label="严重" value="critical" />
                    <el-option label="高级" value="high" />
                    <el-option label="中级" value="medium" />
                    <el-option label="低级" value="low" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="告警类型">
                  <el-select v-model="filters.type" placeholder="全部类型" clearable>
                    <el-option label="摄像头离线" value="camera_offline" />
                    <el-option label="可疑车辆" value="suspicious_vehicle" />
                    <el-option label="交通异常" value="traffic_anomaly" />
                    <el-option label="系统错误" value="system_error" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="状态">
                  <el-select v-model="filters.status" placeholder="全部状态" clearable>
                    <el-option label="未读" value="unread" />
                    <el-option label="已读" value="read" />
                    <el-option label="已处理" value="resolved" />
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
          
          <!-- 告警列表 -->
          <div class="alert-list">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>告警列表</span>
                  <el-button type="text" @click="refreshAlerts">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              
              <el-table 
                :data="filteredAlerts" 
                style="width: 100%"
                @row-click="handleAlertClick"
                :row-class-name="getRowClassName"
              >
                <el-table-column width="50">
                  <template #default="{ row }">
                    <el-icon 
                      :class="getAlertIconClass(row.level)"
                      :style="{ color: getAlertColor(row.level) }"
                    >
                      <Warning v-if="row.level === 'critical' || row.level === 'high'" />
                      <InfoFilled v-else />
                    </el-icon>
                  </template>
                </el-table-column>
                
                <el-table-column prop="level" label="级别" width="80">
                  <template #default="{ row }">
                    <el-tag :type="getLevelTagType(row.level)" size="small">
                      {{ getLevelText(row.level) }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column prop="type" label="类型" width="120">
                  <template #default="{ row }">
                    {{ getTypeText(row.type) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="title" label="标题" min-width="200">
                  <template #default="{ row }">
                    <div class="alert-title">
                      <span :class="{ 'unread': !row.isRead }">{{ row.title }}</span>
                      <el-badge v-if="!row.isRead" value="NEW" class="unread-badge" />
                    </div>
                  </template>
                </el-table-column>
                
                <el-table-column prop="message" label="描述" min-width="300" show-overflow-tooltip />
                
                <el-table-column prop="location" label="位置" width="150" />
                
                <el-table-column prop="timestamp" label="时间" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.timestamp) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getStatusTagType(row.status)" size="small">
                      {{ getStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button 
                      type="text" 
                      size="small" 
                      @click.stop="markAsRead(row)"
                      v-if="!row.isRead"
                    >
                      标记已读
                    </el-button>
                    <el-button 
                      type="text" 
                      size="small" 
                      @click.stop="resolveAlert(row)"
                      v-if="row.status !== 'resolved'"
                    >
                      处理
                    </el-button>
                    <el-button 
                      type="text" 
                      size="small" 
                      class="danger"
                      @click.stop="deleteAlert(row)"
                    >
                      删除
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
                  :total="totalAlerts"
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
    
    <!-- 告警详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="selectedAlert?.title"
      width="600px"
    >
      <div v-if="selectedAlert" class="alert-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="告警级别">
            <el-tag :type="getLevelTagType(selectedAlert.level)" size="small">
              {{ getLevelText(selectedAlert.level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="告警类型">
            {{ getTypeText(selectedAlert.type) }}
          </el-descriptions-item>
          <el-descriptions-item label="发生时间">
            {{ formatTime(selectedAlert.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedAlert.status)" size="small">
              {{ getStatusText(selectedAlert.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="位置" :span="2">
            {{ selectedAlert.location }}
          </el-descriptions-item>
          <el-descriptions-item label="详细描述" :span="2">
            {{ selectedAlert.message }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedAlert.attachments && selectedAlert.attachments.length > 0" class="attachments">
          <h4>相关附件</h4>
          <div class="attachment-list">
            <div v-for="attachment in selectedAlert.attachments" :key="attachment.id" class="attachment-item">
              <el-icon><Document /></el-icon>
              <span>{{ attachment.name }}</span>
              <el-button type="text" size="small" @click="downloadAttachment(attachment)">
                下载
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="markAsRead(selectedAlert)"
          v-if="selectedAlert && !selectedAlert.isRead"
        >
          标记已读
        </el-button>
        <el-button 
          type="success" 
          @click="resolveAlert(selectedAlert)"
          v-if="selectedAlert && selectedAlert.status !== 'resolved'"
        >
          标记处理
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()

// 响应式数据
const alerts = ref([
  {
    id: '1',
    level: 'critical',
    type: 'camera_offline',
    title: '摄像头离线告警',
    message: '摄像头CAM-001在郑州市中原路与建设路交叉口出现离线状态，已持续5分钟',
    location: '中原路与建设路交叉口',
    timestamp: new Date().toISOString(),
    status: 'unread',
    isRead: false,
    attachments: [
      { id: '1', name: 'camera_log.txt', url: '/logs/camera_log.txt' }
    ]
  },
  {
    id: '2',
    level: 'high',
    type: 'suspicious_vehicle',
    title: '可疑车辆检测',
    message: '检测到车牌号为豫A12345的车辆在监控区域内停留超过30分钟，行为异常',
    location: '金水区花园路',
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    status: 'read',
    isRead: true,
    attachments: []
  },
  {
    id: '3',
    level: 'medium',
    type: 'traffic_anomaly',
    title: '交通流量异常',
    message: '建设路与大学路交叉口交通流量异常，当前流量比平时高出150%',
    location: '建设路与大学路交叉口',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    status: 'resolved',
    isRead: true,
    attachments: []
  },
  {
    id: '4',
    level: 'low',
    type: 'system_error',
    title: '系统性能警告',
    message: '系统CPU使用率超过80%，建议检查系统负载',
    location: '系统服务器',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    status: 'read',
    isRead: true,
    attachments: []
  }
])

const filters = reactive({
  level: '',
  type: '',
  status: '',
  dateRange: null as any
})

const currentPage = ref(1)
const pageSize = ref(20)
const showDetailDialog = ref(false)
const selectedAlert = ref<any>(null)

// 计算属性
const criticalCount = computed(() => 
  alerts.value.filter(alert => alert.level === 'critical' && !alert.isRead).length
)

const highCount = computed(() => 
  alerts.value.filter(alert => alert.level === 'high' && !alert.isRead).length
)

const mediumCount = computed(() => 
  alerts.value.filter(alert => alert.level === 'medium' && !alert.isRead).length
)

const unreadCount = computed(() => 
  alerts.value.filter(alert => !alert.isRead).length
)

const totalAlerts = computed(() => filteredAlerts.value.length)

const filteredAlerts = computed(() => {
  let result = alerts.value
  
  if (filters.level) {
    result = result.filter(alert => alert.level === filters.level)
  }
  
  if (filters.type) {
    result = result.filter(alert => alert.type === filters.type)
  }
  
  if (filters.status) {
    if (filters.status === 'unread') {
      result = result.filter(alert => !alert.isRead)
    } else {
      result = result.filter(alert => alert.status === filters.status)
    }
  }
  
  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    result = result.filter(alert => {
      const alertTime = new Date(alert.timestamp)
      return alertTime >= new Date(start) && alertTime <= new Date(end)
    })
  }
  
  return result
})

// 方法
const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    critical: '严重',
    high: '高级',
    medium: '中级',
    low: '低级'
  }
  return levelMap[level] || level
}

const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    camera_offline: '摄像头离线',
    suspicious_vehicle: '可疑车辆',
    traffic_anomaly: '交通异常',
    system_error: '系统错误'
  }
  return typeMap[type] || type
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    unread: '未读',
    read: '已读',
    resolved: '已处理'
  }
  return statusMap[status] || status
}

const getLevelTagType = (level: string) => {
  const typeMap: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'info',
    low: 'success'
  }
  return typeMap[level] || 'info'
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    unread: 'danger',
    read: 'info',
    resolved: 'success'
  }
  return typeMap[status] || 'info'
}

const getAlertColor = (level: string) => {
  const colorMap: Record<string, string> = {
    critical: '#f56c6c',
    high: '#e6a23c',
    medium: '#409eff',
    low: '#67c23a'
  }
  return colorMap[level] || '#909399'
}

const getAlertIconClass = (level: string) => {
  return `alert-icon alert-icon-${level}`
}

const getRowClassName = ({ row }: { row: any }) => {
  return row.isRead ? '' : 'unread-row'
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
    level: '',
    type: '',
    status: '',
    dateRange: null
  })
  currentPage.value = 1
  ElMessage.success('筛选条件已重置')
}

const refreshAlerts = () => {
  ElMessage.success('告警列表已刷新')
}

const handleAlertClick = (row: any) => {
  selectedAlert.value = row
  showDetailDialog.value = true
}

const markAsRead = (alert: any) => {
  if (alert) {
    alert.isRead = true
    alert.status = 'read'
    ElMessage.success('告警已标记为已读')
  }
}

const markAllAsRead = () => {
  alerts.value.forEach(alert => {
    alert.isRead = true
    if (alert.status === 'unread') {
      alert.status = 'read'
    }
  })
  ElMessage.success('所有告警已标记为已读')
}

const resolveAlert = (alert: any) => {
  if (alert) {
    alert.status = 'resolved'
    ElMessage.success('告警已标记为已处理')
  }
}

const deleteAlert = async (alert: any) => {
  try {
    await ElMessageBox.confirm('确定要删除此告警吗？', '确认删除', {
      type: 'warning'
    })
    
    const index = alerts.value.findIndex(a => a.id === alert.id)
    if (index > -1) {
      alerts.value.splice(index, 1)
      ElMessage.success('告警已删除')
    }
  } catch {
    // 用户取消删除
  }
}

const clearAllAlerts = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有告警吗？此操作不可恢复！', '确认清空', {
      type: 'warning'
    })
    
    alerts.value = []
    ElMessage.success('所有告警已清空')
  } catch {
    // 用户取消清空
  }
}

const downloadAttachment = (attachment: any) => {
  ElMessage.info(`下载附件: ${attachment.name}`)
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
.alert-center-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.alert-center-content {
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

.alert-center-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.alert-center-header h1 {
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.alert-center-content-wrapper {
  max-width: 1400px;
}

.alert-stats {
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

.stat-icon.critical {
  background: var(--danger-color);
}

.stat-icon.high {
  background: var(--warning-color);
}

.stat-icon.medium {
  background: var(--info-color);
}

.stat-icon.unread {
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

.alert-filters {
  margin-bottom: 20px;
}

.alert-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-title .unread {
  font-weight: bold;
}

.unread-badge {
  margin-left: 5px;
}

.alert-detail {
  padding: 10px 0;
}

.attachments {
  margin-top: 20px;
}

.attachments h4 {
  color: var(--text-color);
  margin-bottom: 10px;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: var(--bg-color-light);
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.danger {
  color: var(--danger-color);
}

:deep(.unread-row) {
  background: var(--bg-color-lighter);
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
