"""
ReID特征模型
"""

from app import db
from datetime import datetime
import uuid
import json

class VehicleReIDFeature(db.Model):
    __tablename__ = 'vehicle_reid_features'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicles.id'))
    detection_id = db.Column(db.String(36), db.ForeignKey('vehicle_detections.id'), nullable=False)
    feature_vector = db.Column(db.JSON, nullable=False)
    feature_dimension = db.Column(db.Integer, nullable=False)
    similarity_threshold = db.Column(db.Float, default=0.8)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关联关系
    vehicle = db.relationship('Vehicle', backref='reid_features')
    
    def __repr__(self):
        return f'<VehicleReIDFeature {self.id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'vehicleId': self.vehicle_id,
            'detectionId': self.detection_id,
            'featureVector': self.feature_vector,
            'featureDimension': self.feature_dimension,
            'similarityThreshold': self.similarity_threshold,
            'createdAt': self.created_at.isoformat()
        }
    
    @classmethod
    def get_features_by_vehicle(cls, vehicle_id, limit=100):
        """获取车辆的所有ReID特征"""
        return cls.query.filter_by(vehicle_id=vehicle_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_recent_features(cls, limit=100):
        """获取最近的ReID特征"""
        return cls.query.order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_features_by_time_range(cls, start_time, end_time):
        """根据时间范围获取ReID特征"""
        return cls.query.filter(
            cls.created_at >= start_time,
            cls.created_at <= end_time
        ).order_by(cls.created_at).all()
    
    @classmethod
    def find_similar_features(cls, query_feature, threshold=0.8, limit=10):
        """查找相似特征"""
        # 这里应该实现实际的相似度计算
        # 现在返回模拟结果
        features = cls.query.limit(limit).all()
        similar_features = []
        
        for feature in features:
            # 模拟相似度计算
            similarity = calculate_similarity(query_feature, feature.feature_vector)
            if similarity >= threshold:
                similar_features.append({
                    'feature': feature.to_dict(),
                    'similarity': similarity
                })
        
        return sorted(similar_features, key=lambda x: x['similarity'], reverse=True)

def calculate_similarity(feature1, feature2):
    """计算特征相似度"""
    import numpy as np
    
    try:
        # 转换为numpy数组
        vec1 = np.array(feature1)
        vec2 = np.array(feature2)
        
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    except:
        return 0
