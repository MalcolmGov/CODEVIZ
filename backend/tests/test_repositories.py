"""
Tests for the /repositories/github endpoint and its 3-tier fallback:
  1. GitHub API  (mocked)
  2. SQLite cache
  3. Hardcoded defaults
"""
import json
import tempfile
import os
import sqlite3
import pytest
from unittest.mock import patch, MagicMock


# ── Helpers ─────────────────────────────────────────────────────────────────

def get_repos(client, headers=None):
    """GET /api/repositories/github and return the parsed list."""
    r = client.get('/api/repositories/github', headers=headers or {})
    assert r.status_code == 200
    data = r.get_json()
    return data['data']['repositories']


# ── Tier 3: hardcoded defaults ───────────────────────────────────────────────

def test_returns_defaults_when_no_token_and_no_cache(client):
    """Without any token or cache the endpoint should still return repos."""
    repos = get_repos(client)   # no auth header → mock_ branch skipped
    assert len(repos) > 0


def test_default_repos_have_required_fields(client):
    repos = get_repos(client)
    for repo in repos:
        assert 'id'        in repo
        assert 'name'      in repo
        assert 'full_name' in repo
        assert 'clone_url' in repo
        assert 'private'   in repo
        assert 'branch'    in repo


def test_mock_token_uses_defaults_not_github_api(client):
    """A mock_ token should never call the GitHub API — use defaults instead."""
    headers = {'Authorization': 'Bearer mock_token_123'}
    with patch('requests.get') as mock_get:
        repos = get_repos(client, headers)
        mock_get.assert_not_called()
    assert len(repos) > 0


# ── Tier 1: live GitHub API ──────────────────────────────────────────────────

def test_real_token_calls_github_api(client):
    """A non-mock token should attempt to call the GitHub API."""
    fake_repo = {
        'id': 999, 'name': 'test-repo', 'full_name': 'user/test-repo',
        'html_url': 'https://github.com/user/test-repo',
        'clone_url': 'https://github.com/user/test-repo.git',
        'description': 'A test repo', 'private': False, 'default_branch': 'main',
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [fake_repo]

    headers = {'Authorization': 'Bearer ghp_realtoken123456789'}
    with patch('requests.get', return_value=mock_response):
        repos = get_repos(client, headers)

    assert any(r['name'] == 'test-repo' for r in repos)


def test_github_api_failure_falls_back_gracefully(client):
    """If GitHub API throws, endpoint should still return something."""
    headers = {'Authorization': 'Bearer ghp_realtoken123456789'}
    with patch('requests.get', side_effect=Exception('network error')):
        repos = get_repos(client, headers)
    assert len(repos) > 0


def test_github_api_non_200_falls_back(client):
    """GitHub API returning non-200 should fall back without erroring."""
    mock_response = MagicMock()
    mock_response.status_code = 401

    headers = {'Authorization': 'Bearer ghp_realtoken123456789'}
    with patch('requests.get', return_value=mock_response):
        repos = get_repos(client, headers)
    assert len(repos) > 0


# ── Tier 2: SQLite cache ─────────────────────────────────────────────────────

def test_sqlite_cache_save_and_load():
    """_save_cached_repos and _load_cached_repos should round-trip correctly."""
    from api.repositories import _save_cached_repos, _load_cached_repos

    test_repos = [
        {'id': '1', 'name': 'cached-repo', 'full_name': 'user/cached-repo',
         'clone_url': 'https://github.com/user/cached-repo.git',
         'private': False, 'branch': 'main'},
    ]

    # Use /tmp directly — tempfile.TemporaryDirectory cleanup hits FUSE issues
    db_path = '/tmp/codeviz_test_cache_roundtrip.db'
    try:
        with patch('api.repositories._get_db_path', return_value=db_path):
            _save_cached_repos(test_repos)
            loaded = _load_cached_repos()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

    assert len(loaded) == 1
    assert loaded[0]['name'] == 'cached-repo'


def test_sqlite_cache_overwrites_previous_entries():
    """Each save should replace the previous cache (only one row kept)."""
    from api.repositories import _save_cached_repos, _load_cached_repos

    batch1 = [{'id': '1', 'name': 'old', 'full_name': 'u/old',
                'clone_url': 'x.git', 'private': False, 'branch': 'main'}]
    batch2 = [{'id': '2', 'name': 'new', 'full_name': 'u/new',
                'clone_url': 'y.git', 'private': False, 'branch': 'main'},
               {'id': '3', 'name': 'new2', 'full_name': 'u/new2',
                'clone_url': 'z.git', 'private': False, 'branch': 'main'}]

    db_path = '/tmp/codeviz_test_cache_overwrite.db'
    try:
        with patch('api.repositories._get_db_path', return_value=db_path):
            _save_cached_repos(batch1)
            _save_cached_repos(batch2)
            loaded = _load_cached_repos()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

    assert len(loaded) == 2
    assert loaded[0]['name'] == 'new'


def test_load_cached_repos_returns_empty_list_when_no_db():
    """If the DB doesn't exist, _load_cached_repos should return [] not raise."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from api.repositories import _load_cached_repos

    with patch('api.repositories._get_db_path', return_value='/tmp/nonexistent_codeviz_xyz.db'):
        result = _load_cached_repos()
    assert result == []


# ── Response shape ────────────────────────────────────────────────────────────

def test_response_includes_count(client):
    r = client.get('/api/repositories/github')
    data = r.get_json()
    assert 'count' in data['data']
    assert data['data']['count'] == len(data['data']['repositories'])
