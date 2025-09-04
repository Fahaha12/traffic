import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLayoutStore = defineStore('layout', () => {
  // 状态
  const isSidebarCollapsed = ref(false)

  // 方法
  const toggleSidebar = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
  }

  const setSidebarCollapsed = (collapsed: boolean) => {
    isSidebarCollapsed.value = collapsed
  }

  return {
    // 状态
    isSidebarCollapsed,
    
    // 方法
    toggleSidebar,
    setSidebarCollapsed
  }
})
