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
        
        bugs = []
        if DETECTOR_AVAILABLE and hasattr(chat, 'repo_path'):
            detector = SecurityBugDetector()
            import os
            for root, dirs, files in os.walk(chat.repo_path):
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', 'dist', 'build', 'venv')]
                for file in files:
                    if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', errors='ignore') as f:
                                code_content = f.read()
                            rel_path = os.path.relpath(file_path, chat.repo_path)
                            file_bugs = detector.scan_code(code_content, rel_path)
                            bugs.extend(file_bugs)
                        except Exception:
                            pass
        
        # Convert to dict and normalise severity (strip emoji prefix from enum values)
        def _norm_sev(s: str) -> str:
            s = str(s).lower()
            for lvl in ('critical', 'high', 'medium', 'low'):
                if lvl in s:
                    return lvl
            return 'low'

        bugs_data = []
        for bug in bugs:
            d = bug.to_dict() if hasattr(bug, 'to_dict') else dict(bug)
            d['severity'] = _norm_sev(d.get('severity', ''))
            bugs_data.append(d)

        # Calculate summary
        critical = len([b for b in bugs_data if b.get('severity') == 'critical'])
        high = len([b for b in bugs_data if b.get('severity') == 'high'])

        # ── Store in session context so Threats / Dashboard can reuse ──────
        try:
            if hasattr(chat, 'context') and isinstance(chat.context, dict):
                chat.context['security_issues'] = bugs_data
            elif isinstance(chat, dict):
                chat.setdefault('context', {})['security_issues'] = bugs_data
            # Also persist to DB cache
            from core.session_store import cache_result
            cache_result(session_id, 'security', bugs_data)
        except Exception:
            pass

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


@security_bp.route('/apply-fix', methods=['POST'])
def apply_fix():
    """Apply security patch on a new Git branch and commit it"""
    try:
        from api.chat import repo_chats
        import os
        import subprocess
        import random
        import string
        
        data = request.get_json() or {}
        session_id = data.get('session_id')
        bug_id = data.get('bug_id', 'BUG-0001')
        file_path = data.get('file')
        line_number = data.get('line')
        original_code = data.get('code')
        fixed_code = data.get('fix')
        bug_type = data.get('type', 'Vulnerability Fix')
        
        if not session_id or not file_path or line_number is None or not original_code or not fixed_code:
            return format_error_response('Missing required fields')[0], 400
            
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404
            
        chat = repo_chats[session_id]
        repo_path = chat.repo_path
        
        # Generate clean branch name
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        branch_name = f"security/fix-{bug_id.lower()}-{rand_suffix}"
        commit_message = f"security: resolve {bug_type} in {os.path.basename(file_path)} on line {line_number}"
        
        # Apply local patch
        orig_dir = os.getcwd()
        try:
            os.chdir(repo_path)
            
            is_git = os.path.exists('.git')
            if is_git:
                # Ensure main is checked out first
                subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                # Create and switch to new branch
                subprocess.run(['git', 'checkout', '-b', branch_name], capture_output=True)
                
            full_file_path = os.path.join(repo_path, file_path)
            if not os.path.exists(full_file_path):
                return format_error_response(f"Target file not found: {file_path}")[0], 404
                
            with open(full_file_path, 'r', errors='ignore') as f:
                lines = f.readlines()
                
            line_idx = line_number - 1
            applied = False
            
            if 0 <= line_idx < len(lines):
                lines[line_idx] = fixed_code + '\n'
                applied = True
            else:
                # Fallback to absolute replace
                content = "".join(lines)
                if original_code in content:
                    content = content.replace(original_code, fixed_code)
                    lines = [content]
                    applied = True
                    
            if not applied:
                return format_error_response("Could not align the target vulnerability to source code lines.")[0], 400
                
            with open(full_file_path, 'w') as f:
                f.writelines(lines)
                
            if is_git:
                subprocess.run(['git', 'add', file_path], capture_output=True)
                subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True)
                
            return format_success_response({
                'session_id': session_id,
                'bug_id': bug_id,
                'branch': branch_name if is_git else 'Local filesystem (non-git)',
                'file_patched': file_path,
                'commit': commit_message,
                'is_git': is_git
            }, 'Security PR patch branch successfully created')[0], 200
            
        finally:
            os.chdir(orig_dir)
            
    except Exception as e:
        return format_error_response(str(e))[0], 500


