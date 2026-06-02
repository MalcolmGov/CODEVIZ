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


@refactoring_bp.route('/stage-pr', methods=['POST'])
def stage_pr():
    """Apply a refactoring recommendation on a new Git branch and commit it"""
    try:
        from api.chat import repo_chats
        import os
        import subprocess
        import random
        import string
        
        data = request.get_json() or {}
        session_id = data.get('session_id')
        file_path = data.get('file')
        line_number = data.get('line')
        original_code = data.get('before')
        fixed_code = data.get('after')
        refactor_type = data.get('type', 'Improvement')
        
        if not session_id or not file_path or line_number is None or not original_code or not fixed_code:
            return format_error_response('Missing required fields')[0], 400
            
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404
            
        chat = repo_chats[session_id]
        repo_path = chat.repo_path
        
        # Generate clean branch name
        clean_type = refactor_type.lower().replace(' ', '-')
        # Strip characters not allowed in git branch names
        clean_type = re.sub(r'[^a-zA-Z0-9\-]', '', clean_type)
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        branch_name = f"refactor/{clean_type}-{rand_suffix}"
        commit_message = f"refactor: apply {refactor_type} in {os.path.basename(file_path)} on line {line_number}"
        
        # Apply local patch
        orig_dir = os.getcwd()
        try:
            os.chdir(repo_path)
            
            is_git = os.path.exists('.git')
            if is_git:
                # Ensure main is checked out first
                subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                # Create and switch to new branch
                subprocess.run(['git', 'checkout', '-b', branch_name], capture_output=True)
                
            full_file_path = os.path.join(repo_path, file_path)
            if not os.path.exists(full_file_path):
                return format_error_response(f"Target file not found: {file_path}")[0], 404
                
            with open(full_file_path, 'r', errors='ignore') as f:
                lines = f.readlines()
                
            line_idx = line_number - 1
            applied = False
            
            if 0 <= line_idx < len(lines):
                lines[line_idx] = fixed_code + '\n'
                applied = True
            else:
                # Fallback to absolute replace
                content = "".join(lines)
                if original_code in content:
                    content = content.replace(original_code, fixed_code)
                    lines = [content]
                    applied = True
                    
            if not applied:
                return format_error_response("Could not align the refactoring patch to source code lines.")[0], 400
                
            with open(full_file_path, 'w') as f:
                f.writelines(lines)
                
            if is_git:
                subprocess.run(['git', 'add', file_path], capture_output=True)
                subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True)
                
            return format_success_response({
                'session_id': session_id,
                'branch': branch_name if is_git else 'Local filesystem (non-git)',
                'file_patched': file_path,
                'commit': commit_message,
                'is_git': is_git
            }, 'Refactoring PR patch branch successfully created')[0], 200
            
        finally:
            os.chdir(orig_dir)
            
    except Exception as e:
        return format_error_response(str(e))[0], 500


@refactoring_bp.route('/auto-stage', methods=['POST'])
def auto_stage():
    """Apply all refactoring fixes to the files on a single unified branch"""
    try:
        from api.chat import repo_chats
        import os
        import re
        import subprocess
        import random
        import string
        
        data = request.get_json() or {}
        session_id = data.get('session_id')
        opps = data.get('opportunities', [])
        
        if not session_id:
            return format_error_response('Session ID required')[0], 400
            
        if session_id not in repo_chats:
            return format_error_response('Session not found')[0], 404
            
        chat = repo_chats[session_id]
        repo_path = chat.repo_path
        
        # Filter opportunities for confidence/priority
        high_conf_opps = []
        for opp in opps:
            conf = opp.get('confidence', 0.8)
            try:
                conf = float(conf)
            except:
                conf = 0.8
            if conf >= 0.7 and opp.get('file') and opp.get('line') and opp.get('current_code') and opp.get('suggested_code'):
                high_conf_opps.append(opp)
                
        if not high_conf_opps:
            return format_success_response({
                'session_id': session_id,
                'branch': 'No changes',
                'files_patched': [],
                'commit': 'No refactor suggestions to apply',
                'is_git': False,
                'applied_count': 0
            }, 'No refactor opportunities to auto-stage')[0], 200
            
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        branch_name = f"remediation/refactor-patch-{rand_suffix}"
        commit_message = f"remediation: apply {len(high_conf_opps)} quality auto-refactoring patches"
        
        orig_dir = os.getcwd()
        try:
            os.chdir(repo_path)
            
            is_git = os.path.exists('.git')
            if is_git:
                subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                subprocess.run(['git', 'checkout', '-b', branch_name], capture_output=True)
                
            files_patched = []
            applied_count = 0
            
            patches_by_file = {}
            for opp in high_conf_opps:
                file_path = opp['file']
                if file_path not in patches_by_file:
                    patches_by_file[file_path] = []
                patches_by_file[file_path].append(opp)
                
            for file_path, file_patches in patches_by_file.items():
                full_file_path = os.path.join(repo_path, file_path)
                if not os.path.exists(full_file_path):
                    continue
                    
                with open(full_file_path, 'r', errors='ignore') as f:
                    lines = f.readlines()
                    
                file_modified = False
                for opp in sorted(file_patches, key=lambda o: o['line'], reverse=True):
                    line_number = opp['line']
                    fixed_code = opp['suggested_code']
                    original_code = opp['current_code']
                    line_idx = line_number - 1
                    
                    if 0 <= line_idx < len(lines):
                        lines[line_idx] = fixed_code + '\n'
                        file_modified = True
                        applied_count += 1
                    else:
                        content = "".join(lines)
                        if original_code in content:
                            content = content.replace(original_code, fixed_code)
                            lines = [content]
                            file_modified = True
                            applied_count += 1
                            
                if file_modified:
                    with open(full_file_path, 'w') as f:
                        f.writelines(lines)
                    files_patched.append(file_path)
                    if is_git:
                        subprocess.run(['git', 'add', file_path], capture_output=True)
                        
            if is_git and files_patched:
                subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True)
                
            return format_success_response({
                'session_id': session_id,
                'branch': branch_name if is_git else 'Local filesystem (non-git)',
                'files_patched': files_patched,
                'commit': commit_message,
                'is_git': is_git,
                'applied_count': applied_count
            }, f'Successfully staged {applied_count} refactoring auto-fixes on branch {branch_name}')[0], 200
            
        finally:
            os.chdir(orig_dir)
            
    except Exception as e:
        return format_error_response(str(e))[0], 500
