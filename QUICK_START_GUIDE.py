#!/usr/bin/env python3
"""
Quick Start Guide for Automated Remediation Engine

This script demonstrates how to use the remediation engine with practical examples.
"""

import os
import sys
import json

sys.path.insert(0, '/Users/malcolmgovender/src')

from remediation_engine import RemediationEngine, RemediationAnalyzer, RemediationDetector


def example_1_detect_issues():
    """Example 1: Detect issues in a repository"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Detect Security Issues in Repository")
    print("="*70 + "\n")
    
    print("Code:")
    print("-" * 70)
    print("""
from remediation_engine import RemediationDetector

detector = RemediationDetector()

# Detect all issues in repository
issues = detector.detect_all_issues("/path/to/repo")

# Print results
for category, items in issues.items():
    print(f"{category}: {len(items)} issues")
    for issue in items:
        print(f"  - {issue['type']}: {issue.get('severity', 'N/A')}")
""")
    print("-" * 70)
    
    print("\nExpected Output:")
    print("-" * 70)
    print("""
outdated_dependencies: 5 issues
  - outdated_dependency: high
  - outdated_dependency: high
  - outdated_dependency: high
  - outdated_dependency: high
  - outdated_dependency: medium

hardcoded_secrets: 2 issues
  - hardcoded_secret: critical
  - hardcoded_secret: critical

code_formatting: 4 issues
  - code_formatting: low
  - code_formatting: low
  - code_formatting: low
  - code_formatting: low

security_misconfigurations: 1 issues
  - misconfiguration: high
""")
    print("-" * 70)


def example_2_analyze_repository():
    """Example 2: Analyze repository for fixable issues"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Analyze Repository (Fixable vs Manual Issues)")
    print("="*70 + "\n")
    
    print("Code:")
    print("-" * 70)
    print("""
from remediation_engine import RemediationAnalyzer

analyzer = RemediationAnalyzer()

# Analyze repository
analysis = analyzer.analyze_repo(
    "https://github.com/owner/repo",
    "main"
)

print(f"Total Issues: {analysis['total_issues']}")
print(f"Auto-Fixable: {analysis['fixable_issues']}")
print(f"Manual Review: {analysis['manual_issues']}")
print(f"Success Rate: {analysis['fixable_percentage']}")

# Print breakdown
print("\\nBreakdown:")
for category, count in analysis['breakdown'].items():
    print(f"  {category}: {count}")
""")
    print("-" * 70)
    
    print("\nExpected Output:")
    print("-" * 70)
    print("""
Total Issues: 15
Auto-Fixable: 12
Manual Review: 3
Success Rate: 80.0%

Breakdown:
  outdated_dependencies: 5
  hardcoded_secrets: 2
  code_formatting: 4
  security_misconfigurations: 1
""")
    print("-" * 70)


def example_3_apply_fixes():
    """Example 3: Apply automatic fixes"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Apply Automatic Fixes")
    print("="*70 + "\n")
    
    print("Code:")
    print("-" * 70)
    print("""
from remediation_engine import RemediationEngine, RemediationDetector

# First detect issues
detector = RemediationDetector()
issues = detector.detect_all_issues("/path/to/repo")

# Then apply fixes
engine = RemediationEngine()
fixes = engine.apply_all_fixes("/path/to/repo", issues)

# Print results
for category, fix_list in fixes.items():
    if fix_list:
        print(f"{category}:")
        for fix in fix_list:
            print(f"  ✓ {fix}")
""")
    print("-" * 70)
    
    print("\nExpected Output:")
    print("-" * 70)
    print("""
dependencies:
  ✓ Updated django to 4.2
  ✓ Updated flask to 3.0.0
  ✓ Updated requests to 2.31.0
  ✓ Updated pyyaml to 6.0.1

secrets:
  ✓ Removed api_key from app.py:2
  ✓ Removed db_password from config.py:5

misconfigurations:
  ✓ Created .gitignore with security best practices
  ✓ Updated Dockerfile to use non-root user
""")
    print("-" * 70)


def example_4_create_remediation_pr():
    """Example 4: Create remediation PR on GitHub"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Create Remediation PR")
    print("="*70 + "\n")
    
    print("Code:")
    print("-" * 70)
    print("""
from remediation_engine import RemediationEngine

engine = RemediationEngine(token="your-github-token")

# Create remediation PR
result = engine.create_remediation_pr(
    repo_url="https://github.com/owner/repo",
    branch="main"
)

if result['status'] == 'success':
    print(f"PR Created: #{result['pr_number']}")
    print(f"URL: {result['pr_url']}")
    print(f"Branch: {result['branch']}")
    print(f"Issues Fixed: {result['issues_fixed']}")
else:
    print(f"Error: {result['error']}")
""")
    print("-" * 70)
    
    print("\nExpected Output:")
    print("-" * 70)
    print("""
PR Created: #42
URL: https://github.com/owner/repo/pull/42
Branch: security/remediation-20240115-103045
Issues Fixed: 12

[GitHub Notification]:
  Title: 🔒 Security: Auto-remediation of vulnerabilities
  
  Description:
    This PR contains automated fixes for detected security vulnerabilities
    
    Issues Detected:
    - Outdated Dependencies (5 issues)
      • django: 3.2.0 → 4.2 [HIGH] CVE-2023-46695
      • flask: 2.0.1 → 3.0.0 [HIGH] CVE-2023-30861
      
    - Hardcoded Secrets Found (2 issues)
      • Removed hardcoded secrets from code
      
    - Code Quality Issues (4 issues)
      • Applied formatting fixes
      
    - Security Misconfigurations (1 issue)
      • Fixed Docker security issues
""")
    print("-" * 70)


