import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from github import Github, GithubException
import redis

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except:
    redis_client = None


class GitHubScanner:
    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        if self.token:
            self.gh = Github(self.token)
        else:
            self.gh = Github()
        self.temp_dir = None

    def clone_repo(self, repo_url: str, branch: str = "main") -> str:
        try:
            self.temp_dir = tempfile.mkdtemp()
            
            clean_url = repo_url.rstrip("/")
            if "/tree/" in clean_url:
                clean_url = clean_url.split("/tree/")[0]
            if "/blob/" in clean_url:
                clean_url = clean_url.split("/blob/")[0]
            
            if not clean_url.startswith("http"):
                clean_url = f"https://github.com/{clean_url}"
            
            if self.token and "github.com" in clean_url:
                clean_url = clean_url.replace("https://github.com/", f"https://{self.token}@github.com/")
            
            cmd = ["git", "clone", "--depth", "1", "-b", branch, clean_url, self.temp_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                cmd = ["git", "clone", "--depth", "1", clean_url, self.temp_dir]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                error_msg = (result.stderr if result.stderr else result.stdout)[:200]
                raise Exception(error_msg)
            
            return self.temp_dir
        except Exception as e:
            msg = str(e)[:150]
            raise Exception(msg)

    def scan_with_bandit(self, repo_path: str) -> Dict[str, Any]:
        try:
            cmd = ["bandit", "-r", repo_path, "-f", "json", "--skip", "B101,B601"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            try:
                output = json.loads(result.stdout)
                return {"tool": "bandit", "issues": output.get("results", []), "status": "success"}
            except:
                return {"tool": "bandit", "issues": [], "status": "no_python"}
        except Exception as e:
            return {"tool": "bandit", "status": "error", "error": str(e)[:100], "issues": []}

    def scan_with_ruff(self, repo_path: str) -> Dict[str, Any]:
        try:
            cmd = ["ruff", "check", repo_path, "--output-format", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            try:
                output = json.loads(result.stdout) if result.stdout else []
                return {"tool": "ruff", "issues": output, "status": "success"}
            except:
                return {"tool": "ruff", "issues": [], "status": "error"}
        except Exception as e:
            return {"tool": "ruff", "status": "error", "error": str(e)[:100], "issues": []}

    def analyze_dependencies(self, repo_path: str) -> Dict[str, Any]:
        issues = []
        req_file = Path(repo_path) / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file) as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                if deps:
                    issues.append({"file": "requirements.txt", "count": len(deps)})
            except:
                pass
        
        for cfg in ["pyproject.toml", "setup.py", "Pipfile"]:
            if (Path(repo_path) / cfg).exists():
                issues.append({"file": cfg, "type": "config"})
        
        return {"tool": "dependency_analyzer", "issues": issues, "status": "success"}

    def get_file_stats(self, repo_path: str) -> Dict[str, Any]:
        stats = {
            "total_files": 0,
            "python_files": 0,
            "javascript_files": 0,
            "test_files": 0,
            "largest_files": [],
        }
        
        files = []
        for root, dirs, filenames in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "venv", ".git"]]
            for filename in filenames:
                if filename.startswith("."):
                    continue
                filepath = Path(root) / filename
                try:
                    size = filepath.stat().st_size
                    rel_path = str(filepath.relative_to(repo_path))
                    stats["total_files"] += 1
                    
                    if filepath.suffix == ".py":
                        stats["python_files"] += 1
                        if "test" in rel_path.lower():
                            stats["test_files"] += 1
                    elif filepath.suffix in [".js", ".ts"]:
                        stats["javascript_files"] += 1
                    
                    files.append({"path": rel_path, "size": size})
                except:
                    pass
        
        files.sort(key=lambda x: x["size"], reverse=True)
        stats["largest_files"] = [f["path"] for f in files[:5]]
        return stats

    def generate_report(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        try:
            repo_path = self.clone_repo(repo_url, branch)
            
            report = {
                "repository": repo_url,
                "branch": branch,
                "timestamp": __import__("datetime").datetime.now().isoformat(),
                "scans": {},
            }
            
            report["scans"]["security"] = self.scan_with_bandit(repo_path)
            report["scans"]["quality"] = self.scan_with_ruff(repo_path)
            report["scans"]["dependencies"] = self.analyze_dependencies(repo_path)
            report["scans"]["stats"] = self.get_file_stats(repo_path)
            
            sec_issues = report["scans"]["security"].get("issues", [])
            qual_issues = report["scans"]["quality"].get("issues", [])
            dep_issues = report["scans"]["dependencies"].get("issues", [])
            
            total = len(sec_issues) + len(qual_issues) + len(dep_issues)
            
            risk_level = "critical" if total > 15 else "high" if total > 5 else "medium" if total > 0 else "low"
            
            report["summary"] = {
                "total_issues": total,
                "security_issues": len(sec_issues),
                "quality_issues": len(qual_issues),
                "dependency_issues": len(dep_issues),
                "risk_level": risk_level,
            }
            
            if redis_client:
                try:
                    cache_key = f"github_scan:{repo_url}:{branch}"
                    redis_client.setex(cache_key, 86400, json.dumps(report))
                except:
                    pass
            
            return report
        except Exception as e:
            return {"repository": repo_url, "status": "error", "error": str(e)[:200]}
        finally:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                try:
                    shutil.rmtree(self.temp_dir)
                except:
                    pass


class RepositoryAnalysisAgent:
    def __init__(self):
        self.scanner = GitHubScanner()

    def analyze_repo(self, repo_url: str, branch: str = "main") -> str:
        report = self.scanner.generate_report(repo_url, branch)
        
        if "error" in report:
            return f"Error: {report['error']}"
        
        return f"""🔍 GitHub Repository Scan
Repository: {report['repository']}
Risk Level: {report['summary']['risk_level'].upper()}

📊 Issues:
- Total: {report['summary']['total_issues']}
- Security: {report['summary']['security_issues']}
- Quality: {report['summary']['quality_issues']}
- Dependencies: {report['summary']['dependency_issues']}

📈 Stats:
- Files: {report['scans']['stats']['total_files']}
- Python: {report['scans']['stats']['python_files']}
- Tests: {report['scans']['stats']['test_files']}
"""
