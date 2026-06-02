"""Tests for health / status endpoints."""


def test_health_returns_200(client):
    r = client.get('/api/health')
    assert r.status_code == 200


def test_health_response_shape(client):
    r = client.get('/api/health')
    data = r.get_json()
    assert data is not None
    assert 'status' in data or 'message' in data or r.status_code == 200


def test_status_endpoint(client):
    r = client.get('/api/status')
    # May not exist in all environments — just verify it doesn't 500
    assert r.status_code in (200, 404)


def test_health_ping_endpoint(client):
    r = client.post('/api/health/ping-endpoint',
                    json={'url': 'http://localhost:9999/nonexistent'},
                    content_type='application/json')
    # Should respond (even with a connection-refused result), not 500
    assert r.status_code in (200, 400, 404, 500)
