import os
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from github_scanner import GitHubScanner


class AuditLogger:
    """Comprehensive audit logging for compliance and security"""

    def __init__(self):
        # Use user home directory if /app is not accessible
        import tempfile
        home = os.path.expanduser("~")
        db_dir = os.path.join(home, ".movedata")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "audit.db")
        self.init_db()

    def init_db(self):
        """Initialize SQLite audit database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                action TEXT,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repository_url TEXT,
                scan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                branch TEXT,
                total_issues INTEGER,
                critical_issues INTEGER,
                high_issues INTEGER,
                medium_issues INTEGER,
                low_issues INTEGER,
                duration_seconds INTEGER,
                git_commit TEXT,
                status TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    def log_action(self, action, resource_type, resource_id, details, user_id="system", ip_address="0.0.0.0", status="success"):
        """Log an action for audit trail"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, action, resource_type, resource_id, json.dumps(details), ip_address, status))
        
        conn.commit()
        conn.close()

    def log_scan(self, repo_url, branch, issues_data, git_commit="", duration_seconds=0):
        """Log scan completion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scan_history 
            (repository_url, branch, total_issues, critical_issues, high_issues, medium_issues, low_issues, git_commit, duration_seconds, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            repo_url,
            branch,
            issues_data.get('total', 0),
            issues_data.get('critical', 0),
            issues_data.get('high', 0),
            issues_data.get('medium', 0),
            issues_data.get('low', 0),
            git_commit,
            duration_seconds,
            'completed'
        ))
        
        conn.commit()
        conn.close()

    def get_audit_trail(self, limit=100, offset=0):
        """Retrieve audit trail"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_logs
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]

    def get_scan_history(self, repo_url=None, limit=50):
        """Get scan history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if repo_url:
            cursor.execute("""
                SELECT * FROM scan_history
                WHERE repository_url = ?
                ORDER BY scan_date DESC
                LIMIT ?
            """, (repo_url, limit))
        else:
            cursor.execute("""
                SELECT * FROM scan_history
                ORDER BY scan_date DESC
                LIMIT ?
            """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]


class IntegrationManager:
    """Manage integrations with Slack, Teams, Jira, GitHub"""

    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        self.teams_webhook = os.getenv("TEAMS_WEBHOOK_URL", "")
        self.jira_url = os.getenv("JIRA_URL", "")
        self.jira_token = os.getenv("JIRA_TOKEN", "")
        self.github_token = os.getenv("GITHUB_TOKEN", "")

    def send_slack_notification(self, title, message, severity="info", repo_name="", issues_count=0):
        """Send Slack notification"""
        if not self.slack_webhook:
            print("Slack webhook not configured")
            return False

        color_map = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#d97706",
            "low": "#16a34a",
            "info": "#3b82f6"
        }

        payload = {
            "attachments": [
                {
                    "color": color_map.get(severity, "#3b82f6"),
                    "title": f"🔐 {title}",
                    "text": message,
                    "fields": [
                        {"title": "Repository", "value": repo_name, "short": True},
                        {"title": "Issues Found", "value": str(issues_count), "short": True},
                        {"title": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "short": True},
                        {"title": "Severity", "value": severity.upper(), "short": True}
                    ]
                }
            ]
        }

        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack notification failed: {str(e)}")
            return False

    def send_teams_notification(self, title, message, severity="info", repo_name="", issues_count=0):
        """Send Microsoft Teams notification"""
        if not self.teams_webhook:
            print("Teams webhook not configured")
            return False

        color_map = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#d97706",
            "low": "#16a34a",
            "info": "#3b82f6"
        }

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": title,
            "themeColor": color_map.get(severity, "#3b82f6"),
            "title": f"🔐 Move Digital - {title}",
            "sections": [
                {
                    "activityTitle": "Security Alert",
                    "activitySubtitle": message,
                    "facts": [
                        {"name": "Repository", "value": repo_name},
                        {"name": "Issues", "value": str(issues_count)},
                        {"name": "Severity", "value": severity.upper()},
                        {"name": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    ]
                }
            ]
        }

        try:
            response = requests.post(self.teams_webhook, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Teams notification failed: {str(e)}")
            return False

    def create_jira_ticket(self, issue_title, issue_description, severity, repo_name, file_name, line_number):
        """Create Jira ticket for vulnerability"""
        if not self.jira_url or not self.jira_token:
            print("Jira not configured")
            return None

        # Map severity to Jira priority
        priority_map = {
            "CRITICAL": "Highest",
            "HIGH": "High",
            "MEDIUM": "Medium",
            "LOW": "Low"
        }

        payload = {
            "fields": {
                "project": {"key": os.getenv("JIRA_PROJECT_KEY", "SEC")},
                "issuetype": {"name": "Bug"},
                "summary": f"[{severity}] {issue_title} - {repo_name}",
                "description": f"{issue_description}\n\nRepository: {repo_name}\nFile: {file_name}\nLine: {line_number}",
                "priority": {"name": priority_map.get(severity, "Medium")},
                "labels": ["security", "automated-scan", repo_name.lower()]
            }
        }

        try:
            headers = {
                "Authorization": f"Bearer {self.jira_token}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue",
                json=payload,
                headers=headers,
                timeout=10
            )
            if response.status_code == 201:
                return response.json().get("key")
            return None
        except Exception as e:
            print(f"Jira ticket creation failed: {str(e)}")
            return None

    def comment_on_github_pr(self, repo_name, pr_number, comment):
        """Add comment to GitHub PR"""
        if not self.github_token:
            print("GitHub token not configured")
            return False

        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments",
                json={"body": comment},
                headers=headers,
                timeout=10
            )
            return response.status_code == 201
        except Exception as e:
            print(f"GitHub PR comment failed: {str(e)}")
            return False


class ComplianceReporter:
    """Generate compliance reports (PCI-DSS, SOC2, ISO27001, HIPAA)"""

    def __init__(self):
        self.standards = {
            "pci-dss": {
                "name": "PCI-DSS v3.2.1",
                "requirements": {
                    "6.2": "Security vulnerability scanning",
                    "6.3.1": "Remove custom code vulnerabilities",
                    "6.5.1": "Injection attacks",
                    "6.5.10": "Broken authentication"
                }
            },
            "soc2": {
                "name": "SOC 2 Type II",
                "requirements": {
                    "CC7.2": "Monitor systems and information",
                    "CC9.1": "Identify, analyze, manage IT related risks"
                }
            },
            "iso27001": {
                "name": "ISO/IEC 27001:2022",
                "requirements": {
                    "8.2.4": "Removal of access rights",
                    "8.3.4": "Password management"
                }
            },
            "hipaa": {
                "name": "HIPAA Security Rule",
                "requirements": {
                    "164.308(a)(5)": "Security awareness",
                    "164.312(b)": "Audit controls"
                }
            }
        }

    def generate_compliance_report(self, scan_data, standard="pci-dss"):
        """Generate compliance report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "standard": self.standards.get(standard, {}),
            "overall_compliance": self._calculate_compliance(scan_data),
            "issues_by_requirement": self._map_issues_to_requirements(scan_data, standard),
            "recommendations": self._generate_recommendations(scan_data, standard),
            "evidence": {
                "scan_date": datetime.now().isoformat(),
                "repositories_scanned": scan_data.get("repositories", []),
                "total_issues": scan_data.get("total_issues", 0),
                "critical_issues": scan_data.get("critical_issues", 0)
            }
        }
        return report

    def _calculate_compliance(self, scan_data):
        """Calculate compliance score"""
        total_issues = scan_data.get("total_issues", 1)
        critical = scan_data.get("critical_issues", 0)
        high = scan_data.get("high_issues", 0)

        # Weighted scoring: Critical=5 points, High=3 points
        penalty = (critical * 5) + (high * 3)
        compliance_score = max(0, 100 - (penalty * 5))

        return {
            "score": compliance_score,
            "status": "Compliant" if compliance_score >= 80 else "Non-Compliant",
            "details": f"{compliance_score}% compliance"
        }

    def _map_issues_to_requirements(self, scan_data, standard):
        """Map issues to compliance requirements"""
        return {
            "security_vulnerabilities": scan_data.get("security_issues", 0),
            "code_quality": scan_data.get("quality_issues", 0),
            "dependency_risks": scan_data.get("dependency_issues", 0)
        }

    def _generate_recommendations(self, scan_data, standard):
        """Generate compliance recommendations"""
        recommendations = []

        if scan_data.get("security_issues", 0) > 0:
            recommendations.append(
                f"Address {scan_data['security_issues']} security vulnerabilities to maintain {standard.upper()} compliance"
            )

        if scan_data.get("critical_issues", 0) > 0:
            recommendations.append(
                "Immediately remediate critical issues to prevent compliance violations"
            )

        return recommendations


