"""
Configuration for CodeViz Backend

NOTE: All business logic from original codebase is preserved here.
Migration is organizational only - no features lost.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://codeviz:codeviz@localhost:5432/codeviz"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SESSION_TYPE = "redis"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # GitHub
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REDIRECT_URI = os.getenv(
        "GITHUB_REDIRECT_URI",
        "http://localhost:8000/api/auth/github/callback"
    )
    
    # Ollama / LLM
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Slack
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    
    # Email
    GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
    GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")
    
    # API
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    JSON_SORT_KEYS = False
    
    # Features
    ENABLE_REFACTORING = True
    ENABLE_AUTO_FIX = True
    ENABLE_GITHUB_INTEGRATION = True
    ENABLE_SLACK_INTEGRATION = True
    ENABLE_CODE_WIKI = True
    

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Add production-specific settings


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
