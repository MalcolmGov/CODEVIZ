"""
Notifications API

Exposes Slack alerting via SlackNotificationManager.
Fires automatically after security scans when SLACK_WEBHOOK_URL is set,
and provides a manual test endpoint.
"""

import os
from flask import request
from . import notifications_bp
from utils import format_success_response, format_error_response

try:
    from services.slack_legacy import SlackNotificationManager
    SLACK_AVAILABLE = True
except ImportError as e:
    SLACK_AVAILABLE = False
    print(f"⚠️  SlackNotificationManager not available: {e}")


def _get_manager(webhook_url: str = None):
    url = webhook_url or os.getenv('SLACK_WEBHOOK_URL', '')
    return SlackNotificationManager(webhook_url=url) if url else None


@notifications_bp.route('/slack/test', methods=['POST'])
def test_slack():
    """Send a test Slack notification. Body: { "webhook_url": "https://..." }"""
    try:
        if not SLACK_AVAILABLE:
            return format_error_response('Slack integration not available')[0], 503

        body = request.get_json() or {}
        webhook_url = body.get('webhook_url') or os.getenv('SLACK_WEBHOOK_URL', '')

        if not webhook_url:
            return format_error_response(
                'No SLACK_WEBHOOK_URL configured. Add it in Settings → Integrations.'
            )[0], 400

        mgr = _get_manager(webhook_url)
        ok = mgr.send_vulnerability_alert(
            repo_name='CodeViz Test',
            severity='high',
            findings=[{
                'title': 'Test alert from CodeViz',
                'cve': 'CVE-TEST-001',
            }],
        )

        if ok:
            return format_success_response({}, 'Test notification sent to Slack')[0], 200
        else:
            return format_error_response('Slack returned an error — check your webhook URL')[0], 502

    except Exception as e:
        return format_error_response(str(e))[0], 500


@notifications_bp.route('/slack/alert/<session_id>', methods=['POST'])
def send_security_alert(session_id):
    """
    Fire a Slack alert for a session's security findings.
    Automatically filters to critical/high only.
    Body: { "webhook_url": "...", "min_severity": "high" }
    """
    try:
        from api.chat import repo_chats
        from utils import get_session_context

        if not SLACK_AVAILABLE:
            return format_error_response('Slack integration not available')[0], 503

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        body = request.get_json() or {}
        webhook_url  = body.get('webhook_url') or os.getenv('SLACK_WEBHOOK_URL', '')
        min_severity = body.get('min_severity', 'high')

        if not webhook_url:
            return format_error_response('No SLACK_WEBHOOK_URL configured')[0], 400

        chat    = repo_chats[session_id]
        context = get_session_context(chat)
        issues  = context.get('security_issues', [])

        SEV_RANK = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        min_rank = SEV_RANK.get(min_severity, 3)
        filtered = [
            i for i in issues
            if SEV_RANK.get(str(i.get('severity', '')).lower(), 0) >= min_rank
        ]

        if not filtered:
            return format_success_response({
                'sent': False,
                'reason': f'No {min_severity}+ severity issues found'
            }, 'No alert needed')[0], 200

        repo_path = getattr(chat, 'repo_path', None) or (
            chat.get('repo_path') if isinstance(chat, dict) else None
        )
        repo_name = (str(repo_path or '').rstrip('/').split('/')[-1]) or 'Unknown'

        # Determine dominant severity
        has_critical = any(
            str(i.get('severity', '')).lower() == 'critical' for i in filtered
        )
        dominant = 'critical' if has_critical else 'high'

        findings = [
            {
                'title': i.get('type', i.get('message', 'Security issue')),
                'cve':   i.get('cve'),
            }
            for i in filtered[:10]
        ]

        mgr = _get_manager(webhook_url)
        ok  = mgr.send_vulnerability_alert(
            repo_name=repo_name,
            severity=dominant,
            findings=findings,
        )

        return format_success_response({
            'sent':     ok,
            'count':    len(filtered),
            'severity': dominant,
        }, f'Slack alert {"sent" if ok else "failed"} — {len(filtered)} issues')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


@notifications_bp.route('/slack/status', methods=['GET'])
def slack_status():
    """Return whether Slack is configured."""
    webhook = os.getenv('SLACK_WEBHOOK_URL', '')
    channel = os.getenv('SLACK_CHANNEL', '#security-alerts')
    return format_success_response({
        'configured': bool(webhook),
        'channel':    channel,
        'available':  SLACK_AVAILABLE,
    }, 'Slack status')[0], 200
