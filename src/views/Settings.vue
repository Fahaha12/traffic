<template>
  <div class="settings-view">
    <LayoutHeader />
    <div class="settings-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="settings-header">
          <h1>系统设置</h1>
        </div>
        
        <div class="settings-content-wrapper">
          <el-tabs v-model="activeTab" class="settings-tabs">
            <el-tab-pane label="基本设置" name="basic">
              <el-card class="settings-card">
                <template #header>
                  <span>基本配置</span>
                </template>
                
                <el-form :model="basicSettings" label-width="120px">
                  <el-form-item label="系统名称">
                    <el-input v-model="basicSettings.systemName" />
                  </el-form-item>
                  
                  <el-form-item label="默认语言">
                    <el-select v-model="basicSettings.language" style="width: 200px">
                      <el-option label="简体中文" value="zh-cn" />
                      <el-option label="English" value="en" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="时区">
                    <el-select v-model="basicSettings.timezone" style="width: 200px">
                      <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                      <el-option label="UTC时间" value="UTC" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="自动刷新">
                    <el-switch v-model="basicSettings.autoRefresh" />
                  </el-form-item>
                  
                  <el-form-item label="刷新间隔(秒)" v-if="basicSettings.autoRefresh">
                    <el-input-number 
                      v-model="basicSettings.refreshInterval" 
                      :min="5" 
                      :max="300" 
                      style="width: 200px"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
                    <el-button @click="resetBasicSettings">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <el-tab-pane label="地图设置" name="map">
              <el-card class="settings-card">
                <template #header>
                  <span>地图配置</span>
                </template>
                
                <el-form :model="mapSettings" label-width="120px">
                  <el-form-item label="地图提供商">
                    <el-select v-model="mapSettings.provider" style="width: 200px">
                      <el-option label="OpenStreetMap" value="osm" />
                      <el-option label="高德地图" value="amap" />
                      <el-option label="百度地图" value="baidu" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="默认中心点">
                    <el-row :gutter="10">
                      <el-col :span="12">
                        <el-input v-model="mapSettings.centerLat" placeholder="纬度" />
                      </el-col>
                      <el-col :span="12">
                        <el-input v-model="mapSettings.centerLng" placeholder="经度" />
                      </el-col>
                    </el-row>
                  </el-form-item>
                  
                  <el-form-item label="默认缩放级别">
                    <el-slider 
                      v-model="mapSettings.defaultZoom" 
                      :min="1" 
                      :max="18" 
                      show-input
                      style="width: 300px"
                    />
                  </el-form-item>
                  
                  <el-form-item label="显示交通状况">
                    <el-switch v-model="mapSettings.showTraffic" />
                  </el-form-item>
                  
                  <el-form-item label="显示摄像头覆盖">
                    <el-switch v-model="mapSettings.showCoverage" />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveMapSettings">保存设置</el-button>
                    <el-button @click="resetMapSettings">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <el-tab-pane label="视频设置" name="video">
              <el-card class="settings-card">
                <template #header>
                  <span>视频配置</span>
                </template>
                
                <el-form :model="videoSettings" label-width="120px">
                  <el-form-item label="默认视频质量">
                    <el-select v-model="videoSettings.defaultQuality" style="width: 200px">
                      <el-option label="低质量" value="low" />
                      <el-option label="中等质量" value="medium" />
                      <el-option label="高质量" value="high" />
                      <el-option label="超高质量" value="ultra" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="自动播放">
                    <el-switch v-model="videoSettings.autoPlay" />
                  </el-form-item>
                  
                  <el-form-item label="显示控制栏">
                    <el-switch v-model="videoSettings.showControls" />
                  </el-form-item>
                  
                  <el-form-item label="视频缓冲时间(秒)">
                    <el-input-number 
                      v-model="videoSettings.bufferTime" 
                      :min="1" 
                      :max="30" 
                      style="width: 200px"
                    />
                  </el-form-item>
                  
                  <el-form-item label="最大同时播放数">
                    <el-input-number 
                      v-model="videoSettings.maxConcurrent" 
                      :min="1" 
                      :max="16" 
                      style="width: 200px"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveVideoSettings">保存设置</el-button>
                    <el-button @click="resetVideoSettings">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <el-tab-pane label="告警设置" name="alert">
              <el-card class="settings-card">
                <template #header>
                  <span>告警配置</span>
                </template>
                
                <el-form :model="alertSettings" label-width="120px">
                  <el-form-item label="启用声音告警">
                    <el-switch v-model="alertSettings.soundEnabled" />
                  </el-form-item>
                  
                  <el-form-item label="告警音量" v-if="alertSettings.soundEnabled">
                    <el-slider 
                      v-model="alertSettings.volume" 
                      :min="0" 
                      :max="100" 
                      show-input
                      style="width: 300px"
                    />
                  </el-form-item>
                  
                  <el-form-item label="启用桌面通知">
                    <el-switch v-model="alertSettings.desktopNotification" />
                  </el-form-item>
                  
                  <el-form-item label="告警保留时间(小时)">
                    <el-input-number 
                      v-model="alertSettings.retentionHours" 
                      :min="1" 
                      :max="168" 
                      style="width: 200px"
                    />
                  </el-form-item>
                  
                  <el-form-item label="自动标记已读">
                    <el-switch v-model="alertSettings.autoMarkRead" />
                  </el-form-item>
                  
                  <el-form-item label="告警级别过滤">
                    <el-checkbox-group v-model="alertSettings.enabledLevels">
                      <el-checkbox label="low">低</el-checkbox>
                      <el-checkbox label="medium">中</el-checkbox>
                      <el-checkbox label="high">高</el-checkbox>
                      <el-checkbox label="critical">严重</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveAlertSettings">保存设置</el-button>
                    <el-button @click="resetAlertSettings">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <el-tab-pane label="用户管理" name="user">
              <el-card class="settings-card">
                <template #header>
                  <span>用户管理</span>
                </template>
                
                <div class="user-management">
                  <div class="user-list">
                    <el-table :data="users" style="width: 100%">
                      <el-table-column prop="username" label="用户名" />
                      <el-table-column prop="role" label="角色" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getRoleType(row.role)" size="small">
                            {{ getRoleText(row.role) }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="lastLogin" label="最后登录" width="180">
                        <template #default="{ row }">
                          {{ formatTime(row.lastLogin) }}
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" width="200">
                        <template #default="{ row }">
                          <el-button type="text" size="small" @click="editUser(row)">
                            编辑
                          </el-button>
                          <el-button type="text" size="small" @click="resetPassword(row)">
                            重置密码
                          </el-button>
                          <el-button type="text" size="small" class="danger" @click="deleteUser(row)">
                            删除
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                  
                  <div class="user-actions">
                    <el-button type="primary" @click="showAddUserDialog = true">
                      <el-icon><Plus /></el-icon>
                      添加用户
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
    
    <!-- 添加用户对话框 -->
    <el-dialog
      v-model="showAddUserDialog"
      title="添加用户"
      width="500px"
    >
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="newUser.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newUser.password" type="password" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="newUser.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="操作员" value="operator" />
            <el-option label="查看者" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddUserDialog = false">取消</el-button>
        <el-button type="primary" @click="addUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

const activeTab = ref('basic')
const showAddUserDialog = ref(false)

// 基本设置
const basicSettings = reactive({
  systemName: '交通监控系统',
  language: 'zh-cn',
  timezone: 'Asia/Shanghai',
  autoRefresh: true,
  refreshInterval: 30
})

// 地图设置
const mapSettings = reactive({
  provider: 'osm',
  centerLat: '39.9042',
  centerLng: '116.4074',
  defaultZoom: 12,
  showTraffic: false,
  showCoverage: true
})

// 视频设置
const videoSettings = reactive({
  defaultQuality: 'medium',
  autoPlay: false,
  showControls: true,
  bufferTime: 5,
  maxConcurrent: 4
})

// 告警设置
const alertSettings = reactive({
  soundEnabled: true,
  volume: 50,
  desktopNotification: true,
  retentionHours: 24,
  autoMarkRead: false,
  enabledLevels: ['medium', 'high', 'critical']
})

// 用户数据
const users = ref([
  {
    id: '1',
    username: 'admin',
    role: 'admin',
    lastLogin: new Date().toISOString()
  },
  {
    id: '2',
    username: 'operator1',
    role: 'operator',
    lastLogin: new Date(Date.now() - 3600000).toISOString()
  }
])

const newUser = reactive({
  username: '',
  password: '',
  role: 'viewer'
})

// 方法
const saveBasicSettings = () => {
  userStore.updateSystemConfig(basicSettings)
  ElMessage.success('基本设置已保存')
}

const resetBasicSettings = () => {
  Object.assign(basicSettings, {
    systemName: '交通监控系统',
    language: 'zh-cn',
    timezone: 'Asia/Shanghai',
    autoRefresh: true,
    refreshInterval: 30
  })
}

const saveMapSettings = () => {
  userStore.updateSystemConfig(mapSettings)
  ElMessage.success('地图设置已保存')
}

const resetMapSettings = () => {
  Object.assign(mapSettings, {
    provider: 'osm',
    centerLat: '39.9042',
    centerLng: '116.4074',
    defaultZoom: 12,
    showTraffic: false,
    showCoverage: true
  })
}

const saveVideoSettings = () => {
  userStore.updateSystemConfig(videoSettings)
  ElMessage.success('视频设置已保存')
}

const resetVideoSettings = () => {
  Object.assign(videoSettings, {
    defaultQuality: 'medium',
    autoPlay: false,
    showControls: true,
    bufferTime: 5,
    maxConcurrent: 4
  })
}

const saveAlertSettings = () => {
  userStore.updateSystemConfig(alertSettings)
  ElMessage.success('告警设置已保存')
}

const resetAlertSettings = () => {
  Object.assign(alertSettings, {
    soundEnabled: true,
    volume: 50,
    desktopNotification: true,
    retentionHours: 24,
    autoMarkRead: false,
    enabledLevels: ['medium', 'high', 'critical']
  })
}

const addUser = () => {
  // 添加用户逻辑
  users.value.push({
    id: Date.now().toString(),
    username: newUser.username,
    role: newUser.role,
    lastLogin: new Date().toISOString()
  })
  
  Object.assign(newUser, {
    username: '',
    password: '',
    role: 'viewer'
  })
  
  showAddUserDialog.value = false
  ElMessage.success('用户添加成功')
}

const editUser = (user: any) => {
  console.log('编辑用户:', user)
}

const resetPassword = (user: any) => {
  console.log('重置密码:', user)
  ElMessage.success('密码重置成功')
}

const deleteUser = (user: any) => {
  const index = users.value.findIndex(u => u.id === user.id)
  if (index > -1) {
    users.value.splice(index, 1)
    ElMessage.success('用户删除成功')
  }
}

const getRoleType = (role: string) => {
  switch (role) {
    case 'admin': return 'danger'
    case 'operator': return 'warning'
    case 'viewer': return 'info'
    default: return 'info'
  }
}

const getRoleText = (role: string) => {
  switch (role) {
    case 'admin': return '管理员'
    case 'operator': return '操作员'
    case 'viewer': return '查看者'
    default: return '未知'
  }
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatDateTime(timestamp)
}

onMounted(() => {
  // 加载保存的设置
  const savedConfig = userStore.systemConfig
  Object.assign(basicSettings, savedConfig)
})
</script>

<style scoped>
.settings-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.settings-content {
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

.settings-header {
  margin-bottom: 20px;
}

.settings-header h1 {
  color: var(--text-color);
  margin: 0;
}

.settings-content-wrapper {
  max-width: 1000px;
}

.settings-tabs {
  background: var(--bg-color-light);
  border-radius: 8px;
  padding: 20px;
}

.settings-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
}

.user-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-actions {
  display: flex;
  justify-content: flex-end;
}

.danger {
  color: var(--danger-color);
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-tabs__item) {
  color: var(--text-color-light);
}

:deep(.el-tabs__item.is-active) {
  color: var(--primary-color);
}

:deep(.el-form-item__label) {
  color: var(--text-color);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  background: var(--bg-color-light);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-table) {
  background: var(--bg-color-light);
  color: var(--text-color);
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
</style>
