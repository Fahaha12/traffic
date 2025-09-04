<template>
  <div class="layout-sidebar">
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapsed"
      :unique-opened="true"
      :default-openeds="defaultOpeneds"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><Odometer /></el-icon>
        <template #title>控制台</template>
      </el-menu-item>
      
      <el-menu-item index="/map">
        <el-icon><Location /></el-icon>
        <template #title>地图监控</template>
      </el-menu-item>
      
      <el-menu-item index="/cameras">
        <el-icon><VideoCamera /></el-icon>
        <template #title>摄像头管理</template>
      </el-menu-item>
      
      <el-sub-menu index="vehicles">
        <template #title>
          <el-icon><Truck /></el-icon>
          <span>车辆管理</span>
        </template>
        <el-menu-item index="/vehicles/list">
          <el-icon><List /></el-icon>
          <span>车辆列表</span>
        </el-menu-item>
        <el-menu-item index="/vehicles/tracking">
          <el-icon><LocationInformation /></el-icon>
          <span>轨迹追踪</span>
        </el-menu-item>
        <el-menu-item index="/vehicles/suspicious">
          <el-icon><Warning /></el-icon>
          <span>可疑车辆</span>
        </el-menu-item>
      </el-sub-menu>
      
      <el-menu-item index="/analytics">
        <el-icon><DataAnalysis /></el-icon>
        <template #title>数据分析</template>
      </el-menu-item>
      
      <el-menu-item index="/alerts">
        <el-icon><Bell /></el-icon>
        <template #title>告警中心</template>
      </el-menu-item>
      
      <el-sub-menu index="system" v-if="userStore.canManageSystem">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>系统管理</span>
        </template>
        <el-menu-item index="/system/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/system/logs">
          <el-icon><Document /></el-icon>
          <span>系统日志</span>
        </el-menu-item>
        <el-menu-item index="/system/config">
          <el-icon><Tools /></el-icon>
          <span>系统配置</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
    
    <div class="sidebar-footer">
      <el-button 
        type="text" 
        @click="toggleCollapse"
        class="collapse-btn"
      >
        <el-icon>
          <Expand v-if="isCollapsed" />
          <Fold v-else />
        </el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()

const isCollapsed = ref(false)

// 计算属性
const activeMenu = computed(() => {
  return route.path
})

// 默认展开的菜单项
const defaultOpeneds = computed(() => {
  const path = route.path
  if (path.startsWith('/vehicles/')) {
    return ['vehicles']
  } else if (path.startsWith('/system/')) {
    return ['system']
  }
  return []
})

// 方法
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.layout-sidebar {
  width: var(--sidebar-width);
  height: 100%;
  background: var(--bg-color-light);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.layout-sidebar.collapsed {
  width: 64px;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.sidebar-footer {
  padding: 10px;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.collapse-btn {
  width: 100%;
  color: var(--text-color-light);
}

.collapse-btn:hover {
  color: var(--primary-color);
}

:deep(.el-menu) {
  background: transparent;
}

:deep(.el-menu-item) {
  color: var(--text-color-light);
  background: transparent;
}

:deep(.el-menu-item:hover) {
  background: var(--border-color);
  color: var(--text-color);
}

:deep(.el-menu-item.is-active) {
  background: var(--primary-color);
  color: white;
}

:deep(.el-sub-menu__title) {
  color: var(--text-color-light);
  background: transparent;
}

:deep(.el-sub-menu__title:hover) {
  background: var(--border-color);
  color: var(--text-color);
}

:deep(.el-sub-menu .el-menu-item) {
  background: var(--bg-color);
  padding-left: 50px;
  transition: all 0.2s ease;
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background: var(--border-color);
}

:deep(.el-sub-menu .el-menu-item.is-active) {
  background: var(--primary-color);
  color: white;
}

:deep(.el-sub-menu .el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 16px;
}

:deep(.el-sub-menu .el-menu-item span) {
  font-size: 14px;
}

:deep(.el-menu--collapse .el-menu-item span),
:deep(.el-menu--collapse .el-sub-menu__title span) {
  display: none;
}

:deep(.el-menu--collapse .el-sub-menu .el-menu-item) {
  padding-left: 20px;
}

/* 优化子菜单展开动效 */
:deep(.el-sub-menu .el-menu) {
  transition: all 0.3s ease;
}

:deep(.el-sub-menu .el-menu-item) {
  transition: all 0.2s ease;
}

/* 确保图标正确显示 */
:deep(.el-menu-item .el-icon),
:deep(.el-sub-menu__title .el-icon) {
  font-size: 18px;
  margin-right: 8px;
}

/* 子菜单项图标样式 */
:deep(.el-sub-menu .el-menu-item .el-icon) {
  font-size: 16px;
  margin-right: 8px;
  color: inherit;
}

/* 活跃状态的图标颜色 */
:deep(.el-menu-item.is-active .el-icon),
:deep(.el-sub-menu .el-menu-item.is-active .el-icon) {
  color: white;
}
</style>
