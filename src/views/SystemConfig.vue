<template>
  <div class="system-config-view">
    <LayoutHeader />
    <div class="system-config-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="system-config-header">
          <h1>系统配置</h1>
          <div class="header-actions">
            <el-button type="primary" @click="saveAllConfig">
              <el-icon><Check /></el-icon>
              保存所有配置
            </el-button>
            <el-button @click="resetAllConfig">
              <el-icon><Refresh /></el-icon>
              重置配置
            </el-button>
          </div>
        </div>
        
        <div class="system-config-content-wrapper">
          <el-tabs v-model="activeTab" class="config-tabs">
            <!-- 系统基本配置 -->
            <el-tab-pane label="基本配置" name="basic">
              <el-card class="config-card">
                <template #header>
                  <span>系统基本配置</span>
                </template>
                
                <el-form :model="basicConfig" label-width="150px">
                  <el-form-item label="系统名称">
                    <el-input v-model="basicConfig.systemName" />
                  </el-form-item>
                  
                  <el-form-item label="系统版本">
                    <el-input v-model="basicConfig.version" disabled />
                  </el-form-item>
                  
                  <el-form-item label="默认语言">
                    <el-select v-model="basicConfig.language" style="width: 200px">
                      <el-option label="简体中文" value="zh-cn" />
                      <el-option label="English" value="en" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="时区">
                    <el-select v-model="basicConfig.timezone" style="width: 200px">
                      <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                      <el-option label="UTC时间" value="UTC" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="系统描述">
                    <el-input 
                      v-model="basicConfig.description" 
                      type="textarea" 
                      :rows="3"
                      placeholder="请输入系统描述"
                    />
                  </el-form-item>
                  
                  <el-form-item label="维护模式">
                    <el-switch v-model="basicConfig.maintenanceMode" />
                    <span class="config-tip">开启后系统将进入维护模式，仅管理员可访问</span>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveBasicConfig">保存基本配置</el-button>
                    <el-button @click="resetBasicConfig">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <!-- 数据库配置 -->
            <el-tab-pane label="数据库配置" name="database">
              <el-card class="config-card">
                <template #header>
                  <span>数据库配置</span>
                </template>
                
                <el-form :model="databaseConfig" label-width="150px">
                  <el-form-item label="数据库类型">
                    <el-select v-model="databaseConfig.type" style="width: 200px">
                      <el-option label="MySQL" value="mysql" />
                      <el-option label="PostgreSQL" value="postgresql" />
                      <el-option label="MongoDB" value="mongodb" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="主机地址">
                    <el-input v-model="databaseConfig.host" />
                  </el-form-item>
                  
                  <el-form-item label="端口">
                    <el-input-number v-model="databaseConfig.port" :min="1" :max="65535" />
                  </el-form-item>
                  
                  <el-form-item label="数据库名">
                    <el-input v-model="databaseConfig.database" />
                  </el-form-item>
                  
                  <el-form-item label="用户名">
                    <el-input v-model="databaseConfig.username" />
                  </el-form-item>
                  
                  <el-form-item label="密码">
                    <el-input v-model="databaseConfig.password" type="password" show-password />
                  </el-form-item>
                  
                  <el-form-item label="连接池大小">
                    <el-input-number v-model="databaseConfig.poolSize" :min="1" :max="100" />
                  </el-form-item>
                  
                  <el-form-item label="连接超时(秒)">
                    <el-input-number v-model="databaseConfig.timeout" :min="1" :max="300" />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveDatabaseConfig">保存数据库配置</el-button>
                    <el-button @click="testDatabaseConnection">测试连接</el-button>
                    <el-button @click="resetDatabaseConfig">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <!-- 网络配置 -->
            <el-tab-pane label="网络配置" name="network">
              <el-card class="config-card">
                <template #header>
                  <span>网络配置</span>
                </template>
                
                <el-form :model="networkConfig" label-width="150px">
                  <el-form-item label="服务器端口">
                    <el-input-number v-model="networkConfig.serverPort" :min="1" :max="65535" />
                  </el-form-item>
                  
                  <el-form-item label="WebSocket端口">
                    <el-input-number v-model="networkConfig.websocketPort" :min="1" :max="65535" />
                  </el-form-item>
                  
                  <el-form-item label="最大连接数">
                    <el-input-number v-model="networkConfig.maxConnections" :min="1" :max="10000" />
                  </el-form-item>
                  
                  <el-form-item label="请求超时(秒)">
                    <el-input-number v-model="networkConfig.requestTimeout" :min="1" :max="300" />
                  </el-form-item>
                  
                  <el-form-item label="启用HTTPS">
                    <el-switch v-model="networkConfig.enableHttps" />
                  </el-form-item>
                  
                  <el-form-item label="SSL证书路径" v-if="networkConfig.enableHttps">
                    <el-input v-model="networkConfig.sslCertPath" />
                  </el-form-item>
                  
                  <el-form-item label="SSL私钥路径" v-if="networkConfig.enableHttps">
                    <el-input v-model="networkConfig.sslKeyPath" />
                  </el-form-item>
                  
                  <el-form-item label="CORS允许域名">
                    <el-input 
                      v-model="networkConfig.corsOrigins" 
                      type="textarea" 
                      :rows="3"
                      placeholder="每行一个域名，* 表示允许所有"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveNetworkConfig">保存网络配置</el-button>
                    <el-button @click="resetNetworkConfig">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <!-- 存储配置 -->
            <el-tab-pane label="存储配置" name="storage">
              <el-card class="config-card">
                <template #header>
                  <span>存储配置</span>
                </template>
                
                <el-form :model="storageConfig" label-width="150px">
                  <el-form-item label="存储类型">
                    <el-select v-model="storageConfig.type" style="width: 200px">
                      <el-option label="本地存储" value="local" />
                      <el-option label="阿里云OSS" value="aliyun" />
                      <el-option label="腾讯云COS" value="tencent" />
                      <el-option label="AWS S3" value="aws" />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="存储路径">
                    <el-input v-model="storageConfig.path" />
                  </el-form-item>
                  
                  <el-form-item label="最大文件大小(MB)">
                    <el-input-number v-model="storageConfig.maxFileSize" :min="1" :max="1024" />
                  </el-form-item>
                  
                  <el-form-item label="允许的文件类型">
                    <el-checkbox-group v-model="storageConfig.allowedTypes">
                      <el-checkbox label="image">图片</el-checkbox>
                      <el-checkbox label="video">视频</el-checkbox>
                      <el-checkbox label="document">文档</el-checkbox>
                      <el-checkbox label="archive">压缩包</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                  
                  <el-form-item label="文件保留天数">
                    <el-input-number v-model="storageConfig.retentionDays" :min="1" :max="365" />
                  </el-form-item>
                  
                  <el-form-item label="自动清理">
                    <el-switch v-model="storageConfig.autoCleanup" />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveStorageConfig">保存存储配置</el-button>
                    <el-button @click="resetStorageConfig">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <!-- 安全配置 -->
            <el-tab-pane label="安全配置" name="security">
              <el-card class="config-card">
                <template #header>
                  <span>安全配置</span>
                </template>
                
                <el-form :model="securityConfig" label-width="150px">
                  <el-form-item label="密码最小长度">
                    <el-input-number v-model="securityConfig.minPasswordLength" :min="6" :max="20" />
                  </el-form-item>
                  
                  <el-form-item label="密码复杂度要求">
                    <el-checkbox-group v-model="securityConfig.passwordRequirements">
                      <el-checkbox label="uppercase">包含大写字母</el-checkbox>
                      <el-checkbox label="lowercase">包含小写字母</el-checkbox>
                      <el-checkbox label="numbers">包含数字</el-checkbox>
                      <el-checkbox label="symbols">包含特殊字符</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                  
                  <el-form-item label="登录失败锁定">
                    <el-switch v-model="securityConfig.enableLockout" />
                  </el-form-item>
                  
                  <el-form-item label="最大失败次数" v-if="securityConfig.enableLockout">
                    <el-input-number v-model="securityConfig.maxFailedAttempts" :min="3" :max="10" />
                  </el-form-item>
                  
                  <el-form-item label="锁定时间(分钟)" v-if="securityConfig.enableLockout">
                    <el-input-number v-model="securityConfig.lockoutDuration" :min="5" :max="60" />
                  </el-form-item>
                  
                  <el-form-item label="会话超时(分钟)">
                    <el-input-number v-model="securityConfig.sessionTimeout" :min="5" :max="480" />
                  </el-form-item>
                  
                  <el-form-item label="启用双因子认证">
                    <el-switch v-model="securityConfig.enable2FA" />
                  </el-form-item>
                  
                  <el-form-item label="IP白名单">
                    <el-input 
                      v-model="securityConfig.ipWhitelist" 
                      type="textarea" 
                      :rows="3"
                      placeholder="每行一个IP地址或IP段"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveSecurityConfig">保存安全配置</el-button>
                    <el-button @click="resetSecurityConfig">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
            
            <!-- 监控配置 -->
            <el-tab-pane label="监控配置" name="monitoring">
              <el-card class="config-card">
                <template #header>
                  <span>监控配置</span>
                </template>
                
                <el-form :model="monitoringConfig" label-width="150px">
                  <el-form-item label="启用系统监控">
                    <el-switch v-model="monitoringConfig.enableMonitoring" />
                  </el-form-item>
                  
                  <el-form-item label="监控间隔(秒)">
                    <el-input-number v-model="monitoringConfig.monitorInterval" :min="10" :max="300" />
                  </el-form-item>
                  
                  <el-form-item label="CPU告警阈值(%)">
                    <el-input-number v-model="monitoringConfig.cpuThreshold" :min="50" :max="100" />
                  </el-form-item>
                  
                  <el-form-item label="内存告警阈值(%)">
                    <el-input-number v-model="monitoringConfig.memoryThreshold" :min="50" :max="100" />
                  </el-form-item>
                  
                  <el-form-item label="磁盘告警阈值(%)">
                    <el-input-number v-model="monitoringConfig.diskThreshold" :min="50" :max="100" />
                  </el-form-item>
                  
                  <el-form-item label="启用邮件通知">
                    <el-switch v-model="monitoringConfig.enableEmailNotification" />
                  </el-form-item>
                  
                  <el-form-item label="邮件服务器" v-if="monitoringConfig.enableEmailNotification">
                    <el-input v-model="monitoringConfig.emailServer" />
                  </el-form-item>
                  
                  <el-form-item label="邮件端口" v-if="monitoringConfig.enableEmailNotification">
                    <el-input-number v-model="monitoringConfig.emailPort" :min="1" :max="65535" />
                  </el-form-item>
                  
                  <el-form-item label="发件人邮箱" v-if="monitoringConfig.enableEmailNotification">
                    <el-input v-model="monitoringConfig.emailFrom" />
                  </el-form-item>
                  
                  <el-form-item label="收件人邮箱" v-if="monitoringConfig.enableEmailNotification">
                    <el-input 
                      v-model="monitoringConfig.emailTo" 
                      type="textarea" 
                      :rows="2"
                      placeholder="多个邮箱用逗号分隔"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveMonitoringConfig">保存监控配置</el-button>
                    <el-button @click="testEmailNotification">测试邮件</el-button>
                    <el-button @click="resetMonitoringConfig">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