def example_5_flask_api():
    """Example 5: Using Flask API endpoints"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Using Flask API Endpoints")
    print("="*70 + "\n")
    
    print("Endpoint 1: POST /api/remediation/analyze-repo")
    print("-" * 70)
    print("""
curl -X POST http://localhost:8000/api/remediation/analyze-repo \\
  -H "Content-Type: application/json" \\
  -d '{
    "repo_url": "https://github.com/owner/repo",
    "branch": "main"
  }'

Response:
{
  "total_issues": 15,
  "fixable_issues": 12,
  "manual_issues": 3,
  "fixable_percentage": "80.0%",
  "breakdown": {
    "outdated_dependencies": 5,
    "hardcoded_secrets": 2,
    "code_formatting": 4,
    "security_misconfigurations": 1
  }
}
""")
    
    print("\nEndpoint 2: POST /api/remediation/scan-and-fix")
    print("-" * 70)
    print("""
curl -X POST http://localhost:8000/api/remediation/scan-and-fix \\
  -H "Content-Type: application/json" \\
  -d '{
    "repo_url": "https://github.com/owner/repo",
    "branch": "main",
    "auto_create_pr": true
  }'

Response:
{
  "status": "pr_created",
  "pr": {
    "pr_number": 42,
    "pr_url": "https://github.com/owner/repo/pull/42",
    "issues_fixed": 12
  }
}
""")
    
    print("\nEndpoint 3: GET /api/remediation/metrics")
    print("-" * 70)
    print("""
curl http://localhost:8000/api/remediation/metrics

Response:
{
  "status": "success",
  "metrics": {
    "total_analyses": 25,
    "prs_created": 18,
    "total_fixable_detected": 342,
    "total_auto_fixed": 298,
    "auto_fix_percentage": "87.1%",
    "average_fixable_per_repo": "13.7"
  }
}
""")


def example_6_integration():
    """Example 6: Full integration workflow"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Complete Integration Workflow")
    print("="*70 + "\n")
    
    print("""
Scenario: Security scan detects vulnerabilities in a repository.
Remediation engine automatically analyzes and fixes what it can.

Flow:
1. Security scan completes → 15 issues detected
2. Remediation engine analyzes → 12 auto-fixable, 3 manual
3. Automatic fixes applied → Dependencies updated, secrets removed
4. Remediation PR created → #42 on GitHub
5. Slack notification sent → #security channel
6. Metrics updated → Tracked for compliance
7. Developer reviews PR → Manual issues still require attention

Result:
✓ 12 issues auto-fixed (80%)
✓ 3 issues flagged for manual review
✓ Full audit trail maintained
✓ Team notified of security improvements
✓ Compliance metrics updated
""")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  AUTOMATED REMEDIATION ENGINE - QUICK START GUIDE")
    print("  Move Digital Security Platform")
    print("="*70)
    
    print("\nThis guide demonstrates practical usage examples of the")
    print("Automated Remediation Engine with code and expected outputs.")
    
    # Run examples
    example_1_detect_issues()
    example_2_analyze_repository()
    example_3_apply_fixes()
    example_4_create_remediation_pr()
    example_5_flask_api()
    example_6_integration()
    
    # Installation guide
    print("\n" + "="*70)
    print("INSTALLATION & SETUP")
    print("="*70 + "\n")
    
    print("1. Install Dependencies:")
    print("-" * 70)
    print("""
pip install PyGithub ruff GitPython requests flask
""")
    
    print("\n2. Set Environment Variables:")
    print("-" * 70)
    print("""
export GITHUB_TOKEN="your-github-token"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export FLASK_ENV="production"
""")
    
    print("\n3. Start Flask Server:")
    print("-" * 70)
    print("""
cd /Users/malcolmgovender/src
python app.py
""")
    
    print("\n4. Test Endpoints:")
    print("-" * 70)
    print("""
# Analyze a repository
curl -X POST http://localhost:8000/api/remediation/analyze-repo \\
  -H "Content-Type: application/json" \\
  -d '{"repo_url": "https://github.com/owner/repo"}'

# Get metrics
curl http://localhost:8000/api/remediation/metrics
""")
    
    # Features checklist
    print("\n" + "="*70)
    print("FEATURES IMPLEMENTED")
    print("="*70 + "\n")
    
    features = [
        ("✓", "Detect outdated dependencies"),
        ("✓", "Detect hardcoded secrets"),
        ("✓", "Detect code formatting issues"),
        ("✓", "Detect security misconfigurations"),
        ("✓", "Auto-fix dependencies"),
        ("✓", "Auto-fix secrets removal"),
        ("✓", "Auto-fix code formatting"),
        ("✓", "Create remediation PRs"),
        ("✓", "GitHub integration"),
        ("✓", "Slack notifications"),
        ("✓", "Audit logging"),
        ("✓", "Metrics tracking"),
        ("✓", "Flask API endpoints (4)"),
        ("✓", "CVE tracking"),
        ("✓", "Multi-language support"),
    ]
    
    for check, feature in features:
        print(f"  {check} {feature}")
    
    # Support info
    print("\n" + "="*70)
    print("SUPPORT & DOCUMENTATION")
    print("="*70 + "\n")
    
    print("Documentation Files:")
    print("  - REMEDIATION_ENGINE_DOCS.md - Full API documentation")
    print("  - REMEDIATION_ENGINE_IMPLEMENTATION.md - Implementation details")
    print()
    print("Test Files:")
    print("  - test_remediation.py - End-to-end tests")
    print("  - test_remediation_core.py - Core functionality tests")
    print()
    print("For questions or issues, contact the Move Digital security team.")
    
    print("\n" + "="*70)
    print("✓ QUICK START GUIDE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
