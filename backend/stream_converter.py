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
        
        # 创建输出目录
        stream_dir = os.path.join(self.output_dir, stream_id)
        os.makedirs(stream_dir, exist_ok=True)
        
        # HLS输出路径
        hls_path = os.path.join(stream_dir, 'playlist.m3u8')
        
        # FFmpeg命令 - 优化HLS兼容性
        cmd = [
            'ffmpeg',
            '-i', rtmp_url,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',     # 使用最快编码预设
            '-tune', 'zerolatency',     # 零延迟调优
            '-profile:v', 'baseline',   # 使用baseline profile提高兼容性
            '-level', '3.0',            # H.264 level
            '-c:a', 'aac',
            '-b:a', '128k',             # 音频比特率
            '-f', 'hls',
            '-hls_time', '4',           # 每个片段4秒，提高稳定性
            '-hls_list_size', '6',      # 保留6个片段
            '-hls_flags', 'delete_segments+independent_segments',  # 删除旧片段+独立片段
            '-hls_segment_filename', os.path.join(stream_dir, 'segment_%03d.ts'),
            '-hls_base_url', f'/api/stream/segment/{stream_id}/',  # 片段基础URL
            '-hls_allow_cache', '0',    # 禁用缓存
            '-hls_start_number_source', 'datetime',  # 从当前时间开始编号
            '-y',  # 覆盖输出文件
            hls_path
        ]
        
        try:
            logger.info(f"开始转换RTMP流: {rtmp_url} -> {hls_path}")
            
            # 启动FFmpeg进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 记录转换信息
            self.active_conversions[stream_id] = process
            self.conversion_status[stream_id] = {
                'rtmp_url': rtmp_url,
                'hls_path': hls_path,
                'start_time': datetime.now(),
                'status': 'converting',
                'process': process
            }
            
            # 启动监控线程
            monitor_thread = threading.Thread(
                target=self._monitor_conversion,
                args=(stream_id, process)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return {
                'success': True,
                'stream_id': stream_id,
                'hls_url': f'/streams/{stream_id}/playlist.m3u8',
                'status': 'converting'
            }
            
        except Exception as e:
            logger.error(f"启动FFmpeg转换失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def _monitor_conversion(self, stream_id: str, process: subprocess.Popen):
        """监控转换进程"""
        try:
            # 等待进程完成或出错
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info(f"RTMP转换成功: {stream_id}")
                self.conversion_status[stream_id]['status'] = 'completed'
            else:
                logger.error(f"RTMP转换失败: {stream_id}, 错误: {stderr}")
                self.conversion_status[stream_id]['status'] = 'failed'
                self.conversion_status[stream_id]['error'] = stderr
                
        except Exception as e:
            logger.error(f"监控转换进程出错: {str(e)}")
            self.conversion_status[stream_id]['status'] = 'error'
            self.conversion_status[stream_id]['error'] = str(e)
        finally:
            # 清理进程记录
            if stream_id in self.active_conversions:
                del self.active_conversions[stream_id]
    
    def stop_conversion(self, stream_id: str) -> bool:
        """停止转换"""
        if stream_id in self.active_conversions:
            process = self.active_conversions[stream_id]
            process.terminate()
            process.wait(timeout=5)
            
            del self.active_conversions[stream_id]
            if stream_id in self.conversion_status:
                self.conversion_status[stream_id]['status'] = 'stopped'
            
            logger.info(f"已停止转换: {stream_id}")
            return True
        return False
    
    def get_conversion_status(self, stream_id: str) -> Optional[dict]:
        """获取转换状态"""
        return self.conversion_status.get(stream_id)
    
    def list_active_conversions(self) -> list:
        """获取所有活跃的转换"""
        return list(self.active_conversions.keys())
    
    def cleanup_old_streams(self, max_age_hours: int = 24):
        """清理旧的流媒体文件"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for stream_id in list(self.conversion_status.keys()):
            status = self.conversion_status[stream_id]
            if 'start_time' in status:
                age = (datetime.now() - status['start_time']).total_seconds()
                if age > max_age_seconds:
                    self.stop_conversion(stream_id)
                    # 删除文件
                    stream_dir = os.path.join(self.output_dir, stream_id)
                    if os.path.exists(stream_dir):
                        import shutil
                        shutil.rmtree(stream_dir)
                    del self.conversion_status[stream_id]

# 全局转换器实例
stream_converter = StreamConverter()
