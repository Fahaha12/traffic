<template>
  <div class="system-logs-view">
    <LayoutHeader />
    <div class="system-logs-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="system-logs-header">
          <h1>系统日志</h1>
          <div class="header-actions">
            <el-button type="primary" @click="refreshLogs">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="exportLogs">
              <el-icon><Download /></el-icon>
              导出日志
            </el-button>
            <el-button @click="clearLogs" type="danger">
              <el-icon><Delete /></el-icon>
              清空日志
            </el-button>
          </div>
        </div>
        
        <div class="system-logs-content-wrapper">
          <!-- 日志筛选 -->
          <div class="log-filters">
            <el-card>
              <el-form :model="filters" inline>
                <el-form-item label="日志级别">
                  <el-select v-model="filters.level" placeholder="全部级别" clearable>
                    <el-option label="错误" value="error" />
                    <el-option label="警告" value="warn" />
                    <el-option label="信息" value="info" />
                    <el-option label="调试" value="debug" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="模块">
                  <el-select v-model="filters.module" placeholder="全部模块" clearable>
                    <el-option label="用户管理" value="user" />
                    <el-option label="摄像头" value="camera" />
                    <el-option label="车辆检测" value="vehicle" />
                    <el-option label="地图服务" value="map" />
                    <el-option label="告警系统" value="alert" />
                    <el-option label="系统" value="system" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="用户">
                  <el-input v-model="filters.user" placeholder="请输入用户名" clearable />
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
          
          <!-- 日志列表 -->
          <div class="log-list">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>系统日志 ({{ totalLogs }} 条)</span>
                  <div class="log-controls">
                    <el-switch
                      v-model="autoRefresh"
                      active-text="自动刷新"
                      @change="toggleAutoRefresh"
                    />
                    <el-select v-model="refreshInterval" size="small" style="width: 100px; margin-left: 10px">
                      <el-option label="5秒" value="5000" />
                      <el-option label="10秒" value="10000" />
                      <el-option label="30秒" value="30000" />
                      <el-option label="1分钟" value="60000" />
                    </el-select>
                  </div>
                </div>
              </template>
              
              <el-table 
                :data="filteredLogs" 
                style="width: 100%"
                @row-click="handleLogClick"
                :row-class-name="getRowClassName"
              >
                <el-table-column width="50">
                  <template #default="{ row }">
                    <el-icon 
                      :class="getLogIconClass(row.level)"
                      :style="{ color: getLogColor(row.level) }"
                    >
                      <CircleClose v-if="row.level === 'error'" />
                      <Warning v-else-if="row.level === 'warn'" />
                      <InfoFilled v-else-if="row.level === 'info'" />
                      <QuestionFilled v-else />
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
                
                <el-table-column prop="timestamp" label="时间" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.timestamp) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="module" label="模块" width="100">
                  <template #default="{ row }">
                    {{ getModuleText(row.module) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="user" label="用户" width="120" />
                
                <el-table-column prop="action" label="操作" width="150" />
                
                <el-table-column prop="message" label="消息" min-width="300" show-overflow-tooltip />
                
                <el-table-column prop="ip" label="IP地址" width="130" />
                
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="{ row }">
                    <el-button type="text" size="small" @click.stop="viewLogDetail(row)">
                      详情
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 分页 -->
              <div class="pagination-wrapper">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[20, 50, 100, 200]"
                  :total="totalLogs"
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
    
    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`日志详情 - ${selectedLog?.level?.toUpperCase()}`"
      width="800px"
    >
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日志级别">
            <el-tag :type="getLevelTagType(selectedLog.level)" size="small">
              {{ getLevelText(selectedLog.level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="时间">
            {{ formatTime(selectedLog.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="模块">
            {{ getModuleText(selectedLog.module) }}
          </el-descriptions-item>
          <el-descriptions-item label="用户">
            {{ selectedLog.user }}
          </el-descriptions-item>
          <el-descriptions-item label="操作">
            {{ selectedLog.action }}
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">
            {{ selectedLog.ip }}
          </el-descriptions-item>
          <el-descriptions-item label="用户代理" :span="2">
            {{ selectedLog.userAgent }}
          </el-descriptions-item>
          <el-descriptions-item label="详细消息" :span="2">
            <pre class="log-message">{{ selectedLog.message }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="堆栈信息" :span="2" v-if="selectedLog.stack">
            <pre class="log-stack">{{ selectedLog.stack }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="copyLogDetail">复制详情</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()

// 响应式数据
const logs = ref([
  {
    id: '1',
    level: 'error',
    timestamp: new Date().toISOString(),
    module: 'camera',
    user: 'admin',
    action: '摄像头连接失败',
    message: '摄像头CAM-001连接超时，请检查网络连接',
    ip: '192.168.1.100',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    stack: 'Error: Connection timeout\n    at Camera.connect (camera.js:45:12)\n    at async connectCamera (index.js:23:8)'
  },
  {
    id: '2',
    level: 'warn',
    timestamp: new Date(Date.now() - 300000).toISOString(),
    module: 'vehicle',
    user: 'operator1',
    action: '可疑车辆检测',
    message: '检测到车牌号为豫B67890的车辆行为异常',
    ip: '192.168.1.101',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  },
  {
    id: '3',
    level: 'info',
    timestamp: new Date(Date.now() - 600000).toISOString(),
    module: 'user',
    user: 'admin',
    action: '用户登录',
    message: '用户admin成功登录系统',
    ip: '192.168.1.100',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  },
  {
    id: '4',
    level: 'info',
    timestamp: new Date(Date.now() - 900000).toISOString(),
    module: 'system',
    user: 'system',
    action: '系统启动',
    message: '交通监控系统启动完成，所有服务正常运行',
    ip: '127.0.0.1',
    userAgent: 'System'
  },
  {
    id: '5',
    level: 'debug',
    timestamp: new Date(Date.now() - 1200000).toISOString(),
    module: 'map',
    user: 'system',
    action: '地图加载',
    message: '地图服务加载完成，共加载100个摄像头标记',
    ip: '127.0.0.1',
    userAgent: 'System'
  }
])

const filters = reactive({
  level: '',
  module: '',
  user: '',
  dateRange: null as any
})

const currentPage = ref(1)
const pageSize = ref(50)
const showDetailDialog = ref(false)
const selectedLog = ref<any>(null)
const autoRefresh = ref(false)
const refreshInterval = ref('10000')
const refreshTimer = ref<any>(null)

// 计算属性
const totalLogs = computed(() => filteredLogs.value.length)

const filteredLogs = computed(() => {
  let result = logs.value
  
  if (filters.level) {
    result = result.filter(log => log.level === filters.level)
  }
  
  if (filters.module) {
    result = result.filter(log => log.module === filters.module)
  }
  
  if (filters.user) {
    result = result.filter(log => 
      log.user.toLowerCase().includes(filters.user.toLowerCase())
    )
  }
  
  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    result = result.filter(log => {
      const logTime = new Date(log.timestamp)
      return logTime >= new Date(start) && logTime <= new Date(end)
    })
  }
  
  return result
})

// 方法
const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    error: '错误',
    warn: '警告',
    info: '信息',
    debug: '调试'
  }
  return levelMap[level] || level
}

const getLevelTagType = (level: string) => {
  const typeMap: Record<string, string> = {
    error: 'danger',
    warn: 'warning',
    info: 'info',
    debug: 'success'
  }
  return typeMap[level] || 'info'
}

const getLogColor = (level: string) => {
  const colorMap: Record<string, string> = {
    error: '#f56c6c',
    warn: '#e6a23c',
    info: '#409eff',
    debug: '#67c23a'
  }
  return colorMap[level] || '#909399'
}

const getLogIconClass = (level: string) => {
  return `log-icon log-icon-${level}`
}

const getModuleText = (module: string) => {
  const moduleMap: Record<string, string> = {
    user: '用户管理',
    camera: '摄像头',
    vehicle: '车辆检测',
    map: '地图服务',
    alert: '告警系统',
    system: '系统'
  }
  return moduleMap[module] || module
}

const getRowClassName = ({ row }: { row: any }) => {
  return `log-row log-row-${row.level}`
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
    module: '',
    user: '',
    dateRange: null
  })
  currentPage.value = 1
  ElMessage.success('筛选条件已重置')
}

const refreshLogs = () => {
  // 模拟添加新日志
  const newLog = {
    id: Date.now().toString(),
    level: 'info',
    timestamp: new Date().toISOString(),
    module: 'system',
    user: 'system',
    action: '日志刷新',
    message: '系统日志已刷新',
    ip: '127.0.0.1',
    userAgent: 'System'
  }
  logs.value.unshift(newLog)
  ElMessage.success('日志已刷新')
}

const exportLogs = () => {
  ElMessage.info('导出功能开发中...')
}

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有日志吗？此操作不可恢复！', '确认清空', {
      type: 'warning'
    })
    
    logs.value = []
    ElMessage.success('日志已清空')
  } catch {
    // 用户取消清空
  }
}

const handleLogClick = (row: any) => {
  selectedLog.value = row
  showDetailDialog.value = true
}

const viewLogDetail = (log: any) => {
  selectedLog.value = log
  showDetailDialog.value = true
}

const copyLogDetail = () => {
  if (selectedLog.value) {
    const logText = `级别: ${getLevelText(selectedLog.value.level)}
时间: ${formatTime(selectedLog.value.timestamp)}
模块: ${getModuleText(selectedLog.value.module)}
用户: ${selectedLog.value.user}
操作: ${selectedLog.value.action}
消息: ${selectedLog.value.message}
IP: ${selectedLog.value.ip}`
    
    navigator.clipboard.writeText(logText).then(() => {
      ElMessage.success('日志详情已复制到剪贴板')
    }).catch(() => {
      ElMessage.error('复制失败')
    })
  }
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  refreshTimer.value = setInterval(() => {
    refreshLogs()
  }, parseInt(refreshInterval.value))
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
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

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.system-logs-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.system-logs-content {
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

.system-logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.system-logs-header h1 {
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.system-logs-content-wrapper {
  max-width: 1400px;
}

.log-filters {
  margin-bottom: 20px;
}

.log-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-controls {
  display: flex;
  align-items: center;
}

.log-detail {
  padding: 10px 0;
}

.log-message,
.log-stack {
  background: var(--bg-color-lighter);
  padding: 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.log-row-error) {
  background: rgba(245, 108, 108, 0.1);
}

:deep(.log-row-warn) {
  background: rgba(230, 162, 60, 0.1);
}

:deep(.log-row-info) {
  background: rgba(64, 158, 255, 0.1);
}

:deep(.log-row-debug) {
  background: rgba(103, 194, 58, 0.1);
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
