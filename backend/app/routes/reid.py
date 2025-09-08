"""
ReID检测API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.reid import VehicleReIDFeature
from app.models.vehicle import Vehicle
from app.models.detection import VehicleDetection
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

reid_bp = Blueprint('reid', __name__)

@reid_bp.route('/features', methods=['GET'])
@jwt_required()
def get_reid_features():
    """获取ReID特征"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        vehicle_id = request.args.get('vehicle_id')
        detection_id = request.args.get('detection_id')
        
        query = VehicleReIDFeature.query
        
        if vehicle_id:
            query = query.filter_by(vehicle_id=vehicle_id)
        if detection_id:
            query = query.filter_by(detection_id=detection_id)
        
        features = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'features': [feature.to_dict() for feature in features.items],
            'total': features.total,
            'page': page,
            'per_page': per_page,
            'pages': features.pages
        }), 200
        
    except Exception as e:
        logger.error(f'获取ReID特征失败: {str(e)}')
        return jsonify({'error': '获取ReID特征失败'}), 500

@reid_bp.route('/features', methods=['POST'])
@jwt_required()
def create_reid_feature():
    """创建ReID特征"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['detectionId', 'featureVector', 'featureDimension']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 创建ReID特征
        feature = VehicleReIDFeature(
            vehicle_id=data.get('vehicleId'),
            detection_id=data['detectionId'],
            feature_vector=json.dumps(data['featureVector']),
            feature_dimension=data['featureDimension'],
            similarity_threshold=data.get('similarityThreshold', 0.8)
        )
        
        db.session.add(feature)
        db.session.commit()
        
        return jsonify({
            'message': 'ReID特征创建成功',
            'feature': feature.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'创建ReID特征失败: {str(e)}')
        return jsonify({'error': '创建ReID特征失败'}), 500

@reid_bp.route('/match', methods=['POST'])
@jwt_required()
def match_vehicles():
    """车辆匹配"""
    try:
        data = request.get_json()
        
        query_feature = data.get('queryFeature')
        threshold = data.get('threshold', 0.8)
        limit = data.get('limit', 10)
        
        if not query_feature:
            return jsonify({'error': '缺少查询特征'}), 400
        
        # 这里应该实现实际的ReID匹配算法
        # 现在返回模拟结果
        matches = simulate_reid_match(query_feature, threshold, limit)
        
        return jsonify({
            'matches': matches,
            'queryFeature': query_feature,
            'threshold': threshold
        }), 200
        
    except Exception as e:
        logger.error(f'车辆匹配失败: {str(e)}')
        return jsonify({'error': '车辆匹配失败'}), 500

@reid_bp.route('/track/<vehicle_id>', methods=['GET'])
@jwt_required()
def get_vehicle_track(vehicle_id):
    """获取车辆轨迹"""
    try:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', 100, type=int)
        
        # 获取车辆的所有ReID特征
        query = VehicleReIDFeature.query.filter_by(vehicle_id=vehicle_id)
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(VehicleReIDFeature.created_at >= start_dt)
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(VehicleReIDFeature.created_at <= end_dt)
        
        features = query.order_by(
            VehicleReIDFeature.created_at.desc()
        ).limit(limit).all()
        
        # 构建轨迹数据
        track_points = []
        for feature in features:
            detection = VehicleDetection.query.get(feature.detection_id)
            if detection:
                track_points.append({
                    'detectionId': detection.id,
                    'cameraId': detection.camera_id,
                    'timestamp': detection.detection_time.isoformat(),
                    'position': {
                        'lat': detection.position_lat,
                        'lng': detection.position_lng
                    },
                    'bbox': {
                        'x1': detection.bbox_x1,
                        'y1': detection.bbox_y1,
                        'x2': detection.bbox_x2,
                        'y2': detection.bbox_y2
                    },
                    'confidence': detection.confidence,
                    'imagePath': detection.image_path
                })
        
        return jsonify({
            'vehicleId': vehicle_id,
            'trackPoints': track_points,
            'totalPoints': len(track_points)
        }), 200
        
    except Exception as e:
        logger.error(f'获取车辆轨迹失败: {str(e)}')
        return jsonify({'error': '获取车辆轨迹失败'}), 500

@reid_bp.route('/similarity', methods=['POST'])
@jwt_required()
def calculate_similarity():
    """计算特征相似度"""
    try:
        data = request.get_json()
        
        feature1 = data.get('feature1')
        feature2 = data.get('feature2')
        
        if not feature1 or not feature2:
            return jsonify({'error': '缺少特征数据'}), 400
        
        # 计算余弦相似度
        similarity = calculate_cosine_similarity(feature1, feature2)
        
        return jsonify({
            'similarity': similarity,
            'isMatch': similarity >= 0.8
        }), 200
        
    except Exception as e:
        logger.error(f'计算相似度失败: {str(e)}')
        return jsonify({'error': '计算相似度失败'}), 500

@reid_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_reid_stats():
    """获取ReID统计信息"""
    try:
        # 总特征数
        total_features = VehicleReIDFeature.query.count()
        
        # 按车辆统计
        vehicle_stats = db.session.query(
            VehicleReIDFeature.vehicle_id,
            db.func.count(VehicleReIDFeature.id)
        ).group_by(VehicleReIDFeature.vehicle_id).all()
        
        # 最近24小时特征数
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_features = VehicleReIDFeature.query.filter(
            VehicleReIDFeature.created_at >= yesterday
        ).count()
        
        # 平均特征维度
        avg_dimension = db.session.query(
            db.func.avg(VehicleReIDFeature.feature_dimension)
        ).scalar() or 0
        
        return jsonify({
            'totalFeatures': total_features,
            'vehicleStats': dict(vehicle_stats),
            'recentFeatures': recent_features,
            'avgDimension': round(avg_dimension, 2)
        }), 200
        
    except Exception as e:
        logger.error(f'获取ReID统计失败: {str(e)}')
        return jsonify({'error': '获取ReID统计失败'}), 500

def simulate_reid_match(query_feature, threshold, limit):
    """模拟ReID匹配"""
    # 这里应该实现实际的ReID匹配算法
    # 现在返回模拟结果
    import random
    
    matches = []
    for i in range(min(limit, 5)):
        matches.append({
            'vehicleId': f'vehicle_{i+1}',
            'detectionId': f'detection_{i+1}',
            'similarity': random.uniform(threshold, 0.95),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return sorted(matches, key=lambda x: x['similarity'], reverse=True)

def calculate_cosine_similarity(feature1, feature2):
    """计算余弦相似度"""
    import numpy as np
    
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