class AutomatedScanOrchestrator:
    """Orchestrate automated scanning across all repositories"""

    def __init__(self):
        self.audit_logger = AuditLogger()
        self.integrations = IntegrationManager()
        self.compliance = ComplianceReporter()
        self.scanner = GitHubScanner()

    def scan_and_notify(self, repo_url, branch="main", notify_channels=None):
        """Scan repo and send notifications"""
        if notify_channels is None:
            notify_channels = ["slack", "teams"]

        start_time = datetime.now()
        
        try:
            # Run scan
            scan_result = self.scanner.generate_report(repo_url, branch)
            
            # Calculate metrics
            total_issues = scan_result.get("summary", {}).get("total_issues", 0)
            critical = scan_result.get("summary", {}).get("critical_issues", 0)
            repo_name = repo_url.split("/")[-1]
            
            # Log scan
            duration = (datetime.now() - start_time).total_seconds()
            self.audit_logger.log_scan(repo_url, branch, {
                "total": total_issues,
                "critical": critical,
                "high": scan_result.get("summary", {}).get("high_issues", 0),
                "medium": scan_result.get("summary", {}).get("medium_issues", 0),
                "low": scan_result.get("summary", {}).get("low_issues", 0)
            }, duration_seconds=int(duration))
            
            # Log action
            self.audit_logger.log_action(
                "scan_completed",
                "repository",
                repo_url,
                {"issues": total_issues, "critical": critical}
            )
            
            # Determine severity
            if critical > 0:
                severity = "critical"
            elif scan_result.get("summary", {}).get("high_issues", 0) > 0:
                severity = "high"
            else:
                severity = "medium"
            
            # Send notifications
            if "slack" in notify_channels:
                self.integrations.send_slack_notification(
                    f"Security Scan: {repo_name}",
                    f"Scan completed with {total_issues} issues found",
                    severity=severity,
                    repo_name=repo_name,
                    issues_count=total_issues
                )
            
            if "teams" in notify_channels:
                self.integrations.send_teams_notification(
                    f"Security Scan: {repo_name}",
                    f"Scan completed with {total_issues} issues found",
                    severity=severity,
                    repo_name=repo_name,
                    issues_count=total_issues
                )
            
            # Create Jira tickets for critical issues
            security_issues = scan_result.get("security_findings", {}).get("issues", [])
            for issue in security_issues[:5]:  # Limit to 5
                if issue.get("severity", "").upper() == "CRITICAL":
                    self.integrations.create_jira_ticket(
                        issue.get("description", "Security Issue"),
                        issue.get("remediation", "Fix required"),
                        issue.get("severity", "HIGH"),
                        repo_name,
                        issue.get("file", "unknown"),
                        issue.get("line", "N/A")
                    )
            
            return {
                "status": "success",
                "issues": total_issues,
                "critical": critical,
                "scan_time": f"{duration:.2f}s"
            }
            
        except Exception as e:
            self.audit_logger.log_action(
                "scan_failed",
                "repository",
                repo_url,
                {"error": str(e)},
                status="error"
            )
            return {"status": "error", "error": str(e)}
