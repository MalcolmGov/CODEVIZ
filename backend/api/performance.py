"""
Performance Analysis API Blueprint

Wires core/performance_analyzer_legacy.py into the REST API.
Scans a session's repository for N+1 queries, memory leaks,
inefficient algorithms, blocking I/O, and more.
"""

from flask import request
from . import performance_bp
from utils import format_success_response, format_error_response, get_repo_path

try:
    from core.performance_analyzer_legacy import PerformanceAnalyzer, PerformanceSeverity
    PERF_AVAILABLE = True
except ImportError as e:
    PERF_AVAILABLE = False
    print(f"⚠️  PerformanceAnalyzer not available: {e}")

# Normalise severity strings coming out of the legacy enum
def _norm_severity(sev_str: str) -> str:
    s = sev_str.lower()
    for level in ('critical', 'high', 'medium', 'low'):
        if level in s:
            return level
    return 'low'


@performance_bp.route('/scan/<session_id>', methods=['POST'])
def scan_performance(session_id):
    """
    Run performance analysis on a session's repository.

    Returns issues + aggregate metrics.
    """
    try:
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        if not PERF_AVAILABLE:
            return format_error_response('Performance analyser not available')[0], 503

        chat = repo_chats[session_id]
        repo_path = get_repo_path(chat)

        if not repo_path:
            return format_error_response('No repository path for this session')[0], 400

        analyzer = PerformanceAnalyzer()
        issues, metrics = analyzer.scan_files(str(repo_path), file_pattern='*.py')

        # Also scan TypeScript/JavaScript files (pattern-based, not AST)
        ts_issues, ts_metrics = analyzer.scan_files(str(repo_path), file_pattern='*.ts')
        tsx_issues, _         = analyzer.scan_files(str(repo_path), file_pattern='*.tsx')

        all_issues = issues + ts_issues + tsx_issues

        # Re-calculate combined metrics
        combined_metrics = analyzer._calculate_metrics(
            all_issues,
            len({i.file_path for i in all_issues})
        )

        issues_data = []
        for issue in all_issues[:60]:   # cap UI at 60 findings
            d = issue.to_dict()
            d['severity'] = _norm_severity(d['severity'])
            issues_data.append(d)

        # Sort by severity
        SEV_ORDER = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        issues_data.sort(key=lambda x: SEV_ORDER.get(x['severity'], 4))

        result = {
            'session_id': session_id,
            'issues': issues_data,
            'metrics': combined_metrics.to_dict(),
            'total': len(all_issues),
        }
        try:
            from core.session_store import cache_result
            cache_result(session_id, 'performance', result)
        except Exception:
            pass
        return format_success_response(result, f'Performance scan complete — {len(all_issues)} issues found')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


@performance_bp.route('/issue/<session_id>/<issue_id>', methods=['GET'])
def get_issue_detail(session_id, issue_id):
    """
    Get optimisation code (before/after) for a specific issue.
    Re-runs the analyser and finds the matching issue.
    """
    try:
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        if not PERF_AVAILABLE:
            return format_error_response('Performance analyser not available')[0], 503

        chat = repo_chats[session_id]
        repo_path = get_repo_path(chat)
        if not repo_path:
            return format_error_response('No repo path')[0], 400

        analyzer = PerformanceAnalyzer()
        issues, _ = analyzer.scan_files(str(repo_path))
        matched   = next((i for i in issues if i.issue_id == issue_id), None)

        if not matched:
            return format_error_response('Issue not found')[0], 404

        opt_code = analyzer.generate_optimization_code(matched)
        d = matched.to_dict()
        d['severity']   = _norm_severity(d['severity'])
        d['before_code'] = opt_code.get('before', matched.code_snippet)
        d['after_code']  = opt_code.get('after', matched.fix_suggestion)

        return format_success_response(d, 'Issue detail fetched')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
