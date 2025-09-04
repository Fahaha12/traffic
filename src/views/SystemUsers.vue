<template>
  <div class="system-users-view">
    <LayoutHeader />
    <div class="system-users-content">
      <LayoutSidebar />
      <div class="main-content">
        <div class="system-users-header">
          <h1>用户管理</h1>
          <div class="header-actions">
            <el-button type="primary" @click="showAddUserDialog = true">
              <el-icon><Plus /></el-icon>
              添加用户
            </el-button>
            <el-button @click="refreshUsers">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
        
        <div class="system-users-content-wrapper">
          <!-- 用户筛选 -->
          <div class="user-filters">
            <el-card>
              <el-form :model="filters" inline>
                <el-form-item label="用户名">
                  <el-input v-model="filters.username" placeholder="请输入用户名" clearable />
                </el-form-item>
                
                <el-form-item label="角色">
                  <el-select v-model="filters.role" placeholder="全部角色" clearable>
                    <el-option label="管理员" value="admin" />
                    <el-option label="操作员" value="operator" />
                    <el-option label="查看者" value="viewer" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="状态">
                  <el-select v-model="filters.status" placeholder="全部状态" clearable>
                    <el-option label="正常" value="active" />
                    <el-option label="禁用" value="disabled" />
                    <el-option label="锁定" value="locked" />
                  </el-select>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="applyFilters">筛选</el-button>
                  <el-button @click="resetFilters">重置</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
          
          <!-- 用户列表 -->
          <div class="user-list">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>用户列表 ({{ totalUsers }} 个)</span>
                </div>
              </template>
              
              <el-table 
                :data="filteredUsers" 
                style="width: 100%"
              >
                <el-table-column prop="username" label="用户名" width="120" />
                
                <el-table-column prop="email" label="邮箱" width="200" />
                
                <el-table-column prop="phone" label="手机号" width="130" />
                
                <el-table-column prop="role" label="角色" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getRoleTagType(row.role)" size="small">
                      {{ getRoleText(row.role) }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column prop="department" label="部门" width="120" />
                
                <el-table-column prop="position" label="职位" width="120" />
                
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getStatusTagType(row.status)" size="small">
                      {{ getStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column prop="lastLogin" label="最后登录" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.lastLogin) }}
                  </template>
                </el-table-column>
                
                <el-table-column prop="createTime" label="创建时间" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.createTime) }}
                  </template>
                </el-table-column>
                
                <el-table-column label="操作" width="250" fixed="right">
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
                      @click="toggleUserStatus(row)"
                      :class="{ 'danger': row.status === 'active' }"
                    >
                      {{ row.status === 'active' ? '禁用' : '启用' }}
                    </el-button>
                    <el-button 
                      type="text" 
                      size="small" 
                      class="danger"
                      @click="deleteUser(row)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 分页 -->
              <div class="pagination-wrapper">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[10, 20, 50, 100]"
                  :total="totalUsers"
                  layout="total, sizes, prev, pager, next, jumper"
                  @size-change="handleSizeChange"
                  @current-change="handleCurrentChange"
                />
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="showAddUserDialog"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="600px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="操作员" value="operator" />
            <el-option label="查看者" value="viewer" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" />
        </el-form-item>
        
        <el-form-item label="职位" prop="position">
          <el-input v-model="userForm.position" />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="userForm.status" style="width: 100%">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
            <el-option label="锁定" value="locked" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddUserDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import LayoutHeader from '@/components/Layout/Header.vue'
import LayoutSidebar from '@/components/Layout/Sidebar.vue'
import { dateUtils } from '@/utils/dateUtils'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()

// 响应式数据
const users = ref([
  {
    id: '1',
    username: 'admin',
    email: 'admin@traffic-monitor.com',
    phone: '13800138000',
    role: 'admin',
    department: '技术部',
    position: '系统管理员',
    status: 'active',
    lastLogin: new Date().toISOString(),
    createTime: new Date(Date.now() - 86400000 * 30).toISOString()
  },
  {
    id: '2',
    username: 'operator1',
    email: 'operator1@traffic-monitor.com',
    phone: '13800138001',
    role: 'operator',
    department: '运营部',
    position: '操作员',
    status: 'active',
    lastLogin: new Date(Date.now() - 3600000).toISOString(),
    createTime: new Date(Date.now() - 86400000 * 15).toISOString()
  },
  {
    id: '3',
    username: 'viewer1',
    email: 'viewer1@traffic-monitor.com',
    phone: '13800138002',
    role: 'viewer',
    department: '监控部',
    position: '监控员',
    status: 'active',
    lastLogin: new Date(Date.now() - 7200000).toISOString(),
    createTime: new Date(Date.now() - 86400000 * 7).toISOString()
  },
  {
    id: '4',
    username: 'test_user',
    email: 'test@traffic-monitor.com',
    phone: '13800138003',
    role: 'viewer',
    department: '测试部',
    position: '测试员',
    status: 'disabled',
    lastLogin: new Date(Date.now() - 86400000 * 3).toISOString(),
    createTime: new Date(Date.now() - 86400000 * 2).toISOString()
  }
])

