"""
AI模型相关API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.ai_model import AIModel, ModelPrediction
from app.models.camera import Camera
from app.models.vehicle import Vehicle, VehicleAlert
from app.models.alert import Alert
from datetime import datetime
import logging
import os
import json

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/models', methods=['GET'])
@jwt_required()
def get_models():
    """获取AI模型列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        model_type = request.args.get('type')
        is_active = request.args.get('is_active')
        
        query = AIModel.query
        
        if model_type:
            query = query.filter_by(model_type=model_type)
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        models = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'models': [model.to_dict() for model in models.items],
            'total': models.total,
            'page': page,
            'per_page': per_page,
            'pages': models.pages
        }), 200
        
    except Exception as e:
        logger.error(f'获取AI模型列表失败: {str(e)}')
        return jsonify({'error': '获取AI模型列表失败'}), 500

@ai_bp.route('/models/<model_id>', methods=['GET'])
@jwt_required()
def get_model(model_id):
    """获取单个AI模型信息"""
    try:
        model = AIModel.query.get(model_id)
        if not model:
            return jsonify({'error': '模型不存在'}), 404
        
        return jsonify({
            'model': model.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'获取AI模型信息失败: {str(e)}')
        return jsonify({'error': '获取AI模型信息失败'}), 500

@ai_bp.route('/models', methods=['POST'])
@jwt_required()
def create_model():
    """创建AI模型"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'modelType', 'framework', 'modelPath']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 创建模型
        model = AIModel(
            name=data['name'],
            model_type=data['modelType'],
            framework=data['framework'],
            model_path=data['modelPath'],
            config_path=data.get('configPath'),
            version=data.get('version', '1.0.0'),
            confidence_threshold=data.get('confidenceThreshold', 0.5),
            input_size=data.get('inputSize'),
            description=data.get('description')
        )
        
        # 设置类别
        if 'classes' in data:
            model.set_classes(data['classes'])
        
        # 设置性能指标
        if 'performanceMetrics' in data:
            model.set_performance_metrics(data['performanceMetrics'])
        
        db.session.add(model)
        db.session.commit()
        
        return jsonify({
            'message': 'AI模型创建成功',
            'model': model.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'创建AI模型失败: {str(e)}')
        return jsonify({'error': '创建AI模型失败'}), 500

@ai_bp.route('/models/<model_id>', methods=['PUT'])
@jwt_required()
def update_model(model_id):
    """更新AI模型"""
    try:
        model = AIModel.query.get(model_id)
        if not model:
            return jsonify({'error': '模型不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            model.name = data['name']
        if 'modelType' in data:
            model.model_type = data['modelType']
        if 'framework' in data:
            model.framework = data['framework']
        if 'modelPath' in data:
            model.model_path = data['modelPath']
        if 'configPath' in data:
            model.config_path = data['configPath']
        if 'version' in data:
            model.version = data['version']
        if 'confidenceThreshold' in data:
            model.confidence_threshold = data['confidenceThreshold']
        if 'inputSize' in data:
            model.input_size = data['inputSize']
        if 'description' in data:
            model.description = data['description']
        if 'isActive' in data:
            model.is_active = data['isActive']
        if 'classes' in data:
            model.set_classes(data['classes'])
        if 'performanceMetrics' in data:
            model.set_performance_metrics(data['performanceMetrics'])
        
        model.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'AI模型更新成功',
            'model': model.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'更新AI模型失败: {str(e)}')
        return jsonify({'error': '更新AI模型失败'}), 500

@ai_bp.route('/models/<model_id>/activate', methods=['POST'])
@jwt_required()
def activate_model(model_id):
    """激活AI模型"""
    try:
        model = AIModel.query.get(model_id)
        if not model:
            return jsonify({'error': '模型不存在'}), 404
        
        # 检查模型文件是否存在
        if not os.path.exists(model.model_path):
            return jsonify({'error': '模型文件不存在'}), 400
        
        model.is_active = True
        model.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '模型激活成功',
            'model': model.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'激活模型失败: {str(e)}')
        return jsonify({'error': '激活模型失败'}), 500

@ai_bp.route('/models/<model_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_model(model_id):
    """停用AI模型"""
    try:
        model = AIModel.query.get(model_id)
        if not model:
            return jsonify({'error': '模型不存在'}), 404
        
        model.is_active = False
        model.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '模型停用成功',
            'model': model.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'停用模型失败: {str(e)}')
        return jsonify({'error': '停用模型失败'}), 500

@ai_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    """执行AI预测"""
    try:
        data = request.get_json()
        
        model_id = data.get('modelId')
        camera_id = data.get('cameraId')
        image_path = data.get('imagePath')
        
        if not all([model_id, camera_id, image_path]):
            return jsonify({'error': '缺少必填参数'}), 400
        
        # 检查模型是否存在且激活
        model = AIModel.query.get(model_id)
        if not model or not model.is_active:
            return jsonify({'error': '模型不存在或未激活'}), 400
        
        # 检查摄像头是否存在
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        # 检查图片文件是否存在
        if not os.path.exists(image_path):
            return jsonify({'error': '图片文件不存在'}), 400
        
        # 这里应该调用实际的AI模型进行预测
        # 现在返回模拟结果
        import random
        import time
        
        start_time = time.time()
        
        # 模拟预测结果
        predictions = []
        if model.model_type == 'detection':
            # 模拟目标检测结果
            for i in range(random.randint(1, 5)):
                predictions.append({
                    'class': random.choice(['car', 'truck', 'bus', 'person']),
                    'confidence': random.uniform(0.5, 0.95),
                    'bbox': [
                        random.randint(0, 100),
                        random.randint(0, 100),
                        random.randint(100, 200),
                        random.randint(100, 200)
                    ]
                })
        elif model.model_type == 'tracking':
            # 模拟目标跟踪结果
            predictions.append({
                'trackId': random.randint(1, 100),
                'class': 'car',
                'confidence': random.uniform(0.7, 0.95),
                'bbox': [
                    random.randint(0, 100),
                    random.randint(0, 100),
                    random.randint(100, 200),
                    random.randint(100, 200)
                ]
            })
        
        processing_time = time.time() - start_time
        
        # 保存预测结果
        prediction = ModelPrediction(
            model_id=model_id,
            camera_id=camera_id,
            prediction_type=model.model_type,
            input_image_path=image_path,
            output_image_path=image_path.replace('.jpg', '_result.jpg'),
            confidence=max([p.get('confidence', 0) for p in predictions]) if predictions else 0,
            processing_time=processing_time
        )
        prediction.set_predictions(predictions)
        
        db.session.add(prediction)
        db.session.commit()
        
        # 如果检测到可疑行为，创建告警
        if predictions and model.model_type == 'detection':
            for pred in predictions:
                if pred.get('confidence', 0) > model.confidence_threshold:
                    # 检查是否检测到可疑行为
                    if pred.get('class') in ['person'] and pred.get('confidence', 0) > 0.8:
                        Alert.create_alert(
                            title=f'检测到可疑行为: {camera.name}',
                            description=f'在摄像头 {camera.name} 检测到可疑行为',
                            alert_type='ai',
                            severity='medium',
                            source='ai_detection',
                            camera_id=camera_id,
                            metadata={'prediction': pred, 'model_id': model_id}
                        )
        
        return jsonify({
            'message': '预测完成',
            'predictions': predictions,
            'processingTime': processing_time,
            'predictionId': prediction.id
        }), 200
        
    except Exception as e:
        logger.error(f'AI预测失败: {str(e)}')
        return jsonify({'error': 'AI预测失败'}), 500

@ai_bp.route('/predictions', methods=['GET'])
@jwt_required()
def get_predictions():
    """获取预测结果"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        camera_id = request.args.get('camera_id')
        model_id = request.args.get('model_id')
        prediction_type = request.args.get('type')
        
        query = ModelPrediction.query
        
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        if model_id:
            query = query.filter_by(model_id=model_id)
        if prediction_type:
            query = query.filter_by(prediction_type=prediction_type)
        
        predictions = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'predictions': [pred.to_dict() for pred in predictions.items],
            'total': predictions.total,
            'page': page,
            'per_page': per_page,
            'pages': predictions.pages
        }), 200
        
    except Exception as e:
        logger.error(f'获取预测结果失败: {str(e)}')
        return jsonify({'error': '获取预测结果失败'}), 500

