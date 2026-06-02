"""
Code Smell Detection API

Exposes CodeSmellDetector (dead code, duplicates, long methods, deep nesting,
magic numbers, high complexity, unused variables) as a REST endpoint.
"""

from flask import request
from . import smells_bp
from utils import format_success_response, format_error_response

try:
    from core.code_smell_detector_legacy import CodeSmellDetector
    SMELLS_AVAILABLE = True
except ImportError as e:
    SMELLS_AVAILABLE = False
    print(f"⚠️  CodeSmellDetector not available: {e}")


def _norm_severity(s: str) -> str:
    s = s.lower()
    if 'major' in s:  return 'major'
    if 'medium' in s: return 'medium'
    if 'minor' in s:  return 'minor'
    return 'minor'


@smells_bp.route('/scan/<session_id>', methods=['POST'])
def scan_smells(session_id):
    """Detect code smells in the session's repository (Python files)."""
    try:
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        if not SMELLS_AVAILABLE:
            return format_error_response('Code smell detector not available')[0], 503

        chat      = repo_chats[session_id]
        repo_path = getattr(chat, 'repo_path', None)
        if not repo_path:
            return format_error_response('No repository path for this session')[0], 400

        detector = CodeSmellDetector()

        # Scan Python + TypeScript/TSX
        py_smells = detector.scan_files(str(repo_path), '*.py')
        ts_smells = detector.scan_files(str(repo_path), '*.ts')
        tsx_smells = detector.scan_files(str(repo_path), '*.tsx')
        all_smells = py_smells + ts_smells + tsx_smells

        SEV_ORDER = {'major': 0, 'medium': 1, 'minor': 2}

        smells_data = []
        for smell in all_smells[:80]:
            d = smell.to_dict()
            d['severity'] = _norm_severity(d['severity'])
            smells_data.append(d)

        smells_data.sort(key=lambda x: SEV_ORDER.get(x['severity'], 3))

        # Summary
        summary = detector.get_complexity_summary(all_smells)
        by_type = {}
        by_sev  = {'major': 0, 'medium': 0, 'minor': 0}
        for s in smells_data:
            by_type[s['type']] = by_type.get(s['type'], 0) + 1
            by_sev[s['severity']] = by_sev.get(s['severity'], 0) + 1

        metrics = {
            'total':           len(all_smells),
            'major':           by_sev['major'],
            'medium':          by_sev['medium'],
            'minor':           by_sev['minor'],
            'files_affected':  len({s['file'] for s in smells_data}),
            'by_type':         by_type,
            'complexity':      summary,
        }

        return format_success_response({
            'session_id': session_id,
            'smells':     smells_data,
            'metrics':    metrics,
            'total':      len(all_smells),
        }, f'Code smell scan complete — {len(all_smells)} smells found')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
