"""
AI模型相关模型
"""

from app import db
from datetime import datetime
import uuid
import json

class AIModel(db.Model):
    __tablename__ = 'ai_models'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # detection, tracking, classification
    framework = db.Column(db.String(20), nullable=False)  # pytorch, tensorflow, onnx
    version = db.Column(db.String(20), default='1.0.0')
    model_path = db.Column(db.String(500), nullable=False)
    config_path = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    confidence_threshold = db.Column(db.Float, default=0.5)
    input_size = db.Column(db.String(50))  # "640x640"
    classes = db.Column(db.Text)  # JSON格式的类别列表
    description = db.Column(db.Text)
    performance_metrics = db.Column(db.Text)  # JSON格式的性能指标
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    predictions = db.relationship('ModelPrediction', backref='model', lazy='dynamic')
    
    def __repr__(self):
        return f'<AIModel {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        classes = None
        if self.classes:
            try:
                classes = json.loads(self.classes)
            except:
                classes = self.classes
        
        performance_metrics = None
        if self.performance_metrics:
            try:
                performance_metrics = json.loads(self.performance_metrics)
            except:
                performance_metrics = self.performance_metrics
        
        return {
            'id': self.id,
            'name': self.name,
            'modelType': self.model_type,
            'framework': self.framework,
            'version': self.version,
            'modelPath': self.model_path,
            'configPath': self.config_path,
            'isActive': self.is_active,
            'confidenceThreshold': self.confidence_threshold,
            'inputSize': self.input_size,
            'classes': classes,
            'description': self.description,
            'performanceMetrics': performance_metrics,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }
    
    def get_classes_list(self):
        """获取类别列表"""
        if self.classes:
            try:
                return json.loads(self.classes)
            except:
                return []
        return []
    
    def set_classes(self, classes_list):
        """设置类别列表"""
        self.classes = json.dumps(classes_list)
    
    def get_performance_metrics(self):
        """获取性能指标"""
        if self.performance_metrics:
            try:
                return json.loads(self.performance_metrics)
            except:
                return {}
        return {}
    
    def set_performance_metrics(self, metrics):
        """设置性能指标"""
        self.performance_metrics = json.dumps(metrics)
    
    @classmethod
    def get_active_models(cls, model_type=None):
        """获取活跃模型"""
        query = cls.query.filter_by(is_active=True)
        if model_type:
            query = query.filter_by(model_type=model_type)
        return query.all()
    
    @classmethod
    def get_detection_models(cls):
        """获取检测模型"""
        return cls.get_active_models('detection')
    
    @classmethod
    def get_tracking_models(cls):
        """获取跟踪模型"""
        return cls.get_active_models('tracking')

class ModelPrediction(db.Model):
    __tablename__ = 'model_predictions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = db.Column(db.String(36), db.ForeignKey('ai_models.id'), nullable=False)
    camera_id = db.Column(db.String(36), db.ForeignKey('cameras.id'), nullable=False)
    prediction_type = db.Column(db.String(50), nullable=False)  # detection, tracking, classification
    input_image_path = db.Column(db.String(500))
    output_image_path = db.Column(db.String(500))
    predictions = db.Column(db.Text)  # JSON格式的预测结果
    confidence = db.Column(db.Float)
    processing_time = db.Column(db.Float)  # 处理时间（秒）
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ModelPrediction {self.prediction_type} at {self.timestamp}>'
    
    def to_dict(self):
        """转换为字典"""
        predictions = None
        if self.predictions:
            try:
                predictions = json.loads(self.predictions)
            except:
                predictions = self.predictions
        
        return {
            'id': self.id,
            'modelId': self.model_id,
            'cameraId': self.camera_id,
            'predictionType': self.prediction_type,
            'inputImagePath': self.input_image_path,
            'outputImagePath': self.output_image_path,
            'predictions': predictions,
            'confidence': self.confidence,
            'processingTime': self.processing_time,
            'timestamp': self.timestamp.isoformat()
        }
    
    def get_predictions_list(self):
        """获取预测结果列表"""
        if self.predictions:
            try:
                return json.loads(self.predictions)
            except:
                return []
        return []
    
    def set_predictions(self, predictions_list):
        """设置预测结果"""
        self.predictions = json.dumps(predictions_list)
    
    @classmethod
    def get_recent_predictions(cls, camera_id=None, model_id=None, limit=100):
        """获取最近的预测结果"""
        query = cls.query
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        if model_id:
            query = query.filter_by(model_id=model_id)
        return query.order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_predictions_by_type(cls, prediction_type, limit=100):
        """根据类型获取预测结果"""
        return cls.query.filter_by(prediction_type=prediction_type)\
                       .order_by(cls.timestamp.desc())\
                       .limit(limit).all()
