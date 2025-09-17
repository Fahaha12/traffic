# 登录验证功能使用指南

## 功能概述

交通监控系统现已集成完整的JWT认证系统，支持用户登录、权限管理和路由守卫。

## 测试账号

### 管理员账号
- **用户名**: `admin`
- **密码**: `admin123`
- **权限**: 所有功能权限

### 操作员账号
- **用户名**: `operator`
- **密码**: `operator123`
- **权限**: 查看权限（无管理权限）

## 功能特性

### 1. 后端认证API

#### 登录接口
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例**:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userInfo": {
    "id": 1,
    "username": "admin",
    "email": "admin@traffic-monitor.com",
    "phone": "13800138000",
    "role": "admin",
    "permissions": ["dashboard:view", "map:view", ...],
    "department": "技术部",
    "position": "系统管理员",
    "lastLoginTime": "2025-09-17T02:05:42.766901",
    "createTime": "2024-01-01T00:00:00Z"
  },
  "expiresIn": 86400
}
```

#### 其他认证接口
- `GET /api/auth/profile` - 获取用户信息
- `GET /api/auth/permissions` - 获取用户权限
- `POST /api/auth/refresh` - 刷新token
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/validate` - 验证token有效性

### 2. 前端功能

#### 路由守卫
- 自动检查用户认证状态
- 根据权限控制页面访问
- 未登录用户自动跳转到登录页
- 已登录用户访问登录页自动跳转到仪表板

#### 权限管理
- 基于角色的权限控制（RBAC）
- 细粒度权限控制
- 动态权限验证

#### 用户状态管理
- 自动保存登录状态
- Token自动刷新
- 登出时清除所有状态

### 3. 权限列表

#### 管理员权限
- `dashboard:view` - 查看仪表板
- `map:view` - 查看地图
- `camera:view` - 查看摄像头
- `camera:manage` - 管理摄像头
- `vehicle:view` - 查看车辆
- `vehicle:manage` - 管理车辆
- `analytics:view` - 查看分析
- `alerts:view` - 查看告警
- `alerts:manage` - 管理告警
- `system:manage` - 系统管理

#### 操作员权限
- `dashboard:view` - 查看仪表板
- `map:view` - 查看地图
- `camera:view` - 查看摄像头
- `vehicle:view` - 查看车辆
- `analytics:view` - 查看分析
- `alerts:view` - 查看告警

## 使用说明

### 1. 启动系统

```bash
# 启动后端
cd backend
python app.py

# 启动前端
npm run dev
```

### 2. 访问系统

1. 打开浏览器访问 `http://localhost:3000`
2. 系统会自动跳转到登录页面
3. 使用测试账号登录
4. 登录成功后跳转到仪表板

### 3. 测试不同权限

1. 使用管理员账号登录，可以访问所有功能
2. 使用操作员账号登录，只能访问查看功能
3. 尝试直接访问需要权限的页面，系统会进行权限检查

### 4. 开发模式

如果需要跳过认证（仅开发使用），可以设置环境变量：
```bash
VITE_SKIP_AUTH=true npm run dev
```

## 技术实现

### 后端技术
- Flask + Flask-JWT-Extended
- JWT Token认证
- 基于角色的权限控制
- 模拟用户数据库

### 前端技术
- Vue 3 + TypeScript
- Pinia状态管理
- Vue Router路由守卫
- Element Plus UI组件

### 安全特性
- JWT Token过期机制
- 自动Token刷新
- 权限验证中间件
- 安全的密码处理

## 注意事项

1. 当前使用模拟用户数据，生产环境需要连接真实数据库
2. 密码未进行哈希处理，生产环境需要加密存储
3. Token未实现黑名单机制，生产环境建议使用Redis
4. 建议在生产环境中使用HTTPS

## 故障排除

### 常见问题

1. **登录失败**
   - 检查用户名和密码是否正确
   - 检查后端服务是否正常运行
   - 查看浏览器控制台错误信息

2. **权限不足**
   - 确认用户角色和权限设置
   - 检查路由权限配置

3. **Token过期**
   - 系统会自动刷新Token
   - 如果刷新失败，需要重新登录

4. **API调用失败**
   - 检查网络连接
   - 确认后端服务状态
   - 查看API响应错误信息
