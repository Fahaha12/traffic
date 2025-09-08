"""
AI模型管理器
"""

import os
import logging
import torch
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from app.models.ai_model import AIModel

logger = logging.getLogger(__name__)

class ModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.models = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f'使用设备: {self.device}')
    
    def load_model(self, model_id: str) -> bool:
        """加载模型"""
        try:
            model = AIModel.query.get(model_id)
            if not model:
                logger.error(f'模型不存在: {model_id}')
                return False
            
            if not os.path.exists(model.model_path):
                logger.error(f'模型文件不存在: {model.model_path}')
                return False
            
            if model.framework == 'pytorch':
                self._load_pytorch_model(model)
            elif model.framework == 'tensorflow':
                self._load_tensorflow_model(model)
            elif model.framework == 'onnx':
                self._load_onnx_model(model)
            else:
                logger.error(f'不支持的框架: {model.framework}')
                return False
            
            self.models[model_id] = {
                'model': model,
                'loaded_model': None,  # 实际加载的模型对象
                'is_loaded': True
            }
            
            logger.info(f'模型加载成功: {model.name}')
            return True
            
        except Exception as e:
            logger.error(f'加载模型失败: {str(e)}')
            return False
    
    def _load_pytorch_model(self, model: AIModel):
        """加载PyTorch模型"""
        try:
            # 这里应该根据实际的模型类型加载
            # 例如：YOLO、ResNet等
            if 'yolo' in model.name.lower():
                from ultralytics import YOLO
                loaded_model = YOLO(model.model_path)
            else:
                loaded_model = torch.load(model.model_path, map_location=self.device)
            
            self.models[model.id]['loaded_model'] = loaded_model
            
        except Exception as e:
            logger.error(f'加载PyTorch模型失败: {str(e)}')
            raise
    
    def _load_tensorflow_model(self, model: AIModel):
        """加载TensorFlow模型"""
        try:
            import tensorflow as tf
            loaded_model = tf.keras.models.load_model(model.model_path)
            self.models[model.id]['loaded_model'] = loaded_model
            
        except Exception as e:
            logger.error(f'加载TensorFlow模型失败: {str(e)}')
            raise
    
    def _load_onnx_model(self, model: AIModel):
        """加载ONNX模型"""
        try:
            import onnxruntime as ort
            loaded_model = ort.InferenceSession(model.model_path)
            self.models[model.id]['loaded_model'] = loaded_model
            
        except Exception as e:
            logger.error(f'加载ONNX模型失败: {str(e)}')
            raise
    
    def predict(self, model_id: str, image: np.ndarray) -> List[Dict[str, Any]]:
        """执行预测"""
        try:
            if model_id not in self.models:
                if not self.load_model(model_id):
                    return []
            
            model_info = self.models[model_id]
            model = model_info['model']
            loaded_model = model_info['loaded_model']
            
            if not model_info['is_loaded']:
                logger.error(f'模型未加载: {model_id}')
                return []
            
            # 预处理图像
            processed_image = self._preprocess_image(image, model)
            
            # 执行预测
            if model.framework == 'pytorch':
                predictions = self._predict_pytorch(loaded_model, processed_image, model)
            elif model.framework == 'tensorflow':
                predictions = self._predict_tensorflow(loaded_model, processed_image, model)
            elif model.framework == 'onnx':
                predictions = self._predict_onnx(loaded_model, processed_image, model)
            else:
                return []
            
            # 后处理结果
            return self._postprocess_predictions(predictions, model)
            
        except Exception as e:
            logger.error(f'预测失败: {str(e)}')
            return []
    
    def _preprocess_image(self, image: np.ndarray, model: AIModel) -> np.ndarray:
        """预处理图像"""
        try:
            # 调整图像大小
            if model.input_size:
                width, height = map(int, model.input_size.split('x'))
                image = cv2.resize(image, (width, height))
            
            # 归一化
            image = image.astype(np.float32) / 255.0
            
            # 添加批次维度
            if len(image.shape) == 3:
                image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            logger.error(f'图像预处理失败: {str(e)}')
            raise
    
    def _predict_pytorch(self, model, image: np.ndarray, model_info: AIModel) -> List[Dict[str, Any]]:
        """PyTorch模型预测"""
        try:
            if hasattr(model, 'predict'):
                # YOLO模型
                results = model.predict(image, conf=model_info.confidence_threshold)
                predictions = []
                for result in results:
                    if result.boxes is not None:
                        for box in result.boxes:
                            predictions.append({
                                'class': model.names[int(box.cls)],
                                'confidence': float(box.conf),
                                'bbox': box.xyxy[0].tolist()
                            })
                return predictions
            else:
                # 其他PyTorch模型
                with torch.no_grad():
                    input_tensor = torch.from_numpy(image).to(self.device)
                    outputs = model(input_tensor)
                    # 这里需要根据具体模型调整
                    return []
                    
        except Exception as e:
            logger.error(f'PyTorch预测失败: {str(e)}')
            return []
    
    def _predict_tensorflow(self, model, image: np.ndarray, model_info: AIModel) -> List[Dict[str, Any]]:
        """TensorFlow模型预测"""
        try:
            predictions = model.predict(image)
            # 这里需要根据具体模型调整
            return []
            
        except Exception as e:
            logger.error(f'TensorFlow预测失败: {str(e)}')
            return []
    
    def _predict_onnx(self, model, image: np.ndarray, model_info: AIModel) -> List[Dict[str, Any]]:
        """ONNX模型预测"""
        try:
            input_name = model.get_inputs()[0].name
            outputs = model.run(None, {input_name: image})
            # 这里需要根据具体模型调整
            return []
            
        except Exception as e:
            logger.error(f'ONNX预测失败: {str(e)}')
            return []
    
    def _postprocess_predictions(self, predictions: List[Dict[str, Any]], model: AIModel) -> List[Dict[str, Any]]:
        """后处理预测结果"""
        try:
            # 过滤低置信度预测
            filtered_predictions = [
                pred for pred in predictions 
                if pred.get('confidence', 0) >= model.confidence_threshold
            ]
            
            # 限制预测数量
            max_predictions = 100
            if len(filtered_predictions) > max_predictions:
                filtered_predictions = sorted(
                    filtered_predictions, 
                    key=lambda x: x.get('confidence', 0), 
                    reverse=True
                )[:max_predictions]
            
            return filtered_predictions
            
        except Exception as e:
            logger.error(f'后处理预测结果失败: {str(e)}')
            return predictions
    
    def unload_model(self, model_id: str) -> bool:
        """卸载模型"""
        try:
            if model_id in self.models:
                del self.models[model_id]
                logger.info(f'模型卸载成功: {model_id}')
                return True
            return False
            
        except Exception as e:
            logger.error(f'卸载模型失败: {str(e)}')
            return False
    
    def get_loaded_models(self) -> List[str]:
        """获取已加载的模型列表"""
        return list(self.models.keys())
    
    def is_model_loaded(self, model_id: str) -> bool:
        """检查模型是否已加载"""
        return model_id in self.models and self.models[model_id]['is_loaded']

# 全局模型管理器实例
model_manager = ModelManager()
