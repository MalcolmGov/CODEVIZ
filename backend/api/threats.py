"""
Threat Actor Simulation API

Consumes security scan results from a session and chains vulnerabilities
into realistic MITRE ATT&CK-aligned kill chains with impact heat map data.
"""

import os
from flask import request
from . import threats_bp
from utils import format_success_response, format_error_response, get_repo_path, get_session_context

# ── MITRE ATT&CK stage definitions ────────────────────────────────────────
STAGES = [
    'Reconnaissance',
    'Initial Access',
    'Execution',
    'Persistence',
    'Privilege Escalation',
    'Defense Evasion',
    'Credential Access',
    'Lateral Movement',
    'Exfiltration',
]

# Bug-type → most likely ATT&CK stages it enables
BUG_STAGE_MAP = {
    'SQL Injection':                  ['Initial Access', 'Credential Access', 'Exfiltration'],
    'Cross-Site Scripting (XSS)':     ['Initial Access', 'Credential Access'],
    'Authentication Flaw':            ['Initial Access', 'Privilege Escalation', 'Lateral Movement'],
    'Hardcoded Secret':               ['Initial Access', 'Credential Access', 'Privilege Escalation'],
    'Command Injection':              ['Execution', 'Privilege Escalation', 'Lateral Movement'],
    'Path Traversal':                 ['Initial Access', 'Credential Access', 'Exfiltration'],
    'Insecure Deserialization':       ['Execution', 'Privilege Escalation'],
    'Weak Cryptography':              ['Credential Access', 'Defense Evasion'],
    'SSRF':                           ['Initial Access', 'Lateral Movement', 'Exfiltration'],
    'Open Redirect':                  ['Initial Access', 'Defense Evasion'],
    'Insecure Direct Object Reference': ['Credential Access', 'Exfiltration'],
    'Security Misconfiguration':      ['Initial Access', 'Defense Evasion', 'Persistence'],
    'Sensitive Data Exposure':        ['Exfiltration'],
    'N+1 Query Problem':              ['Exfiltration'],   # data-heavy endpoint → dump vector
    'Memory Leak':                    ['Defense Evasion'],
}

# Severity → numeric risk weight
SEV_WEIGHT = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}

# Stage → MITRE tactic ID (for display)
STAGE_TACTIC = {
    'Reconnaissance':     'TA0043',
    'Initial Access':     'TA0001',
    'Execution':          'TA0002',
    'Persistence':        'TA0003',
    'Privilege Escalation': 'TA0004',
    'Defense Evasion':    'TA0005',
    'Credential Access':  'TA0006',
    'Lateral Movement':   'TA0008',
    'Exfiltration':       'TA0010',
}

# Business impact labels per stage
STAGE_IMPACT = {
    'Reconnaissance':     'Attacker maps attack surface',
    'Initial Access':     'Attacker enters the system',
    'Execution':          'Malicious code runs on host',
    'Persistence':        'Attacker maintains foothold',
    'Privilege Escalation': 'Attacker gains admin rights',
    'Defense Evasion':    'Attacker hides activity',
    'Credential Access':  'Credentials / secrets stolen',
    'Lateral Movement':   'Attacker spreads to other systems',
    'Exfiltration':       'Data leaves the organisation',
}


def _norm_severity(s: str) -> str:
    s = s.lower()
    for level in ('critical', 'high', 'medium', 'low'):
        if level in s:
            return level
    return 'low'


def _norm_type(t: str) -> str:
    """Strip emoji prefix from bug type."""
    return t.strip().lstrip('🔴🟠🟡🟢 ')


def _build_kill_chains(issues: list) -> list:
    """
    Group issues by file, then for each file build the longest
    contiguous attack chain that spans at least 3 MITRE stages.
    Returns a list of chain dicts sorted by risk score descending.
    """
    from collections import defaultdict

    # Map issues to stages
    enriched = []
    for iss in issues:
        raw_type = _norm_type(iss.get('type', ''))
        stages   = BUG_STAGE_MAP.get(raw_type, [])
        sev      = _norm_severity(iss.get('severity', 'low'))
        enriched.append({**iss, 'norm_type': raw_type, 'stages': stages, 'norm_sev': sev})

    # Group by file
    by_file: dict = defaultdict(list)
    for e in enriched:
        if e['stages']:
            by_file[e.get('file', 'unknown')].append(e)

    chains = []
    for file_path, file_issues in by_file.items():
        # Collect all stages this file enables (ordered)
        covered = {}   # stage → [issues]
        for iss in file_issues:
            for st in iss['stages']:
                covered.setdefault(st, []).append(iss)

        if len(covered) < 2:
            continue   # need ≥2 stages to be interesting

        ordered_stages = [s for s in STAGES if s in covered]
        risk_score = sum(
            SEV_WEIGHT.get(i['norm_sev'], 1)
            for iss_list in covered.values()
            for i in iss_list
        )

        steps = []
        for st in ordered_stages:
            rep_issue = sorted(covered[st], key=lambda x: SEV_WEIGHT.get(x['norm_sev'], 0), reverse=True)[0]
            steps.append({
                'stage':    st,
                'tactic':   STAGE_TACTIC.get(st, ''),
                'impact':   STAGE_IMPACT.get(st, ''),
                'issue_type': rep_issue['norm_type'],
                'severity': rep_issue['norm_sev'],
                'file':     rep_issue.get('file', ''),
                'line':     rep_issue.get('line', 0),
                'description': rep_issue.get('description', ''),
            })

        highest_sev = max(
            (SEV_WEIGHT.get(i['norm_sev'], 0) for iss_list in covered.values() for i in iss_list),
            default=0
        )
        sev_label = {4: 'critical', 3: 'high', 2: 'medium', 1: 'low'}.get(highest_sev, 'low')

        chains.append({
            'chain_id':     f"chain-{len(chains)+1}",
            'file':         file_path,
            'stages':       ordered_stages,
            'steps':        steps,
            'risk_score':   risk_score,
            'severity':     sev_label,
            'stage_count':  len(ordered_stages),
            'issue_count':  len(file_issues),
        })

    chains.sort(key=lambda c: c['risk_score'], reverse=True)
    return chains[:10]   # top 10


