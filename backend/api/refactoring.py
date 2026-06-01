"""
Refactoring API Blueprint

Handles code refactoring suggestions and transformations.
Uses legacy refactoring_detector_legacy.py and ai_refactorer_legacy.py
"""

from flask import request, jsonify
from . import refactoring_bp
from utils import format_success_response, format_error_response


try:
    from core.refactoring_detector_legacy import RefactoringDetector
    from core.ai_refactorer_legacy import AIRefactorer
    REFACTORING_AVAILABLE = True
except ImportError:
    REFACTORING_AVAILABLE = False
    print("⚠️  Refactoring modules not available")


@refactoring_bp.route('/opportunities/<session_id>', methods=['GET'])
def get_opportunities(session_id):
    """
    Get refactoring opportunities for session.
    
    Uses legacy RefactoringDetector to analyze code.
    """
    try:
        from api.chat import repo_chats
        
        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404
        
        chat = repo_chats[session_id]
        artifacts = None
        
        if REFACTORING_AVAILABLE and hasattr(chat, 'context'):
            artifacts = chat.context
        elif isinstance(chat, dict):
            artifacts = chat.get('context', {})
        
        if not artifacts:
            return format_success_response({
                'session_id': session_id,
                'opportunities': [],
                'summary': {
                    'total': 0,
                    'extract_method': 0,
                    'simplify_conditional': 0,
                    'rename_variables': 0,
                    'remove_duplication': 0,
                    'reduce_complexity': 0
                }
            }, 'No opportunities found')[0], 200
        
        # Use legacy detector
        detector = RefactoringDetector(artifacts)
        opportunities = detector.find_opportunities()
        summary = detector.get_summary()
        
        return format_success_response({
            'session_id': session_id,
            'opportunities': [opp.to_dict() if hasattr(opp, 'to_dict') else opp 
                            for opp in opportunities[:20]],
            'summary': summary
        }, f'Found {len(opportunities)} opportunities')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@refactoring_bp.route('/suggest/<session_id>/<int:opp_index>', methods=['GET'])
def get_suggestion(session_id, opp_index):
    """
    Get AI-powered suggestion for specific opportunity.
    
    Uses legacy AIRefactorer to generate refactored code and tests.
    """
    try:
        from api.chat import repo_chats
        
        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404
        
        chat = repo_chats[session_id]
        artifacts = None
        
        if hasattr(chat, 'context'):
            artifacts = chat.context
        elif isinstance(chat, dict):
            artifacts = chat.get('context', {})
        
        if not artifacts:
            return format_error_response('No artifacts found')[0], 404
        
        detector = RefactoringDetector(artifacts)
        opportunities = detector.find_opportunities()
        
        if opp_index >= len(opportunities):
            return format_error_response('Opportunity index out of range')[0], 400
        
        opportunity = opportunities[opp_index]
        
        # Generate suggestion using AI refactorer
        if REFACTORING_AVAILABLE:
            refactorer = AIRefactorer()
            suggestion = refactorer.suggest_refactoring(opportunity)
        else:
            suggestion = {
                'type': opportunity.get('type', 'unknown'),
                'priority': opportunity.get('priority', 5),
                'refactored_code': '# Refactored code would appear here',
                'tests': '# Tests would appear here',
                'explanation': 'AI suggestion not available',
                'confidence': 0.5
            }
        
        return format_success_response({
            'session_id': session_id,
            'opportunity_index': opp_index,
            'suggestion': suggestion
        }, 'Suggestion generated')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@refactoring_bp.route('/pr/<session_id>/<int:opp_index>', methods=['GET'])
def get_pr_content(session_id, opp_index):
    """
    Get GitHub PR content for refactoring suggestion.
    
    Returns PR title, description, branch name ready to create.
    """
    try:
        from api.chat import repo_chats
        
        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404
        
        chat = repo_chats[session_id]
        artifacts = chat.context if hasattr(chat, 'context') else {}
        
        if not artifacts:
            return format_error_response('No artifacts found')[0], 404
        
        detector = RefactoringDetector(artifacts)
        opportunities = detector.find_opportunities()
        
        if opp_index >= len(opportunities):
            return format_error_response('Opportunity index out of range')[0], 400
        
        opportunity = opportunities[opp_index]
        
        # Generate PR content
        pr_content = {
            'title': f"🔄 Refactoring: {opportunity.get('type', 'Code Improvement')}",
            'description': f"""# Refactoring Opportunity

## Type
{opportunity.get('type', 'Unknown')}

## Priority
{opportunity.get('priority', 5)}/10

## Location
{opportunity.get('file', 'unknown')}

## Benefits
- Improved code quality
- Better maintainability
- Reduced complexity

## Changes
See attached refactored code and tests.
""",
            'branch': f"refactor/{opportunity.get('type', 'improvement').lower().replace(' ', '-')}",
            'files_changed': 1
        }
        
        return format_success_response({
            'session_id': session_id,
            'pr_content': pr_content
        }, 'PR content ready')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@refactoring_bp.route('/create-pr', methods=['POST'])
def create_pr():
    """
    Create GitHub PR with refactoring suggestion.
    
    Requires: repo_name, pr_content, github_token
    """
    try:
        data = request.get_json() or {}
        repo_name = data.get('repo_name', '')
        pr_content = data.get('pr_content', {})
        github_token = data.get('github_token', '')
        
        if not all([repo_name, pr_content, github_token]):
            return format_error_response('Missing required fields')[0], 400
        
        # In production, would use GitHub API
        # For now, return mock success
        pr_url = f"https://github.com/{repo_name}/pull/mock-123"
        
        return format_success_response({
            'pr_url': pr_url,
            'status': 'mock_created',
            'note': 'GitHub integration coming soon'
        }, 'PR creation initiated')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500
