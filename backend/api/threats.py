"""
Threat Simulation API Blueprint
GET /api/threats/<session_id>?actor=apt   — full simulation for a session
GET /api/threats/actors                   — list available threat actor profiles
"""

from flask import request
from . import threats_bp
from utils import format_success_response, format_error_response

try:
    from core.threat_simulator import ThreatSimulator, THREAT_ACTORS
    SIMULATOR_AVAILABLE = True
except ImportError as e:
    SIMULATOR_AVAILABLE = False
    print(f"⚠️  Threat simulator not available: {e}")


@threats_bp.route('/actors', methods=['GET'])
def list_actors():
    if not SIMULATOR_AVAILABLE:
        return format_error_response('Simulator not available')[0], 500
    return format_success_response({'actors': THREAT_ACTORS})[0], 200


@threats_bp.route('/<session_id>', methods=['GET'])
def simulate(session_id):
    """Run threat simulation for a scanned session."""
    try:
        from api.chat import repo_chats
        if session_id not in repo_chats:
            return format_error_response('Session not found — scan a repository first')[0], 404

        chat = repo_chats[session_id]
        artifacts = (chat.context if hasattr(chat, 'context') and chat.context
                     else chat.get('context', {}) if isinstance(chat, dict) else {})

        if not artifacts:
            return format_error_response('No scan data — run a scan first')[0], 400

        if not SIMULATOR_AVAILABLE:
            return format_error_response('Simulator not available')[0], 500

        actor_id = request.args.get('actor', 'apt')
        result = ThreatSimulator().simulate(artifacts, actor_id)
        return format_success_response(result, 'Threat simulation complete')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
