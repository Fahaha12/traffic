#!/usr/bin/env python3
"""
定时清理临时文件服务
用于清理HLS流文件、视频临时文件等
"""

import os
import time
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class TempFileCleaner:
    def __init__(self, base_dir='.'):
        self.base_dir = Path(base_dir)
        self.cleanup_config = {
            # HLS流文件目录
            'streams': {
                'path': self.base_dir / 'streams',
                'max_age_hours': 2,  # 2小时后清理
                'extensions': ['.m3u8', '.ts', '.mp4']
            },
            # 临时文件目录
            'temp': {
                'path': self.base_dir / 'temp',
                'max_age_hours': 1,  # 1小时后清理
                'extensions': ['.tmp', '.temp', '.log']
            },
            # 上传文件目录
            'uploads': {
                'path': self.base_dir / 'uploads',
                'max_age_hours': 24,  # 24小时后清理
                'extensions': ['.mp4', '.avi', '.mov', '.mkv']
            },
            # 日志文件
            'logs': {
                'path': self.base_dir / 'logs',
                'max_age_hours': 168,  # 7天后清理
                'extensions': ['.log']
            }
        }
    
    def cleanup_directory(self, config):
        """清理指定目录中的过期文件"""
        directory = config['path']
        max_age = timedelta(hours=config['max_age_hours'])
        extensions = config['extensions']
        
        if not directory.exists():
            logger.info(f"目录不存在，跳过: {directory}")
            return
        
        current_time = datetime.now()
        cleaned_count = 0
        total_size = 0
        
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    # 检查文件扩展名
                    if extensions and not any(str(file_path).endswith(ext) for ext in extensions):
                        continue
                    
                    # 检查文件年龄
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if current_time - file_mtime > max_age:
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.info(f"已删除过期文件: {file_path} (大小: {file_size} bytes)")
                        except Exception as e:
                            logger.error(f"删除文件失败 {file_path}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"目录 {directory} 清理完成: 删除 {cleaned_count} 个文件, 释放 {total_size} bytes")
            else:
                logger.info(f"目录 {directory} 无需清理")
                
        except Exception as e:
            logger.error(f"清理目录 {directory} 时出错: {e}")
    
    def cleanup_empty_directories(self):
        """清理空目录"""
        cleaned_count = 0
        
        for config in self.cleanup_config.values():
            directory = config['path']
            if not directory.exists():
                continue
            
            try:
                # 递归删除空目录
                for dir_path in sorted(directory.rglob('*'), key=lambda p: len(p.parts), reverse=True):
                    if dir_path.is_dir() and not any(dir_path.iterdir()):
                        try:
                            dir_path.rmdir()
                            cleaned_count += 1
                            logger.info(f"已删除空目录: {dir_path}")
                        except Exception as e:
                            logger.error(f"删除空目录失败 {dir_path}: {e}")
            except Exception as e:
                logger.error(f"清理空目录时出错: {e}")
        
        if cleaned_count > 0:
            logger.info(f"清理完成: 删除 {cleaned_count} 个空目录")
    
    def cleanup_files(self):
        """执行文件清理（兼容性方法）"""
        return self.cleanup_all()
    
    def cleanup_all(self):
        """执行完整清理"""
        logger.info("开始执行定时清理任务...")
        start_time = time.time()
        
        # 清理各个目录
        for name, config in self.cleanup_config.items():
            logger.info(f"清理 {name} 目录...")
            self.cleanup_directory(config)
        
        # 清理空目录
        self.cleanup_empty_directories()
        
        # 清理系统临时文件
        self.cleanup_system_temp()
        
        end_time = time.time()
        logger.info(f"定时清理任务完成，耗时: {end_time - start_time:.2f} 秒")
        return {
            'success': True,
            'duration': end_time - start_time,
            'message': '清理任务执行完成'
        }
    
    def cleanup_system_temp(self):
        """清理系统临时文件"""
        temp_dirs = [
            '/tmp' if os.name != 'nt' else os.environ.get('TEMP', ''),
            '/var/tmp' if os.name != 'nt' else os.environ.get('TMP', ''),
            os.path.join(os.getcwd(), 'temp'),
            os.path.join(os.getcwd(), 'tmp')
        ]
        
        for temp_dir in temp_dirs:
            if not temp_dir or not os.path.exists(temp_dir):
                continue
            
            try:
                current_time = time.time()
                max_age = 3600  # 1小时
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            if current_time - os.path.getmtime(file_path) > max_age:
                                # 检查是否是我们的临时文件
                                if any(keyword in file for keyword in ['traffic', 'stream', 'hls', 'rtmp']):
                                    os.remove(file_path)
                                    logger.info(f"已删除系统临时文件: {file_path}")
                        except Exception as e:
                            logger.error(f"删除系统临时文件失败 {file_path}: {e}")
            except Exception as e:
                logger.error(f"清理系统临时目录 {temp_dir} 时出错: {e}")
    
    def get_disk_usage(self):
        """获取磁盘使用情况"""
        usage_info = {}
        
        for name, config in self.cleanup_config.items():
            directory = config['path']
            if directory.exists():
                total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
                file_count = len(list(directory.rglob('*')))
                usage_info[name] = {
                    'size': total_size,
                    'files': file_count,
                    'path': str(directory)
                }
        
        return usage_info
    
    def print_usage_report(self):
        """打印使用情况报告"""
        usage_info = self.get_disk_usage()
        
        logger.info("=== 磁盘使用情况报告 ===")
        for name, info in usage_info.items():
            size_mb = info['size'] / (1024 * 1024)
            logger.info(f"{name}: {info['files']} 个文件, {size_mb:.2f} MB")
        logger.info("========================")
