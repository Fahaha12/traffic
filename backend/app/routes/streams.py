"""
视频流处理API
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.camera import Camera
from app.models.ai_model import AIModel, ModelPrediction
import cv2
import numpy as np
import base64
import io
from PIL import Image
import logging
import threading
import time

logger = logging.getLogger(__name__)

streams_bp = Blueprint('streams', __name__)

# 全局变量存储活跃的流
active_streams = {}
stream_threads = {}

@streams_bp.route('/test-connection', methods=['POST'])
@jwt_required()
def test_stream_connection():
    """测试流连接"""
    try:
        data = request.get_json()
        stream_url = data.get('streamUrl')
        stream_type = data.get('streamType', 'rtmp')
        
        if not stream_url:
            return jsonify({'error': '缺少流地址'}), 400
        
        # 根据流类型进行不同的测试
        if stream_type == 'rtmp':
            # RTMP流测试（模拟）
            success = test_rtmp_connection(stream_url)
            message = 'RTMP流连接成功' if success else 'RTMP流连接失败'
        elif stream_type == 'hls':
            # HLS流测试
            success = test_hls_connection(stream_url)
            message = 'HLS流连接成功' if success else 'HLS流连接失败'
        elif stream_type == 'http':
            # HTTP流测试
            success = test_http_connection(stream_url)
            message = 'HTTP流连接成功' if success else 'HTTP流连接失败'
        else:
            return jsonify({'error': '不支持的流类型'}), 400
        
        return jsonify({
            'success': success,
            'message': message,
            'streamType': stream_type
        }), 200
        
    except Exception as e:
        logger.error(f'测试流连接失败: {str(e)}')
        return jsonify({'error': '测试流连接失败'}), 500

def test_rtmp_connection(stream_url):
    """测试RTMP连接（模拟）"""
    # 在实际应用中，这里应该使用FFmpeg或其他工具测试RTMP连接
    import random
    return random.choice([True, True, True, False])  # 75%成功率

def test_hls_connection(stream_url):
    """测试HLS连接"""
    try:
        import requests
        response = requests.head(stream_url, timeout=10)
        return response.status_code == 200
    except:
        return False

def test_http_connection(stream_url):
    """测试HTTP连接"""
    try:
        import requests
        response = requests.head(stream_url, timeout=10)
        return response.status_code == 200
    except:
        return False

@streams_bp.route('/start/<camera_id>', methods=['POST'])
@jwt_required()
def start_stream(camera_id):
    """启动视频流处理"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        if camera_id in active_streams:
            return jsonify({'message': '流已在运行中'}), 200
        
        # 启动流处理线程
        thread = threading.Thread(
            target=process_stream,
            args=(camera_id, camera.stream_url, camera.stream_type)
        )
        thread.daemon = True
        thread.start()
        
        stream_threads[camera_id] = thread
        active_streams[camera_id] = {
            'status': 'running',
            'start_time': time.time(),
            'frame_count': 0
        }
        
        return jsonify({
            'message': '流处理已启动',
            'cameraId': camera_id
        }), 200
        
    except Exception as e:
        logger.error(f'启动流处理失败: {str(e)}')
        return jsonify({'error': '启动流处理失败'}), 500

@streams_bp.route('/stop/<camera_id>', methods=['POST'])
@jwt_required()
def stop_stream(camera_id):
    """停止视频流处理"""
    try:
        if camera_id not in active_streams:
            return jsonify({'error': '流未运行'}), 400
        
        # 停止流处理
        active_streams[camera_id]['status'] = 'stopping'
        
        # 等待线程结束
        if camera_id in stream_threads:
            stream_threads[camera_id].join(timeout=5)
            del stream_threads[camera_id]
        
        del active_streams[camera_id]
        
        return jsonify({
            'message': '流处理已停止',
            'cameraId': camera_id
        }), 200
        
    except Exception as e:
        logger.error(f'停止流处理失败: {str(e)}')
        return jsonify({'error': '停止流处理失败'}), 500

@streams_bp.route('/status/<camera_id>', methods=['GET'])
@jwt_required()
def get_stream_status(camera_id):
    """获取流状态"""
    try:
        if camera_id not in active_streams:
            return jsonify({
                'status': 'stopped',
                'message': '流未运行'
            }), 200
        
        stream_info = active_streams[camera_id]
        return jsonify({
            'status': stream_info['status'],
            'startTime': stream_info['start_time'],
            'frameCount': stream_info['frame_count'],
            'uptime': time.time() - stream_info['start_time']
        }), 200
        
    except Exception as e:
        logger.error(f'获取流状态失败: {str(e)}')
        return jsonify({'error': '获取流状态失败'}), 500

