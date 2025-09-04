import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { 
        title: '登录',
        requiresAuth: false,
        hideForAuth: true // 已登录用户隐藏此页面
      }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { 
        title: '仪表板',
        requiresAuth: true,
        permissions: ['dashboard:view']
      }
    },
    {
      path: '/map',
      name: 'MapView',
      component: () => import('@/views/MapView.vue'),
      meta: { 
        title: '地图视图',
        requiresAuth: true,
        permissions: ['map:view']
      }
    },
    {
      path: '/cameras',
      name: 'CameraView',
      component: () => import('@/views/CameraView.vue'),
      meta: { 
        title: '摄像头管理',
        requiresAuth: true,
        permissions: ['camera:view']
      }
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: () => import('@/views/Analytics.vue'),
      meta: { 
        title: '数据分析',
        requiresAuth: true,
        permissions: ['analytics:view']
      }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('@/views/Settings.vue'),
      meta: { 
        title: '系统设置',
        requiresAuth: true,
        permissions: ['system:manage']
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: {
        title: '页面未找到',
        requiresAuth: false
      }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 交通监控系统`
  }
  
  // 开发模式：跳过认证检查，直接进入主界面
  if (import.meta.env.DEV) {
    // 初始化模拟用户数据
    if (!userStore.isAuthenticated) {
      await userStore.initializeMockUser()
    }
    next()
    return
  }
  
  // 生产环境的认证检查（暂时注释掉）
  /*
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    // 检查是否已登录
    if (!userStore.isAuthenticated) {
      // 尝试从localStorage恢复用户状态
      await userStore.initialize()
      
      if (!userStore.isAuthenticated) {
        ElMessage.warning('请先登录')
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }
    
    // 检查权限
    if (to.meta.permissions && Array.isArray(to.meta.permissions)) {
      const hasPermission = to.meta.permissions.some(permission => 
        userStore.hasPermission(permission)
      )
      
      if (!hasPermission) {
        ElMessage.error('您没有访问此页面的权限')
        next('/dashboard') // 重定向到仪表板
        return
      }
    }
  }
  
  // 如果已登录用户访问登录页面，重定向到仪表板
  if (to.meta.hideForAuth && userStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  */
  
  next()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  ElMessage.error('页面加载失败，请刷新重试')
})

export default router
