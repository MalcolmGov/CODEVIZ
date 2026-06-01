"""
Utility functions for the application
"""

import json
import uuid
from datetime import datetime


def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())[:8]


def generate_request_id():
    """Generate a unique request ID for logging"""
    return str(uuid.uuid4())


def safe_json_loads(data, default=None):
    """Safely parse JSON with fallback"""
    try:
        if isinstance(data, str):
            return json.loads(data)
        return data
    except:
        return default or {}


def safe_json_dumps(obj, default=None):
    """Safely serialize to JSON"""
    try:
        return json.dumps(obj, default=str)
    except:
        return json.dumps(default or {})


def format_error_response(message, code=None):
    """Format error response consistently"""
    return {
        "status": "error",
        "message": message,
        "code": code,
        "timestamp": datetime.now().isoformat()
    }, 400


def format_success_response(data, message=None):
    """Format success response consistently"""
    return {
        "status": "success",
        "data": data,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }, 200


def truncate_string(s, max_length=100):
    """Truncate string to max length"""
    return (s[:max_length] + '...') if len(s) > max_length else s


def get_file_size_mb(path):
    """Get file size in MB"""
    import os
    return os.path.getsize(path) / (1024 * 1024)
