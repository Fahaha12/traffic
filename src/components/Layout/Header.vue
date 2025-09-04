<template>
  <header class="layout-header">
    <div class="header-left">
      <div class="logo">
        <el-icon><VideoCamera /></el-icon>
        <span>交通监控系统</span>
      </div>
    </div>
    
    <div class="header-center">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item 
          v-for="item in breadcrumbs" 
          :key="item.path"
          :to="item.path"
        >
          {{ item.name }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    
    <div class="header-right">
      <div class="header-actions">
        <!-- WebSocket连接状态 -->
        <el-tooltip :content="wsStatusText" placement="bottom">
          <el-badge :value="wsStatus" :type="wsStatusType" class="ws-status">
            <el-icon><Connection /></el-icon>
          </el-badge>
        </el-tooltip>
        
        <!-- 全屏按钮 -->
        <el-tooltip content="全屏" placement="bottom">
          <el-button type="text" @click="toggleFullscreen">
            <el-icon><FullScreen /></el-icon>
          </el-button>
        </el-tooltip>
        
        <!-- 主题切换 -->
        <el-tooltip content="切换主题" placement="bottom">
          <el-button type="text" @click="toggleTheme">
            <el-icon><Moon v-if="isDark" /><Sunny v-else /></el-icon>
          </el-button>
        </el-tooltip>
        
        <!-- 用户菜单 -->
        <el-dropdown @command="handleUserCommand">
          <div class="user-info">
            <el-avatar :size="32" :src="userAvatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="username">{{ userStore.user?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人资料
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                系统设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { wsManager } from '@/api/websocket'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isDark = ref(false) // 默认浅色主题

// 计算属性
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    name: item.meta?.title as string,
    path: item.path
  }))
})

const userAvatar = computed(() => {
  // 这里可以根据用户信息返回头像URL
  return ''
})

const wsStatus = computed(() => {
  return wsManager.isConnected ? '●' : '○'
})

const wsStatusType = computed(() => {
  return wsManager.isConnected ? 'success' : 'danger'
})

const wsStatusText = computed(() => {
  return `WebSocket: ${wsManager.connectionState}`
})

// 方法
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  const html = document.documentElement
  if (isDark.value) {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
  // 保存主题设置到localStorage
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人资料页面
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}

// 初始化主题
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
})
</script>

<style scoped>
.layout-header {
  height: var(--header-height);
  background: var(--bg-color-light);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: relative;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-color);
}

.logo .el-icon {
  font-size: 24px;
  color: var(--primary-color);
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.ws-status {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background: var(--border-color);
}

.username {
  color: var(--text-color);
  font-size: 14px;
}

:deep(.el-breadcrumb__item) {
  color: var(--text-color-light);
}

:deep(.el-breadcrumb__item:last-child) {
  color: var(--text-color);
}

:deep(.el-breadcrumb__inner) {
  color: inherit;
}

:deep(.el-breadcrumb__inner:hover) {
  color: var(--primary-color);
}
</style>
