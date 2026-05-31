"""
Security Policy Engine for Move Digital
Define, enforce, and track security policies across repositories
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import re


class PolicyType(Enum):
    """Types of security policies"""
    SECURITY = "security"
    DEPENDENCY = "dependency"
    PROCESS = "process"
    QUALITY = "quality"
    COMPLIANCE = "compliance"


class PolicyViolationSeverity(Enum):
    """Severity levels for policy violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityPolicy:
    """Represents a single security policy"""
    
    def __init__(
        self,
        name: str,
        description: str,
        policy_type: PolicyType,
        rules: List[Dict],
        enabled: bool = True,
        severity: PolicyViolationSeverity = PolicyViolationSeverity.HIGH,
        auto_block_prs: bool = True
    ):
        self.id = self._generate_id()
        self.name = name
        self.description = description
        self.policy_type = policy_type
        self.rules = rules
        self.enabled = enabled
        self.severity = severity
        self.auto_block_prs = auto_block_prs
        self.created_at = datetime.now().isoformat()
        self.violation_count = 0
        self.last_violation_at = None
    
    def _generate_id(self) -> str:
        """Generate unique policy ID"""
        import hashlib
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict:
        """Convert policy to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.policy_type.value,
            "rules": self.rules,
            "enabled": self.enabled,
            "severity": self.severity.value,
            "auto_block_prs": self.auto_block_prs,
            "created_at": self.created_at,
            "violation_count": self.violation_count,
            "last_violation_at": self.last_violation_at
        }


class PolicyEngine:
    """Manages and enforces security policies"""
    
    def __init__(self):
        self.policies: Dict[str, SecurityPolicy] = {}
        self.violations: List[Dict] = []
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Create default security policies"""
        
        # Policy 1: No hardcoded secrets
        self.create_policy(
            name="No Hardcoded Secrets",
            description="Prevent hardcoded credentials in code",
            policy_type=PolicyType.SECURITY,
            rules=[
                {
                    "type": "regex_detection",
                    "patterns": [
                        r"(password|pwd|passwd)\s*[:=]\s*['\"].*['\"]",
                        r"(api_key|apikey|api-key)\s*[:=]\s*['\"].*['\"]",
                        r"(secret|token)\s*[:=]\s*['\"].*['\"]",
                        r"AWS_SECRET.*=",
                        r"PRIVATE_KEY.*=",
                    ],
                    "message": "Hardcoded credential detected"
                }
            ],
            severity=PolicyViolationSeverity.CRITICAL,
            auto_block_prs=True
        )
        
        # Policy 2: Minimum code reviewers
        self.create_policy(
            name="Minimum Code Reviewers",
            description="Require minimum 2 code reviewers for all PRs",
            policy_type=PolicyType.PROCESS,
            rules=[
                {
                    "type": "min_reviewers",
                    "min_count": 2,
                    "message": "PR requires at least 2 code reviewers"
                }
            ],
            severity=PolicyViolationSeverity.HIGH,
            auto_block_prs=True
        )
        
        # Policy 3: No critical dependencies
        self.create_policy(
            name="No Critical Vulnerabilities in Dependencies",
            description="Block PRs that introduce critical dependency vulnerabilities",
            policy_type=PolicyType.DEPENDENCY,
            rules=[
                {
                    "type": "vulnerability_check",
                    "severity_threshold": "critical",
                    "message": "Critical vulnerability found in dependencies"
                }
            ],
            severity=PolicyViolationSeverity.CRITICAL,
            auto_block_prs=True
        )
        
        # Policy 4: Test coverage minimum
        self.create_policy(
            name="Minimum Test Coverage",
            description="Ensure minimum 80% test coverage",
            policy_type=PolicyType.QUALITY,
            rules=[
                {
                    "type": "coverage_check",
                    "min_coverage_percent": 80,
                    "message": "Test coverage below 80%"
                }
            ],
            severity=PolicyViolationSeverity.MEDIUM,
            auto_block_prs=False
        )
    
    def create_policy(
        self,
        name: str,
        description: str,
        policy_type: PolicyType,
        rules: List[Dict],
        severity: PolicyViolationSeverity = PolicyViolationSeverity.HIGH,
        auto_block_prs: bool = True
    ) -> SecurityPolicy:
        """Create a new security policy"""
        
        policy = SecurityPolicy(
            name=name,
            description=description,
            policy_type=policy_type,
            rules=rules,
            severity=severity,
            auto_block_prs=auto_block_prs
        )
        
        self.policies[policy.id] = policy
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Get policy by ID"""
        return self.policies.get(policy_id)
    
    def get_all_policies(self) -> List[SecurityPolicy]:
        """Get all policies"""
        return list(self.policies.values())
    
    def get_active_policies(self) -> List[SecurityPolicy]:
        """Get all active policies"""
        return [p for p in self.policies.values() if p.enabled]
    
    def disable_policy(self, policy_id: str) -> bool:
        """Disable a policy"""
        policy = self.get_policy(policy_id)
        if policy:
            policy.enabled = False
            return True
        return False
    
    def enable_policy(self, policy_id: str) -> bool:
        """Enable a policy"""
        policy = self.get_policy(policy_id)
        if policy:
            policy.enabled = True
            return True
        return False
    
    def check_code_for_violations(
        self,
        repo_name: str,
        file_path: str,
        file_content: str,
        pr_number: int = 0
    ) -> List[Dict]:
        """Check code for policy violations"""
        
        violations = []
        active_policies = self.get_active_policies()
        
        for policy in active_policies:
            for rule in policy.rules:
                rule_type = rule.get("type")
                
                if rule_type == "regex_detection":
                    patterns = rule.get("patterns", [])
                    for pattern in patterns:
                        if re.search(pattern, file_content, re.IGNORECASE):
                            violation = {
                                "policy_id": policy.id,
                                "policy_name": policy.name,
                                "repository": repo_name,
                                "file": file_path,
                                "pr_number": pr_number,
                                "severity": policy.severity.value,
                                "message": rule.get("message", "Policy violation detected"),
                                "detected_at": datetime.now().isoformat(),
                                "auto_block": policy.auto_block_prs
                            }
                            violations.append(violation)
                            policy.violation_count += 1
                            policy.last_violation_at = datetime.now().isoformat()
                            self.violations.append(violation)
        
        return violations
    
    def check_pr_for_violations(
        self,
        repo_name: str,
        pr_number: int,
        pr_files: List[Dict],
        pr_reviewers: int = 0,
        test_coverage_percent: int = 0
    ) -> Dict:
        """Check PR for all policy violations"""
        
        all_violations = []
        pr_should_block = False
        
        # Check each file in the PR
        for file in pr_files:
            file_path = file.get("filename", "")
            file_content = file.get("content", "")
            
            violations = self.check_code_for_violations(
                repo_name=repo_name,
                file_path=file_path,
                file_content=file_content,
                pr_number=pr_number
            )
            
            all_violations.extend(violations)
            
            if violations and any(v.get("auto_block") for v in violations):
                pr_should_block = True
        
        # Check minimum reviewers policy
        for policy in self.get_active_policies():
            for rule in policy.rules:
                if rule.get("type") == "min_reviewers":
                    min_reviewers = rule.get("min_count", 2)
                    if pr_reviewers < min_reviewers:
                        violation = {
                            "policy_id": policy.id,
                            "policy_name": policy.name,
                            "repository": repo_name,
                            "pr_number": pr_number,
                            "severity": policy.severity.value,
                            "message": f"PR has {pr_reviewers} reviewer(s), requires {min_reviewers}",
                            "detected_at": datetime.now().isoformat(),
                            "auto_block": policy.auto_block_prs
                        }
                        all_violations.append(violation)
                        self.violations.append(violation)
                        if policy.auto_block_prs:
                            pr_should_block = True
        
        # Check test coverage policy
        for policy in self.get_active_policies():
            for rule in policy.rules:
                if rule.get("type") == "coverage_check":
                    min_coverage = rule.get("min_coverage_percent", 80)
                    if test_coverage_percent < min_coverage:
                        violation = {
                            "policy_id": policy.id,
                            "policy_name": policy.name,
                            "repository": repo_name,
                            "pr_number": pr_number,
                            "severity": policy.severity.value,
                            "message": f"Test coverage {test_coverage_percent}%, requires {min_coverage}%",
                            "detected_at": datetime.now().isoformat(),
                            "auto_block": policy.auto_block_prs
                        }
                        all_violations.append(violation)
                        self.violations.append(violation)
                        if policy.auto_block_prs:
                            pr_should_block = True
        
        return {
            "repo": repo_name,
            "pr_number": pr_number,
            "violations": all_violations,
            "violation_count": len(all_violations),
            "should_block": pr_should_block,
            "critical_count": len([v for v in all_violations if v["severity"] == "critical"]),
            "high_count": len([v for v in all_violations if v["severity"] == "high"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_violations(
        self,
        limit: int = 100,
        repo_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get violation history"""
        
        violations = self.violations
        
        if repo_filter:
            violations = [v for v in violations if v.get("repository") == repo_filter]
        
        return violations[-limit:]
    
    def get_policy_stats(self) -> Dict:
        """Get policy statistics"""
        
        total_violations = len(self.violations)
        critical = len([v for v in self.violations if v.get("severity") == "critical"])
        high = len([v for v in self.violations if v.get("severity") == "high"])
        medium = len([v for v in self.violations if v.get("severity") == "medium"])
        
        policies = self.get_all_policies()
        
        return {
            "total_policies": len(policies),
            "active_policies": len(self.get_active_policies()),
            "total_violations": total_violations,
            "critical_violations": critical,
            "high_violations": high,
            "medium_violations": medium,
            "policies_with_violations": len(set(v.get("policy_id") for v in self.violations)),
            "timestamp": datetime.now().isoformat()
        }


