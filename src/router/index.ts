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
      path: '/alerts',
      name: 'AlertCenter',
      component: () => import('@/views/AlertCenter.vue'),
      meta: { 
        title: '告警中心',
        requiresAuth: true,
        permissions: ['alerts:view']
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
    // 车辆管理路由
    {
      path: '/vehicles',
      redirect: '/vehicles/list'
    },
    {
      path: '/vehicles/list',
      name: 'VehicleList',
      component: () => import('@/views/VehicleList.vue'),
      meta: { 
        title: '车辆列表',
        requiresAuth: true,
        permissions: ['vehicle:view']
      }
    },
    {
      path: '/vehicles/tracking',
      name: 'VehicleTracking',
      component: () => import('@/views/VehicleTracking.vue'),
      meta: { 
        title: '轨迹追踪',
        requiresAuth: true,
        permissions: ['vehicle:view']
      }
    },
    {
      path: '/vehicles/suspicious',
      name: 'SuspiciousVehicles',
      component: () => import('@/views/SuspiciousVehicles.vue'),
      meta: { 
        title: '可疑车辆',
        requiresAuth: true,
        permissions: ['vehicle:view']
      }
    },
    // 系统管理路由
    {
      path: '/system/users',
      name: 'SystemUsers',
      component: () => import('@/views/SystemUsers.vue'),
      meta: { 
        title: '用户管理',
        requiresAuth: true,
        permissions: ['system:manage']
      }
    },
    {
      path: '/system/logs',
      name: 'SystemLogs',
      component: () => import('@/views/SystemLogs.vue'),
      meta: { 
        title: '系统日志',
        requiresAuth: true,
        permissions: ['system:manage']
      }
    },
    {
      path: '/system/config',
      name: 'SystemConfig',
      component: () => import('@/views/SystemConfig.vue'),
      meta: { 
        title: '系统配置',
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
  
  // 开发模式：可以选择跳过认证检查或使用真实认证
  if (import.meta.env.DEV && import.meta.env.VITE_SKIP_AUTH === 'true') {
    // 初始化模拟用户数据
    if (!userStore.isAuthenticated) {
      await userStore.initializeMockUser()
    }
    next()
    return
  }
  
  // 真实认证检查
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
    
    // 确保权限已加载
    if (userStore.permissions.length === 0) {
      try {
        await userStore.fetchUserPermissions()
      } catch (error) {
        console.error('获取用户权限失败:', error)
        // 如果权限获取失败，检查是否是admin角色
        if (!userStore.hasRole('admin')) {
          ElMessage.error('获取用户权限失败，请重新登录')
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }
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
  
  next()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  ElMessage.error('页面加载失败，请刷新重试')
})

export default router
