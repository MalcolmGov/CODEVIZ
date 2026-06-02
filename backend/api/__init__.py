"""
API Blueprints initialization

All API endpoints are organized as blueprints for clean separation.
Each blueprint handles a specific domain (chat, security, refactoring, etc).
"""

from flask import Blueprint

# Create blueprint instances
chat_bp = Blueprint('chat', __name__)
security_bp = Blueprint('security', __name__)
refactoring_bp = Blueprint('refactoring', __name__)
auth_bp = Blueprint('auth', __name__)
repositories_bp = Blueprint('repositories', __name__)
health_bp = Blueprint('health', __name__)
scoring_bp = Blueprint('scoring', __name__)
compliance_bp = Blueprint('compliance', __name__)
reports_bp = Blueprint('reports', __name__)
settings_bp = Blueprint('settings', __name__)
performance_bp = Blueprint('performance', __name__)
threats_bp = Blueprint('threats', __name__)
remediation_bp = Blueprint('remediation', __name__)
smells_bp = Blueprint('smells', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
notifications_bp = Blueprint('notifications', __name__)
apis_bp = Blueprint('apis', __name__)
history_bp = Blueprint('history', __name__)

# Import route handlers (at bottom to avoid circular imports)
from . import chat, security, refactoring, auth, repositories, health, scoring, compliance, reports, settings, performance, threats, remediation, smells, dashboard, notifications, apis, history

__all__ = [
    'chat_bp', 'security_bp', 'refactoring_bp', 'auth_bp',
    'repositories_bp', 'health_bp', 'scoring_bp', 'compliance_bp', 'reports_bp', 'settings_bp', 'performance_bp',
    'threats_bp', 'remediation_bp', 'smells_bp', 'dashboard_bp', 'notifications_bp', 'apis_bp', 'history_bp',
]