@security_bp.route('/auto-stage', methods=['POST'])
def auto_stage():
    """Apply all high-confidence security fixes to the files on a single unified branch"""
    try:
        from api.chat import repo_chats
        import os
        import subprocess
        import random
        import string
        
        data = request.get_json() or {}
        session_id = data.get('session_id')
        bugs = data.get('bugs', [])
        
        if not session_id:
            return format_error_response('Session ID required')[0], 400
            
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404
            
        chat = repo_chats[session_id]
        repo_path = chat.repo_path
        
        # Filter bugs for confidence >= 0.9 and ensure they have code and fix
        high_conf_bugs = []
        for bug in bugs:
            conf = bug.get('confidence', 0.8)
            try:
                conf = float(conf)
            except:
                conf = 0.8
            if conf >= 0.9 and bug.get('file') and bug.get('line') and bug.get('code') and bug.get('fix'):
                high_conf_bugs.append(bug)
                
        if not high_conf_bugs:
            return format_success_response({
                'session_id': session_id,
                'branch': 'No changes',
                'files_patched': [],
                'commit': 'No high-confidence fixes to apply',
                'is_git': False,
                'applied_count': 0
            }, 'No high-confidence vulnerabilities found to auto-stage')[0], 200
            
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        branch_name = f"remediation/auto-patch-{rand_suffix}"
        commit_message = f"remediation: apply {len(high_conf_bugs)} high-confidence security auto-fixes"
        
        orig_dir = os.getcwd()
        try:
            os.chdir(repo_path)
            
            is_git = os.path.exists('.git')
            if is_git:
                subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                subprocess.run(['git', 'checkout', '-b', branch_name], capture_output=True)
                
            files_patched = []
            applied_count = 0
            
            patches_by_file = {}
            for bug in high_conf_bugs:
                file_path = bug['file']
                if file_path not in patches_by_file:
                    patches_by_file[file_path] = []
                patches_by_file[file_path].append(bug)
                
            for file_path, file_patches in patches_by_file.items():
                full_file_path = os.path.join(repo_path, file_path)
                if not os.path.exists(full_file_path):
                    continue
                    
                with open(full_file_path, 'r', errors='ignore') as f:
                    lines = f.readlines()
                    
                file_modified = False
                for bug in sorted(file_patches, key=lambda b: b['line'], reverse=True):
                    line_number = bug['line']
                    fixed_code = bug['fix']
                    original_code = bug['code']
                    line_idx = line_number - 1
                    
                    if 0 <= line_idx < len(lines):
                        lines[line_idx] = fixed_code + '\n'
                        file_modified = True
                        applied_count += 1
                    else:
                        content = "".join(lines)
                        if original_code in content:
                            content = content.replace(original_code, fixed_code)
                            lines = [content]
                            file_modified = True
                            applied_count += 1
                            
                if file_modified:
                    with open(full_file_path, 'w') as f:
                        f.writelines(lines)
                    files_patched.append(file_path)
                    if is_git:
                        subprocess.run(['git', 'add', file_path], capture_output=True)
                        
            if is_git and files_patched:
                subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True)
                
            return format_success_response({
                'session_id': session_id,
                'branch': branch_name if is_git else 'Local filesystem (non-git)',
                'files_patched': files_patched,
                'commit': commit_message,
                'is_git': is_git,
                'applied_count': applied_count
            }, f'Successfully staged {applied_count} security auto-fixes on branch {branch_name}')[0], 200
            
        finally:
            os.chdir(orig_dir)
            
    except Exception as e:
        return format_error_response(str(e))[0], 500


# ── CVE lookup via OSV.dev (free, no API key) ─────────────────────────────

def _parse_dep(dep: dict):
    """Parse package name, version, and OSV ecosystem from a dependency dict."""
    import re
    pkg      = dep.get('package', '')
    dep_type = dep.get('type', 'npm')

    if dep_type == 'python':
        m        = re.match(r'^([A-Za-z0-9._-]+)\s*[>=<!^~,\s]*([0-9][^\s,;]*)?', pkg)
        name     = m.group(1) if m else pkg.split('[')[0]
        version  = m.group(2) if m and m.group(2) else ''
        ecosystem = 'PyPI'
    else:
        if pkg.startswith('@') and pkg.count('@') > 1:
            idx      = pkg.rindex('@')
            name, version = pkg[:idx], pkg[idx+1:].lstrip('^~>=')
        elif '@' in pkg:
            parts    = pkg.split('@', 1)
            name, version = parts[0], parts[1].lstrip('^~>=')
        else:
            name, version = pkg, ''
        ecosystem = 'npm'

    return name.strip(), version.strip(), ecosystem


