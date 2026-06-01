"""
Authentication API Blueprint

Handles GitHub OAuth and session management.
"""

from flask import request, jsonify, redirect, session
from . import auth_bp
from utils import format_success_response, format_error_response
import os


@auth_bp.route('/github/login', methods=['GET'])
def github_login():
    """Redirect to GitHub OAuth"""
    try:
        client_id = os.getenv("GITHUB_CLIENT_ID", "")
        if not client_id:
            return format_error_response('GitHub OAuth not configured')[0], 400
        
        redirect_uri = os.getenv(
            "GITHUB_REDIRECT_URI",
            "http://localhost:8000/api/auth/github/callback"
        )
        
        github_auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=repo"
        )
        
        return format_success_response({
            'auth_url': github_auth_url
        })[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@auth_bp.route('/github/callback', methods=['GET'])
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        code = request.args.get('code')
        if not code:
            return redirect('/?error=no_code')
        
        # In production, exchange code for token
        # For now, return mock token
        mock_token = 'mock_github_token_' + code[:8]
        
        session['github_token'] = mock_token
        
        return redirect('/dashboard?authenticated=true')
        
    except Exception as e:
        return redirect(f'/?error={str(e)}')


@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Get current authentication status"""
    try:
        github_token = session.get('github_token')
        
        return format_success_response({
            'authenticated': bool(github_token),
            'token_type': 'github' if github_token else None
        })[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        return format_success_response(None, 'Logged out')[0], 200
    except Exception as e:
        return format_error_response(str(e))[0], 500
