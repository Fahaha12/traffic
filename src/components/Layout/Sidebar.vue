<template>
  <div class="layout-sidebar">
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapsed"
      :unique-opened="true"
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
        <el-menu-item index="/vehicles/list">车辆列表</el-menu-item>
        <el-menu-item index="/vehicles/tracking">轨迹追踪</el-menu-item>
        <el-menu-item index="/vehicles/suspicious">可疑车辆</el-menu-item>
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
        <el-menu-item index="/system/users">用户管理</el-menu-item>
        <el-menu-item index="/system/logs">系统日志</el-menu-item>
        <el-menu-item index="/system/config">系统配置</el-menu-item>
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
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background: var(--border-color);
}

:deep(.el-sub-menu .el-menu-item.is-active) {
  background: var(--primary-color);
  color: white;
}

:deep(.el-menu--collapse .el-menu-item span),
:deep(.el-menu--collapse .el-sub-menu__title span) {
  display: none;
}

:deep(.el-menu--collapse .el-sub-menu .el-menu-item) {
  padding-left: 20px;
}
</style>
