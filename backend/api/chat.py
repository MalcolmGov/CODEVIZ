"""
Chat API Blueprint

Handles repository scanning and Q&A functionality.
Uses legacy scanner logic preserved from original codebase.
"""

from flask import request, jsonify
from . import chat_bp
from utils import generate_session_id, format_success_response, format_error_response


# Legacy imports (business logic is preserved)
try:
    from core.scanner_legacy import RepositoryChat
    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False
    print("⚠️  Scanner not available - will use mocks")

# Session storage (will migrate to database)
repo_chats = {}


@chat_bp.route('/session', methods=['POST'])
def create_session():
    """
    Create a new chat session for a repository.
    
    Request:
        {
            "repo_path": "/app/src" or "https://github.com/user/repo",
            "branch": "main" (optional)
        }
    
    Response:
        {
            "status": "success",
            "session_id": "abc12345",
            "repo_path": "/path/to/repo"
        }
    """
    try:
        data = request.get_json() or {}
        repo_input = data.get('repo_path', '/app/src')
        session_id = generate_session_id()
        
        actual_path = repo_input
        temp_path = None
        
        if repo_input.startswith('http') or 'github.com' in repo_input:
            mock_repos = {
                'MalcolmGov/CODEVIZ': '/Users/malcolmgovender/.gemini/antigravity-ide/scratch/codeviz',
                'MalcolmGov/coastal-clean': '/Users/malcolmgovender/.gemini/antigravity-ide/scratch/coastal-clean',
                'MalcolmGov/SwifterWallet': '/Users/malcolmgovender/.gemini/antigravity-ide/scratch/SwifterWallet',
                'MalcolmGov/intelligencehub': '/Users/malcolmgovender/.gemini/antigravity-ide/scratch/intelligencehub'
            }
            
            matched_local = None
            for key, val in mock_repos.items():
                if key.lower() in repo_input.lower():
                    import os
                    if os.path.exists(val):
                        matched_local = val
                        break
            
            if matched_local:
                actual_path = matched_local
            else:
                from services.github_legacy import GitHubScanner
                auth_header = request.headers.get('Authorization')
                token = None
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                if token and token.startswith('mock_'):
                    token = None
                    
                scanner = GitHubScanner(token=token)
                branch = data.get('branch', 'main')
                temp_path = scanner.clone_repo(repo_input, branch)
                actual_path = temp_path
        
        if SCANNER_AVAILABLE:
            chat = RepositoryChat(actual_path)
            if temp_path:
                chat._temp_path = temp_path
                chat._original_url = repo_input
            repo_chats[session_id] = chat
        else:
            repo_chats[session_id] = {
                'repo_path': repo_input,
                'is_scanned': False,
                'context': {}
            }

        # Persist session to DB so it survives restarts
        try:
            from core.session_store import save_session
            save_session(session_id, repo_chats[session_id])
        except Exception:
            pass

        return format_success_response({
            'session_id': session_id,
            'repo_path': repo_input
        }, 'Chat session created')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 400


@chat_bp.route('/scan/<session_id>', methods=['POST'])
def scan_repository(session_id):
    """
    Scan repository for a session.
    
    Uses all preserved scanner logic from original codebase.
    """
    try:
        if session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404
        
        chat = repo_chats[session_id]
        
        if SCANNER_AVAILABLE:
            # Call legacy scanner
            context = chat.scan()
            status = chat.get_scan_status()
        else:
            # Mock scan
            status = {
                'files': 42,
                'loc': 15000,
                'apis': 52,
                'functions': 189,
                'classes': 63,
                'security_issues': 8
            }
            chat['is_scanned'] = True
        
        return format_success_response({
            'session_id': session_id,
            'scan_status': status
        }, 'Repository scanned')[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@chat_bp.route('/artifacts/<session_id>', methods=['GET'])
def get_artifacts(session_id):
    """Get all discovered artifacts from scan"""
    try:
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404
        
        chat = repo_chats[session_id]
        
        if SCANNER_AVAILABLE and hasattr(chat, 'context'):
            artifacts = chat.context
        elif isinstance(chat, dict):
            artifacts = chat.get('context', {})
        else:
            artifacts = {}
        
        return format_success_response({
            'artifacts': artifacts
        })[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@chat_bp.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question about repository (after scanning)"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        question = data.get('question', '').strip()
        
        if not session_id or session_id not in repo_chats:
            return format_error_response('Invalid session ID')[0], 404
        
        if not question:
            return format_error_response('Question required')[0], 400
        
        chat = repo_chats[session_id]
        
        if SCANNER_AVAILABLE and hasattr(chat, 'ask'):
            answer = chat.ask(question)
            # 'llm' when answered by the language model, 'keyword' on fallback
            source = getattr(chat, 'last_answer_source', None)
        else:
            # Mock answer
            answer = f"Mock response to: {question}"
            source = 'mock'
        
        return format_success_response({
            'session_id': session_id,
            'question': question,
            'answer': answer,
            'source': source
        })[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get conversation history"""
    try:
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404
        
        chat = repo_chats[session_id]
        
        if SCANNER_AVAILABLE and hasattr(chat, 'get_history'):
            history = chat.get_history()
        else:
            history = []
        
        return format_success_response({
            'session_id': session_id,
            'history': history
        })[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@chat_bp.route('/clear/<session_id>', methods=['POST'])
def clear_session(session_id):
    """Clear a session"""
    try:
        if session_id in repo_chats:
            chat = repo_chats[session_id]
            if hasattr(chat, '_temp_path') and chat._temp_path:
                import shutil
                try:
                    shutil.rmtree(chat._temp_path)
                except:
                    pass
            del repo_chats[session_id]
            try:
                from core.session_store import delete_session
                delete_session(session_id)
            except Exception:
                pass
            return format_success_response(None, 'Session cleared')[0], 200
        
        return format_error_response('Session not found')[0], 404
        
    except Exception as e:
        return format_error_response(str(e))[0], 500
