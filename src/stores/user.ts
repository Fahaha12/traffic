import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { User, SystemConfig } from '@/types'
import type { UserInfo, LoginData, UserState } from '@/types/user'
import { 
  login as apiLogin, 
  logout as apiLogout, 
  getUserInfo, 
  refreshToken,
  validateToken,
  getUserPermissions 
} from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const systemConfig = ref<SystemConfig>({
    mapProvider: 'leaflet',
    defaultZoom: 12,
    maxCameras: 50,
    videoQuality: 'medium',
    alertSound: true,
    autoRefresh: true,
    refreshInterval: 5000,
    defaultCenter: [34.7466, 113.6253] // 郑州市政府
  })
  const isLoading = ref(false)

  // 计算属性
  const userRole = computed(() => user.value?.role || 'viewer')
  const userPermissions = computed(() => user.value?.permissions || [])
  const canManageCameras = computed(() => 
    userPermissions.value.includes('camera:manage')
  )
  const canViewAlerts = computed(() => 
    userPermissions.value.includes('alert:view')
  )
  const canManageSystem = computed(() => 
    userPermissions.value.includes('system:manage')
  )

  // 认证相关状态
  const token = ref(localStorage.getItem('token') || '')
  const refreshTokenValue = ref(localStorage.getItem('refreshToken') || '')
  const userInfo = ref<UserInfo | null>(null)
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])

  // 方法
  const login = async (loginData: LoginData) => {
    isLoading.value = true
    try {
      const response = await apiLogin(loginData)
      const { token: newToken, refreshToken: newRefreshToken, userInfo: newUserInfo, expiresIn } = response.data
      
      // 存储token和用户信息
      token.value = newToken
      refreshTokenValue.value = newRefreshToken
      userInfo.value = newUserInfo
      isAuthenticated.value = true
      
      // 存储到localStorage
      localStorage.setItem('token', newToken)
      localStorage.setItem('refreshToken', newRefreshToken)
      localStorage.setItem('userInfo', JSON.stringify(newUserInfo))
      
      // 获取用户权限
      await fetchUserPermissions()
      
      // 设置token过期时间
      if (expiresIn) {
        const expireTime = Date.now() + expiresIn * 1000
        localStorage.setItem('tokenExpireTime', expireTime.toString())
      }
      
      ElMessage.success('登录成功！')
      return { success: true }
    } catch (error: any) {
      console.error('Login failed:', error)
      ElMessage.error(error.response?.data?.message || '登录失败，请检查用户名和密码')
      logout()
      return { success: false, error: error.response?.data?.message || '登录失败' }
    } finally {
      isLoading.value = false
    }
  }

  // 获取用户权限
  const fetchUserPermissions = async () => {
    try {
      const response = await getUserPermissions()
      permissions.value = response.data.permissions
      roles.value = response.data.roles
      return response.data
    } catch (error) {
      console.error('Failed to fetch user permissions:', error)
      throw error
    }
  }

  // 刷新token
  const refreshUserToken = async () => {
    try {
      if (!refreshTokenValue.value) {
        throw new Error('No refresh token available')
      }
      
      const response = await refreshToken(refreshTokenValue.value)
      const { token: newToken, expiresIn } = response.data
      
      token.value = newToken
      localStorage.setItem('token', newToken)
      
      if (expiresIn) {
        const expireTime = Date.now() + expiresIn * 1000
        localStorage.setItem('tokenExpireTime', expireTime.toString())
      }
      
      return newToken
    } catch (error) {
      console.error('Failed to refresh token:', error)
      logout()
      throw error
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await apiLogout()
      }
    } catch (error) {
      console.error('Logout API failed:', error)
    } finally {
      // 清除所有状态
      user.value = null
      userInfo.value = null
      isAuthenticated.value = false
      token.value = ''
      refreshTokenValue.value = ''
      permissions.value = []
      roles.value = []
      
      // 清除localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('tokenExpireTime')
      
      ElMessage.success('已退出登录')
    }
  }

  // 初始化用户状态（从localStorage恢复）
  const initialize = async () => {
    const savedToken = localStorage.getItem('token')
    const savedRefreshToken = localStorage.getItem('refreshToken')
    const savedUserInfo = localStorage.getItem('userInfo')
    const tokenExpireTime = localStorage.getItem('tokenExpireTime')
    
    if (savedToken && savedRefreshToken && savedUserInfo) {
      // 检查token是否过期
      if (tokenExpireTime && Date.now() > parseInt(tokenExpireTime)) {
        // token已过期，尝试刷新
        try {
          await refreshUserToken()
          userInfo.value = JSON.parse(savedUserInfo)
          isAuthenticated.value = true
          await fetchUserPermissions()
        } catch (error) {
          logout()
        }
      } else {
        // token未过期，直接恢复状态
        token.value = savedToken
        refreshTokenValue.value = savedRefreshToken
        userInfo.value = JSON.parse(savedUserInfo)
        isAuthenticated.value = true
        await fetchUserPermissions()
      }
    }
    
    // 从本地存储恢复系统配置
    const savedConfig = localStorage.getItem('systemConfig')
    if (savedConfig) {
      try {
        systemConfig.value = { ...systemConfig.value, ...JSON.parse(savedConfig) }
      } catch (error) {
        console.error('恢复系统配置失败:', error)
      }
    }
  }

  const updateSystemConfig = (config: Partial<SystemConfig>) => {
    systemConfig.value = { ...systemConfig.value, ...config }
    localStorage.setItem('systemConfig', JSON.stringify(systemConfig.value))
  }

  const hasPermission = (permission: string) => {
    return permissions.value.includes(permission) || roles.value.includes('admin')
  }

  const hasRole = (role: string) => {
    return roles.value.includes(role)
  }

  const checkAuth = () => {
    if (!token.value) {
      logout()
      return false
    }
    return true
  }

  // 验证token有效性
  const validateUserToken = async () => {
    try {
      if (!token.value) {
        return false
      }
      
      const response = await validateToken()
      if (response.data.valid && response.data.userInfo) {
        userInfo.value = response.data.userInfo
        isAuthenticated.value = true
        return true
      } else {
        logout()
        return false
      }
    } catch (error) {
      console.error('Token validation failed:', error)
      logout()
      return false
    }
  }

  // 初始化模拟用户数据（开发环境使用）
  const initializeMockUser = async () => {
    const mockUserInfo: UserInfo = {
      id: '1',
      username: 'admin',
      email: 'admin@traffic-monitor.com',
      phone: '13800138000',
      avatar: '',
      roles: ['admin'],
                   permissions: [
               'dashboard:view',
               'map:view',
               'camera:view',
               'camera:manage',
               'vehicle:view',
               'vehicle:manage',
               'analytics:view',
               'alerts:view',
               'alerts:manage',
               'system:manage'
             ],
      department: '技术部',
      position: '系统管理员',
      lastLoginTime: new Date().toISOString(),
      createTime: new Date().toISOString()
    }

    // 设置模拟数据
    userInfo.value = mockUserInfo
    isAuthenticated.value = true
    token.value = 'mock-token-' + Date.now()
    refreshTokenValue.value = 'mock-refresh-token-' + Date.now()
    permissions.value = mockUserInfo.permissions
    roles.value = mockUserInfo.roles

    // 同时设置旧的user对象以保持兼容性
    user.value = {
      id: mockUserInfo.id,
      username: mockUserInfo.username,
      role: 'admin',
      permissions: mockUserInfo.permissions,
      lastLogin: mockUserInfo.lastLoginTime || new Date().toISOString()
    }

    console.log('模拟用户数据已初始化:', mockUserInfo)
  }

  return {
    // 状态
    user,
    isAuthenticated,
    systemConfig,
    isLoading,
    token,
    refreshToken: refreshTokenValue,
    userInfo,
    permissions,
    roles,
    
    // 计算属性
    userRole,
    userPermissions,
    canManageCameras,
    canViewAlerts,
    canManageSystem,
    
    // 方法
    login,
    logout,
    initialize,
    updateSystemConfig,
    hasPermission,
    hasRole,
    checkAuth,
    fetchUserPermissions,
    refreshUserToken,
    validateUserToken,
    initializeMockUser
  }
})
