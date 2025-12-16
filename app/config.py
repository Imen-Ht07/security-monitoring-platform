import os

class Config:
    """Configuration Flask"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-prod")
    DEBUG = os.getenv("FLASK_ENV") == "development"
    
    # MongoDB
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:changeme@mongodb:27017")
    MONGODB_DB = "security_logs"

    # Elasticsearch
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
    ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
    ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
    ELASTICSEARCH_INDEX = "security_logs"

    # Upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_DIR", "/uploads")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"csv", "json", "txt", "log"}