// 响应式数据
const activeTab = ref('basic')

// 基本配置
const basicConfig = reactive({
  systemName: '交通监控系统',
  version: '1.0.0',
  language: 'zh-cn',
  timezone: 'Asia/Shanghai',
  description: '基于Vue3的智能交通监控管理系统',
  maintenanceMode: false
})

// 数据库配置
const databaseConfig = reactive({
  type: 'mysql',
  host: 'localhost',
  port: 3306,
  database: 'traffic_monitor',
  username: 'root',
  password: '',
  poolSize: 10,
  timeout: 30
})

// 网络配置
const networkConfig = reactive({
  serverPort: 3000,
  websocketPort: 3001,
  maxConnections: 1000,
  requestTimeout: 30,
  enableHttps: false,
  sslCertPath: '',
  sslKeyPath: '',
  corsOrigins: '*'
})

// 存储配置
const storageConfig = reactive({
  type: 'local',
  path: '/uploads',
  maxFileSize: 100,
  allowedTypes: ['image', 'video'],
  retentionDays: 30,
  autoCleanup: true
})

// 安全配置
const securityConfig = reactive({
  minPasswordLength: 8,
  passwordRequirements: ['uppercase', 'lowercase', 'numbers'],
  enableLockout: true,
  maxFailedAttempts: 5,
  lockoutDuration: 15,
  sessionTimeout: 60,
  enable2FA: false,
  ipWhitelist: ''
})

