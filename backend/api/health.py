"""
Health/Status API Blueprint

System health checks and status information.
"""

from flask import jsonify
from . import health_bp
from extensions import redis_client
from extensions import db
import os


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns status of all services:
    - Flask app
    - Database
    - Redis
    - Ollama (LLM)
    """
    
    health_status = {
        'status': 'healthy',
        'services': {},
        'version': '2.0.0',
        'environment': os.getenv('FLASK_ENV', 'development')
    }
    
    # Flask app is running (we're here!)
    health_status['services']['app'] = {
        'status': 'healthy',
        'type': 'Flask'
    }
    
    # Check database
    try:
        # Simple query to verify DB connection
        db.session.execute('SELECT 1')
        health_status['services']['database'] = {
            'status': 'healthy',
            'type': 'PostgreSQL'
        }
    except Exception as e:
        health_status['services']['database'] = {
            'status': 'unhealthy',
            'type': 'PostgreSQL',
            'error': str(e)
        }
        health_status['status'] = 'degraded'
    
    # Check Redis
    try:
        if redis_client:
            redis_client.ping()
            health_status['services']['cache'] = {
                'status': 'healthy',
                'type': 'Redis'
            }
        else:
            health_status['services']['cache'] = {
                'status': 'unavailable',
                'type': 'Redis'
            }
    except Exception as e:
        health_status['services']['cache'] = {
            'status': 'unhealthy',
            'type': 'Redis',
            'error': str(e)
        }
    
    # Check Ollama (LLM)
    try:
        import requests
        ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        
        if response.status_code == 200:
            health_status['services']['ollama'] = {
                'status': 'healthy',
                'type': 'Ollama LLM'
            }
        else:
            health_status['services']['ollama'] = {
                'status': 'unhealthy',
                'type': 'Ollama LLM',
                'error': f'Status {response.status_code}'
            }
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['services']['ollama'] = {
            'status': 'unavailable',
            'type': 'Ollama LLM',
            'error': str(e)
        }
    
    # Overall status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return jsonify(health_status), status_code


@health_bp.route('/status', methods=['GET'])
def status():
    """Quick status check (shorter than health)"""
    return jsonify({
        'status': 'running',
        'version': '2.0.0'
    }), 200


@health_bp.route('/info', methods=['GET'])
def info():
    """Get system information"""
    return jsonify({
        'name': 'CodeViz Platform',
        'version': '2.0.0',
        'environment': os.getenv('FLASK_ENV', 'development'),
        'debug': os.getenv('DEBUG', 'false') == 'true',
        'endpoints': {
            'chat': '/api/chat',
            'security': '/api/security',
            'refactoring': '/api/refactoring',
            'auth': '/api/auth',
            'repositories': '/api/repositories',
            'health': '/api/health'
        }
    }), 200
