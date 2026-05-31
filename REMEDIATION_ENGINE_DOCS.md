# Automated Remediation Engine - Documentation

## Overview

The Automated Remediation Engine is a comprehensive security automation module for the Move Digital platform that detects and auto-fixes security vulnerabilities and misconfigurations in software repositories.

## Capabilities

The remediation engine provides 5+ auto-fix capabilities:

### 1. **Outdated Dependency Detection & Fix**
- Detects outdated packages in `requirements.txt`, `setup.py`, `package.json`, `pyproject.toml`
- Maps CVEs to outdated dependencies
- Automatically updates dependencies to latest secure versions
- Supports Python and Node.js ecosystems

**Example Fix:**
```
Before: django==3.2.0 (CVE-2023-46695)
After:  django==4.2
```

### 2. **Hardcoded Secret Detection & Removal**
- Detects API keys, passwords, private keys, tokens
- Regex patterns for: AWS keys, GitHub tokens, Slack tokens, database connection strings
- Removes secrets from code and replaces with environment variable references
- Severity: CRITICAL

**Example Detection:**
```python
# Detected
API_KEY = 'sk-1234567890abcdefghij'

# Fixed
API_KEY = os.getenv('API_KEY')
```

### 3. **Code Formatting Issues**
- Uses Ruff for Python code quality
- Auto-fixes linting and formatting violations
- Enforces consistent code style
- Severity: LOW to MEDIUM

### 4. **Security Misconfigurations**
- Detects missing `.gitignore` files
- Identifies running containers as root user
- Finds hardcoded Flask SECRET_KEY
- Detects missing CORS configuration
- Finds undocumented Docker ports

**Fixes Applied:**
- Creates `.gitignore` with security best practices
- Updates Dockerfile to use non-root user
- Recommends environment variable usage

### 5. **Docker Security Issues**
- Detects containers running as root
- Finds missing EXPOSE directives
- Ensures proper user isolation

## Module Structure

### Core Classes

#### `RemediationDetector`
Detects auto-fixable security issues in repositories.

**Methods:**
- `detect_outdated_dependencies()` - Check for outdated packages
- `detect_hardcoded_secrets()` - Find hardcoded credentials
- `detect_code_formatting_issues()` - Detect code quality issues
- `detect_security_misconfigurations()` - Find config issues
- `detect_all_issues()` - Run all detections

#### `RemediationEngine`
Applies auto-fixes and creates remediation pull requests.

**Methods:**
- `clone_repository()` - Clone repo to temp directory
- `fix_outdated_dependencies()` - Update dependencies
- `remove_hardcoded_secrets()` - Remove secrets from code
- `fix_code_formatting()` - Apply formatting fixes
- `fix_security_misconfigurations()` - Fix config issues
- `apply_all_fixes()` - Apply all available fixes
- `create_remediation_pr()` - Create PR with fixes

#### `RemediationAnalyzer`
Analyzes repository and reports on fixable vs manual issues.

**Methods:**
- `analyze_repo()` - Comprehensive repository analysis

## Flask Integration

### Endpoints

#### 1. `POST /api/remediation/scan-and-fix`
Scans repository and creates remediation PR with auto-fixes.

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "branch": "main",
  "auto_create_pr": true
}
```

**Response:**
```json
{
  "status": "pr_created",
  "repository": "https://github.com/owner/repo",
  "analysis": {
    "total_issues": 15,
    "fixable_issues": 12,
    "manual_issues": 3,
    "fixable_percentage": "80.0%"
  },
  "pr": {
    "status": "success",
    "pr_number": 42,
    "pr_url": "https://github.com/owner/repo/pull/42",
    "issues_fixed": 12
  }
}
```

#### 2. `POST /api/remediation/analyze-repo`
Analyze repository to detect fixable security issues.

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "branch": "main"
}
```

**Response:**
```json
{
  "repository": "https://github.com/owner/repo",
  "branch": "main",
  "total_issues": 15,
  "fixable_issues": 12,
  "manual_issues": 3,
  "fixable_percentage": "80.0%",
  "breakdown": {
    "outdated_dependencies": 5,
    "hardcoded_secrets": 2,
    "code_formatting": 4,
    "security_misconfigurations": 1
  },
  "recommendations": [
    "Use /api/remediation/scan-and-fix to auto-fix 12 issues"
  ]
}
```

