"""Tests for the dashboard API."""


def test_dashboard_sessions_returns_200(client, auth_headers):
    r = client.get('/api/dashboard/sessions', headers=auth_headers)
    assert r.status_code == 200


def test_dashboard_sessions_response_shape(client, auth_headers):
    r = client.get('/api/dashboard/sessions', headers=auth_headers)
    data = r.get_json()
    assert data['status'] == 'success'
    assert 'data' in data


def test_dashboard_summary_invalid_session(client, auth_headers):
    """Requesting summary for a nonexistent session should return 404."""
    r = client.get('/api/dashboard/summary/nonexistent_session_id',
                   headers=auth_headers)
    assert r.status_code == 404


def test_dashboard_summary_missing_session_returns_error(client):
    r = client.get('/api/dashboard/summary/does_not_exist')
    assert r.status_code in (400, 404, 500)
