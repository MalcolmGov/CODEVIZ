import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
from psycopg2.extras import RealDictCursor
import schedule
import threading
import time
from github_scanner import GitHubScanner


class ReportGenerator:
    """Generate comprehensive security reports"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.db_url = os.getenv("DATABASE_URL", "")

    def generate_comprehensive_report(self, scan_report, repo_url, branch):
        """Generate detailed comprehensive report"""
        summary = scan_report.get("summary", {})
        scans = scan_report.get("scans", {})
        stats = scans.get("stats", {})
        security = scans.get("security", {})
        quality = scans.get("quality", {})
        dependencies = scans.get("dependencies", {})

        risk_level = summary.get("risk_level", "unknown").upper()
        total_issues = summary.get("total_issues", 0)

        # Generate recommendations based on findings
        recommendations = self._generate_recommendations(summary, scans)

        report = {
            "repository": repo_url,
            "branch": branch,
            "generated_at": datetime.now().isoformat(),
            "executive_summary": {
                "risk_level": risk_level,
                "total_issues": total_issues,
                "security_issues": summary.get("security_issues", 0),
                "quality_issues": summary.get("quality_issues", 0),
                "dependency_issues": summary.get("dependency_issues", 0),
            },
            "repository_statistics": {
                "total_files": stats.get("total_files", 0),
                "python_files": stats.get("python_files", 0),
                "javascript_files": stats.get("javascript_files", 0),
                "test_files": stats.get("test_files", 0),
                "largest_files": stats.get("largest_files", []),
            },
            "security_findings": {
                "status": security.get("status", "unknown"),
                "issues_count": len(security.get("issues", [])),
                "top_issues": security.get("issues", [])[:5],
            },
            "code_quality": {
                "status": quality.get("status", "unknown"),
                "issues_count": len(quality.get("issues", [])),
                "top_issues": quality.get("issues", [])[:5],
            },
            "dependencies": {
                "status": dependencies.get("status", "unknown"),
                "issues_count": len(dependencies.get("issues", [])),
                "issues": dependencies.get("issues", [])[:10],
            },
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(summary, recommendations),
        }

        return report

    def _generate_recommendations(self, summary, scans):
        """Generate actionable recommendations"""
        recommendations = []
        total = summary.get("total_issues", 0)
        security_issues = summary.get("security_issues", 0)
        quality_issues = summary.get("quality_issues", 0)

        if security_issues > 0:
            recommendations.append({
                "priority": "HIGH",
                "category": "Security",
                "recommendation": f"Address {security_issues} security issues immediately",
                "action": "Review security findings and apply patches",
            })

        if quality_issues > 10:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Code Quality",
                "recommendation": f"Refactor code to reduce {quality_issues} quality issues",
                "action": "Consider using automated code formatting and linting",
            })

        if total == 0:
            recommendations.append({
                "priority": "INFO",
                "category": "Status",
                "recommendation": "Repository is in good shape",
                "action": "Maintain current practices and schedule regular scans",
            })

        recommendations.append({
            "priority": "LOW",
            "category": "Testing",
            "recommendation": "Increase test coverage",
            "action": "Add more unit and integration tests",
        })

        return recommendations

    def _generate_next_steps(self, summary, recommendations):
        """Generate next steps"""
        risk_level = summary.get("risk_level", "low")

        if risk_level == "critical":
            return [
                "1. Conduct immediate security review",
                "2. Create incident response plan",
                "3. Schedule emergency patch deployment",
                "4. Notify security team",
            ]
        elif risk_level == "high":
            return [
                "1. Schedule security audit",
                "2. Create action plan for critical issues",
                "3. Set timeline for remediation",
                "4. Implement preventive measures",
            ]
        else:
            return [
                "1. Schedule regular scans (weekly/monthly)",
                "2. Implement automated CI/CD security checks",
                "3. Keep dependencies updated",
                "4. Monitor for new vulnerabilities",
            ]

    def send_report_email(self, recipient_email, report, repo_url):
        """Send comprehensive report via email"""
        if not self.sender_email or not self.sender_password:
            raise Exception("Email configuration not set. Set SENDER_EMAIL and SENDER_PASSWORD env vars")

        html_content = self._generate_html_report(report, repo_url)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Security Report: {repo_url} - {report['executive_summary']['risk_level']} Risk"
        msg["From"] = self.sender_email
        msg["To"] = recipient_email

        text_part = MIMEText("Please view this email in HTML format", "plain")
        html_part = MIMEText(html_content, "html")

        msg.attach(text_part)
        msg.attach(html_part)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise

    def _generate_html_report(self, report, repo_url):
        """Generate HTML formatted report"""
        risk_color = self._get_risk_color(report["executive_summary"]["risk_level"])

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; max-width: 900px; margin: 0 auto; }}
                .header {{ text-align: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #333; margin: 0; }}
                .header p {{ color: #666; margin: 5px 0; }}
                .risk-badge {{ display: inline-block; padding: 10px 20px; border-radius: 6px; color: white; font-weight: bold; background: {risk_color}; }}
                .section {{ margin-bottom: 30px; }}
                .section-title {{ font-size: 18px; font-weight: bold; color: #333; border-left: 4px solid #667eea; padding-left: 15px; margin-bottom: 15px; }}
                .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }}
                .stat-box {{ background: #f9f9f9; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; }}
                .stat-label {{ font-size: 12px; color: #999; text-transform: uppercase; }}
                .stat-value {{ font-size: 28px; font-weight: bold; color: #333; }}
                .recommendation {{ background: #f0f8ff; padding: 15px; border-left: 4px solid #2196F3; margin-bottom: 10px; border-radius: 4px; }}
                .priority-high {{ border-left-color: #f44336; }}
                .priority-medium {{ border-left-color: #ff9800; }}
                .priority-low {{ border-left-color: #4caf50; }}
                .recommendation-title {{ font-weight: bold; color: #333; }}
                .recommendation-action {{ font-size: 13px; color: #666; margin-top: 5px; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; padding-top: 20px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 Security Report</h1>
                    <p>{repo_url}</p>
                    <p>Generated: {report['generated_at']}</p>
                    <div class="risk-badge">{report['executive_summary']['risk_level']} RISK</div>
                </div>

                <div class="section">
                    <div class="section-title">Executive Summary</div>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-label">Total Issues</div>
                            <div class="stat-value">{report['executive_summary']['total_issues']}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Security Issues</div>
                            <div class="stat-value">{report['executive_summary']['security_issues']}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Quality Issues</div>
                            <div class="stat-value">{report['executive_summary']['quality_issues']}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Dependency Issues</div>
                            <div class="stat-value">{report['executive_summary']['dependency_issues']}</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Repository Statistics</div>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-label">Total Files</div>
                            <div class="stat-value">{report['repository_statistics']['total_files']}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Python Files</div>
                            <div class="stat-value">{report['repository_statistics']['python_files']}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Test Files</div>
                            <div class="stat-value">{report['repository_statistics']['test_files']}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">JavaScript Files</div>
                            <div class="stat-value">{report['repository_statistics']['javascript_files']}</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Recommendations</div>
                    {''.join([f'''
                    <div class="recommendation priority-{r['priority'].lower()}">
                        <div class="recommendation-title">{r['category']}: {r['recommendation']}</div>
                        <div class="recommendation-action">Action: {r['action']}</div>
                    </div>
                    ''' for r in report['recommendations']])}
                </div>

                <div class="section">
                    <div class="section-title">Next Steps</div>
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 6px;">
                        {'<br>'.join(report['next_steps'])}
                    </div>
                </div>

                <div class="footer">
                    <p>This report was automatically generated by the GitHub Security Scanner.</p>
                    <p>Schedule: Daily • Report Type: Comprehensive Security Analysis</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _get_risk_color(self, risk_level):
        """Get color for risk level"""
        colors = {
            "CRITICAL": "#f44336",
            "HIGH": "#ff9800",
            "MEDIUM": "#ffc107",
            "LOW": "#4caf50",
        }
        return colors.get(risk_level.upper(), "#999")

    def save_report_to_db(self, report, repo_url, email):
        """Save report to PostgreSQL"""
        if not self.db_url:
            return False

        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_reports (
                    id SERIAL PRIMARY KEY,
                    repository VARCHAR(255),
                    email VARCHAR(255),
                    report JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                INSERT INTO security_reports (repository, email, report)
                VALUES (%s, %s, %s)
            """, (repo_url, email, json.dumps(report)))

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Failed to save report to DB: {str(e)}")
            return False


