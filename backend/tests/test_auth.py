"""Tests for authentication endpoints."""


def test_auth_status_unauthenticated(client):
    """Auth status with no session token should report unauthenticated."""
    r = client.get('/api/auth/status')
    assert r.status_code == 200
    data = r.get_json()
    assert data['data']['authenticated'] is False


def test_github_login_returns_auth_url(client, monkeypatch):
    """Login endpoint should return a GitHub OAuth URL when client ID is set."""
    monkeypatch.setenv('GITHUB_CLIENT_ID', 'test_client_id_xyz')
    r = client.get('/api/auth/github/login?frontend_url=http://localhost:5174')
    assert r.status_code == 200
    data = r.get_json()
    auth_url = data['data']['auth_url']
    assert 'github.com/login/oauth/authorize' in auth_url
    assert 'test_client_id_xyz' in auth_url
    assert 'scope=repo' in auth_url


def test_github_login_stores_frontend_url(client, monkeypatch):
    """frontend_url param should be stored so the callback redirects to the right port."""
    monkeypatch.setenv('GITHUB_CLIENT_ID', 'test_client_id_xyz')
    with client.session_transaction() as sess:
        sess.clear()

    r = client.get('/api/auth/github/login?frontend_url=http://localhost:5174')
    assert r.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get('frontend_url') == 'http://localhost:5174'


def test_github_login_returns_400_when_client_id_missing(client, monkeypatch):
    """Without GITHUB_CLIENT_ID configured the endpoint should return 400."""
    monkeypatch.delenv('GITHUB_CLIENT_ID', raising=False)
    r = client.get('/api/auth/github/login')
    assert r.status_code == 400


def test_github_callback_no_code(client):
    """Callback with no code and no error should redirect to login."""
    r = client.get('/api/auth/github/callback')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_github_callback_user_denied(client):
    """access_denied error from GitHub should redirect with error param."""
    r = client.get('/api/auth/github/callback?error=access_denied')
    assert r.status_code == 302
    assert 'error=access_denied' in r.headers['Location']


def test_logout(client):
    """Logout should return 200."""
    r = client.post('/api/auth/logout')
    assert r.status_code == 200


def test_get_user_profile_mock_token(client, auth_headers):
    """Mock token should return the hardcoded developer profile."""
    r = client.get('/api/auth/user', headers=auth_headers)
    assert r.status_code == 200
    data = r.get_json()
    assert 'name' in data['data']
