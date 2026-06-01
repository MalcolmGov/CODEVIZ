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
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
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


@health_bp.route('/health/ping-endpoint', methods=['POST'])
def ping_endpoint():
    """Test a specific endpoint's reachability and return its HTTP status"""
    try:
        from flask import request
        data = request.get_json() or {}
        path = data.get('path', '')
        method = data.get('method', 'GET').upper()
        base_url = data.get('base_url', '').strip()
        
        if not base_url:
            try:
                from api.chat import repo_chats
                if repo_chats:
                    latest_chat = list(repo_chats.values())[-1]
                    if hasattr(latest_chat, 'context') and latest_chat.context:
                        prod_url = latest_chat.context.get('production_base_url')
                        if prod_url:
                            base_url = prod_url
                        else:
                            apis = latest_chat.context.get('apis', [])
                            if apis and apis[0].get('base_url'):
                                base_url = apis[0]['base_url']
            except Exception:
                pass
                
        if not base_url:
            base_url = 'http://localhost:8000'
        
        if not path:
            return jsonify({'status': 'error', 'message': 'Path required'}), 400
            
        import requests
        
        # Ensure base_url does not end with / and clean_path starts with /
        if base_url.endswith('/'):
            base_url = base_url.rstrip('/')
            
        clean_path = path.strip()
        if not clean_path.startswith('/'):
            clean_path = '/' + clean_path
            
        target_url = f"{base_url}{clean_path}"
        
        try:
            if method == 'GET':
                response = requests.get(target_url, timeout=3)
            elif method == 'POST':
                response = requests.post(target_url, json={}, timeout=3)
            elif method == 'PUT':
                response = requests.put(target_url, json={}, timeout=3)
            elif method == 'DELETE':
                response = requests.delete(target_url, timeout=3)
            else:
                response = requests.request(method, target_url, timeout=3)
                
            status_code = response.status_code
            is_active = status_code != 404
            
            return jsonify({
                'status': 'success',
                'status_code': status_code,
                'is_active': is_active,
                'message': f"Returned HTTP {status_code}"
            }), 200
            
        except requests.exceptions.RequestException as req_err:
            return jsonify({
                'status': 'success',
                'status_code': None,
                'is_active': False,
                'message': f"Offline: Connection refused"
            }), 200
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