# Flask endpoints to add to app.py
POLICY_ENDPOINTS = """
@app.route("/api/policies", methods=["GET"])
def get_policies():
    '''Get all security policies'''
    try:
        engine = PolicyEngine()
        policies = [p.to_dict() for p in engine.get_all_policies()]
        return jsonify({
            "status": "success",
            "policies": policies,
            "count": len(policies)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/policies", methods=["POST"])
def create_policy():
    '''Create a new security policy'''
    try:
        data = request.json
        engine = PolicyEngine()
        
        policy = engine.create_policy(
            name=data.get("name", ""),
            description=data.get("description", ""),
            policy_type=PolicyType(data.get("type", "security")),
            rules=data.get("rules", []),
            severity=PolicyViolationSeverity(data.get("severity", "high")),
            auto_block_prs=data.get("auto_block_prs", True)
        )
        
        return jsonify({
            "status": "success",
            "policy": policy.to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/policies/check-pr", methods=["POST"])
def check_pr_policies():
    '''Check PR for policy violations'''
    try:
        data = request.json
        engine = PolicyEngine()
        
        result = engine.check_pr_for_violations(
            repo_name=data.get("repo", ""),
            pr_number=data.get("pr_number", 0),
            pr_files=data.get("files", []),
            pr_reviewers=data.get("reviewers", 0),
            test_coverage_percent=data.get("coverage", 0)
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/policies/violations", methods=["GET"])
def get_violations():
    '''Get policy violations'''
    try:
        engine = PolicyEngine()
        repo_filter = request.args.get("repo")
        violations = engine.get_violations(repo_filter=repo_filter)
        
        return jsonify({
            "status": "success",
            "violations": violations,
            "count": len(violations)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/policies/stats", methods=["GET"])
def get_policy_stats():
    '''Get policy statistics'''
    try:
        engine = PolicyEngine()
        stats = engine.get_policy_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

if __name__ == "__main__":
    # Test example
    engine = PolicyEngine()
    
    # Test PR check
    test_files = [
        {
            "filename": "config.py",
            "content": "DATABASE_PASSWORD = 'secret123'"
        },
        {
            "filename": "api_handler.py",
            "content": "API_KEY = 'sk_live_xxxxx'"
        }
    ]
    
    result = engine.check_pr_for_violations(
        repo_name="test-repo",
        pr_number=42,
        pr_files=test_files,
        pr_reviewers=1,
        test_coverage_percent=75
    )
    
    print(json.dumps(result, indent=2))
