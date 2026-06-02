"""
Shared test fixtures for CodeViz backend test suite.

Uses 'testing' config:
  - SQLite in-memory (no PostgreSQL needed)
  - TESTING = True

Redis is not available in the sandbox — init_session already handles
this gracefully (catches the exception, prints a warning, continues).
No patching needed.
"""
import os
import sys
import pytest

# Ensure the backend root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope='session')
def app():
    """Create a Flask test application."""
    from app import create_app
    application = create_app('testing')
    application.config.update({
        'SECRET_KEY':          'test-secret-key',
        'GITHUB_CLIENT_ID':    'test_client_id',
        'GITHUB_CLIENT_SECRET': 'test_client_secret',
        'TESTING':             True,
        'WTF_CSRF_ENABLED':    False,
    })

    with application.app_context():
        try:
            from extensions import db
            db.create_all()
        except Exception:
            pass

    yield application


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Headers that simulate a logged-in user with a mock token."""
    return {'Authorization': 'Bearer mock_token_123'}
