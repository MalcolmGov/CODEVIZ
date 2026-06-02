"""
Auto-Remediation API

Exposes RemediationDetector (local scan, no GitHub needed) and
RemediationEngine (apply fixes + open PR, requires GITHUB_TOKEN).
"""

from flask import request
from . import remediation_bp
from utils import format_success_response, format_error_response

try:
    from core.remediation_legacy import RemediationDetector
    DETECTOR_AVAILABLE = True
except ImportError as e:
    DETECTOR_AVAILABLE = False
    print(f"⚠️  RemediationDetector not available: {e}")


def _flatten_issues(raw: dict) -> list:
    """
    Flatten the category-keyed detect_all_issues() dict into a list,
    adding a 'category' field and normalising severity to lowercase.
    """
    items = []
    SEV_MAP = {
        'critical': 'critical', 'high': 'high',
        'medium': 'medium', 'low': 'low',
        'warning': 'medium', 'info': 'low', '': 'low',
    }
    CATEGORY_LABELS = {
        'outdated_dependencies':     'Outdated Dependency',
        'hardcoded_secrets':         'Hardcoded Secret',
        'code_formatting':           'Code Formatting',
        'security_misconfigurations': 'Security Misconfiguration',
    }
    for cat, issue_list in raw.items():
        label = CATEGORY_LABELS.get(cat, cat.replace('_', ' ').title())
        for iss in issue_list:
            sev_raw = str(iss.get('severity', '')).lower()
            sev = SEV_MAP.get(sev_raw, 'low')
            items.append({
                **iss,
                'category': cat,
                'category_label': label,
                'severity': sev,
                # ensure these fields always exist
                'file':        iss.get('file', iss.get('file_path', '')),
                'description': iss.get('description', iss.get('issue', '')),
                'fix':         iss.get('fix', iss.get('fix_suggestion', iss.get('recommended_fix', ''))),
            })
    return items


def _build_metrics(issues: list, raw: dict) -> dict:
    from collections import Counter
    sevs = Counter(i['severity'] for i in issues)
    cats = Counter(i['category_label'] for i in issues)
    auto_fixable = sum(1 for i in issues if i.get('fix') or i.get('auto_fixable'))
    return {
        'total': len(issues),
        'by_severity': dict(sevs),
        'by_category': dict(cats),
        'auto_fixable': auto_fixable,
        'categories_with_issues': [k for k, v in raw.items() if v],
    }


@remediation_bp.route('/scan/<session_id>', methods=['POST'])
def scan_remediation(session_id):
    """Detect auto-fixable issues in the session's repository."""
    try:
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        if not DETECTOR_AVAILABLE:
            return format_error_response('Remediation detector not available')[0], 503

        chat = repo_chats[session_id]
        repo_path = getattr(chat, 'repo_path', None)
        if not repo_path:
            return format_error_response('No repository path for this session')[0], 400

        detector = RemediationDetector()
        raw = detector.detect_all_issues(str(repo_path))

        issues  = _flatten_issues(raw)
        metrics = _build_metrics(issues, raw)

        # Sort: critical → high → medium → low
        SEV_ORDER = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        issues.sort(key=lambda x: SEV_ORDER.get(x['severity'], 4))

        return format_success_response({
            'session_id': session_id,
            'issues':     issues[:80],   # cap UI at 80
            'metrics':    metrics,
            'total':      len(issues),
        }, f'Remediation scan complete — {len(issues)} fixable issues found')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


@remediation_bp.route('/preview/<session_id>', methods=['POST'])
def preview_fix(session_id):
    """
    Return a preview of what would be changed for a given category.
    Body: { "category": "outdated_dependencies" }
    """
    try:
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        if not DETECTOR_AVAILABLE:
            return format_error_response('Remediation detector not available')[0], 503

        body     = request.get_json() or {}
        category = body.get('category', '')

        chat      = repo_chats[session_id]
        repo_path = getattr(chat, 'repo_path', None)
        if not repo_path:
            return format_error_response('No repository path')[0], 400

        detector = RemediationDetector()
        raw = detector.detect_all_issues(str(repo_path))
        issues_for_cat = raw.get(category, [])

        return format_success_response({
            'category': category,
            'count':    len(issues_for_cat),
            'issues':   issues_for_cat[:20],
            'note':     'These changes would be applied in a fix run.',
        }, f'{len(issues_for_cat)} issues in {category}')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


@remediation_bp.route('/create-pr/<session_id>', methods=['POST'])
def create_pr(session_id):
    """
    Apply auto-fixes and open a GitHub PR.
    Requires GITHUB_TOKEN in env or X-GitHub-Token header.
    Body: { "branch": "main" }
    """
    try:
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        chat     = repo_chats[session_id]
        repo_url = getattr(chat, '_original_url', None) or getattr(chat, 'repo_path', '')

        if not repo_url or not repo_url.startswith('http'):
            return format_error_response(
                'PR creation requires a GitHub repository URL. Scan a GitHub repo to enable this.'
            )[0], 400

        import os
        token = (
            request.headers.get('X-GitHub-Token')
            or os.getenv('GITHUB_TOKEN', '')
        )
        if not token:
            return format_error_response(
                'No GITHUB_TOKEN configured. Add it in Settings → API Keys.'
            )[0], 400

        body   = request.get_json() or {}
        branch = body.get('branch', 'main')

        from core.remediation_legacy import RemediationEngine, RemediationDetector
        repo_path_local = getattr(chat, 'repo_path', None)
        detected = {}
        if repo_path_local and DETECTOR_AVAILABLE:
            detected = RemediationDetector().detect_all_issues(str(repo_path_local))

        engine = RemediationEngine(token=token)
        result = engine.create_remediation_pr(
            repo_url=repo_url,
            branch=branch,
            detected_issues=detected,
        )

        return format_success_response(result or {}, 'Pull request created successfully')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