def process_stream(camera_id, stream_url, stream_type):
    """处理视频流"""
    try:
        logger.info(f'开始处理摄像头 {camera_id} 的流')
        
        # 根据流类型创建不同的捕获器
        if stream_type == 'rtmp':
            cap = cv2.VideoCapture(stream_url)
        elif stream_type == 'hls':
            cap = cv2.VideoCapture(stream_url)
        elif stream_type == 'http':
            cap = cv2.VideoCapture(stream_url)
        else:
            logger.error(f'不支持的流类型: {stream_type}')
            return
        
        if not cap.isOpened():
            logger.error(f'无法打开流: {stream_url}')
            return
        
        frame_count = 0
        
        while active_streams.get(camera_id, {}).get('status') == 'running':
            ret, frame = cap.read()
            if not ret:
                logger.warning(f'无法读取帧: {camera_id}')
                break
            
            frame_count += 1
            active_streams[camera_id]['frame_count'] = frame_count
            
            # 每10帧进行一次AI分析
            if frame_count % 10 == 0:
                analyze_frame(camera_id, frame)
            
            # 控制帧率
            time.sleep(0.033)  # 约30fps
        
        cap.release()
        logger.info(f'摄像头 {camera_id} 的流处理已停止')
        
    except Exception as e:
        logger.error(f'处理流失败: {str(e)}')
    finally:
        if camera_id in active_streams:
            active_streams[camera_id]['status'] = 'stopped'

def analyze_frame(camera_id, frame):
    """分析视频帧"""
    try:
        # 获取活跃的检测模型
        detection_models = AIModel.get_detection_models()
        
        for model in detection_models:
            # 这里应该调用实际的AI模型进行检测
            # 现在使用模拟结果
            predictions = simulate_detection(frame, model)
            
            if predictions:
                # 保存预测结果
                prediction = ModelPrediction(
                    model_id=model.id,
                    camera_id=camera_id,
                    prediction_type='detection',
                    confidence=max([p.get('confidence', 0) for p in predictions]),
                    processing_time=0.1  # 模拟处理时间
                )
                prediction.set_predictions(predictions)
                
                db.session.add(prediction)
                db.session.commit()
                
                # 检查是否检测到可疑行为
                check_suspicious_behavior(camera_id, predictions)
        
    except Exception as e:
        logger.error(f'分析帧失败: {str(e)}')

def simulate_detection(frame, model):
    """模拟目标检测"""
    import random
    
    # 模拟检测结果
    predictions = []
    num_objects = random.randint(0, 3)
    
    for i in range(num_objects):
        if random.random() > model.confidence_threshold:
            predictions.append({
                'class': random.choice(['car', 'truck', 'bus', 'person']),
                'confidence': random.uniform(model.confidence_threshold, 0.95),
                'bbox': [
                    random.randint(0, frame.shape[1]//2),
                    random.randint(0, frame.shape[0]//2),
                    random.randint(frame.shape[1]//2, frame.shape[1]),
                    random.randint(frame.shape[0]//2, frame.shape[0])
                ]
            })
    
    return predictions

def check_suspicious_behavior(camera_id, predictions):
    """检查可疑行为"""
    try:
        for pred in predictions:
            if pred.get('class') == 'person' and pred.get('confidence', 0) > 0.8:
                # 检测到可疑行为，创建告警
                from app.models.alert import Alert
                Alert.create_alert(
                    title=f'检测到可疑行为: 摄像头 {camera_id}',
                    description=f'在摄像头 {camera_id} 检测到可疑行为',
                    alert_type='ai',
                    severity='medium',
                    source='ai_detection',
                    camera_id=camera_id,
                    metadata={'prediction': pred}
                )
                break
    except Exception as e:
        logger.error(f'检查可疑行为失败: {str(e)}')

@streams_bp.route('/capture/<camera_id>', methods=['POST'])
@jwt_required()
def capture_frame(camera_id):
    """捕获当前帧"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': '摄像头不存在'}), 404
        
        # 这里应该从实际的流中捕获帧
        # 现在返回模拟响应
        return jsonify({
            'message': '帧捕获功能开发中',
            'cameraId': camera_id
        }), 200
        
    except Exception as e:
        logger.error(f'捕获帧失败: {str(e)}')
        return jsonify({'error': '捕获帧失败'}), 500

@streams_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_streams():
    """获取活跃流列表"""
    try:
        return jsonify({
            'streams': active_streams
        }), 200
        
    except Exception as e:
        logger.error(f'获取活跃流列表失败: {str(e)}')
        return jsonify({'error': '获取活跃流列表失败'}), 500
