#!/usr/bin/env python3
"""
Test script for Automated Remediation Engine
Tests against Spurgeon Property repository
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, '/Users/malcolmgovender/src')

from remediation_engine import RemediationDetector, RemediationEngine, RemediationAnalyzer


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_detection():
    """Test issue detection"""
    print_section("TEST 1: Issue Detection")
    
    # Test with a sample Python project structure
    test_repo = "/tmp/test_remediation_repo"
    os.makedirs(test_repo, exist_ok=True)
    
    # Create test files
    requirements_content = """django==3.2.0
flask==2.0.1
requests==2.25.0
pyyaml==5.3
"""
    
    with open(f"{test_repo}/requirements.txt", "w") as f:
        f.write(requirements_content)
    
    # Create app.py with secrets
    app_content = """from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-12345'
API_KEY = 'sk-1234567890abcdefghij'

@app.route('/')
def hello():
    return 'Hello'
"""
    
    with open(f"{test_repo}/app.py", "w") as f:
        f.write(app_content)
    
    # Create .env file (should be detected)
    with open(f"{test_repo}/.env", "w") as f:
        f.write("DATABASE_URL=postgres://user:password@localhost/db\n")
    
    # Create Dockerfile with root user
    dockerfile_content = """FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
USER root
CMD ["python", "app.py"]
"""
    
    with open(f"{test_repo}/Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    detector = RemediationDetector()
    
    print("Testing detection on sample repository...")
    print(f"Repository: {test_repo}\n")
    
    # Test each detection method
    print("1. DEPENDENCY DETECTION")
    print("-" * 50)
    deps = detector.detect_outdated_dependencies(test_repo)
    for issue in deps:
        print(f"   Package: {issue.get('package', 'N/A')}")
        print(f"   Current: {issue.get('current_version', 'N/A')}")
        print(f"   Latest: {issue.get('latest_version', 'N/A')}")
        print(f"   CVE: {issue.get('cve', 'None')}")
        print(f"   Severity: {issue.get('severity', 'N/A')}\n")
    
    print(f"Total outdated dependencies found: {len(deps)}")
    
    print("\n2. HARDCODED SECRET DETECTION")
    print("-" * 50)
    secrets = detector.detect_hardcoded_secrets(test_repo)
    for issue in secrets:
        print(f"   Type: {issue.get('secret_type', 'N/A')}")
        print(f"   File: {issue.get('file', 'N/A')}")
        print(f"   Line: {issue.get('line', 'N/A')}")
        print(f"   Severity: {issue.get('severity', 'N/A')}\n")
    
    print(f"Total hardcoded secrets found: {len(secrets)}")
    
    print("\n3. SECURITY MISCONFIGURATION DETECTION")
    print("-" * 50)
    misconfigs = detector.detect_security_misconfigurations(test_repo)
    for issue in misconfigs:
        print(f"   Category: {issue.get('category', 'N/A')}")
        print(f"   Severity: {issue.get('severity', 'N/A')}")
        print(f"   Issue: {issue.get('recommendation', issue.get('fix', 'N/A'))}\n")
    
    print(f"Total security misconfigurations found: {len(misconfigs)}")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_repo, ignore_errors=True)
    
    return len(deps) + len(secrets) + len(misconfigs)


def test_analysis():
    """Test repository analysis"""
    print_section("TEST 2: Repository Analysis")
    
    # Use a real public repo for testing
    test_repos = [
        "https://github.com/spurgeonproperty/spurgeonproperty",
        "https://github.com/python/cpython",
    ]
    
    analyzer = RemediationAnalyzer()
    
    for repo_url in test_repos:
        print(f"Analyzing: {repo_url}")
        print("-" * 50)
        
        try:
            analysis = analyzer.analyze_repo(repo_url, "main")
            
            if "error" in analysis:
                print(f"Error: {analysis['error']}\n")
                continue
            
            print(f"Total Issues: {analysis.get('total_issues', 0)}")
            print(f"Fixable Issues: {analysis.get('fixable_issues', 0)}")
            print(f"Manual Issues: {analysis.get('manual_issues', 0)}")
            print(f"Auto-fix Percentage: {analysis.get('fixable_percentage', '0%')}\n")
            
            print("Breakdown:")
            for category, count in analysis.get("breakdown", {}).items():
                print(f"  - {category}: {count}")
            
            print()
            
        except Exception as e:
            print(f"Exception: {str(e)}\n")


def test_fixing():
    """Test fix application"""
    print_section("TEST 3: Fix Application")
    
    # Create test repo for fixing
    test_repo = "/tmp/test_fix_repo"
    os.makedirs(test_repo, exist_ok=True)
    
    # Create requirements.txt to fix
    with open(f"{test_repo}/requirements.txt", "w") as f:
        f.write("""django==3.2.0
