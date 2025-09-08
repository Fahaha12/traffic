"""
视频处理器
"""

import cv2
import numpy as np
import logging
import threading
import time
from typing import Callable, Optional, Dict, Any
from app.ai.model_manager import model_manager
from app.models.camera import Camera
from app.models.ai_model import AIModel

logger = logging.getLogger(__name__)

class VideoProcessor:
    """视频处理器"""
    
    def __init__(self):
        self.active_processors = {}
        self.stop_events = {}
    
    def start_processing(self, camera_id: str, callback: Optional[Callable] = None):
        """开始处理视频流"""
        try:
            camera = Camera.query.get(camera_id)
            if not camera:
                logger.error(f'摄像头不存在: {camera_id}')
                return False
            
            if camera_id in self.active_processors:
                logger.warning(f'摄像头 {camera_id} 已在处理中')
                return True
            
            # 创建停止事件
            self.stop_events[camera_id] = threading.Event()
            
            # 启动处理线程
            thread = threading.Thread(
                target=self._process_video_stream,
                args=(camera_id, camera.stream_url, camera.stream_type, callback)
            )
            thread.daemon = True
            thread.start()
            
            self.active_processors[camera_id] = thread
            logger.info(f'开始处理摄像头 {camera_id} 的视频流')
            return True
            
        except Exception as e:
            logger.error(f'启动视频处理失败: {str(e)}')
            return False
    
    def stop_processing(self, camera_id: str):
        """停止处理视频流"""
        try:
            if camera_id in self.stop_events:
                self.stop_events[camera_id].set()
            
            if camera_id in self.active_processors:
                self.active_processors[camera_id].join(timeout=5)
                del self.active_processors[camera_id]
            
            if camera_id in self.stop_events:
                del self.stop_events[camera_id]
            
            logger.info(f'停止处理摄像头 {camera_id} 的视频流')
            return True
            
        except Exception as e:
            logger.error(f'停止视频处理失败: {str(e)}')
            return False
    
    def _process_video_stream(self, camera_id: str, stream_url: str, stream_type: str, callback: Optional[Callable]):
        """处理视频流"""
        try:
            # 创建视频捕获器
            cap = cv2.VideoCapture(stream_url)
            if not cap.isOpened():
                logger.error(f'无法打开视频流: {stream_url}')
                return
            
            frame_count = 0
            last_analysis_time = 0
            analysis_interval = 1.0  # 每秒分析一次
            
            while not self.stop_events.get(camera_id, threading.Event()).is_set():
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f'无法读取帧: {camera_id}')
                    break
                
                frame_count += 1
                current_time = time.time()
                
                # 定期进行AI分析
                if current_time - last_analysis_time >= analysis_interval:
                    self._analyze_frame(camera_id, frame, callback)
                    last_analysis_time = current_time
                
                # 控制帧率
                time.sleep(0.033)  # 约30fps
            
            cap.release()
            logger.info(f'摄像头 {camera_id} 的视频流处理结束')
            
        except Exception as e:
            logger.error(f'处理视频流失败: {str(e)}')
        finally:
            if camera_id in self.active_processors:
                del self.active_processors[camera_id]
    
    def _analyze_frame(self, camera_id: str, frame: np.ndarray, callback: Optional[Callable]):
        """分析视频帧"""
        try:
            # 获取活跃的检测模型
            detection_models = AIModel.get_detection_models()
            
            all_predictions = []
            
            for model in detection_models:
                if not model_manager.is_model_loaded(model.id):
                    if not model_manager.load_model(model.id):
                        continue
                
                # 执行预测
                predictions = model_manager.predict(model.id, frame)
                
                if predictions:
                    all_predictions.extend(predictions)
            
            # 如果有预测结果，调用回调函数
            if all_predictions and callback:
                callback(camera_id, frame, all_predictions)
            
        except Exception as e:
            logger.error(f'分析帧失败: {str(e)}')
    
    def capture_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """捕获当前帧"""
        try:
            camera = Camera.query.get(camera_id)
            if not camera:
                return None
            
            cap = cv2.VideoCapture(camera.stream_url)
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            return frame if ret else None
            
        except Exception as e:
            logger.error(f'捕获帧失败: {str(e)}')
            return None
    
    def get_processing_status(self, camera_id: str) -> Dict[str, Any]:
        """获取处理状态"""
        return {
            'is_processing': camera_id in self.active_processors,
            'thread_alive': camera_id in self.active_processors and self.active_processors[camera_id].is_alive()
        }
    
    def get_all_processing_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有处理状态"""
        return {
            camera_id: self.get_processing_status(camera_id)
            for camera_id in self.active_processors.keys()
        }

# 全局视频处理器实例
video_processor = VideoProcessor()
