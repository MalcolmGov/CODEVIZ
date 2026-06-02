"""
Dashboard Summary API

Aggregates live data from all analysers into a single summary endpoint.
Falls back to cached results if available; runs fresh scans if not.
"""

from flask import request
from . import dashboard_bp
from utils import format_success_response, format_error_response


def _norm_sev(s: str) -> str:
    s = s.lower()
    for lvl in ('critical', 'high', 'medium', 'low'):
        if lvl in s:
            return lvl
    return 'low'


def _count_by_severity(items: list, sev_key: str = 'severity') -> dict:
    counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for item in items:
        sev = _norm_sev(str(item.get(sev_key, 'low')))
        counts[sev] = counts.get(sev, 0) + 1
    return counts


@dashboard_bp.route('/summary/<session_id>', methods=['GET'])
def get_summary(session_id):
    """
    Return aggregated stats for all analysers for a given session.
    Uses cached results where available, skips analysers that haven't run.
    """
    try:
        from api.chat import repo_chats
        from core.session_store import get_cached

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        chat      = repo_chats[session_id]
        repo_path = getattr(chat, 'repo_path', None) or (
            chat.get('repo_path') if isinstance(chat, dict) else None
        )
        repo_name = (repo_path or '').rstrip('/').split('/')[-1] if repo_path else 'Unknown'

        summary = {
            'session_id': session_id,
            'repo_name':  repo_name,
            'repo_path':  repo_path,
            'sections':   {},
        }

        # ── Security ──────────────────────────────────────────────────────
        try:
            from core.security_detector_legacy import SecurityBugDetector
            detector = SecurityBugDetector()
            bugs, _  = detector.scan_files(str(repo_path)) if repo_path else ([], None)
            sec_sevs = _count_by_severity([b.to_dict() for b in bugs])
            summary['sections']['security'] = {
                'total':    len(bugs),
                'critical': sec_sevs['critical'],
                'high':     sec_sevs['high'],
                'medium':   sec_sevs['medium'],
                'low':      sec_sevs['low'],
                'label':    'Security Issues',
                'route':    '/security',
                'color':    '#ef4444',
            }
        except Exception:
            summary['sections']['security'] = _empty_section('Security Issues', '/security', '#ef4444')

        # ── Performance ───────────────────────────────────────────────────
        try:
            cached = get_cached(session_id, 'performance')
            if cached:
                m = cached.get('metrics', {})
                summary['sections']['performance'] = {
                    'total':    m.get('total_issues', 0),
                    'critical': m.get('by_severity', {}).get('critical', 0),
                    'high':     m.get('by_severity', {}).get('high', 0),
                    'medium':   m.get('by_severity', {}).get('medium', 0),
                    'low':      m.get('by_severity', {}).get('low', 0),
                    'label':    'Performance Issues',
                    'route':    '/performance',
                    'color':    '#f97316',
                }
            else:
                from core.performance_analyzer_legacy import PerformanceAnalyzer
                analyzer = PerformanceAnalyzer()
                perf_issues, perf_metrics = analyzer.scan_files(str(repo_path)) if repo_path else ([], None)
                m = perf_metrics.to_dict() if perf_metrics else {}
                summary['sections']['performance'] = {
                    'total':    len(perf_issues),
                    'critical': m.get('critical', 0),
                    'high':     0,
                    'medium':   0,
                    'low':      0,
                    'label':    'Performance Issues',
                    'route':    '/performance',
                    'color':    '#f97316',
                }
        except Exception:
            summary['sections']['performance'] = _empty_section('Performance Issues', '/performance', '#f97316')

        # ── Code Smells ───────────────────────────────────────────────────
        try:
            from core.code_smell_detector_legacy import CodeSmellDetector
            det    = CodeSmellDetector()
            smells = det.scan_files(str(repo_path)) if repo_path else []
            sm_sevs = {'major': 0, 'medium': 0, 'minor': 0}
            for s in smells:
                d   = s.to_dict()
                sev = d['severity'].lower()
                if 'major' in sev:     sm_sevs['major']  += 1
                elif 'medium' in sev:  sm_sevs['medium'] += 1
                else:                  sm_sevs['minor']  += 1
            summary['sections']['smells'] = {
                'total':    len(smells),
                'critical': sm_sevs['major'],
                'high':     sm_sevs['medium'],
                'medium':   sm_sevs['minor'],
                'low':      0,
                'label':    'Code Smells',
                'route':    '/code-smells',
                'color':    '#a855f7',
            }
        except Exception:
            summary['sections']['smells'] = _empty_section('Code Smells', '/code-smells', '#a855f7')

        # ── Threats ───────────────────────────────────────────────────────
        try:
            from api.threats import _build_kill_chains, _build_metrics as _t_metrics
            sec_data = summary['sections']['security']
            # reuse bug data already fetched above
            from core.security_detector_legacy import SecurityBugDetector
            det2   = SecurityBugDetector()
            bugs2, _ = det2.scan_files(str(repo_path)) if repo_path else ([], None)
            issues_data = [b.to_dict() for b in (bugs2 or [])]
            chains = _build_kill_chains(issues_data)
            tm = _t_metrics(issues_data, chains)
            summary['sections']['threats'] = {
                'total':    len(chains),
                'critical': tm.get('critical_chains', 0),
                'high':     0,
                'medium':   0,
                'low':      0,
                'blast_radius': tm.get('blast_radius_pct', 0),
                'label':    'Attack Chains',
                'route':    '/threats',
                'color':    '#dc2626',
            }
        except Exception:
            summary['sections']['threats'] = _empty_section('Attack Chains', '/threats', '#dc2626')

        # ── Overall risk score (0-100) ─────────────────────────────────────
        total_critical = sum(
            s.get('critical', 0) for s in summary['sections'].values()
        )
        total_high = sum(
            s.get('high', 0) for s in summary['sections'].values()
        )
        total_issues = sum(
            s.get('total', 0) for s in summary['sections'].values()
        )
        risk = min(100, total_critical * 8 + total_high * 3 + max(0, total_issues - 10))
        summary['risk_score']   = risk
        summary['risk_label']   = 'Critical' if risk >= 70 else 'High' if risk >= 40 else 'Medium' if risk >= 15 else 'Low'
        summary['total_issues'] = total_issues

        return format_success_response(summary, 'Dashboard summary ready')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


def _empty_section(label: str, route: str, color: str) -> dict:
    return {
        'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0,
        'label': label, 'route': route, 'color': color,
    }


@dashboard_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """Return list of all persisted scan sessions."""
    try:
        from core.session_store import list_sessions
        from api.chat import repo_chats
        sessions = list_sessions()
        # Mark which ones are currently live in memory
        for s in sessions:
            s['live'] = s['session_id'] in repo_chats
        return format_success_response({'sessions': sessions}, 'Sessions fetched')[0], 200
    except Exception as e:
        return format_error_response(str(e))[0], 500