#### 3. `POST /api/remediation/detect-issues`
Detect auto-fixable issues without creating PR.

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "branch": "main"
}
```

**Response:**
```json
{
  "status": "success",
  "repository": "https://github.com/owner/repo",
  "summary": {
    "total_issues": 15,
    "fixable": 12,
    "manual": 3,
    "fixable_percentage": "80.0%"
  },
  "detailed_breakdown": {
    "outdated_dependencies": 5,
    "hardcoded_secrets": 2,
    "code_formatting": 4,
    "security_misconfigurations": 1
  }
}
```

#### 4. `GET /api/remediation/metrics`
Get remediation metrics and statistics.

**Response:**
```json
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
```

## Usage Examples

### Example 1: Scan and Auto-Fix Repository

```python
from remediation_engine import RemediationEngine

engine = RemediationEngine(token="your_github_token")

result = engine.create_remediation_pr(
    repo_url="https://github.com/owner/repo",
    branch="main"
)

print(f"PR Created: {result['pr_url']}")
print(f"Issues Fixed: {result['issues_fixed']}")
```

### Example 2: Analyze Repository

```python
from remediation_engine import RemediationAnalyzer

analyzer = RemediationAnalyzer()

analysis = analyzer.analyze_repo(
    repo_url="https://github.com/owner/repo",
    branch="main"
)

print(f"Total Issues: {analysis['total_issues']}")
print(f"Fixable: {analysis['fixable_issues']}")
print(f"Auto-fix %: {analysis['fixable_percentage']}")
```

### Example 3: Detect Issues Only

```python
from remediation_engine import RemediationDetector

detector = RemediationDetector()

issues = detector.detect_all_issues("/path/to/repo")

for category, items in issues.items():
    print(f"{category}: {len(items)} issues")
    for issue in items:
        print(f"  - {issue}")
```

## Integration with Slack Alerts

The remediation engine automatically sends Slack notifications when:

1. Remediation PR is created
2. High-severity issues are detected
3. Security metrics change significantly

Example notification:
```
🔒 Security Remediation PR: my-repo

Automated security fixes created in PR #42

Repository: my-repo
Issues Found: 15
Auto-Fixed: 12 (80%)
Severity: HIGH
```

## Metrics Tracking

The engine tracks:
- **Total Analyses**: Number of repositories analyzed
- **PRs Created**: Number of remediation PRs created
- **Total Fixable Issues**: Total auto-fixable issues detected across all repos
- **Total Auto-Fixed**: Total issues automatically fixed
- **Auto-fix Percentage**: Percentage of detected issues that can be auto-fixed
- **Average Fixable per Repo**: Average auto-fixable issues per repository

## Testing

Run the comprehensive test suite:

```bash
cd /Users/malcolmgovender/src
python test_remediation.py
```

Tests cover:
1. Issue detection across multiple categories
2. Repository analysis and metrics
3. Fix application and validation
4. Integration with audit logging

## Technical Details

### Dependencies
- PyGithub: GitHub API interaction
- Ruff: Python code quality analysis
- Subprocess: External tool execution
- SQLite: Audit logging

### Database
- Location: `~/.movedata/audit.db`
- Tables: `audit_logs`, `scan_history`
- Purpose: Track all remediation actions for compliance

### Environment Variables
- `GITHUB_TOKEN`: GitHub API token for PR creation
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications
- `TEAMS_WEBHOOK_URL`: Teams webhook for notifications

## Remediation PR Template

All remediation PRs include:
1. Title: "🔒 Security: Auto-remediation of vulnerabilities"
2. Detailed description of all issues fixed
3. CVE information for vulnerable dependencies
4. Security checklist for reviewers
5. Link to MoveDigital documentation

## Future Enhancements

1. Support for additional package managers (Cargo, Go modules)
2. Machine learning-based issue prioritization
3. Automated remediation testing before PR creation
4. Integration with security scanning tools (OWASP, SonarQube)
5. Multi-repository orchestration

## Troubleshooting

### "unable to open database file"
Solution: Ensure `~/.movedata/` directory exists with write permissions.

### "GitHub token not configured"
Solution: Set `GITHUB_TOKEN` environment variable with valid token.

### "Git clone failed"
Solution: Ensure the repository URL is valid and accessible with the provided token.

### "Ruff not found"
Solution: Install Ruff: `pip install ruff`

## Support

For issues or questions, contact the Move Digital security team.