def _build_heat_map(issues: list) -> list:
    """
    Return stage × severity counts for the heat-map grid.
    Each cell: { stage, severity, count, issues[] }
    """
    from collections import defaultdict

    grid: dict = defaultdict(lambda: defaultdict(list))

    for iss in issues:
        raw_type = _norm_type(iss.get('type', ''))
        stages   = BUG_STAGE_MAP.get(raw_type, [])
        sev      = _norm_severity(iss.get('severity', 'low'))
        for st in stages:
            grid[st][sev].append({
                'type': raw_type,
                'file': iss.get('file', ''),
                'line': iss.get('line', 0),
            })

    cells = []
    for stage in STAGES:
        for sev in ('critical', 'high', 'medium', 'low'):
            iss_list = grid[stage][sev]
            cells.append({
                'stage':    stage,
                'severity': sev,
                'count':    len(iss_list),
                'issues':   iss_list[:5],   # preview up to 5
            })

    return cells


def _build_metrics(issues: list, chains: list) -> dict:
    from collections import Counter

    sevs = [_norm_severity(i.get('severity', 'low')) for i in issues]
    sev_counts = Counter(sevs)

    # Which stages are covered by current vulns?
    covered_stages = set()
    for iss in issues:
        raw_type = _norm_type(iss.get('type', ''))
        covered_stages.update(BUG_STAGE_MAP.get(raw_type, []))

    blast_radius = round(len(covered_stages) / len(STAGES) * 100)

    return {
        'total_chains':      len(chains),
        'critical_chains':   sum(1 for c in chains if c['severity'] == 'critical'),
        'stages_exposed':    len(covered_stages),
        'blast_radius_pct':  blast_radius,
        'by_severity':       dict(sev_counts),
        'stage_coverage':    sorted(covered_stages),
    }


@threats_bp.route('/simulate/<session_id>', methods=['POST'])
def simulate_threats(session_id):
    """
    Build kill chains and heat map from the session's security scan results.
    Re-runs the security scanner if needed, then simulates attacker paths.
    """
    try:
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        chat      = repo_chats[session_id]
        context   = get_session_context(chat)
        repo_path = get_repo_path(chat)

        # 1. Check session context (populated by security scan endpoint)
        security_issues = context.get('security_issues', [])

        # 2. Check DB cache (survives backend restart)
        if not security_issues:
            try:
                from core.session_store import get_cached
                security_issues = get_cached(session_id, 'security') or []
            except Exception:
                pass

        # 3. Accept bugs passed directly from frontend in request body
        if not security_issues:
            body = request.get_json(silent=True) or {}
            security_issues = body.get('bugs', [])

        # 4. Last resort — walk all file types (not just *.py)
        if not security_issues and repo_path:
            try:
                from core.security_detector_legacy import SecurityBugDetector
                detector = SecurityBugDetector()
                bugs = []
                for root, dirs, files in os.walk(repo_path):
                    dirs[:] = [d for d in dirs if d not in
                                ('.git', 'node_modules', '__pycache__', 'dist', 'build', 'venv')]
                    for file in files:
                        if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                            fp = os.path.join(root, file)
                            try:
                                with open(fp, 'r', errors='ignore') as f:
                                    code = f.read()
                                rel = os.path.relpath(fp, repo_path)
                                bugs.extend(detector.scan_code(code, rel))
                            except Exception:
                                pass
                security_issues = [b.to_dict() if hasattr(b, 'to_dict') else b for b in bugs]
                # Store for next time
                if security_issues:
                    context['security_issues'] = security_issues
                    try:
                        from core.session_store import cache_result
                        cache_result(session_id, 'security', security_issues)
                    except Exception:
                        pass
            except Exception:
                pass

        if not security_issues:
            return format_success_response({
                'session_id':  session_id,
                'chains':      [],
                'heat_map':    _build_heat_map([]),
                'metrics':     _build_metrics([], []),
                'no_issues':   True,
            }, 'No security issues found — no attack chains to simulate')[0], 200

        chains   = _build_kill_chains(security_issues)
        heat_map = _build_heat_map(security_issues)
        metrics  = _build_metrics(security_issues, chains)

        return format_success_response({
            'session_id': session_id,
            'chains':     chains,
            'heat_map':   heat_map,
            'metrics':    metrics,
            'total_issues': len(security_issues),
        }, f'Threat simulation complete — {len(chains)} attack chains identified')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
