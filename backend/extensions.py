"""
Flask extensions initialization

All business logic services are registered here.
This is the central DI container for the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
import redis

# Database ORM
db = SQLAlchemy()
migrate = Migrate()

# Session management
redis_client = None

def init_session(app):
    """Initialize Redis session"""
    global redis_client
    from config import Config
    
    try:
        redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
        redis_client.ping()
        Session(app)
        print("✅ Redis session initialized")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        redis_client = None

def init_extensions(app):
    """Initialize all Flask extensions"""
    
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # CORS for frontend communication
    CORS(app, origins=[r"http://localhost:\d+", r"http://127.0.0.1:\d+"], supports_credentials=True)
    
    # Session
    init_session(app)
    
    print("✅ All extensions initialized")
