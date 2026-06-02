"""
Auto-Remediation API

Exposes RemediationDetector (local scan, no GitHub needed) and
RemediationEngine (apply fixes + open PR, requires GITHUB_TOKEN).
"""

from flask import request
from . import remediation_bp
from utils import format_success_response, format_error_response, get_repo_path

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
        repo_path = get_repo_path(chat)
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
        repo_path = get_repo_path(chat)
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
        repo_path_local = get_repo_path(chat)
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


# ── AI Test Generation ────────────────────────────────────────────────────────

_TEST_PROMPT = """\
You are an expert software engineer. Given a security or code-quality issue and its fix,
generate a focused unit test that:
1. Verifies the vulnerability is NOT present after the fix
2. Optionally includes a regression test proving the original vulnerable behaviour
3. Follows best practices for the detected language ({language})
4. Uses standard test frameworks: pytest for Python, Jest/Vitest for JS/TS

Issue type:   {issue_type}
File:         {file_path}
Description:  {description}
Original code (before fix):
```
{original_code}
```
Fixed code (after fix):
```
{fixed_code}
```

Return ONLY the test code — no explanation, no markdown fences. Start directly with the import or test function.
"""


@remediation_bp.route('/generate-tests', methods=['POST'])
def generate_tests():
    """
    Generate a unit test for a fix using the local Ollama LLM.

    Body:
    {
        "issue_type":    "SQL Injection",
        "file_path":     "app/models.py",
        "description":   "Unsanitised user input passed to execute()",
        "original_code": "...",
        "fixed_code":    "...",
        "language":      "python"   // optional, auto-detected if omitted
    }
    """
    try:
        body         = request.get_json() or {}
        issue_type   = body.get('issue_type', 'Security Issue')
        file_path    = body.get('file_path', 'unknown')
        description  = body.get('description', '')
        original_code = body.get('original_code', '# (original code not provided)')
        fixed_code   = body.get('fixed_code', '# (fixed code not provided)')

        # Auto-detect language from file extension
        ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
        language = body.get('language') or {
            'py': 'Python (pytest)', 'ts': 'TypeScript (Jest)',
            'tsx': 'TypeScript/React (Vitest)', 'js': 'JavaScript (Jest)',
            'jsx': 'JavaScript/React (Vitest)',
        }.get(ext, 'Python (pytest)')

        prompt = _TEST_PROMPT.format(
            language=language,
            issue_type=issue_type,
            file_path=file_path,
            description=description,
            original_code=original_code[:800],
            fixed_code=fixed_code[:800],
        )

        # Try Ollama first
        test_code = None
        try:
            from services.ollama import OllamaClient
            client    = OllamaClient()
            test_code = client.generate(prompt)
        except Exception as llm_err:
            print(f"[test-gen] Ollama unavailable: {llm_err}")

        # Deterministic fallback when Ollama isn't running
        if not test_code or len(test_code.strip()) < 20:
            is_python = 'python' in language.lower()
            if is_python:
                test_code = f'''\
import pytest
# Auto-generated regression test for: {issue_type}
# File: {file_path}

def test_{issue_type.lower().replace(" ", "_").replace("-", "_")}_is_fixed():
    """
    Verify that the fix for '{issue_type}' in {file_path} is applied correctly.
    Replace the assertion below with a real call to the fixed function.
    """
    # TODO: import the fixed function and assert the vulnerability is gone
    # Example: assert sanitised_input("'; DROP TABLE users;--") != "'; DROP TABLE users;--"
    assert True, "Replace with a real assertion targeting the fix"


def test_{issue_type.lower().replace(" ", "_").replace("-", "_")}_regression():
    """Ensure original vulnerable behaviour no longer exists."""
    # TODO: confirm the dangerous input path is blocked
    pass
'''
            else:
                test_code = f'''\
// Auto-generated regression test for: {issue_type}
// File: {file_path}
import {{ describe, it, expect }} from 'vitest'

describe('{issue_type}', () => {{
  it('should not be present after the fix', () => {{
    // TODO: import the fixed function and assert the vulnerability is gone
    expect(true).toBe(true) // Replace with a real assertion
  }})

  it('regression: original vulnerable input should be handled safely', () => {{
    // TODO: confirm the dangerous input path is blocked
    expect(true).toBe(true)
  }})
}})
'''

        # Derive a suggested filename
        base    = file_path.rsplit('/', 1)[-1].rsplit('.', 1)
        stem    = base[0] if len(base) > 1 else base[0]
        ext_out = 'py' if 'python' in language.lower() else 'test.ts' if 'typescript' in language.lower() else 'test.js'
        suggested_filename = f'test_{stem}.{ext_out}' if 'python' in language.lower() else f'{stem}.{ext_out}'

        return format_success_response({
            'test_code':          test_code.strip(),
            'language':           language,
            'suggested_filename': suggested_filename,
            'issue_type':         issue_type,
            'llm_used':           test_code is not None and 'TODO' not in test_code,
        }, 'Test generated')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