const filters = reactive({
  username: '',
  role: '',
  status: ''
})

const currentPage = ref(1)
const pageSize = ref(20)
const showAddUserDialog = ref(false)
const isEdit = ref(false)
const userFormRef = ref()

const userForm = reactive({
  id: '',
  username: '',
  email: '',
  phone: '',
  password: '',
  role: 'viewer',
  department: '',
  position: '',
  status: 'active'
})

const userRules = {
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
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  department: [
    { required: true, message: '请输入部门', trigger: 'blur' }
  ],
  position: [
    { required: true, message: '请输入职位', trigger: 'blur' }
  ]
}

// 计算属性
const totalUsers = computed(() => filteredUsers.value.length)

const filteredUsers = computed(() => {
  let result = users.value
  
  if (filters.username) {
    result = result.filter(user => 
      user.username.toLowerCase().includes(filters.username.toLowerCase())
    )
  }
  
  if (filters.role) {
    result = result.filter(user => user.role === filters.role)
  }
  
  if (filters.status) {
    result = result.filter(user => user.status === filters.status)
  }
  
  return result
})

// 方法
const getRoleText = (role: string) => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    operator: '操作员',
    viewer: '查看者'
  }
  return roleMap[role] || role
}

const getRoleTagType = (role: string) => {
  const typeMap: Record<string, string> = {
    admin: 'danger',
    operator: 'warning',
    viewer: 'info'
  }
  return typeMap[role] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '正常',
    disabled: '禁用',
    locked: '锁定'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    disabled: 'info',
    locked: 'danger'
  }
  return typeMap[status] || 'info'
}

const formatTime = (timestamp: string) => {
  return dateUtils.formatDateTime(timestamp)
}

const applyFilters = () => {
  currentPage.value = 1
  ElMessage.success('筛选条件已应用')
}

const resetFilters = () => {
  Object.assign(filters, {
    username: '',
    role: '',
    status: ''
  })
  currentPage.value = 1
  ElMessage.success('筛选条件已重置')
}

const refreshUsers = () => {
  ElMessage.success('用户列表已刷新')
}

const editUser = (user: any) => {
  isEdit.value = true
  Object.assign(userForm, user)
  showAddUserDialog.value = true
}

const saveUser = async () => {
  try {
    await userFormRef.value.validate()
    
    if (isEdit.value) {
      // 编辑用户
      const index = users.value.findIndex(u => u.id === userForm.id)
      if (index > -1) {
        users.value[index] = { ...users.value[index], ...userForm }
        ElMessage.success('用户信息已更新')
      }
    } else {
      // 添加用户
      const newUser = {
        ...userForm,
        id: Date.now().toString(),
        lastLogin: new Date().toISOString(),
        createTime: new Date().toISOString()
      }
      users.value.push(newUser)
      ElMessage.success('用户添加成功')
    }
    
    showAddUserDialog.value = false
    resetUserForm()
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const resetUserForm = () => {
  Object.assign(userForm, {
    id: '',
    username: '',
    email: '',
    phone: '',
    password: '',
    role: 'viewer',
    department: '',
    position: '',
    status: 'active'
  })
  isEdit.value = false
}

const resetPassword = async (user: any) => {
  try {
    await ElMessageBox.confirm('确定要重置该用户的密码吗？', '确认重置', {
      type: 'warning'
    })
    
    ElMessage.success('密码重置成功，新密码已发送到用户邮箱')
  } catch {
    // 用户取消重置
  }
}

const toggleUserStatus = async (user: any) => {
  const action = user.status === 'active' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}该用户吗？`, `确认${action}`, {
      type: 'warning'
    })
    
    user.status = user.status === 'active' ? 'disabled' : 'active'
    ElMessage.success(`用户已${action}`)
  } catch {
    // 用户取消操作
  }
}

const deleteUser = async (user: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？此操作不可恢复！', '确认删除', {
      type: 'warning'
    })
    
    const index = users.value.findIndex(u => u.id === user.id)
    if (index > -1) {
      users.value.splice(index, 1)
      ElMessage.success('用户删除成功')
    }
  } catch {
    // 用户取消删除
  }
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.system-users-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.system-users-content {
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

.system-users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.system-users-header h1 {
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.system-users-content-wrapper {
  max-width: 1400px;
}

.user-filters {
  margin-bottom: 20px;
}

.user-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.danger {
  color: var(--danger-color);
}

:deep(.el-table th),
:deep(.el-table td) {
  background: var(--bg-color-light);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-table__header-wrapper) {
  background: var(--bg-color-light);
}

:deep(.el-card) {
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
}

:deep(.el-card__header) {
  background: var(--bg-color-lighter);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
}

:deep(.el-form-item__label) {
  color: var(--text-color);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  background: var(--bg-color);
  border-color: var(--border-color);
  color: var(--text-color);
}
</style>
