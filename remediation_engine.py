"""
Automated Remediation Engine for Move Digital Security Platform

Detects and fixes auto-fixable security issues:
- Outdated dependencies (requirements.txt, setup.py, package.json)
- Hardcoded secrets (regex detection)
- Code formatting issues
- Common security misconfigurations
"""

import os
import re
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from github import Github, GithubException, Branch
from enterprise_features import AuditLogger, IntegrationManager
import requests


class RemediationDetector:
    """Detect auto-fixable security issues in repositories"""

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.github = Github(self.github_token) if self.github_token else Github()
        self.issues_detected = []

    def detect_outdated_dependencies(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect outdated dependencies in requirements.txt, setup.py, package.json"""
        issues = []
        
        # Check requirements.txt
        req_file = Path(repo_path) / "requirements.txt"
        if req_file.exists():
            issues.extend(self._check_requirements_txt(req_file))
        
        # Check setup.py
        setup_file = Path(repo_path) / "setup.py"
        if setup_file.exists():
            issues.extend(self._check_setup_py(setup_file))
        
        # Check package.json
        package_file = Path(repo_path) / "package.json"
        if package_file.exists():
            issues.extend(self._check_package_json(package_file))
        
        # Check pyproject.toml
        pyproject_file = Path(repo_path) / "pyproject.toml"
        if pyproject_file.exists():
            issues.extend(self._check_pyproject_toml(pyproject_file))
        
        return issues

    def _check_requirements_txt(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check for outdated Python dependencies"""
        issues = []
        known_outdated = {
            "django": {"latest": "4.2", "cve": "CVE-2023-46695"},
            "flask": {"latest": "3.0.0", "cve": "CVE-2023-30861"},
            "requests": {"latest": "2.31.0", "cve": "None"},
            "pyyaml": {"latest": "6.0.1", "cve": "CVE-2020-14343"},
            "pillow": {"latest": "10.0.0", "cve": "CVE-2023-44271"},
            "cryptography": {"latest": "41.0.4", "cve": "CVE-2023-49083"},
        }
        
        try:
            with open(file_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    
                    # Parse dependency
                    match = re.match(r"([a-zA-Z0-9_-]+)(==|>=|<=|>|<)([0-9.]+)", line)
                    if match:
                        pkg_name, op, version = match.groups()
                        pkg_lower = pkg_name.lower()
                        
                        if pkg_lower in known_outdated:
                            info = known_outdated[pkg_lower]
                            issues.append({
                                "type": "outdated_dependency",
                                "file": "requirements.txt",
                                "package": pkg_name,
                                "current_version": version,
                                "latest_version": info["latest"],
                                "cve": info["cve"],
                                "severity": "high" if info["cve"] != "None" else "medium",
                                "fix": f"{pkg_name}=={info['latest']}",
                                "original_line": line
                            })
        except Exception as e:
            print(f"Error checking requirements.txt: {e}")
        
        return issues

    def _check_setup_py(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check for outdated dependencies in setup.py"""
        issues = []
        
        try:
            with open(file_path) as f:
                content = f.read()
            
            # Look for install_requires
            install_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if install_match:
                deps_str = install_match.group(1)
                
                # Find outdated packages
                for line in deps_str.split(","):
                    line = line.strip().strip("'\"")
                    if line and not line.startswith("#"):
                        if any(pkg in line.lower() for pkg in ["django", "flask", "requests"]):
                            issues.append({
                                "type": "outdated_dependency",
                                "file": "setup.py",
                                "package": line.split("==")[0] if "==" in line else line,
                                "current": line,
                                "severity": "medium",
                                "note": "Found in setup.py - requires manual update"
                            })
        except Exception as e:
            print(f"Error checking setup.py: {e}")
        
        return issues

    def _check_package_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check for outdated dependencies in package.json"""
        issues = []
        
        try:
            with open(file_path) as f:
                data = json.load(f)
            
            dependencies = data.get("dependencies", {})
            dev_dependencies = data.get("devDependencies", {})
            
            all_deps = {**dependencies, **dev_dependencies}
            
            # Check for known vulnerable packages
            vulnerable_packages = {
                "lodash": {"latest": "4.17.21", "cve": "CVE-2021-23337"},
                "underscore": {"latest": "1.13.6", "cve": "CVE-2021-23337"},
                "serialize-javascript": {"latest": "6.0.0", "cve": "CVE-2020-7660"},
            }
            
            for pkg, version in all_deps.items():
                if pkg.lower() in vulnerable_packages:
                    info = vulnerable_packages[pkg.lower()]
                    issues.append({
                        "type": "outdated_dependency",
                        "file": "package.json",
                        "package": pkg,
                        "current_version": version,
                        "latest_version": info["latest"],
                        "cve": info["cve"],
                        "severity": "high",
                        "fix": info["latest"]
                    })
        except Exception as e:
            print(f"Error checking package.json: {e}")
        
        return issues

    def _check_pyproject_toml(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check for outdated dependencies in pyproject.toml"""
        issues = []
        
        try:
            with open(file_path) as f:
                content = f.read()
            
            # Look for dependencies section
            if "dependencies" in content:
                issues.append({
                    "type": "pyproject_toml_found",
                    "file": "pyproject.toml",
                    "note": "Modern Python project - ensure all dependencies are up to date",
                    "severity": "info"
                })
        except Exception as e:
            print(f"Error checking pyproject.toml: {e}")
        
        return issues

    def detect_hardcoded_secrets(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect hardcoded secrets using regex patterns"""
        issues = []
        
        # Secret patterns
        secret_patterns = {
            "api_key": r'[Aa][Pp][Ii][\._-]?[Kk][Ee][Yy]\s*=\s*["\']([a-zA-Z0-9_-]{20,})["\']',
            "password": r'[Pp]assword\s*=\s*["\']([^"\']{8,})["\']',
            "aws_key": r'AKIA[0-9A-Z]{16}',
            "private_key": r'-----BEGIN PRIVATE KEY-----',
            "github_token": r'ghp_[0-9a-zA-Z]{36}',
            "slack_token": r'xox[baprs]-[0-9]{10,13}-[a-zA-Z0-9]{24,34}',
            "db_connection": r'(mongodb|postgres|mysql)://.*:.*@',
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in [".git", ".venv", "node_modules", ".env", "__pycache__"]]
            
            for file in files:
                # Only check code files
                if not any(file.endswith(ext) for ext in [".py", ".js", ".ts", ".go", ".java", ".rb", ".php", ".env.example"]):
                    continue
                
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for secret_type, pattern in secret_patterns.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            issues.append({
                                "type": "hardcoded_secret",
                                "secret_type": secret_type,
                                "file": str(file_path.relative_to(repo_path)),
                                "line": line_num,
                                "severity": "critical",
                                "fix_method": "Remove secret and use environment variables",
                                "example_fix": f"import os\n{secret_type.upper()} = os.getenv('{secret_type.upper()}')"
                            })
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
        
        return issues

    def detect_code_formatting_issues(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect code formatting issues using ruff/pylint"""
        issues = []
        
        try:
            # Run ruff for Python files
            cmd = ["ruff", "check", repo_path, "--output-format", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                try:
                    ruff_issues = json.loads(result.stdout)
                    for issue in ruff_issues[:10]:  # Limit to 10
                        issues.append({
                            "type": "code_formatting",
                            "tool": "ruff",
                            "file": issue.get("filename", ""),
                            "line": issue.get("row", 0),
                            "rule": issue.get("rule", ""),
                            "message": issue.get("message", ""),
                            "severity": "low",
                            "fix_method": "Run: ruff check --fix"
                        })
                except:
                    pass
        except Exception as e:
            print(f"Error running ruff: {e}")
        
        return issues

    def detect_security_misconfigurations(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect common security misconfigurations"""
        issues = []
        
        # Check for missing .gitignore
        gitignore = Path(repo_path) / ".gitignore"
        if not gitignore.exists():
            issues.append({
                "type": "misconfiguration",
                "category": "missing_gitignore",
                "severity": "medium",
                "fix": "Create .gitignore with sensitive files",
                "recommendation": "Add .env, *.log, node_modules, __pycache__, .DS_Store"
            })
        
        # Check for missing security headers in Flask apps
        app_file = Path(repo_path) / "app.py"
        if app_file.exists():
            try:
                with open(app_file) as f:
                    content = f.read()
                
                if "CORS" not in content and "flask_cors" not in content:
                    issues.append({
                        "type": "misconfiguration",
                        "category": "missing_cors",
                        "file": "app.py",
                        "severity": "medium",
                        "recommendation": "Implement CORS policy properly"
                    })
                
                if "SECRET_KEY" not in content or "os.getenv" not in content:
                    issues.append({
                        "type": "misconfiguration",
                        "category": "hardcoded_secret_key",
                        "file": "app.py",
                        "severity": "high",
                        "fix": "Use os.getenv('SECRET_KEY') instead of hardcoded values"
                    })
            except:
                pass
        
        # Check Docker files for security issues
        dockerfile = Path(repo_path) / "Dockerfile"
        if dockerfile.exists():
            try:
                with open(dockerfile) as f:
                    content = f.read()
                
                if "USER root" in content or "USER 0" in content:
                    issues.append({
                        "type": "misconfiguration",
                        "category": "running_as_root",
                        "file": "Dockerfile",
                        "severity": "high",
                        "fix": "Create non-root user and use it in Dockerfile"
                    })
                
                if "EXPOSE" not in content:
                    issues.append({
                        "type": "misconfiguration",
                        "category": "undocumented_ports",
                        "file": "Dockerfile",
                        "severity": "low",
                        "fix": "Add EXPOSE instruction for clarity"
                    })
            except:
                pass
        
        return issues

    def detect_all_issues(self, repo_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Run all detection methods"""
        return {
            "outdated_dependencies": self.detect_outdated_dependencies(repo_path),
            "hardcoded_secrets": self.detect_hardcoded_secrets(repo_path),
            "code_formatting": self.detect_code_formatting_issues(repo_path),
            "security_misconfigurations": self.detect_security_misconfigurations(repo_path)
        }


class RemediationEngine:
    """Apply auto-fixes to detected issues and create PRs"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.github = Github(self.token) if self.token else None
        self.audit_logger = AuditLogger()
        self.integrations = IntegrationManager()
        self.temp_dir = None

    def clone_repository(self, repo_url: str, branch: str = "main") -> str:
        """Clone repository to temp directory"""
        self.temp_dir = tempfile.mkdtemp()
        
        clean_url = repo_url.rstrip("/")
        if not clean_url.startswith("http"):
            clean_url = f"https://github.com/{clean_url}"
        
        if self.token and "github.com" in clean_url:
            clean_url = clean_url.replace("https://github.com/", f"https://{self.token}@github.com/")
        
        cmd = ["git", "clone", "--depth", "1", "-b", branch, clean_url, self.temp_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            raise Exception(f"Git clone failed: {result.stderr}")
        
        return self.temp_dir

    def fix_outdated_dependencies(self, repo_path: str, issues: List[Dict[str, Any]]) -> List[str]:
        """Fix outdated dependencies"""
        fixes = []
        
        for issue in issues:
            if issue.get("file") == "requirements.txt":
                req_file = Path(repo_path) / "requirements.txt"
                try:
                    with open(req_file) as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        if issue["package"].lower() in line.lower():
                            lines[i] = f"{issue['fix']}\n"
                            fixes.append(f"Updated {issue['package']} to {issue['latest_version']}")
                    
                    with open(req_file, 'w') as f:
                        f.writelines(lines)
                except Exception as e:
                    print(f"Error fixing requirements.txt: {e}")
        
        return fixes

    def remove_hardcoded_secrets(self, repo_path: str, issues: List[Dict[str, Any]]) -> List[str]:
        """Remove hardcoded secrets from files"""
        fixes = []
        
        for issue in issues:
            if issue.get("type") != "hardcoded_secret":
                continue
            
            file_path = Path(repo_path) / issue["file"]
            try:
                with open(file_path) as f:
                    lines = f.readlines()
                
                line_num = issue["line"] - 1
                if 0 <= line_num < len(lines):
                    # Replace the line with a safer version
                    lines[line_num] = f"# Secret removed - use environment variables\n"
                    fixes.append(f"Removed {issue['secret_type']} from {issue['file']}:{issue['line']}")
                
                with open(file_path, 'w') as f:
                    f.writelines(lines)
            except Exception as e:
                print(f"Error removing secret from {file_path}: {e}")
        
        return fixes

    def fix_code_formatting(self, repo_path: str) -> List[str]:
        """Auto-fix code formatting issues"""
        fixes = []
        
        try:
            # Run ruff with --fix flag
            cmd = ["ruff", "check", repo_path, "--fix"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                fixes.append("Applied ruff formatting fixes")
            
            # Run ruff format
            cmd = ["ruff", "format", repo_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                fixes.append("Applied ruff formatting")
        except Exception as e:
            print(f"Error running ruff: {e}")
        
        return fixes

    def fix_security_misconfigurations(self, repo_path: str, issues: List[Dict[str, Any]]) -> List[str]:
        """Fix common security misconfigurations"""
        fixes = []
        
        for issue in issues:
            if issue["category"] == "missing_gitignore":
                gitignore_path = Path(repo_path) / ".gitignore"
                gitignore_content = """.env
.env.local
*.log
__pycache__/
*.py[cod]
*$py.class
.venv/
node_modules/
.DS_Store
*.swp
*.swo
dist/
build/
*.egg-info/
.pytest_cache/
.vscode/
.idea/
coverage/
"""
                try:
                    with open(gitignore_path, 'w') as f:
                        f.write(gitignore_content)
                    fixes.append("Created .gitignore with security best practices")
                except Exception as e:
                    print(f"Error creating .gitignore: {e}")
            
            elif issue["category"] == "running_as_root":
                dockerfile = Path(repo_path) / "Dockerfile"
                try:
                    with open(dockerfile) as f:
                        content = f.read()
                    
                    if "USER root" in content or "USER 0" in content:
                        content = re.sub(r'USER\s+(root|0)', 'USER appuser', content)
                        if "RUN adduser -D appuser" not in content:
                            content = re.sub(
                                r'FROM\s+',
                                'FROM \n',
                                content,
                                count=1
                            )
                        
                        with open(dockerfile, 'w') as f:
                            f.write(content)
                        fixes.append("Updated Dockerfile to use non-root user")
                except Exception as e:
                    print(f"Error fixing Dockerfile: {e}")
        
        return fixes

    def apply_all_fixes(self, repo_path: str, detected_issues: Dict[str, Any]) -> Dict[str, List[str]]:
        """Apply all available fixes"""
        all_fixes = {}
        
        # Fix outdated dependencies
        if detected_issues.get("outdated_dependencies"):
            all_fixes["dependencies"] = self.fix_outdated_dependencies(
                repo_path, 
                detected_issues["outdated_dependencies"]
            )
        
        # Remove hardcoded secrets
        if detected_issues.get("hardcoded_secrets"):
            all_fixes["secrets"] = self.remove_hardcoded_secrets(
                repo_path, 
                detected_issues["hardcoded_secrets"]
            )
        
        # Fix code formatting
        if detected_issues.get("code_formatting"):
            all_fixes["formatting"] = self.fix_code_formatting(repo_path)
        
        # Fix security misconfigurations
        if detected_issues.get("security_misconfigurations"):
            all_fixes["misconfigurations"] = self.fix_security_misconfigurations(
                repo_path, 
                detected_issues["security_misconfigurations"]
            )
        
        return all_fixes

    def create_remediation_pr(
        self, 
        repo_url: str, 
        branch: str = "main",
        detected_issues: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create PR with remediation fixes"""
        
        if not self.github:
            raise Exception("GitHub token not configured")
        
        try:
            # Parse repo URL
            repo_parts = repo_url.rstrip("/").split("/")
            repo_name = repo_parts[-1].replace(".git", "")
            repo_owner = repo_parts[-2]
            
            # Get GitHub repo
            repo = self.github.get_user(repo_owner).get_repo(repo_name)
            
            # Clone repository
            repo_path = self.clone_repository(repo_url, branch)
            
            # Detect issues if not provided
            detector = RemediationDetector()
            if not detected_issues:
                detected_issues = detector.detect_all_issues(repo_path)
            
            # Count fixable issues
            fixable_count = sum(len(v) for k, v in detected_issues.items() if k != "security_misconfigurations")
            
            if fixable_count == 0:
                return {
                    "status": "no_issues",
                    "message": "No auto-fixable issues detected"
                }
            
            # Create feature branch
            base_branch = repo.get_branch(branch)
            fix_branch_name = f"security/remediation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            repo.create_git_ref(
                f"refs/heads/{fix_branch_name}",
                base_branch.commit.sha
            )
            
            # Apply fixes
            all_fixes = self.apply_all_fixes(repo_path, detected_issues)
            
            # Commit changes
            self._commit_changes(repo_path, all_fixes, repo_owner, repo_name, fix_branch_name)
            
            # Create PR
            pr_title = "🔒 Security: Auto-remediation of vulnerabilities"
            pr_body = self._generate_pr_description(detected_issues, all_fixes)
            
            pull_request = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=fix_branch_name,
                base=branch
            )
            
            # Log action
            self.audit_logger.log_action(
                "remediation_pr_created",
                "pull_request",
                pull_request.html_url,
                {
                    "repo": f"{repo_owner}/{repo_name}",
                    "pr_number": pull_request.number,
                    "issues_fixed": fixable_count,
                    "fixes": all_fixes
                }
            )
            
            # Send notification
            self.integrations.send_slack_notification(
                f"Security Remediation PR: {repo_name}",
                f"Automated security fixes created in PR #{pull_request.number}",
                severity="info",
                repo_name=repo_name,
                issues_count=fixable_count
            )
            
            return {
                "status": "success",
                "pr_number": pull_request.number,
                "pr_url": pull_request.html_url,
                "branch": fix_branch_name,
                "issues_detected": len(detected_issues),
                "issues_fixed": fixable_count,
                "fixes": all_fixes
            }
            
        except Exception as e:
            print(f"Error creating remediation PR: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                try:
                    shutil.rmtree(self.temp_dir)
                except:
                    pass

    def _commit_changes(self, repo_path: str, fixes: Dict[str, Any], owner: str, repo: str, branch: str) -> None:
        """Commit changes to the repository"""
        try:
            os.chdir(repo_path)
            
            # Configure git
            subprocess.run(["git", "config", "user.name", "Move Digital Bot"], check=True)
            subprocess.run(["git", "config", "user.email", "bot@movedigital.security"], check=True)
            
            # Stage changes
            subprocess.run(["git", "add", "-A"], check=True)
            
            # Create commit
            commit_msg = "🔒 Security: Auto-fix vulnerabilities\n\n"
            for category, items in fixes.items():
                if items:
                    commit_msg += f"- {category}: {', '.join(items[:3])}\n"
            
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            
            # Push changes
            push_url = f"https://{self.token}@github.com/{owner}/{repo}.git"
            subprocess.run(["git", "push", "-u", "origin", branch], check=True, env={**os.environ, "GIT_URL": push_url})
            
        except Exception as e:
            print(f"Error committing changes: {e}")

    def _generate_pr_description(self, detected_issues: Dict[str, Any], fixes: Dict[str, Any]) -> str:
        """Generate PR description with security details and CVEs"""
        description = """# 🔒 Security Remediation PR

This PR contains automated fixes for detected security vulnerabilities and misconfigurations.

## Issues Detected

"""
        
        # Dependencies
        if detected_issues.get("outdated_dependencies"):
            description += "### Outdated Dependencies\n"
            for issue in detected_issues["outdated_dependencies"][:5]:
                cve = issue.get("cve", "None")
                severity = issue.get("severity", "unknown").upper()
                description += f"- **{issue['package']}**: {issue['current_version']} → {issue['latest_version']} [{severity}] {cve}\n"
        
        # Hardcoded Secrets
        if detected_issues.get("hardcoded_secrets"):
            description += f"\n### Hardcoded Secrets Found\n"
            description += f"- Removed {len(detected_issues['hardcoded_secrets'])} hardcoded secrets\n"
            description += "- Secrets must be managed via environment variables\n"
        
        # Code Formatting
        if detected_issues.get("code_formatting"):
            description += f"\n### Code Quality Issues\n"
            description += f"- Found {len(detected_issues['code_formatting'])} code quality issues\n"
        
        # Misconfigurations
        if detected_issues.get("security_misconfigurations"):
            description += f"\n### Security Misconfigurations\n"
            for issue in detected_issues["security_misconfigurations"][:5]:
                description += f"- {issue.get('category', 'unknown')}: {issue.get('recommendation', issue.get('fix', 'Fix required'))}\n"
        
        # Fixes Applied
        description += "\n## Fixes Applied\n"
        for category, items in fixes.items():
            if items:
                description += f"\n### {category.title()}\n"
                for item in items[:5]:
                    description += f"- ✅ {item}\n"
        
        description += """

## Security Checklist

- [ ] All dependencies are up to date
- [ ] No hardcoded secrets present
- [ ] Security configuration is correct
- [ ] Code follows security best practices

## Notes

This is an automated security remediation. Please review all changes before merging.

---

*Generated by Move Digital Automated Remediation Engine*
"""
        
        return description


class RemediationAnalyzer:
    """Analyze repository for fixable vs manual issues"""

    def __init__(self):
        self.detector = RemediationDetector()
        self.audit_logger = AuditLogger()

    def analyze_repo(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """Analyze repository and report on fixable issues"""
        
        try:
            # Clone repo temporarily
            temp_dir = tempfile.mkdtemp()
            
            clean_url = repo_url.rstrip("/")
            if not clean_url.startswith("http"):
                clean_url = f"https://github.com/{clean_url}"
            
            cmd = ["git", "clone", "--depth", "1", "-b", branch, clean_url, temp_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                raise Exception("Failed to clone repository")
            
            # Detect all issues
            detected_issues = self.detector.detect_all_issues(temp_dir)
            
            # Calculate metrics
            total_issues = sum(len(v) for v in detected_issues.values())
            fixable_issues = sum(
                len(v) for k, v in detected_issues.items() 
                if k in ["outdated_dependencies", "hardcoded_secrets", "code_formatting"]
            )
            manual_issues = total_issues - fixable_issues
            
            fixable_percentage = (fixable_issues / total_issues * 100) if total_issues > 0 else 0
            
            # Log analysis
            self.audit_logger.log_action(
                "remediation_analysis_completed",
                "repository",
                repo_url,
                {
                    "total_issues": total_issues,
                    "fixable_issues": fixable_issues,
                    "manual_issues": manual_issues,
                    "fixable_percentage": fixable_percentage
                }
            )
            
            # Cleanup
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            return {
                "repository": repo_url,
                "branch": branch,
                "timestamp": datetime.now().isoformat(),
                "total_issues": total_issues,
                "fixable_issues": fixable_issues,
                "manual_issues": manual_issues,
                "fixable_percentage": f"{fixable_percentage:.1f}%",
                "breakdown": {
                    "outdated_dependencies": len(detected_issues.get("outdated_dependencies", [])),
                    "hardcoded_secrets": len(detected_issues.get("hardcoded_secrets", [])),
                    "code_formatting": len(detected_issues.get("code_formatting", [])),
                    "security_misconfigurations": len(detected_issues.get("security_misconfigurations", []))
                },
                "issues": detected_issues
            }
            
        except Exception as e:
            return {
                "repository": repo_url,
                "status": "error",
                "error": str(e)
            }