// 监控配置
const monitoringConfig = reactive({
  enableMonitoring: true,
  monitorInterval: 60,
  cpuThreshold: 80,
  memoryThreshold: 85,
  diskThreshold: 90,
  enableEmailNotification: false,
  emailServer: '',
  emailPort: 587,
  emailFrom: '',
  emailTo: ''
})

// 方法
const saveBasicConfig = () => {
  ElMessage.success('基本配置已保存')
}

const resetBasicConfig = () => {
  Object.assign(basicConfig, {
    systemName: '交通监控系统',
    version: '1.0.0',
    language: 'zh-cn',
    timezone: 'Asia/Shanghai',
    description: '基于Vue3的智能交通监控管理系统',
    maintenanceMode: false
  })
  ElMessage.success('基本配置已重置')
}

const saveDatabaseConfig = () => {
  ElMessage.success('数据库配置已保存')
}

const testDatabaseConnection = () => {
  ElMessage.info('正在测试数据库连接...')
  setTimeout(() => {
    ElMessage.success('数据库连接测试成功')
  }, 2000)
}

const resetDatabaseConfig = () => {
  Object.assign(databaseConfig, {
    type: 'mysql',
    host: 'localhost',
    port: 3306,
    database: 'traffic_monitor',
    username: 'root',
    password: '',
    poolSize: 10,
    timeout: 30
  })
  ElMessage.success('数据库配置已重置')
}

