"""
API Analyzer — surfaces discovered endpoints from the scanner context
and optionally probes them for health/response time.
"""

import os
import time
import requests as req
from flask import request
from . import apis_bp
from utils import format_success_response, format_error_response, get_repo_path, get_session_context


def _probe_endpoint(base_url: str, path: str, method: str = 'GET', timeout: int = 5) -> dict:
    """Fire a single HTTP request and return timing + status."""
    url = base_url.rstrip('/') + '/' + path.lstrip('/')
    try:
        start = time.time()
        resp = req.request(method, url, timeout=timeout, allow_redirects=True)
        elapsed = round((time.time() - start) * 1000)
        return {
            'status':  resp.status_code,
            'latency': elapsed,
            'ok':      resp.status_code < 400,
            'error':   None,
        }
    except req.exceptions.ConnectionError:
        return {'status': None, 'latency': None, 'ok': False, 'error': 'Connection refused'}
    except req.exceptions.Timeout:
        return {'status': None, 'latency': timeout * 1000, 'ok': False, 'error': 'Timeout'}
    except Exception as e:
        return {'status': None, 'latency': None, 'ok': False, 'error': str(e)[:80]}


@apis_bp.route('/endpoints/<session_id>', methods=['GET'])
def list_endpoints(session_id):
    """Return discovered API endpoints from the scanner context."""
    try:
        from api.chat import repo_chats
        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        chat    = repo_chats[session_id]
        context = get_session_context(chat)
        apis    = context.get('apis', [])

        return format_success_response({
            'session_id': session_id,
            'endpoints':  apis,
            'total':      len(apis),
        }, f'{len(apis)} endpoints discovered')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


@apis_bp.route('/probe/<session_id>', methods=['POST'])
def probe_endpoints(session_id):
    """
    Probe discovered endpoints.
    Body: { "base_url": "http://localhost:8000", "timeout": 5 }
    """
    try:
        from api.chat import repo_chats
        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        chat    = repo_chats[session_id]
        context = get_session_context(chat)
        apis    = context.get('apis', [])

        body     = request.get_json() or {}
        base_url = body.get('base_url', context.get('production_base_url', 'http://localhost:8000'))
        timeout  = min(int(body.get('timeout', 5)), 15)

        results = []
        for ep in apis[:30]:   # cap at 30 probes per call
            path   = ep.get('path', '/')
            method = ep.get('method', 'GET')
            probe  = _probe_endpoint(base_url, path, method, timeout)
            results.append({**ep, **probe})

        ok_count   = sum(1 for r in results if r.get('ok'))
        fail_count = len(results) - ok_count
        avg_latency = (
            round(sum(r['latency'] for r in results if r.get('latency')) / max(ok_count, 1))
            if ok_count else None
        )

        return format_success_response({
            'session_id':  session_id,
            'base_url':    base_url,
            'results':     results,
            'summary': {
                'total':       len(results),
                'ok':          ok_count,
                'failed':      fail_count,
                'avg_latency': avg_latency,
            },
        }, f'Probed {len(results)} endpoints')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


@apis_bp.route('/graph/<session_id>', methods=['GET'])
def dependency_graph(session_id):
    """
    Build a file-level dependency graph from scanner context.
    Returns nodes (files) and edges (import relationships) for D3.
    """
    try:
        from api.chat import repo_chats
        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404

        chat      = repo_chats[session_id]
        context   = get_session_context(chat)
        repo_path = get_repo_path(chat)

        # Build graph by walking import statements
        nodes = []
        edges = []
        node_ids: dict = {}

        def get_node_id(path: str) -> int:
            if path not in node_ids:
                node_ids[path] = len(node_ids)
            return node_ids[path]

        if repo_path:
            import re
            from pathlib import Path

            # Patterns for different import styles
            PY_IMPORT  = re.compile(r'^\s*(?:from|import)\s+([\w.]+)', re.M)
            TS_IMPORT  = re.compile(r'''from\s+['"]([^'"]+)['"]''', re.M)
            JS_REQUIRE = re.compile(r'''require\s*\(\s*['"]([^'"]+)['"]\s*\)''', re.M)

            path_obj = Path(repo_path)
            scan_exts = ('.py', '.ts', '.tsx', '.js', '.jsx')

            for file_path in path_obj.rglob('*'):
                if not file_path.is_file():
                    continue
                if file_path.suffix not in scan_exts:
                    continue
                # Skip build/node folders
                parts = file_path.parts
                if any(p in parts for p in ('node_modules', '__pycache__', '.git', 'dist', 'build', 'venv')):
                    continue

                rel = str(file_path.relative_to(path_obj))
                fid = get_node_id(rel)

                # Determine file type for colouring
                if file_path.suffix == '.py':
                    ftype = 'python'
                elif file_path.suffix in ('.ts', '.tsx'):
                    ftype = 'typescript'
                else:
                    ftype = 'javascript'

                nodes.append({
                    'id':   fid,
                    'name': file_path.name,
                    'path': rel,
                    'type': ftype,
                    'group': ftype,
                })

                try:
                    code = file_path.read_text(errors='ignore')
                except Exception:
                    continue

                # Extract imports and resolve relative paths
                imports = set()
                if file_path.suffix == '.py':
                    for m in PY_IMPORT.finditer(code):
                        imp = m.group(1).replace('.', '/')
                        imports.add(imp)
                else:
                    for pattern in (TS_IMPORT, JS_REQUIRE):
                        for m in pattern.finditer(code):
                            imp = m.group(1)
                            if imp.startswith('.'):
                                imports.add(imp)

                # Resolve relative imports to file paths
                for imp in imports:
                    if imp.startswith('.'):
                        resolved = str((file_path.parent / imp).resolve().relative_to(path_obj.resolve()))
                        # Try with common extensions
                        for ext in scan_exts + ('',):
                            candidate = resolved + ext
                            if (path_obj / candidate).exists():
                                tid = get_node_id(candidate)
                                edges.append({'source': fid, 'target': tid})
                                break

        # Cap for performance
        nodes = nodes[:200]
        valid_ids = {n['id'] for n in nodes}
        edges = [e for e in edges if e['source'] in valid_ids and e['target'] in valid_ids][:400]

        return format_success_response({
            'session_id': session_id,
            'nodes':      nodes,
            'edges':      edges,
            'stats': {
                'files':   len(nodes),
                'imports': len(edges),
            },
        }, f'Graph built — {len(nodes)} files, {len(edges)} imports')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
