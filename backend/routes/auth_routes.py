"""
认证相关路由
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
import os

auth_bp = Blueprint('auth', __name__)

# JWT密钥（生产环境应该从环境变量获取）
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-here')

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 简单的硬编码验证（生产环境应该使用数据库）
        if username == 'admin' and password == 'admin123':
            # 生成JWT token
            payload = {
                'user_id': 1,
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
            
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': 1,
                    'username': username,
                    'role': 'admin'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '登录失败'
        }), 500

@auth_bp.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    try:
        # 从请求头获取token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '未提供有效的认证令牌'}), 401
        
        token = auth_header.split(' ')[1]
        
        # 验证token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return jsonify({
                'id': payload['user_id'],
                'username': payload['username'],
                'role': 'admin'
            }), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的令牌'}), 401
            
    except Exception as e:
        return jsonify({'error': '获取用户信息失败'}), 500
