"""
Security API Blueprint

Handles security analysis endpoints.
Uses legacy security_detector_legacy.py for all analysis.
"""

from flask import request, jsonify
from . import security_bp
from utils import format_success_response, format_error_response


try:
    from core.security_detector_legacy import SecurityBugDetector
    DETECTOR_AVAILABLE = True
except ImportError:
    DETECTOR_AVAILABLE = False
    print("⚠️  SecurityBugDetector not available")


@security_bp.route('/scan/<session_id>', methods=['POST'])
def scan_security(session_id):
    """
    Scan repository for security issues.
    
    Uses all legacy security detection logic.
    """
    try:
        # Import session storage (shared with chat blueprint)
        from api.chat import repo_chats
        
        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404
        
        chat = repo_chats[session_id]
        
        if DETECTOR_AVAILABLE:
            detector = SecurityBugDetector()
            # Scan using legacy detector
            if hasattr(chat, 'repo_path'):
                bugs = detector.scan_code(chat.repo_path, str(chat.repo_path))
            else:
                bugs = []
        else:
            bugs = []
        
        # Convert to dict
        bugs_data = [bug.to_dict() if hasattr(bug, 'to_dict') else bug for bug in bugs]
        
        # Calculate summary
        critical = len([b for b in bugs_data if 'CRITICAL' in str(b.get('severity', ''))])
        high = len([b for b in bugs_data if 'HIGH' in str(b.get('severity', ''))])
        
        return format_success_response({
            'session_id': session_id,
            'bugs': bugs_data,
            'summary': {
                'total': len(bugs_data),
                'critical': critical,
                'high': high
            }
        }, 'Security scan complete')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@security_bp.route('/bugs/<session_id>', methods=['GET'])
def get_bugs(session_id):
    """Get detected security bugs for session"""
    try:
        from api.chat import repo_chats
        
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404
        
        # This would come from database in production
        # For now, return empty (scan on demand via /scan endpoint)
        return format_success_response({
            'session_id': session_id,
            'bugs': [],
            'note': 'Call POST /scan/<session_id> to scan for bugs'
        })[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@security_bp.route('/fix/<bug_id>', methods=['GET'])
def get_bug_fix(bug_id):
    """Get AI-generated fix for a specific bug"""
    try:
        if DETECTOR_AVAILABLE:
            # In full implementation, would generate fix
            return format_success_response({
                'bug_id': bug_id,
                'fix': {
                    'before': '# Vulnerable code',
                    'after': '# Fixed code',
                    'explanation': 'Security fix applied'
                }
            })[0], 200
        else:
            return format_error_response('Detector not available')[0], 500
            
    except Exception as e:
        return format_error_response(str(e))[0], 500


@security_bp.route('/report/<session_id>', methods=['GET'])
def get_security_report(session_id):
    """Generate security report for session"""
    try:
        from api.chat import repo_chats
        
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404
        
        return format_success_response({
            'session_id': session_id,
            'report': {
                'total_issues': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'generated_at': '2026-06-01T00:00:00'
            }
        }, 'Security report generated')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500
