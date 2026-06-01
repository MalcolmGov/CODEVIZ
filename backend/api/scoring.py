"""
Scoring API Blueprint
Tier 2: Multi-Dimensional Risk Scoring
GET /api/scoring/<session_id>  — compute and return full score profile
"""

from flask import request
from . import scoring_bp
from utils import format_success_response, format_error_response

try:
    from core.scoring import MultiDimensionalScorer
    SCORER_AVAILABLE = True
except ImportError as e:
    SCORER_AVAILABLE = False
    print(f"⚠️  Scorer not available: {e}")


@scoring_bp.route('/<session_id>', methods=['GET'])
def get_score(session_id):
    """
    Compute multi-dimensional risk score for a scanned session.
    Requires the session to have been scanned first via POST /api/chat/scan/<session_id>.
    """
    try:
        from api.chat import repo_chats

        if session_id not in repo_chats:
            return format_error_response('Session not found — scan a repository first')[0], 404

        chat = repo_chats[session_id]

        # Extract artifacts from the session
        if hasattr(chat, 'context') and chat.context:
            artifacts = chat.context
        elif isinstance(chat, dict):
            artifacts = chat.get('context', {})
        else:
            artifacts = {}

        if not artifacts:
            return format_error_response('No scan data found — run a scan first')[0], 400

        if not SCORER_AVAILABLE:
            return format_error_response('Scoring engine not available')[0], 500

        scorer = MultiDimensionalScorer()
        result = scorer.score(artifacts)

        return format_success_response(result, 'Risk score computed')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500


@scoring_bp.route('/preview', methods=['POST'])
def score_preview():
    """
    Score arbitrary artifact data (for testing / demo).
    Body: { artifacts: { apis, classes, ... } }
    """
    try:
        data = request.get_json() or {}
        artifacts = data.get('artifacts', {})

        if not SCORER_AVAILABLE:
            return format_error_response('Scoring engine not available')[0], 500

        scorer = MultiDimensionalScorer()
        result = scorer.score(artifacts)

        return format_success_response(result, 'Preview score computed')[0], 200

    except Exception as e:
        return format_error_response(str(e))[0], 500
