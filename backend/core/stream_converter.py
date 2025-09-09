"""
流媒体转换服务
使用FFmpeg将RTMP流转换为HLS流
"""

import os
import subprocess
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class StreamConverter:
    """流媒体转换器"""
    
    def __init__(self, output_dir: str = "streams"):
        self.output_dir = output_dir
        self.active_conversions: Dict[str, subprocess.Popen] = {}
        self.conversion_status: Dict[str, dict] = {}
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
    
    def convert_rtmp_to_hls(self, rtmp_url: str, stream_id: str = None) -> dict:
        """
        将RTMP流转换为HLS流
        
        Args:
            rtmp_url: RTMP流地址
            stream_id: 流ID，如果为None则自动生成
            
        Returns:
            dict: 转换结果信息
        """
        if stream_id is None:
            stream_id = str(uuid.uuid4())
        
        # 检查是否已经在转换
        if stream_id in self.active_conversions:
            return {
                'success': True,
                'stream_id': stream_id,
                'hls_url': f'/streams/{stream_id}/playlist.m3u8',
                'status': 'already_converting'
            }
        
        try:
            # 创建流目录
            stream_dir = os.path.join(self.output_dir, stream_id)
            os.makedirs(stream_dir, exist_ok=True)
            
            # 构建FFmpeg命令
            hls_path = os.path.join(stream_dir, 'playlist.m3u8')
            
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', rtmp_url,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-f', 'hls',
                '-hls_time', '2',
                '-hls_list_size', '10',
                '-hls_flags', 'delete_segments',
                '-hls_segment_filename', os.path.join(stream_dir, 'segment_%03d.ts'),
                hls_path
            ]
            
            # 启动FFmpeg进程
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 记录转换信息
            self.active_conversions[stream_id] = process
            self.conversion_status[stream_id] = {
                'status': 'converting',
                'start_time': datetime.now(),
                'rtmp_url': rtmp_url,
                'hls_url': f'/streams/{stream_id}/playlist.m3u8'
            }
            
            # 启动监控线程
            monitor_thread = threading.Thread(
                target=self._monitor_conversion,
                args=(stream_id, process)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            logger.info(f"开始转换流: {stream_id} from {rtmp_url}")
            
            return {
                'success': True,
                'stream_id': stream_id,
                'hls_url': f'/streams/{stream_id}/playlist.m3u8',
                'status': 'converting'
            }
            
        except Exception as e:
            logger.error(f"启动流转换失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def _monitor_conversion(self, stream_id: str, process: subprocess.Popen):
        """监控转换进程"""
        try:
            # 等待进程结束
            return_code = process.wait()
            
            if return_code == 0:
                self.conversion_status[stream_id]['status'] = 'completed'
                logger.info(f"流转换完成: {stream_id}")
            else:
                self.conversion_status[stream_id]['status'] = 'failed'
                logger.error(f"流转换失败: {stream_id}, 返回码: {return_code}")
                
        except Exception as e:
            logger.error(f"监控流转换时出错: {e}")
            self.conversion_status[stream_id]['status'] = 'error'
        finally:
            # 清理进程记录
            if stream_id in self.active_conversions:
                del self.active_conversions[stream_id]
    
    def stop_conversion(self, stream_id: str) -> bool:
        """停止流转换"""
        try:
            if stream_id in self.active_conversions:
                process = self.active_conversions[stream_id]
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                del self.active_conversions[stream_id]
                self.conversion_status[stream_id]['status'] = 'stopped'
                
                logger.info(f"已停止流转换: {stream_id}")
                return True
            else:
                logger.warning(f"流转换不存在: {stream_id}")
                return False
                
        except Exception as e:
            logger.error(f"停止流转换失败: {e}")
            return False
    
    def get_conversion_status(self, stream_id: str) -> dict:
        """获取转换状态"""
        if stream_id in self.conversion_status:
            status = self.conversion_status[stream_id].copy()
            status['is_active'] = stream_id in self.active_conversions
            return status
        else:
            return {
                'status': 'not_found',
                'is_active': False
            }
    
    def list_active_conversions(self) -> list:
        """获取所有活跃的转换"""
        return list(self.active_conversions.keys())
    
    def cleanup_old_streams(self, max_age_hours: int = 24):
        """清理旧的流文件"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for stream_id in list(self.conversion_status.keys()):
                status = self.conversion_status[stream_id]
                if 'start_time' in status:
                    age = current_time - status['start_time'].timestamp()
                    if age > max_age_seconds:
                        # 停止转换
                        self.stop_conversion(stream_id)
                        
                        # 删除文件
                        stream_dir = os.path.join(self.output_dir, stream_id)
                        if os.path.exists(stream_dir):
                            import shutil
                            shutil.rmtree(stream_dir)
                            logger.info(f"已清理旧流文件: {stream_id}")
                        
                        # 删除状态记录
                        del self.conversion_status[stream_id]
                        
        except Exception as e:
            logger.error(f"清理旧流文件失败: {e}")

# 创建全局转换器实例
stream_converter = StreamConverter()
