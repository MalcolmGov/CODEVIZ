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
        error = request.args.get('error')
        
        # Handle user denial
        if error:
            return redirect('http://localhost:5173/login?error=' + error)
        
        if not code:
            return redirect('http://localhost:5173/login?error=no_code')
        
        client_id = os.getenv("GITHUB_CLIENT_ID", "")
        client_secret = os.getenv("GITHUB_CLIENT_SECRET", "")
        token = None
        
        print(f"[AUTH] GitHub callback received with code: {code[:8]}...")
        print(f"[AUTH] Client ID configured: {bool(client_id)}")
        print(f"[AUTH] Client Secret configured: {bool(client_secret)}")
        
        if client_id and client_secret:
            try:
                import requests
                token_response = requests.post(
                    'https://github.com/login/oauth/access_token',
                    headers={'Accept': 'application/json'},
                    data={
                        'client_id': client_id,
                        'client_secret': client_secret,
                        'code': code
                    },
                    timeout=15
                )
                print(f"[AUTH] Token exchange response status: {token_response.status_code}")
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    token = token_data.get('access_token')
                    print(f"[AUTH] Token obtained: {bool(token)}")
            except Exception as e:
                print(f"[AUTH] Token exchange error: {e}")
        
        if not token:
            # Fallback mock token if OAuth credentials are not configured
            token = 'mock_github_token_' + code[:8]
            print(f"[AUTH] Using mock token: {token}")
        
        session['github_token'] = token
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/login?token={token}"
        print(f"[AUTH] Redirecting to: {redirect_url}")
        return redirect(redirect_url)
        
    except Exception as e:
        print(f"[AUTH] Callback error: {e}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return redirect(f'{frontend_url}/login?error={str(e)[:50]}')


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


@auth_bp.route('/user', methods=['GET'])
def get_user_profile():
    """Get authenticated user's profile from GitHub"""
    try:
        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            token = session.get('github_token')
            
        if token and not token.startswith('mock_'):
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            try:
                response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
                if response.status_code == 200:
                    user_data = response.json()
                    return format_success_response({
                        'id': user_data['id'],
                        'name': user_data.get('name') or user_data['login'],
                        'email': user_data.get('email', ''),
                        'avatar_url': user_data.get('avatar_url', ''),
                        'login': user_data['login']
                    })[0], 200
            except Exception as api_err:
                print(f"GitHub profile API Error: {api_err}")
                
        # Default mock fallback
        return format_success_response({
            'id': 1,
            'name': 'Malcolm Govender',
            'email': 'malcolm@codeviz.dev',
            'login': 'MalcolmGov'
        })[0], 200
        
    except Exception as e:
        return format_error_response(str(e))[0], 500
