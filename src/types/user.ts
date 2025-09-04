// 用户认证相关类型定义

// 登录请求数据
export interface LoginData {
  username: string;
  password: string;
  rememberMe?: boolean; // 记住我选项
}

// 注册请求数据
export interface RegisterData {
  username: string;
  password: string;
  confirmPassword: string;
  email: string;
  phone?: string;
}

// 用户信息
export interface UserInfo {
  id: string;
  username: string;
  email: string;
  phone?: string;
  avatar?: string;
  roles: string[]; // 用户角色/权限
  permissions: string[]; // 具体权限列表
  department?: string; // 部门
  position?: string; // 职位
  lastLoginTime?: string; // 最后登录时间
  createTime: string; // 创建时间
}

// 登录响应数据
export interface LoginResponse {
  token: string;
  refreshToken: string;
  userInfo: UserInfo;
  expiresIn: number; // token过期时间（秒）
}

// 修改密码请求数据
export interface ChangePasswordData {
  oldPassword: string;
  newPassword: string;
  confirmPassword: string;
}

// 重置密码请求数据
export interface ResetPasswordData {
  email: string;
  verificationCode: string;
  newPassword: string;
}

// 用户状态
export interface UserState {
  token: string;
  refreshToken: string;
  userInfo: UserInfo | null;
  isLoggedIn: boolean;
  permissions: string[];
  roles: string[];
}
