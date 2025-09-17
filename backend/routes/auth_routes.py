"""
认证相关路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from datetime import datetime, timedelta
import hashlib
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 模拟用户数据库（生产环境应该使用真实数据库）
USERS = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password': 'admin123',  # 实际应该存储哈希值
        'email': 'admin@traffic-monitor.com',
        'phone': '13800138000',
        'role': 'admin',
        'permissions': [
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
        'department': '技术部',
        'position': '系统管理员',
        'last_login': None,
        'created_at': '2024-01-01T00:00:00Z'
    },
    'operator': {
        'id': 2,
        'username': 'operator',
        'password': 'operator123',
        'email': 'operator@traffic-monitor.com',
        'phone': '13800138001',
        'role': 'operator',
        'permissions': [
            'dashboard:view',
            'map:view',
            'camera:view',
            'vehicle:view',
            'analytics:view',
            'alerts:view'
        ],
        'department': '运营部',
        'position': '操作员',
        'last_login': None,
        'created_at': '2024-01-01T00:00:00Z'
    }
}

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 查找用户
        user = USERS.get(username)
        if not user or user['password'] != password:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 更新最后登录时间
        user['last_login'] = datetime.utcnow().isoformat()
        
        # 创建JWT token
        access_token = create_access_token(
            identity=str(user['id']),
            additional_claims={
                'username': user['username'],
                'role': user['role'],
                'permissions': user['permissions']
            }
        )
        refresh_token = create_refresh_token(identity=str(user['id']))
        
        # 准备用户信息
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'phone': user['phone'],
            'role': user['role'],
            'permissions': user['permissions'],
            'department': user['department'],
            'position': user['position'],
            'lastLoginTime': user['last_login'],
            'createTime': user['created_at']
        }
        
        return jsonify({
            'success': True,
            'token': access_token,
            'refreshToken': refresh_token,
            'userInfo': user_info,
            'expiresIn': 86400  # 24小时
        }), 200
            
    except Exception as e:
        logger.error(f'登录失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # 查找用户
        user = None
        for u in USERS.values():
            if str(u['id']) == str(user_id):
                user = u
                break
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'phone': user['phone'],
            'role': user['role'],
            'permissions': user['permissions'],
            'department': user['department'],
            'position': user['position'],
            'lastLoginTime': user['last_login'],
            'createTime': user['created_at']
        }
        
        return jsonify(user_info), 200
            
    except Exception as e:
        logger.error(f'获取用户信息失败: {str(e)}')
        return jsonify({'error': '获取用户信息失败'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新token"""
    try:
        user_id = get_jwt_identity()
        
        # 查找用户
        user = None
        for u in USERS.values():
            if str(u['id']) == str(user_id):
                user = u
                break
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 创建新的access token
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={
                'username': user['username'],
                'role': user['role'],
                'permissions': user['permissions']
            }
        )
        
        return jsonify({
            'token': access_token,
            'expiresIn': 86400
        }), 200
        
    except Exception as e:
        logger.error(f'刷新token失败: {str(e)}')
        return jsonify({'error': '刷新token失败'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        # 这里可以将token加入黑名单（需要Redis等存储）
        # 目前只是简单返回成功
        return jsonify({'message': '登出成功'}), 200
        
    except Exception as e:
        logger.error(f'登出失败: {str(e)}')
        return jsonify({'error': '登出失败'}), 500

@auth_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate():
    """验证token有效性"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # 查找用户
        user = None
        for u in USERS.values():
            if str(u['id']) == str(user_id):
                user = u
                break
        
        if not user:
            return jsonify({'valid': False}), 401
        
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'phone': user['phone'],
            'role': user['role'],
            'permissions': user['permissions'],
            'department': user['department'],
            'position': user['position'],
            'lastLoginTime': user['last_login'],
            'createTime': user['created_at']
        }
        
        return jsonify({
            'valid': True,
            'userInfo': user_info
        }), 200
        
    except Exception as e:
        logger.error(f'验证token失败: {str(e)}')
        return jsonify({'valid': False}), 401

@auth_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions():
    """获取用户权限"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # 从claims中获取权限
        permissions = claims.get('permissions', [])
        roles = [claims.get('role', '')]
        
        return jsonify({
            'permissions': permissions,
            'roles': roles
        }), 200
        
    except Exception as e:
        logger.error(f'获取权限失败: {str(e)}')
        return jsonify({'error': '获取权限失败'}), 500