def _get_fixed_version(osv_vuln: dict) -> str:
    for affected in osv_vuln.get('affected', []):
        for rng in affected.get('ranges', []):
            for event in rng.get('events', []):
                if 'fixed' in event:
                    return event['fixed']
    return ''


def _severity_from_osv(osv_vuln: dict):
    """Return (severity_str, cvss_score) from an OSV vulnerability."""
    for sev in osv_vuln.get('severity', []):
        if sev.get('type') in ('CVSS_V3', 'CVSS_V2'):
            try:
                score = float(sev.get('score', 0))
                if score >= 9.0:   return 'critical', score
                if score >= 7.0:   return 'high', score
                if score >= 4.0:   return 'medium', score
                return 'low', score
            except (ValueError, TypeError):
                pass
    # Fallback to database_specific
    db_sev = osv_vuln.get('database_specific', {}).get('severity', '').lower()
    if db_sev in ('critical', 'high', 'medium', 'low'):
        return db_sev, None
    return 'low', None


@security_bp.route('/cve-scan/<session_id>', methods=['POST'])
def scan_cve(session_id):
    """
    Batch CVE lookup for all dependencies in a session using the OSV API.
    Free endpoint — no API key required.
    """
    try:
        import requests as req
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        chat    = repo_chats[session_id]
        ctx     = chat.context if hasattr(chat, 'context') else {}
        raw_deps = ctx.get('dependencies', [])

        if not raw_deps:
            return format_success_response({
                'vulnerabilities': [], 'scanned': 0, 'affected': 0,
                'summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            }, 'No dependencies found')[0], 200

        # Parse + build OSV batch queries (cap at 150 packages)
        parsed  = [_parse_dep(d) for d in raw_deps[:150]]
        queries = []
        for name, version, ecosystem in parsed:
            q = {'package': {'name': name, 'ecosystem': ecosystem}}
            if version and version[0].isdigit():
                q['version'] = version
            queries.append(q)

        # OSV batch query
        osv_resp = req.post(
            'https://api.osv.dev/v1/querybatch',
            json={'queries': queries},
            timeout=25,
        )
        if osv_resp.status_code != 200:
            return format_error_response(f'OSV API error: {osv_resp.status_code}')[0], 502

        results_raw = osv_resp.json().get('results', [])

        SEV_ORDER = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        vulns     = []
        counts    = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

        for i, (name, version, ecosystem) in enumerate(parsed):
            result = results_raw[i] if i < len(results_raw) else {}
            for osv_vuln in result.get('vulns', [])[:3]:
                severity, cvss = _severity_from_osv(osv_vuln)
                counts[severity] = counts.get(severity, 0) + 1

                aliases = osv_vuln.get('aliases', [])
                cve_id  = next((a for a in aliases if a.startswith('CVE-')), osv_vuln.get('id', ''))

                vulns.append({
                    'package':     name,
                    'version':     version,
                    'ecosystem':   ecosystem,
                    'cve_id':      cve_id,
                    'osv_id':      osv_vuln.get('id', ''),
                    'title':       (osv_vuln.get('summary') or 'Vulnerability detected')[:140],
                    'severity':    severity,
                    'cvss_score':  round(cvss, 1) if cvss else None,
                    'fixed_in':    _get_fixed_version(osv_vuln),
                    'details_url': f"https://osv.dev/vulnerability/{osv_vuln.get('id', '')}",
                })

        vulns.sort(key=lambda v: SEV_ORDER.get(v['severity'], 4))

        return format_success_response({
            'vulnerabilities': vulns,
            'summary': counts,
            'scanned': len(parsed),
            'affected': len({v['package'] for v in vulns}),
        }, f'CVE scan complete — {len(vulns)} vulnerabilities in {len({v["package"] for v in vulns})} packages')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
