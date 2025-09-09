"""
流媒体工具模块
包含流媒体转换、处理等核心功能
"""
import os
import logging
from .stream_converter import stream_converter

logger = logging.getLogger(__name__)

class StreamManager:
    """流媒体管理器"""
    
    def __init__(self):
        self.converter = stream_converter
    
    def start_conversion(self, camera_id, stream_url, stream_type='rtmp'):
        """启动流媒体转换"""
        try:
            if stream_type.lower() == 'rtmp':
                # 启动RTMP到HLS转换
                success = self.converter.start_conversion(camera_id, stream_url)
                if success:
                    logger.info(f"流媒体转换已启动: {camera_id}")
                    return True
                else:
                    logger.error(f"流媒体转换启动失败: {camera_id}")
                    return False
            else:
                logger.warning(f"不支持的流媒体类型: {stream_type}")
                return False
        except Exception as e:
            logger.error(f"启动流媒体转换异常: {str(e)}")
            return False
    
    def stop_conversion(self, camera_id):
        """停止流媒体转换"""
        try:
            success = self.converter.stop_conversion(camera_id)
            if success:
                logger.info(f"流媒体转换已停止: {camera_id}")
                return True
            else:
                logger.warning(f"流媒体转换停止失败: {camera_id}")
                return False
        except Exception as e:
            logger.error(f"停止流媒体转换异常: {str(e)}")
            return False
    
    def get_conversion_status(self, camera_id):
        """获取转换状态"""
        try:
            return self.converter.get_status(camera_id)
        except Exception as e:
            logger.error(f"获取转换状态异常: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_hls_url(self, camera_id):
        """获取HLS播放URL"""
        try:
            return f"/streams/{camera_id}/playlist.m3u8"
        except Exception as e:
            logger.error(f"获取HLS URL异常: {str(e)}")
            return None

# 创建全局流媒体管理器实例
stream_manager = StreamManager()
