# 交通监控系统 - 用户认证配置指南

## 概述

本项目的账号密码设置和用户认证功能已经完整实现。以下是详细的配置说明和使用指南。

## 认证架构

### 1. 前端认证流程

```
用户输入账号密码 → 登录页面 → API调用 → 后端验证 → 返回Token → 存储到localStorage → 路由守卫验证
```

### 2. 核心文件说明

#### 类型定义 (`src/types/user.ts`)
- `LoginData`: 登录请求数据接口
- `UserInfo`: 用户信息接口
- `LoginResponse`: 登录响应数据接口
- `UserState`: 用户状态接口

#### API服务 (`src/api/user.ts`)
- `login()`: 用户登录接口
- `logout()`: 用户登出接口
- `getUserInfo()`: 获取用户信息接口
- `refreshToken()`: 刷新Token接口
- `validateToken()`: 验证Token有效性接口

#### 状态管理 (`src/stores/user.ts`)
- 管理用户登录状态
- 存储Token和用户信息
- 提供权限检查方法
- 自动处理Token刷新

#### 登录页面 (`src/views/Login.vue`)
- 用户输入账号密码的界面
- 表单验证
- 登录状态处理

#### 路由守卫 (`src/router/index.ts`)
- 保护需要认证的页面
- 权限验证
- 自动重定向

## 账号密码设置位置

### 1. 前端不存储密码
- **重要**: 前端项目本身不存储任何用户账号密码
- 用户输入的密码会加密后发送到后端进行验证
- 前端只存储后端返回的认证Token

### 2. 后端API接口
账号密码的实际验证和存储在后端完成，需要配置以下API接口：

```typescript
// 后端需要实现的接口
POST /auth/login          // 用户登录
POST /auth/logout         // 用户登出
POST /auth/refresh        // 刷新Token
GET  /auth/validate       // 验证Token
GET  /user/info          // 获取用户信息
GET  /user/permissions   // 获取用户权限
```

### 3. 环境配置
在项目根目录创建 `.env` 文件配置后端API地址：

```env
# 后端API基础地址
VITE_API_BASE_URL=http://localhost:3000/api

# Token过期时间（秒）
VITE_TOKEN_EXPIRE_TIME=7200

# 是否启用调试模式
VITE_DEBUG=true
```

## 用户权限系统

### 1. 权限定义
系统使用基于角色的权限控制（RBAC），预定义权限包括：

```typescript
// 仪表板权限
'dashboard:view'

// 地图权限
'map:view'

// 摄像头权限
'camera:view'
'camera:manage'

// 数据分析权限
'analytics:view'

// 系统管理权限
'system:manage'
```

### 2. 角色定义
- `admin`: 管理员，拥有所有权限
- `operator`: 操作员，拥有大部分查看和管理权限
- `viewer`: 查看者，只有查看权限

## 使用说明

### 1. 开发环境测试
项目已配置模拟登录功能，可以使用以下测试账号：

```typescript
// 测试账号（仅开发环境）
用户名: admin
密码: admin123

用户名: operator  
密码: operator123

用户名: viewer
密码: viewer123
```

### 2. 生产环境配置
在生产环境中，需要：

1. **配置真实的后端API地址**
2. **实现完整的用户认证后端服务**
3. **配置HTTPS确保数据传输安全**
4. **设置合适的Token过期时间**

### 3. 安全建议

#### 前端安全
- 使用HTTPS传输
- Token存储在localStorage中，定期刷新
- 实现自动登出机制
- 敏感操作需要重新验证

#### 后端安全
- 密码使用强加密算法（如bcrypt）
- 实现登录失败次数限制
- 使用JWT Token进行身份验证
- 实现Token黑名单机制

## 部署配置

### 1. 环境变量
```bash
# 生产环境
VITE_API_BASE_URL=https://your-api-domain.com/api
VITE_TOKEN_EXPIRE_TIME=3600
VITE_DEBUG=false
```

### 2. 构建部署
```bash
# 安装依赖
npm install

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

## 故障排除

### 1. 常见问题

**Q: 登录后页面跳转失败**
A: 检查路由守卫配置和用户权限设置

**Q: Token过期后无法自动刷新**
A: 检查refreshToken接口是否正常工作

**Q: 权限验证失败**
A: 检查用户权限配置和后端返回的权限数据

### 2. 调试方法

1. 打开浏览器开发者工具
2. 查看Network标签页的API请求
3. 查看Console标签页的错误信息
4. 检查localStorage中的Token和用户信息

## 扩展功能

### 1. 多语言支持
可以扩展登录页面支持多语言：

```typescript
// 在Login.vue中添加语言切换
const currentLanguage = ref('zh-CN')
const switchLanguage = (lang: string) => {
  currentLanguage.value = lang
  // 更新界面语言
}
```

### 2. 双因素认证
可以集成2FA功能：

```typescript
// 扩展LoginData接口
interface LoginData {
  username: string
  password: string
  totpCode?: string // 双因素认证码
}
```

### 3. 单点登录(SSO)
可以集成企业SSO系统：

```typescript
// 添加SSO登录方法
const ssoLogin = () => {
  window.location.href = '/auth/sso'
}
```

## 总结

本项目的用户认证系统已经完整实现，包括：

✅ 完整的类型定义  
✅ API服务封装  
✅ 状态管理  
✅ 登录界面  
✅ 路由守卫  
✅ 权限控制  

**重要提醒**: 账号密码的实际存储和验证需要在后端实现，前端只负责用户界面和状态管理。请确保后端API按照定义的接口规范实现相应的认证服务。