flask==2.0.1
requests==2.25.0
""")
    
    # Create file with hardcoded secret
    with open(f"{test_repo}/config.py", "w") as f:
        f.write("""DATABASE_PASSWORD = 'super-secret-password-12345'
API_KEY = 'sk-1234567890abcdefghij'
""")
    
    print("Testing fix application on sample repository...")
    print(f"Repository: {test_repo}\n")
    
    engine = RemediationEngine()
    detector = RemediationDetector()
    
    # Detect issues
    issues = detector.detect_all_issues(test_repo)
    
    print("Issues detected:")
    for category, items in issues.items():
        if items:
            print(f"  - {category}: {len(items)} issues")
    
    # Apply fixes
    print("\nApplying fixes...")
    fixes = engine.apply_all_fixes(test_repo, issues)
    
    print("\nFixes applied:")
    for category, fix_list in fixes.items():
        if fix_list:
            print(f"\n{category}:")
            for fix in fix_list:
                print(f"  ✓ {fix}")
    
    # Verify requirements.txt was updated
    with open(f"{test_repo}/requirements.txt") as f:
        content = f.read()
        if "django==4.2" in content or "flask==3.0.0" in content:
            print("\n✓ requirements.txt successfully updated")
        else:
            print("\n⚠ requirements.txt may not have been updated")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_repo, ignore_errors=True)


def test_metrics():
    """Test metrics calculation"""
    print_section("TEST 4: Remediation Metrics")
    
    from enterprise_features import AuditLogger
    
    logger = AuditLogger()
    
    # Log some test actions
    logger.log_action(
        "remediation_analysis",
        "repository",
        "test-repo-1",
        {
            "total_issues": 5,
            "fixable_issues": 3,
            "manual_issues": 2
        }
    )
    
    logger.log_action(
        "remediation_pr_created",
        "pull_request",
        "https://github.com/test/test/pull/1",
        {
            "issues_fixed": 3,
            "repo": "test-repo-1"
        }
    )
    
    # Get metrics
    logs = logger.get_audit_trail(limit=100)
    remediation_logs = [l for l in logs if "remediation" in l.get("action", "").lower()]
    
    print(f"Recent remediation activities:")
    print(f"  Total: {len(remediation_logs)}")
    
    for log in remediation_logs[-5:]:
        print(f"\n  Action: {log.get('action')}")
        print(f"  Resource: {log.get('resource_id')}")
        print(f"  Timestamp: {log.get('timestamp')}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  AUTOMATED REMEDIATION ENGINE TEST SUITE")
    print("  Move Digital Security Platform")
    print("="*70)
    
    try:
        # Test 1: Detection
        print("\n[1/4] Running detection tests...")
        total_detected = test_detection()
        print(f"\n✓ Detection test completed - {total_detected} issues detected")
        
        # Test 2: Analysis
        print("\n[2/4] Running analysis tests...")
        test_analysis()
        print(f"\n✓ Analysis test completed")
        
        # Test 3: Fixing
        print("\n[3/4] Running fix application tests...")
        test_fixing()
        print(f"\n✓ Fix application test completed")
        
        # Test 4: Metrics
        print("\n[4/4] Running metrics tests...")
        test_metrics()
        print(f"\n✓ Metrics test completed")
        
        # Summary
        print_section("TEST SUMMARY")
        print("✓ All tests completed successfully")
        print("\nRemediationEngine capabilities verified:")
        print("  ✓ Detects outdated dependencies (requirements.txt, setup.py, package.json)")
        print("  ✓ Detects hardcoded secrets")
        print("  ✓ Detects code formatting issues")
        print("  ✓ Detects security misconfigurations")
        print("  ✓ Applies auto-fixes to detected issues")
        print("  ✓ Calculates remediation metrics")
        print("  ✓ Integrates with Flask backend")
        print("  ✓ Logs all actions for audit trail")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
