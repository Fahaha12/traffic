<template>
  <div class="system-users-view">
    <LayoutHeader />
    <div class="users-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="users-header">
          <h1>用户管理</h1>
          <div class="header-actions">
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              添加用户
            </el-button>
          </div>
        </div>
        
        <div class="users-stats">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon total">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ totalUsers }}</div>
                    <div class="stat-label">总用户数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon online">
                    <el-icon><UserFilled /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ onlineUsers }}</div>
                    <div class="stat-label">在线用户</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon admin">
                    <el-icon><Avatar /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ adminUsers }}</div>
                    <div class="stat-label">管理员</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon operator">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ operatorUsers }}</div>
                    <div class="stat-label">操作员</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="users-table">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>用户列表</span>
                <div class="header-actions">
                  <el-input
                    v-model="searchKeyword"
                    placeholder="搜索用户名、邮箱"
                    style="width: 300px"
                    clearable
                    @input="handleSearch"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </div>
              </div>
            </template>
            
            <el-table 
              :data="filteredUsers" 
              style="width: 100%"
              v-loading="loading"
            >
              <el-table-column prop="username" label="用户名" width="150" />
              <el-table-column prop="email" label="邮箱" width="200" />
              <el-table-column prop="phone" label="手机号" width="150" />
              <el-table-column prop="role" label="角色" width="120">
                <template #default="{ row }">
                  <el-tag :type="getRoleType(row.role)" size="small">
                    {{ getRoleText(row.role) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="department" label="部门" width="120" />
              <el-table-column prop="position" label="职位" width="120" />
              <el-table-column prop="lastLoginTime" label="最后登录" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.lastLoginTime) }}
                </template>
              </el-table-column>
              <el-table-column prop="createTime" label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.createTime) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button type="text" size="small" @click="editUser(row)">
                    编辑
                  </el-button>
                  <el-button type="text" size="small" @click="resetPassword(row)">
                    重置密码
                  </el-button>
                  <el-button 
                    type="text" 
                    size="small" 
                    @click="deleteUser(row)"
                    v-if="row.id !== currentUser?.id"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </div>
    </div>
    
    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="formData.phone" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="操作员" value="operator" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-input v-model="formData.department" />
        </el-form-item>
        <el-form-item label="职位" prop="position">
          <el-input v-model="formData.position" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="formData.password" type="password" show-password />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="formLoading">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, User, UserFilled, Avatar, Search } from '@element-plus/icons-vue'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { useUserStore } from '@/stores/user'
import { dateUtils } from '@/utils/dateUtils'

const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const searchKeyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const formLoading = ref(false)
const formRef = ref<FormInstance>()

// 统计数据
const totalUsers = ref(0)
const onlineUsers = ref(0)
const adminUsers = ref(0)
const operatorUsers = ref(0)

// 用户列表
const users = ref<any[]>([])
const currentUser = computed(() => userStore.userInfo)

// 表单数据
const formData = reactive({
  id: '',
  username: '',
  email: '',
  phone: '',
  role: 'operator',
  department: '',
  position: '',
  password: ''
})

// 表单验证规则
const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  department: [
    { required: true, message: '请输入部门', trigger: 'blur' }
  ],
  position: [
    { required: true, message: '请输入职位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const filteredUsers = computed(() => {
  if (!searchKeyword.value) return users.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(keyword) ||
    user.email.toLowerCase().includes(keyword)
  )
})

// 方法
const loadUsers = async () => {
  try {
    loading.value = true
    // 模拟数据，实际应该调用API
    users.value = [
      {
        id: 1,
        username: 'admin',
        email: 'admin@traffic-monitor.com',
        phone: '13800138000',
        role: 'admin',
        department: '技术部',
        position: '系统管理员',
        lastLoginTime: '2024-01-15T10:30:00Z',
        createTime: '2024-01-01T00:00:00Z'
      },
      {
        id: 2,
        username: 'operator',
        email: 'operator@traffic-monitor.com',
        phone: '13800138001',
        role: 'operator',
        department: '运营部',
        position: '操作员',
        lastLoginTime: '2024-01-15T09:15:00Z',
        createTime: '2024-01-01T00:00:00Z'
      }
    ]
    
    // 更新统计数据
    totalUsers.value = users.value.length
    onlineUsers.value = users.value.filter(u => u.lastLoginTime).length
    adminUsers.value = users.value.filter(u => u.role === 'admin').length
    operatorUsers.value = users.value.filter(u => u.role === 'operator').length
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  dialogVisible.value = true
  resetForm()
}

const editUser = (user: any) => {
  isEdit.value = true
  dialogVisible.value = true
  Object.assign(formData, user)
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(formData, {
    id: '',
    username: '',
    email: '',
    phone: '',
    role: 'operator',
    department: '',
    position: '',
    password: ''
  })
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    formLoading.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (isEdit.value) {
      ElMessage.success('用户更新成功')
    } else {
      ElMessage.success('用户创建成功')
    }
    
    dialogVisible.value = false
    loadUsers()
  } catch (error) {
    console.error('提交表单失败:', error)
  } finally {
    formLoading.value = false
  }
}

const resetPassword = async (user: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户 ${user.username} 的密码吗？`,
      '重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('密码重置成功，新密码已发送到用户邮箱')
  } catch (error) {
    // 用户取消
  }
}

const deleteUser = async (user: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 ${user.username} 吗？此操作不可恢复！`,
      '删除用户',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('用户删除成功')
    loadUsers()
  } catch (error) {
    // 用户取消
  }
}

const handleSearch = () => {
  // 搜索逻辑在computed中处理
}

const getRoleType = (role: string) => {
  switch (role) {
    case 'admin': return 'danger'
    case 'operator': return 'primary'
    default: return 'info'
  }
}

const getRoleText = (role: string) => {
  switch (role) {
    case 'admin': return '管理员'
    case 'operator': return '操作员'
    default: return '未知'
  }
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatTime(timestamp)
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.system-users-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.users-content {
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

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.users-header h1 {
  color: var(--text-color);
  margin: 0;
}

.users-stats {
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.total {
  background: var(--primary-color);
}

.stat-icon.online {
  background: var(--success-color);
}

.stat-icon.admin {
  background: var(--danger-color);
}

.stat-icon.operator {
  background: var(--warning-color);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--text-color-light);
  margin-top: 5px;
}

.users-table {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th),
:deep(.el-table td) {
  padding: 8px 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>