class ScheduledReportService:
    """Handle scheduled report generation and sending"""

    def __init__(self):
        self.scheduled_jobs = {}
        self.scheduler_thread = None

    def schedule_daily_report(self, repo_url, email, hour=9, minute=0):
        """Schedule a daily report"""
        job_id = f"{repo_url}:{email}"
        self.scheduled_jobs[job_id] = {
            "repo_url": repo_url,
            "email": email,
            "hour": hour,
            "minute": minute,
            "next_run": None,
        }

        schedule_time = f"{hour:02d}:{minute:02d}"
        schedule.every().day.at(schedule_time).do(
            self._run_scheduled_report,
            repo_url=repo_url,
            email=email,
        )

        return job_id

    def _run_scheduled_report(self, repo_url, email):
        """Run scheduled report"""
        try:
            scanner = GitHubScanner()
            scan_report = scanner.generate_report(repo_url)

            generator = ReportGenerator()
            comprehensive_report = generator.generate_comprehensive_report(scan_report, repo_url, "main")
            generator.send_report_email(email, comprehensive_report, repo_url)
            generator.save_report_to_db(comprehensive_report, repo_url, email)

            print(f"Scheduled report sent to {email} for {repo_url}")
        except Exception as e:
            print(f"Failed to run scheduled report: {str(e)}")

    def start_scheduler(self):
        """Start the scheduler thread"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def get_scheduled_reports(self):
        """Get all scheduled reports"""
        return list(self.scheduled_jobs.values())
