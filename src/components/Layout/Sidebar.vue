<template>
  <div class="layout-sidebar" :class="{ collapsed: isCollapsed }">
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
          <el-icon><Van /></el-icon>
          <span>车辆管理</span>
        </template>
        <el-menu-item index="/vehicles/list">
          <el-icon><List /></el-icon>
          <template #title>车辆列表</template>
        </el-menu-item>
        <el-menu-item index="/vehicles/tracking">
          <el-icon><LocationInformation /></el-icon>
          <template #title>轨迹追踪</template>
        </el-menu-item>
        <el-menu-item index="/vehicles/suspicious">
          <el-icon><Warning /></el-icon>
          <template #title>可疑车辆</template>
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
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/system/logs">
          <el-icon><Document /></el-icon>
          <template #title>系统日志</template>
        </el-menu-item>
        <el-menu-item index="/system/config">
          <el-icon><Tools /></el-icon>
          <template #title>系统配置</template>
        </el-menu-item>
      </el-sub-menu>
      
    </el-menu>
    
    <!-- 紧凑的折叠按钮 -->
    <div class="sidebar-collapse-btn" @click="toggleCollapse">
      <el-icon>
        <Expand v-if="isCollapsed" />
        <Fold v-else />
      </el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useLayoutStore } from '@/stores/layout'
import { Van } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()
const layoutStore = useLayoutStore()

const isCollapsed = computed(() => layoutStore.isSidebarCollapsed)

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
  layoutStore.toggleSidebar()
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
  flex-shrink: 0;
  position: relative;
  padding-bottom: 32px;
}

.layout-sidebar.collapsed {
  width: 64px;
}

.layout-sidebar.collapsed .sidebar-collapse-btn {
  width: 64px;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
}

/* 折叠按钮 */
.sidebar-collapse-btn {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 32px;
  background: var(--bg-color-light);
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-color-light);
  font-size: 14px;
  transition: all 0.3s ease;
  z-index: 10;
  box-sizing: border-box;
}

.sidebar-collapse-btn:hover {
  background: var(--border-color);
  color: var(--primary-color);
}

.sidebar-collapse-btn .el-icon {
  font-size: 16px;
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
  display: inline-block;
}

/* 确保子菜单项图标显示 */
:deep(.el-sub-menu .el-menu-item) {
  display: flex;
  align-items: center;
}

:deep(.el-sub-menu .el-menu-item .el-icon) {
  flex-shrink: 0;
}

/* 活跃状态的图标颜色 */
:deep(.el-menu-item.is-active .el-icon),
:deep(.el-sub-menu .el-menu-item.is-active .el-icon) {
  color: white;
}
</style>