@ai_bp.route('/models/active', methods=['GET'])
@jwt_required()
def get_active_models():
    """获取活跃模型"""
    try:
        model_type = request.args.get('type')
        models = AIModel.get_active_models(model_type)
        
        return jsonify({
            'models': [model.to_dict() for model in models]
        }), 200
        
    except Exception as e:
        logger.error(f'获取活跃模型失败: {str(e)}')
        return jsonify({'error': '获取活跃模型失败'}), 500

@ai_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_ai_stats():
    """获取AI统计信息"""
    try:
        # 总模型数
        total_models = AIModel.query.count()
        
        # 活跃模型数
        active_models = AIModel.query.filter_by(is_active=True).count()
        
        # 按类型统计
        type_stats = db.session.query(
            AIModel.model_type,
            db.func.count(AIModel.id)
        ).group_by(AIModel.model_type).all()
        
        # 按框架统计
        framework_stats = db.session.query(
            AIModel.framework,
            db.func.count(AIModel.id)
        ).group_by(AIModel.framework).all()
        
        # 最近24小时的预测数
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_predictions = ModelPrediction.query.filter(
            ModelPrediction.timestamp >= yesterday
        ).count()
        
        # 平均处理时间
        avg_processing_time = db.session.query(
            db.func.avg(ModelPrediction.processing_time)
        ).scalar() or 0
        
        return jsonify({
            'totalModels': total_models,
            'activeModels': active_models,
            'typeStats': dict(type_stats),
            'frameworkStats': dict(framework_stats),
            'recentPredictions': recent_predictions,
            'avgProcessingTime': round(avg_processing_time, 3)
        }), 200
        
    except Exception as e:
        logger.error(f'获取AI统计失败: {str(e)}')
        return jsonify({'error': '获取AI统计失败'}), 500
