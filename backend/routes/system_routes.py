"""
系统相关路由
"""
from flask import Blueprint, jsonify
from datetime import datetime
import logging

system_bp = Blueprint('system', __name__)
logger = logging.getLogger(__name__)

@system_bp.route('/api/health')
def health_check():
    """健康检查"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'traffic-monitor-backend',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f'健康检查失败: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@system_bp.route('/api/system/cleanup', methods=['POST'])
def manual_cleanup():
    """手动触发清理任务"""
    try:
        from core import TempFileCleaner
        cleaner = TempFileCleaner()
        
        # 执行清理
        result = cleaner.cleanup_files()
        
        return jsonify({
            'message': '清理任务执行成功',
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f'手动清理失败: {str(e)}')
        return jsonify({'error': '清理任务执行失败'}), 500

@system_bp.route('/api/system/cleanup/status', methods=['GET'])
def cleanup_status():
    """获取清理服务状态和磁盘使用情况"""
    try:
        from core import TempFileCleaner
        cleaner = TempFileCleaner()
        
        usage_info = cleaner.get_disk_usage()
        
        return jsonify({
            'status': 'active',
            'usage_info': usage_info,
            'last_cleanup': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f'获取清理状态失败: {str(e)}')
        return jsonify({'error': '获取清理状态失败'}), 500
