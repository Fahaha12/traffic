"""
数据库配置文件
支持MySQL数据库连接和配置
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'traffic_monitor')
        self.charset = 'utf8mb4'
        
    def get_database_url(self):
        """获取数据库连接URL"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"
    
    def get_engine(self):
        """获取数据库引擎"""
        database_url = self.get_database_url()
        
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=os.getenv('DB_ECHO', 'False').lower() == 'true'
        )
        
        return engine
    
    def get_session(self):
        """获取数据库会话"""
        engine = self.get_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()

# 数据库配置实例
db_config = DatabaseConfig()

# 数据库连接参数
DATABASE_CONFIG = {
    'host': db_config.host,
    'port': db_config.port,
    'user': db_config.user,
    'password': db_config.password,
    'database': db_config.database,
    'charset': db_config.charset
}

# SQLAlchemy配置
SQLALCHEMY_DATABASE_URI = db_config.get_database_url()
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'echo': os.getenv('DB_ECHO', 'False').lower() == 'true'
}
