// 用户认证相关API服务
import request from '@/utils/request';
import type { 
  LoginData, 
  RegisterData, 
  LoginResponse, 
  UserInfo, 
  ChangePasswordData, 
  ResetPasswordData 
} from '@/types/user';

// 用户登录
export function login(data: LoginData) {
  return request<LoginResponse>({
    url: '/auth/login',
    method: 'post',
    data,
  });
}

// 用户注册
export function register(data: RegisterData) {
  return request<{ message: string }>({
    url: '/auth/register',
    method: 'post',
    data,
  });
}

// 用户登出
export function logout() {
  return request<{ message: string }>({
    url: '/auth/logout',
    method: 'post',
  });
}

// 刷新token
export function refreshToken(refreshToken: string) {
  return request<{ token: string; expiresIn: number }>({
    url: '/auth/refresh',
    method: 'post',
    data: { refreshToken },
  });
}

// 获取用户信息
export function getUserInfo() {
  return request<UserInfo>({
    url: '/user/info',
    method: 'get',
  });
}

// 更新用户信息
export function updateUserInfo(data: Partial<UserInfo>) {
  return request<UserInfo>({
    url: '/user/info',
    method: 'put',
    data,
  });
}

// 修改密码
export function changePassword(data: ChangePasswordData) {
  return request<{ message: string }>({
    url: '/user/change-password',
    method: 'post',
    data,
  });
}

// 发送重置密码验证码
export function sendResetPasswordCode(email: string) {
  return request<{ message: string }>({
    url: '/auth/send-reset-code',
    method: 'post',
    data: { email },
  });
}

// 重置密码
export function resetPassword(data: ResetPasswordData) {
  return request<{ message: string }>({
    url: '/auth/reset-password',
    method: 'post',
    data,
  });
}

// 获取用户权限列表
export function getUserPermissions() {
  return request<{ permissions: string[]; roles: string[] }>({
    url: '/user/permissions',
    method: 'get',
  });
}

// 上传用户头像
export function uploadAvatar(file: File) {
  const formData = new FormData();
  formData.append('avatar', file);
  
  return request<{ avatar: string }>({
    url: '/user/upload-avatar',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

// 验证token是否有效
export function validateToken() {
  return request<{ valid: boolean; userInfo?: UserInfo }>({
    url: '/auth/validate',
    method: 'get',
  });
}
