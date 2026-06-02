"""
Repositories API Blueprint

Handles repository management, scanning, and analysis.
"""

from flask import request
from . import repositories_bp
from utils import format_success_response, format_error_response
import uuid


# In-memory storage (will use database in Phase B)
repositories_db = {}


@repositories_bp.route('', methods=['GET'])
def list_repositories():
    """Get all monitored repositories"""
    try:
        repos = list(repositories_db.values())
        
        return format_success_response({
            'repositories': repos,
            'count': len(repos)
        }, f'Found {len(repos)} repositories')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@repositories_bp.route('', methods=['POST'])
def add_repository():
    """Add a new repository to monitor"""
    try:
        data = request.get_json() or {}
        repo_name = data.get('name', '')
        repo_url = data.get('url', '')
        branch = data.get('branch', 'main')
        
        if not repo_name or not repo_url:
            return format_error_response('Name and URL required')[0], 400
        
        repo_id = str(uuid.uuid4())
        repository = {
            'id': repo_id,
            'name': repo_name,
            'url': repo_url,
            'branch': branch,
            'last_scan': None,
            'status': 'active',
            'created_at': '2026-06-01T00:00:00'
        }
        
        repositories_db[repo_id] = repository
        
        return format_success_response(repository, 'Repository added')[0], 201
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@repositories_bp.route('/<repo_id>', methods=['GET'])
def get_repository(repo_id):
    """Get specific repository details"""
    try:
        if repo_id not in repositories_db:
            return format_error_response('Repository not found')[0], 404
        
        return format_success_response(
            repositories_db[repo_id]
        )[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@repositories_bp.route('/<repo_id>', methods=['PUT'])
def update_repository(repo_id):
    """Update repository configuration"""
    try:
        if repo_id not in repositories_db:
            return format_error_response('Repository not found')[0], 404
        
        data = request.get_json() or {}
        repo = repositories_db[repo_id]
        
        # Update fields
        for key in ['name', 'url', 'branch']:
            if key in data:
                repo[key] = data[key]
        
        return format_success_response(repo, 'Repository updated')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@repositories_bp.route('/<repo_id>', methods=['DELETE'])
def delete_repository(repo_id):
    """Delete a repository"""
    try:
        if repo_id not in repositories_db:
            return format_error_response('Repository not found')[0], 404
        
        del repositories_db[repo_id]
        
        return format_success_response(None, 'Repository deleted')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@repositories_bp.route('/<repo_id>/scan', methods=['POST'])
def scan_repository(repo_id):
    """Trigger scan for repository"""
    try:
        if repo_id not in repositories_db:
            return format_error_response('Repository not found')[0], 404
        
        repo = repositories_db[repo_id]
        repo['last_scan'] = '2026-06-01T00:00:00'
        repo['status'] = 'scanning'
        
        return format_success_response({
            'repository': repo,
            'scan_id': str(uuid.uuid4())
        }, 'Scan initiated')[0], 202
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@repositories_bp.route('/<repo_id>/scans', methods=['GET'])
def get_scan_history(repo_id):
    """Get scan history for repository"""
    try:
        if repo_id not in repositories_db:
            return format_error_response('Repository not found')[0], 404
        
        # Mock scan history
        scans = [
            {
                'id': str(uuid.uuid4()),
                'timestamp': '2026-06-01T00:00:00',
                'total_issues': 5,
                'critical': 1,
                'high': 2,
                'medium': 2,
                'low': 0
            }
        ]
        
        return format_success_response({
            'repository_id': repo_id,
            'scans': scans,
            'count': len(scans)
        })[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


def _get_db_path():
    """Return path to the SQLite DB used for repo caching."""
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'instance', 'codeviz.db')


def _load_cached_repos() -> list:
    """Load previously-fetched repos from SQLite (table: cached_repos)."""
    import sqlite3, json
    try:
        conn = sqlite3.connect(_get_db_path())
        cur = conn.execute(
            "SELECT data FROM cached_repos ORDER BY fetched_at DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
        return json.loads(row[0]) if row else []
    except Exception:
        return []


def _save_cached_repos(repos: list) -> None:
    """Persist repos to SQLite so they survive backend restarts."""
    import sqlite3, json
    try:
        conn = sqlite3.connect(_get_db_path())
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cached_repos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                data       TEXT    NOT NULL,
                fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("DELETE FROM cached_repos")          # keep only latest
        conn.execute("INSERT INTO cached_repos (data) VALUES (?)", (json.dumps(repos),))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[repos] Cache write failed: {e}")


_DEFAULT_REPOS = [
    {
        'id': '101', 'name': 'CODEVIZ',
        'full_name': 'MalcolmGov/CODEVIZ',
        'url': 'https://github.com/MalcolmGov/CODEVIZ',
        'clone_url': 'https://github.com/MalcolmGov/CODEVIZ.git',
        'description': 'AI-Powered Code Analysis & Refactoring Platform',
        'private': False, 'branch': 'main',
        'local_path': '/Users/malcolmgovender/codeviz-proper',
    },
    {
        'id': '102', 'name': 'coastal-clean',
        'full_name': 'MalcolmGov/coastal-clean',
        'url': 'https://github.com/MalcolmGov/coastal-clean',
        'clone_url': 'https://github.com/MalcolmGov/coastal-clean.git',
        'description': 'Coastal environmental data monitor dashboard',
        'private': True, 'branch': 'main',
    },
    {
        'id': '103', 'name': 'SwifterWallet',
        'full_name': 'MalcolmGov/SwifterWallet',
        'url': 'https://github.com/MalcolmGov/SwifterWallet',
        'clone_url': 'https://github.com/MalcolmGov/SwifterWallet.git',
        'description': 'iOS Swift finance wallet application',
        'private': False, 'branch': 'main',
    },
    {
        'id': '104', 'name': 'intelligencehub',
        'full_name': 'MalcolmGov/intelligencehub',
        'url': 'https://github.com/MalcolmGov/intelligencehub',
        'clone_url': 'https://github.com/MalcolmGov/intelligencehub.git',
        'description': 'AI models hosting aggregator',
        'private': True, 'branch': 'main',
    },
]


@repositories_bp.route('/github', methods=['GET'])
def list_github_repositories():
    """
    List GitHub repos for the authenticated user.
    Priority: GitHub API → SQLite cache → hardcoded defaults.
    Always returns something — never a blank list.
    """
    try:
        import requests as req

        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            from flask import session
            token = session.get('github_token')

        repos = []

        # 1️⃣ Try GitHub API with a real token
        if token and not token.startswith('mock_'):
            try:
                resp = req.get(
                    'https://api.github.com/user/repos?per_page=100&sort=updated',
                    headers={
                        'Authorization': f'token {token}',
                        'Accept': 'application/vnd.github.v3+json',
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    for r in resp.json():
                        repos.append({
                            'id':          str(r['id']),
                            'name':        r['name'],
                            'full_name':   r['full_name'],
                            'url':         r['html_url'],
                            'clone_url':   r['clone_url'],
                            'description': r.get('description'),
                            'private':     r['private'],
                            'branch':      r.get('default_branch', 'main'),
                        })
                    if repos:
                        _save_cached_repos(repos)   # ✅ persist for next time
                        print(f"[repos] Fetched {len(repos)} repos from GitHub API")
            except Exception as api_err:
                print(f"[repos] GitHub API error: {api_err}")

        # 2️⃣ Fall back to SQLite cache
        if not repos:
            repos = _load_cached_repos()
            if repos:
                print(f"[repos] Serving {len(repos)} repos from SQLite cache")

        # 3️⃣ Last resort: hardcoded defaults
        if not repos:
            repos = _DEFAULT_REPOS
            print("[repos] Serving hardcoded default repos")

        return format_success_response({
            'repositories': repos,
            'count': len(repos),
        })[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
