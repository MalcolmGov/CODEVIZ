"""
Compliance API Blueprint
Tier 2: Continuous Compliance Monitoring
GET /api/compliance/frameworks          — list available frameworks
GET /api/compliance/<session_id>        — full compliance report for a session
GET /api/compliance/<session_id>/<fw>   — single framework check
"""

from flask import request
from . import compliance_bp
from utils import format_success_response, format_error_response

try:
    from core.compliance import ComplianceEngine, FRAMEWORKS
    COMPLIANCE_AVAILABLE = True
except ImportError as e:
    COMPLIANCE_AVAILABLE = False
    print(f"⚠️  Compliance engine not available: {e}")


@compliance_bp.route('/frameworks', methods=['GET'])
def list_frameworks():
    """List all available compliance frameworks."""
    if not COMPLIANCE_AVAILABLE:
        return format_error_response('Compliance engine not available')[0], 500
    return format_success_response({'frameworks': FRAMEWORKS})[0], 200


@compliance_bp.route('/<session_id>', methods=['GET'])
def get_compliance(session_id):
    """Run all compliance frameworks against a scanned session."""
    try:
        from api.chat import repo_chats
        if session_id not in repo_chats:
            return format_error_response('Session not found — scan a repository first')[0], 404

        chat = repo_chats[session_id]
        artifacts = (chat.context if hasattr(chat, 'context') and chat.context
                     else chat.get('context', {}) if isinstance(chat, dict) else {})

        if not artifacts:
            return format_error_response('No scan data — run a scan first')[0], 400

        if not COMPLIANCE_AVAILABLE:
            return format_error_response('Compliance engine not available')[0], 500

        fw_param = request.args.get('frameworks', '')
        frameworks = [f.strip() for f in fw_param.split(',') if f.strip()] or None

        engine = ComplianceEngine()
        result = engine.check(artifacts, frameworks)

        return format_success_response(result, 'Compliance check complete')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


@compliance_bp.route('/<session_id>/<framework_id>', methods=['GET'])
def get_framework_compliance(session_id, framework_id):
    """Run a single compliance framework against a scanned session."""
    try:
        from api.chat import repo_chats
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404

        chat = repo_chats[session_id]
        artifacts = (chat.context if hasattr(chat, 'context') and chat.context
                     else chat.get('context', {}) if isinstance(chat, dict) else {})

        if not artifacts:
            return format_error_response('No scan data')[0], 400

        if not COMPLIANCE_AVAILABLE:
            return format_error_response('Compliance engine not available')[0], 500

        if framework_id not in FRAMEWORKS:
            return format_error_response(f'Unknown framework: {framework_id}')[0], 400

        engine = ComplianceEngine()
        result = engine.check(artifacts, [framework_id])
        fw_result = result['frameworks'].get(framework_id, {})

        return format_success_response(fw_result, f'{framework_id.upper()} check complete')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