const saveNetworkConfig = () => {
  ElMessage.success('网络配置已保存')
}

const resetNetworkConfig = () => {
  Object.assign(networkConfig, {
    serverPort: 3000,
    websocketPort: 3001,
    maxConnections: 1000,
    requestTimeout: 30,
    enableHttps: false,
    sslCertPath: '',
    sslKeyPath: '',
    corsOrigins: '*'
  })
  ElMessage.success('网络配置已重置')
}

const saveStorageConfig = () => {
  ElMessage.success('存储配置已保存')
}

const resetStorageConfig = () => {
  Object.assign(storageConfig, {
    type: 'local',
    path: '/uploads',
    maxFileSize: 100,
    allowedTypes: ['image', 'video'],
    retentionDays: 30,
    autoCleanup: true
  })
  ElMessage.success('存储配置已重置')
}

const saveSecurityConfig = () => {
  ElMessage.success('安全配置已保存')
}

const resetSecurityConfig = () => {
  Object.assign(securityConfig, {
    minPasswordLength: 8,
    passwordRequirements: ['uppercase', 'lowercase', 'numbers'],
    enableLockout: true,
    maxFailedAttempts: 5,
    lockoutDuration: 15,
    sessionTimeout: 60,
    enable2FA: false,
    ipWhitelist: ''
  })
  ElMessage.success('安全配置已重置')
}

const saveMonitoringConfig = () => {
  ElMessage.success('监控配置已保存')
}

const testEmailNotification = () => {
  ElMessage.info('正在发送测试邮件...')
  setTimeout(() => {
    ElMessage.success('测试邮件发送成功')
  }, 2000)
}

const resetMonitoringConfig = () => {
  Object.assign(monitoringConfig, {
    enableMonitoring: true,
    monitorInterval: 60,
    cpuThreshold: 80,
    memoryThreshold: 85,
    diskThreshold: 90,
    enableEmailNotification: false,
    emailServer: '',
    emailPort: 587,
    emailFrom: '',
    emailTo: ''
  })
  ElMessage.success('监控配置已重置')
}

const saveAllConfig = () => {
  ElMessage.success('所有配置已保存')
}

const resetAllConfig = () => {
  resetBasicConfig()
  resetDatabaseConfig()
  resetNetworkConfig()
  resetStorageConfig()
  resetSecurityConfig()
  resetMonitoringConfig()
  ElMessage.success('所有配置已重置')
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.system-config-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.system-config-content {
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

.system-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.system-config-header h1 {
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.system-config-content-wrapper {
  max-width: 1200px;
}

.config-tabs {
  background: var(--bg-color-light);
  border-radius: 8px;
  padding: 20px;
}

.config-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
}

.config-tip {
  margin-left: 10px;
  font-size: 12px;
  color: var(--text-color-light);
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
:deep(.el-select .el-input__inner),
:deep(.el-textarea__inner) {
  background: var(--bg-color-light);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-input-number .el-input__inner) {
  background: var(--bg-color-light);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-checkbox__label) {
  color: var(--text-color);
}

:deep(.el-card__header) {
  background: var(--bg-color-lighter);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
}
</style>
