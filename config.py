import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'redis://localhost:6379')
    
    # Application Settings
    MAX_POPULATION_SIZE = int(os.environ.get('MAX_POPULATION_SIZE', 10000))
    DEFAULT_BATCH_SIZE = int(os.environ.get('DEFAULT_BATCH_SIZE', 50))
    CACHE_TTL = int(os.environ.get('CACHE_TTL', 3600))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    FLASK_ENV = 'testing'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}