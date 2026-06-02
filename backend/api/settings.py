"""
Settings API Blueprint

Handles reading and saving workspace configuration, and testing
third-party service connections (GitHub, Ollama, Slack).
"""

from flask import request
from . import settings_bp
from utils import format_success_response, format_error_response
import os

# In-memory settings store (persists for backend session)
# Frontend also persists in localStorage — these stay in sync via API
_settings: dict = {
    'githubToken':               os.getenv('GITHUB_TOKEN', ''),
    'ollamaUrl':                 os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
    'ollamaModel':               os.getenv('OLLAMA_MODEL', 'mistral'),
    'slackWebhook':              os.getenv('SLACK_WEBHOOK_URL', ''),
    'gmailAddress':              os.getenv('GMAIL_ADDRESS', ''),
    'enableSlackNotifications':  bool(os.getenv('SLACK_WEBHOOK_URL')),
    'enableEmailReports':        bool(os.getenv('GMAIL_ADDRESS')),
    'defaultRemediationMode':    'hitl',
    'scanDepth':                 'standard',
    'excludePaths':              'node_modules, .git, dist, build, venv, __pycache__',
    'maxFilesPerScan':           100,
}

# Fields that should never be returned in full (masked)
_SENSITIVE = {'githubToken', 'slackWebhook', 'gmailAddress'}


def _mask(key: str, val: str) -> str:
    if key in _SENSITIVE and val:
        visible = val[:4] if len(val) >= 4 else val
        return visible + '•' * min(len(val) - 4, 20)
    return val


@settings_bp.route('', methods=['GET'])
def get_settings():
    """Return current settings (sensitive fields masked)."""
    try:
        masked = {
            k: _mask(k, v) if isinstance(v, str) else v
            for k, v in _settings.items()
        }
        return format_success_response(masked, 'Settings loaded')[0], 200
    except Exception as e:
        return format_error_response(str(e))[0], 500


@settings_bp.route('', methods=['POST'])
def save_settings():
    """Save one or more settings fields."""
    try:
        data = request.get_json() or {}
        allowed = set(_settings.keys())
        updated = []
        for key, val in data.items():
            if key in allowed:
                # Don't overwrite a real token with a masked preview
                if isinstance(val, str) and '•' in val:
                    continue
                _settings[key] = val
                updated.append(key)
        return format_success_response({'updated': updated}, 'Settings saved')[0], 200
    except Exception as e:
        return format_error_response(str(e))[0], 500


@settings_bp.route('/test/github', methods=['POST'])
def test_github():
    """Validate a GitHub personal access token."""
    try:
        import requests as req
        token = request.get_json().get('token') or _settings.get('githubToken', '')
        if not token or '•' in token:
            return format_error_response('No token provided')[0], 400

        resp = req.get(
            'https://api.github.com/user',
            headers={'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'},
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            return format_success_response({
                'valid': True,
                'username': data.get('login'),
                'name': data.get('name'),
                'public_repos': data.get('public_repos'),
                'scopes': resp.headers.get('X-OAuth-Scopes', ''),
            }, f"Connected as {data.get('login')}")[0], 200
        else:
            return format_error_response(f'GitHub returned {resp.status_code}')[0], 400
    except Exception as e:
        return format_error_response(str(e))[0], 500


@settings_bp.route('/test/ollama', methods=['POST'])
def test_ollama():
    """Ping Ollama and list available models."""
    try:
        import requests as req
        base_url = (request.get_json() or {}).get('url') or _settings.get('ollamaUrl', 'http://localhost:11434')
        base_url = base_url.rstrip('/')

        resp = req.get(f'{base_url}/api/tags', timeout=5)
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
            return format_success_response({
                'reachable': True,
                'models': models,
                'model_count': len(models),
            }, f'Ollama reachable · {len(models)} model(s) available')[0], 200
        return format_error_response(f'Ollama returned {resp.status_code}')[0], 400
    except Exception as e:
        return format_error_response(f'Cannot reach Ollama: {e}')[0], 500


@settings_bp.route('/test/slack', methods=['POST'])
def test_slack():
    """Send a test message to a Slack webhook."""
    try:
        import requests as req
        webhook = (request.get_json() or {}).get('webhook') or _settings.get('slackWebhook', '')
        if not webhook or '•' in webhook:
            return format_error_response('No webhook URL provided')[0], 400

        payload = {'text': '✅ CodeViz settings test — Slack integration is working.'}
        resp = req.post(webhook, json=payload, timeout=8)
        if resp.status_code == 200:
            return format_success_response({'sent': True}, 'Test message sent to Slack')[0], 200
        return format_error_response(f'Slack returned {resp.status_code}: {resp.text}')[0], 400
    except Exception as e:
        return format_error_response(str(e))[0], 500
