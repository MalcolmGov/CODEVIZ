"""Tests for the security API endpoint."""


def test_security_invalid_session_returns_404(client, auth_headers):
    r = client.get('/api/security/bad_session_id', headers=auth_headers)
    assert r.status_code == 404


def test_security_response_on_invalid_session_has_error_status(client, auth_headers):
    r = client.get('/api/security/bad_session_id', headers=auth_headers)
    data = r.get_json()
    assert data['status'] == 'error'
