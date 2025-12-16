import os
from datetime import timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration Flask par défaut"""
    
    # Flask
    SECRET_KEY = os. getenv("SECRET_KEY", "dev-key-change-in-production")
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    TESTING = False
    
    # Session - Sécurisée
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Elasticsearch
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
    ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
    ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
    ELASTICSEARCH_INDEX = "security-logs"
    
    # MongoDB
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:changeme@mongodb:27017")
    MONGODB_DB = "security_logs"
    
    # Redis
    REDIS_URL = os. getenv("REDIS_URL", "redis://:changeme@redis:6379/0")
    
    # Upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/uploads")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS = {"csv", "json", "txt", "log"}
    
    # Pagination
    ITEMS_PER_PAGE = 50
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class DevelopmentConfig(Config):
    """Config développement"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Config tests"""
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    """Config production"""
    DEBUG = False
    TESTING = False