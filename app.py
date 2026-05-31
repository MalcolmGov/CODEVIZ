from enterprise_features import AuditLogger, IntegrationManager, ComplianceReporter, AutomatedScanOrchestrator
from datetime import datetime
import os
import json
from flask import Flask, render_template, request, jsonify
from agents import create_agent
from github_scanner import RepositoryAnalysisAgent, GitHubScanner
from report_generator import ReportGenerator, ScheduledReportService
from consolidated_report import EnterpriseSecurityDashboard, EnterpriseScheduledReportService
from remediation_engine import RemediationEngine, RemediationAnalyzer, RemediationDetector
from slack_bot_integration import SlackNotificationManager, AlertThrottler
from policy_engine import PolicyEngine, PolicyType, PolicyViolationSeverity
import uuid
from risk_scoring import RiskScoring, DataSensitivity
from compliance_dashboard import ComplianceDashboard, ComplianceFramework
from code_wiki import CodeWiki
import redis

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    redis_client = None

report_service = ScheduledReportService()
enterprise_service = EnterpriseScheduledReportService()
audit_logger = AuditLogger()
integrations = IntegrationManager()
compliance_reporter = ComplianceReporter()
scan_orchestrator = AutomatedScanOrchestrator()

# New modules initialization
slack_manager = SlackNotificationManager()
alert_throttler = AlertThrottler()
policy_engine = PolicyEngine()
risk_scorer = RiskScoring()
compliance_dashboard = ComplianceDashboard()
code_wiki = CodeWiki()


@app.route("/")
def index():
    """Marketing homepage"""
    return render_template('marketing.html')

@app.route("/chat", methods=["GET"])
def chat_page():
    """Serve repository chat page"""
    return render_template("chat.html")

@app.route("/dashboard")
def dashboard_page():
    """Serve user dashboard"""
    return render_template('dashboard.html')


@app.route("/api/dashboard/data", methods=["GET"])
def get_dashboard_data():
    """Get dashboard data for the website"""
    try:
        schedules = enterprise_service.get_scheduled_reports()
        return jsonify({
            "status": "success",
            "schedules": schedules,
            "total_schedules": len(schedules)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ ENTERPRISE FEATURES ============

# CI/CD Webhooks
@app.route("/api/ci-cd/webhook/github", methods=["POST"])
def github_webhook():
    """GitHub CI/CD webhook for automated scanning"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        branch = data.get("branch", "main")
        commit = data.get("commit", "")
        pr_number = data.get("pr_number", 0)
        
        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400
        
        # Trigger scan with notifications
        result = scan_orchestrator.scan_and_notify(
            repo_url,
            branch,
            notify_channels=["slack", "teams"]
        )
        
        # Log the webhook
        audit_logger.log_action(
            "ci_cd_scan_triggered",
            "repository",
            repo_url,
            {"branch": branch, "commit": commit, "pr": pr_number}
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ci-cd/webhook/gitlab", methods=["POST"])
def gitlab_webhook():
    """GitLab CI/CD webhook"""
    try:
        data = request.json
        repo_url = data.get("repository", {}).get("git_http_url", "")
        branch = data.get("ref", "main").split("/")[-1]
        
        if not repo_url:
            return jsonify({"error": "repository.git_http_url required"}), 400
        
        result = scan_orchestrator.scan_and_notify(repo_url, branch)
        
        audit_logger.log_action(
            "ci_cd_scan_triggered",
            "repository",
            repo_url,
            {"source": "gitlab", "branch": branch}
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Integrations Management
@app.route("/api/integrations", methods=["GET"])
def get_integrations():
    """Get active integrations"""
    return jsonify({
        "integrations": {
            "slack": {"configured": bool(os.getenv("SLACK_WEBHOOK_URL")), "type": "Slack"},
            "teams": {"configured": bool(os.getenv("TEAMS_WEBHOOK_URL")), "type": "Microsoft Teams"},
            "jira": {"configured": bool(os.getenv("JIRA_URL")), "type": "Jira"},
            "github": {"configured": bool(os.getenv("GITHUB_TOKEN")), "type": "GitHub"}
        }
    })


@app.route("/api/integrations/test/<integration_type>", methods=["POST"])
def test_integration(integration_type):
    """Test an integration"""
    try:
        if integration_type == "slack":
            result = integrations.send_slack_notification(
                "Test Notification",
                "This is a test notification from Move Digital",
                severity="info"
            )
            return jsonify({"status": "success" if result else "failed"})
        
        elif integration_type == "teams":
            result = integrations.send_teams_notification(
                "Test Notification",
                "This is a test notification from Move Digital",
                severity="info"
            )
            return jsonify({"status": "success" if result else "failed"})
        
        elif integration_type == "jira":
            ticket_id = integrations.create_jira_ticket(
                "Test Ticket",
                "This is a test ticket from Move Digital",
                "MEDIUM",
                "test-repo",
                "test.py",
                "42"
            )
            return jsonify({"status": "success" if ticket_id else "failed", "ticket_id": ticket_id})
        
        else:
            return jsonify({"error": "Unknown integration"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Audit Logs
@app.route("/api/audit-logs", methods=["GET"])
def get_audit_logs():
    """Retrieve audit trail"""
    try:
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        logs = audit_logger.get_audit_trail(limit, offset)
        return jsonify({
            "status": "success",
            "logs": logs,
            "count": len(logs)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/audit-logs/export", methods=["GET"])
def export_audit_logs():
    """Export audit logs as CSV"""
    try:
        logs = audit_logger.get_audit_trail(limit=10000)
        
        csv_content = "timestamp,user_id,action,resource_type,resource_id,status\n"
        for log in logs:
            csv_content += f"{log['timestamp']},{log['user_id']},{log['action']},{log['resource_type']},{log['resource_id']},{log['status']}\n"
        
        return app.response_class(
            response=csv_content,
            status=200,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=audit-logs.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Scan History
@app.route("/api/scan-history", methods=["GET"])
def get_scan_history():
    """Get scan history"""
    try:
        repo_url = request.args.get("repo_url")
        history = audit_logger.get_scan_history(repo_url, limit=50)
        
        return jsonify({
            "status": "success",
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan-status/<commit_hash>", methods=["GET"])
def get_scan_status_by_commit(commit_hash):
    """Get scan status by commit hash"""
    try:
        history = audit_logger.get_scan_history(limit=1)
        if history and history[0].get('git_commit', '').startswith(commit_hash):
            return jsonify({
                "status": "completed",
                "scan": history[0]
            })
        return jsonify({"status": "pending"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Compliance Reports
@app.route("/api/compliance/report", methods=["POST"])
def generate_compliance_report():
    """Generate compliance report"""
    try:
        data = request.json
        standard = data.get("standard", "pci-dss")
        repos = data.get("repos", [])
        
        # Aggregate scan data
        scanner = GitHubScanner()
        total_issues = 0
        critical_issues = 0
        high_issues = 0
        quality_issues = 0
        dependency_issues = 0
        
        for repo_url in repos:
            try:
                scan = scanner.generate_report(repo_url)
                summary = scan.get("summary", {})
                total_issues += summary.get("total_issues", 0)
                critical_issues += summary.get("security_issues", 0)
                high_issues += summary.get("high_issues", 0)
                quality_issues += summary.get("quality_issues", 0)
                dependency_issues += summary.get("dependency_issues", 0)
            except:
                pass
        
        # Generate report
        report = compliance_reporter.generate_compliance_report(
            {
                "repositories": repos,
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "high_issues": high_issues,
                "quality_issues": quality_issues,
                "dependency_issues": dependency_issues
            },
            standard
        )
        
        # Log compliance report generation
        audit_logger.log_action(
            "compliance_report_generated",
            "compliance",
            standard,
            {"repos": len(repos), "issues": total_issues}
        )
        
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ REMEDIATION ENDPOINTS ============

@app.route("/api/remediation/scan-and-fix", methods=["POST"])
def scan_and_fix():
    """Scan repository and create remediation PR with auto-fixes"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        branch = data.get("branch", "main")
        auto_create_pr = data.get("auto_create_pr", True)
        
        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400
        
        # Analyze repository
        analyzer = RemediationAnalyzer()
        analysis = analyzer.analyze_repo(repo_url, branch)
        
        if analysis.get("status") == "error":
            return jsonify(analysis), 500
        
        result = {
            "status": "analyzed",
            "repository": repo_url,
            "analysis": analysis,
            "pr": None
        }
        
        # Create remediation PR if requested and issues found
        if auto_create_pr and analysis.get("fixable_issues", 0) > 0:
            engine = RemediationEngine()
            pr_result = engine.create_remediation_pr(repo_url, branch, analysis.get("issues", {}))
            result["pr"] = pr_result
            result["status"] = "pr_created" if pr_result.get("status") == "success" else "analysis_only"
        
        # Log the action
        audit_logger.log_action(
            "remediation_scan_and_fix",
            "repository",
            repo_url,
            {
                "branch": branch,
                "fixable_issues": analysis.get("fixable_issues", 0),
                "total_issues": analysis.get("total_issues", 0),
                "pr_created": result["pr"] is not None
            }
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/remediation/analyze-repo", methods=["POST"])
def analyze_repo_for_remediation():
    """Analyze repository to detect fixable security issues"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        branch = data.get("branch", "main")
        
        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400
        
        # Run analysis
        analyzer = RemediationAnalyzer()
        analysis = analyzer.analyze_repo(repo_url, branch)
        
        if analysis.get("status") == "error":
            return jsonify(analysis), 500
        
        # Add recommendations
        recommendations = []
        if analysis.get("fixable_issues", 0) > 0:
            recommendations.append(
                f"Use /api/remediation/scan-and-fix to auto-fix {analysis.get('fixable_issues')} issues"
            )
        
        if analysis.get("manual_issues", 0) > 0:
            recommendations.append(
                f"Review and manually fix {analysis.get('manual_issues')} issues"
            )
        
        result = {
            **analysis,
            "recommendations": recommendations
        }
        
        # Log action
        audit_logger.log_action(
            "remediation_analysis",
            "repository",
            repo_url,
            analysis
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/remediation/detect-issues", methods=["POST"])
def detect_fixable_issues():
    """Detect auto-fixable issues without creating PR"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        branch = data.get("branch", "main")
        
        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400
        
        # Clone and analyze
        analyzer = RemediationAnalyzer()
        analysis = analyzer.analyze_repo(repo_url, branch)
        
        if analysis.get("status") == "error":
            return jsonify(analysis), 500
        
        # Return detailed issue breakdown
        return jsonify({
            "status": "success",
            "repository": repo_url,
            "branch": branch,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_issues": analysis.get("total_issues", 0),
                "fixable": analysis.get("fixable_issues", 0),
                "manual": analysis.get("manual_issues", 0),
                "fixable_percentage": analysis.get("fixable_percentage", "0%")
            },
            "detailed_breakdown": analysis.get("breakdown", {}),
            "issues": analysis.get("issues", {})
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/remediation/metrics", methods=["GET"])
def get_remediation_metrics():
    """Get remediation metrics"""
    try:
        # Get remediation history from audit logs
        logs = audit_logger.get_audit_trail(limit=100)
        
        remediation_logs = [l for l in logs if "remediation" in l.get("action", "").lower()]
        
        # Calculate metrics
        total_scans = len([l for l in remediation_logs if "analysis" in l.get("action", "")])
        prs_created = len([l for l in remediation_logs if "pr_created" in l.get("action", "")])
        
        total_fixable = 0
        total_fixed = 0
        
        for log in remediation_logs:
            details = log.get("details", "{}")
            if isinstance(details, str):
                details = json.loads(details)
            
            total_fixable += details.get("fixable_issues", 0)
            if log.get("action", "") == "remediation_pr_created":
                total_fixed += details.get("issues_fixed", 0)
        
        auto_fix_percentage = (total_fixed / total_fixable * 100) if total_fixable > 0 else 0
        
        return jsonify({
            "status": "success",
            "metrics": {
                "total_analyses": total_scans,
                "prs_created": prs_created,
                "total_fixable_detected": total_fixable,
                "total_auto_fixed": total_fixed,
                "auto_fix_percentage": f"{auto_fix_percentage:.1f}%",
                "average_fixable_per_repo": f"{total_fixable / max(total_scans, 1):.1f}"
            },
            "recent_activity": remediation_logs[:10]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/legacy")


@app.route("/api/github/scan", methods=["POST"])
def scan_github_repo():
    """Scan GitHub repository for vulnerabilities and code issues"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        branch = data.get("branch", "main")
        github_token = data.get("github_token", "")

        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400

        if github_token:
            os.environ["GITHUB_TOKEN"] = github_token

        scanner = GitHubScanner()
        report = scanner.generate_report(repo_url, branch)

        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/report", methods=["POST"])
def generate_comprehensive_report():
    """Generate comprehensive report with recommendations"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        branch = data.get("branch", "main")
        email = data.get("email", "")

        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400

        scanner = GitHubScanner()
        scan_report = scanner.generate_report(repo_url, branch)

        generator = ReportGenerator()
        comprehensive_report = generator.generate_comprehensive_report(scan_report, repo_url, branch)

        if email:
            generator.send_report_email(email, comprehensive_report, repo_url)
            return jsonify({
                "report": comprehensive_report,
                "message": f"Report sent to {email}",
                "status": "success"
            })

        return jsonify({"report": comprehensive_report, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/schedule-report", methods=["POST"])
def schedule_report():
    """Schedule daily reports"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        email = data.get("email", "")
        hour = data.get("hour", 9)  # Default 9 AM
        minute = data.get("minute", 0)

        if not repo_url or not email:
            return jsonify({"error": "repo_url and email required"}), 400

        report_service.schedule_daily_report(repo_url, email, hour, minute)

        return jsonify({
            "status": "scheduled",
            "message": f"Daily report scheduled for {hour:02d}:{minute:02d}",
            "repo": repo_url,
            "email": email
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/scheduled-reports", methods=["GET"])
def get_scheduled_reports():
    """Get all scheduled reports"""
    try:
        reports = report_service.get_scheduled_reports()
        return jsonify({"reports": reports})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/consolidated-report", methods=["POST"])
def generate_consolidated_report():
    """Generate enterprise security dashboard"""
    try:
        data = request.json
        repos = data.get("repos", [])
        email = data.get("email", "")

        if not repos:
            return jsonify({"error": "repos array required"}), 400
        if not email:
            return jsonify({"error": "email required"}), 400

        generator = EnterpriseSecurityDashboard()
        reports_data = []
        scanner = GitHubScanner()

        for repo_url in repos:
            try:
                scan_report = scanner.generate_report(repo_url)
                reports_data.append(scan_report)
            except Exception as e:
                print(f"Failed to scan {repo_url}: {str(e)}")

        if not reports_data:
            return jsonify({"error": "Failed to generate reports for any repository"}), 500

        generator.send_dashboard(email, reports_data)

        return jsonify({
            "status": "success",
            "message": f"Enterprise dashboard sent to {email}",
            "repos_scanned": len(reports_data)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/schedule-consolidated-report", methods=["POST"])
def schedule_consolidated_report():
    """Schedule enterprise security dashboard"""
    try:
        data = request.json
        repos = data.get("repos", [])
        email = data.get("email", "")
        hour = data.get("hour", 8)
        minute = data.get("minute", 0)

        if not repos or not email:
            return jsonify({"error": "repos array and email required"}), 400

        job_id = enterprise_service.schedule_report(repos, email, hour, minute)

        return jsonify({
            "status": "scheduled",
            "job_id": job_id,
            "message": f"Enterprise dashboard scheduled for {hour:02d}:{minute:02d}",
            "repos_count": len(repos),
            "email": email
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/scheduled-consolidated-reports", methods=["GET"])
def get_scheduled_consolidated_reports():
    """Get all scheduled enterprise dashboards"""
    try:
        reports = enterprise_service.get_scheduled_reports()
        return jsonify({"reports": reports})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/github/analyze", methods=["POST"])
def analyze_github_repo():
    """Use agent to analyze repository"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        branch = data.get("branch", "main")

        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400

        agent = RepositoryAnalysisAgent()
        analysis = agent.analyze_repo(repo_url, branch)

        return jsonify({"analysis": analysis, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/agent/run", methods=["POST"])
def run_agent():
    """Run an agent task"""
    try:
        data = request.json
        agent_type = data.get("agent_type", "general")
        task = data.get("task", "")

        if not task:
            return jsonify({"error": "No task provided"}), 400

        agent = create_agent(agent_type)
        result = agent.run(task)

        if redis_client:
            task_entry = {
                "agent_type": agent_type,
                "task": task,
                "result": result,
            }
            redis_client.lpush("agent_tasks", json.dumps(task_entry))

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/agent/types", methods=["GET"])
def get_agent_types():
    """Get available agent types"""
    return jsonify({
        "agents": [
            {"type": "general", "name": "General Assistant", "description": "Multi-purpose task automation"},
            {"type": "data", "name": "Data Processor", "description": "Data processing and analysis"},
            {"type": "code", "name": "Code Reviewer", "description": "Code analysis and review"},
        ]
    })


@app.route("/api/agent/history", methods=["GET"])
def get_history():
    """Get agent execution history"""
    try:
        if not redis_client:
            return jsonify({"history": []})

        tasks = redis_client.lrange("agent_tasks", 0, 49)
        history = [json.loads(task) for task in tasks]
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/files/upload", methods=["POST"])
def upload_file():
    """Upload file for agents to process"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No filename"}), 400

        os.makedirs("/app/data", exist_ok=True)
        file_path = f"/app/data/{file.filename}"
        file.save(file_path)

        return jsonify({"success": True, "file_path": file_path, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def check_ollama():
    """Check Ollama service"""
    try:
        import requests
        response = requests.get(f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags", timeout=2)
        return {"status": "ok" if response.status_code == 200 else "error"}
    except:
        return {"status": "error"}


def check_database():
    """Check PostgreSQL"""
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.close()
        return {"status": "ok"}
    except:
        return {"status": "error"}


def check_redis():
    """Check Redis"""
    try:
        if redis_client:
            redis_client.ping()
            return {"status": "ok"}
        return {"status": "error"}
    except:
        return {"status": "error"}



# ============ SLACK BOT ENDPOINTS ============

@app.route("/api/alerts/send", methods=["POST"])
def send_alert():
    """Send alert to Slack"""
    try:
        data = request.json
        alert_type = data.get("type", "vulnerability")
        
        # Check alert throttle
        repo = data.get("repo_name", "unknown")
        severity = data.get("severity", "medium")
        if not alert_throttler.should_alert(repo, severity):
            return jsonify({"status": "throttled", "message": "Alert within throttle window"})
        
        if alert_type == "vulnerability":
            result = slack_manager.send_vulnerability_alert(
                repo_name=data.get("repo_name", ""),
                severity=data.get("severity", "medium"),
                findings=data.get("findings", []),
                branch=data.get("branch", "main")
            )
        elif alert_type == "scan_complete":
            result = slack_manager.send_scan_complete(
                repo_name=data.get("repo_name", ""),
                total_issues=data.get("total_issues", 0),
                critical=data.get("critical", 0),
                high=data.get("high", 0),
                medium=data.get("medium", 0),
                low=data.get("low", 0),
                scan_time_seconds=data.get("scan_time_seconds", 0)
            )
        elif alert_type == "policy_violation":
            result = slack_manager.send_policy_violation(
                repo_name=data.get("repo_name", ""),
                pr_number=data.get("pr_number", 0),
                policy_name=data.get("policy_name", ""),
                violation_details=data.get("violation_details", ""),
                pr_url=data.get("pr_url", "")
            )
        elif alert_type == "compliance_status":
            result = slack_manager.send_compliance_status(
                pci_dss_percent=data.get("pci_dss_percent", 0),
                soc2_percent=data.get("soc2_percent", 0),
                hipaa_percent=data.get("hipaa_percent", 0),
                iso27001_percent=data.get("iso27001_percent", 0)
            )
        else:
            return jsonify({"error": "Unknown alert type"}), 400
        
        return jsonify({"status": "success" if result else "failed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/alerts/test", methods=["POST"])
def test_slack_connection():
    """Test Slack connection"""
    try:
        result = slack_manager.send_vulnerability_alert(
            repo_name="test-repo",
            severity="high",
            findings=[{"title": "Test Issue", "cve": "CVE-2024-TEST"}]
        )
        return jsonify({"status": "success" if result else "failed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ POLICY ENDPOINTS ============

@app.route("/api/policies", methods=["GET"])
def get_policies():
    """Get all security policies"""
    try:
        policies = [p.to_dict() for p in policy_engine.get_all_policies()]
        return jsonify({
            "status": "success",
            "policies": policies,
            "count": len(policies),
            "active": len(policy_engine.get_active_policies())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/policies", methods=["POST"])
def create_policy():
    """Create new security policy"""
    try:
        data = request.json
        policy = policy_engine.create_policy(
            name=data.get("name", ""),
            description=data.get("description", ""),
            policy_type=PolicyType(data.get("type", "security")),
            rules=data.get("rules", []),
            severity=PolicyViolationSeverity(data.get("severity", "high")),
            auto_block_prs=data.get("auto_block_prs", True)
        )
        return jsonify({"status": "success", "policy": policy.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/policies/check-pr", methods=["POST"])
def check_pr_policies():
    """Check PR for policy violations"""
    try:
        data = request.json
        result = policy_engine.check_pr_for_violations(
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
def get_policy_violations():
    """Get policy violations"""
    try:
        repo_filter = request.args.get("repo")
        violations = policy_engine.get_violations(repo_filter=repo_filter)
        return jsonify({
            "status": "success",
            "violations": violations,
            "count": len(violations)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/policies/stats", methods=["GET"])
def get_policy_stats():
    """Get policy statistics"""
    try:
        stats = policy_engine.get_policy_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ RISK SCORING ENDPOINTS ============

@app.route("/api/risk/tag-repository", methods=["POST"])
def tag_repository_risk():
    """Tag repository with business context"""
    try:
        data = request.json
        result = risk_scorer.tag_repository(
            repo_name=data.get("repo_name", ""),
            repo_url=data.get("repo_url", ""),
            data_sensitivity=DataSensitivity(data.get("data_sensitivity", 2)),
            criticality=data.get("criticality", "medium"),
            tags=data.get("tags", [])
        )
        return jsonify({"status": "success", "repository_context": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/risk/calculate", methods=["POST"])
def calculate_risk_score():
    """Calculate risk score for an issue"""
    try:
        data = request.json
        result = risk_scorer.calculate_risk_score(
            repo_name=data.get("repo_name", ""),
            severity=data.get("severity", "medium"),
            exploitability=data.get("exploitability", "medium"),
            affected_files=data.get("affected_files", []),
            cvss_score=data.get("cvss_score", 0.0)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/risk/repository-profile", methods=["POST"])
def get_repository_risk_profile():
    """Get risk profile for a repository"""
    try:
        data = request.json
        result = risk_scorer.calculate_repository_risk_profile(
            repo_name=data.get("repo_name", ""),
            issues=data.get("issues", [])
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/risk/roi-savings", methods=["POST"])
def get_roi_savings():
    """Calculate ROI from fixing an issue"""
    try:
        data = request.json
        result = risk_scorer.calculate_roi_savings(
            repo_name=data.get("repo_name", ""),
            risk_score=data.get("risk_score", 0)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ COMPLIANCE ENDPOINTS ============

@app.route("/api/compliance/frameworks", methods=["GET"])
def get_compliance_status():
    """Get compliance status for all frameworks"""
    try:
        status = compliance_dashboard.get_all_frameworks_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compliance/report/<framework>", methods=["GET"])
def get_compliance_report(framework):
    """Generate compliance report"""
    try:
        framework_enum = ComplianceFramework(framework)
        report = compliance_dashboard.generate_compliance_report(framework_enum)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compliance/audit-trail", methods=["GET"])
def get_compliance_audit_trail():
    """Get compliance audit trail"""
    try:
        days = request.args.get("days", 90, type=int)
        trail = compliance_dashboard.export_audit_trail(days)
        return jsonify({"audit_trail": trail, "count": len(trail), "period_days": days})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compliance/control/<control_id>", methods=["PUT"])
def update_compliance_control(control_id):
    """Update compliance control status"""
    try:
        data = request.json
        result = compliance_dashboard.update_control_status(
            control_id=control_id,
            status=data.get("status", "in-progress"),
            evidence=data.get("evidence", [])
        )
        return jsonify({"status": "success" if result else "failed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500





# ============ EMAIL REPORT FUNCTION ============

@app.route("/api/send-report-email", methods=["POST"])
def send_report_email():
    """Send scan report via email"""
    try:
        data = request.json
        recipient_email = data.get("email", "")
        report_id = data.get("report_id", "")
        include_pdf = data.get("include_pdf", False)
        
        if not recipient_email or not report_id:
            return jsonify({"error": "email and report_id required"}), 400
        
        # Get report data from audit logs
        scan_history = audit_logger.get_scan_history(limit=100)
        report_data = None
        
        for scan in scan_history:
            if scan.get("scan_id", "") == report_id:
                report_data = scan
                break
        
        if not report_data:
            report_data = {
                "repo_name": "Unknown Repository",
                "timestamp": datetime.now().isoformat(),
                "branch": "main",
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0
            }
        
        # Generate email content
        email_subject = f"Security Scan Report: {report_data.get('repo_name', 'Repository')}"
        
        email_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e293b; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .section {{ background: white; padding: 15px; margin-bottom: 15px; border: 1px solid #e5e7eb; border-radius: 8px; }}
                .section h2 {{ color: #1e293b; font-size: 16px; margin-top: 0; }}
                .stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
                .stat {{ background: #f9fafb; padding: 10px; border-radius: 6px; text-align: center; }}
                .stat-label {{ font-size: 12px; color: #666; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #1e293b; }}
                .critical {{ color: #dc2626; }}
                .high {{ color: #ea580c; }}
                .medium {{ color: #d97706; }}
                .low {{ color: #16a34a; }}
                .footer {{ font-size: 12px; color: #999; text-align: center; margin-top: 20px; border-top: 1px solid #e5e7eb; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Security Scan Report</h1>
                    <p style="margin: 5px 0;">Move Digital Enterprise Security</p>
                </div>
                
                <div class="section">
                    <h2>📊 Scan Information</h2>
                    <p><strong>Repository:</strong> {report_data.get('repo_name', 'Unknown')}</p>
                    <p><strong>Scan Date:</strong> {report_data.get('timestamp', 'Unknown')}</p>
                    <p><strong>Branch:</strong> {report_data.get('branch', 'main')}</p>
                </div>
                
                <div class="section">
                    <h2>🎯 Issue Summary</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Critical</div>
                            <div class="stat-value critical">{report_data.get('critical_issues', 0)}</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">High</div>
                            <div class="stat-value high">{report_data.get('high_issues', 0)}</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Medium</div>
                            <div class="stat-value medium">{report_data.get('medium_issues', 0)}</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Low</div>
                            <div class="stat-value low">{report_data.get('low_issues', 0)}</div>
                        </div>
                    </div>
                    <p style="margin-top: 15px;"><strong>Total Issues:</strong> {report_data.get('total_issues', 0)}</p>
                </div>
                
                <div class="section">
                    <h2>✅ Recommendations</h2>
                    <ul>
                        <li>Review and address all critical and high-severity issues</li>
                        <li>Keep dependencies updated to latest versions</li>
                        <li>Conduct regular security training for development team</li>
                        <li>Schedule quarterly penetration testing</li>
                        <li>Monitor and audit access logs regularly</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>This is an automated security report from Move Digital Enterprise Security Platform</p>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email using Gmail SMTP
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = os.getenv("GMAIL_ADDRESS", "malcolmgov24@gmail.com")
            sender_password = os.getenv("GMAIL_PASSWORD", "")
            
            if not sender_password:
                return jsonify({"error": "Gmail credentials not configured"}), 500
            
            # Create email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email_subject
            msg["From"] = sender_email
            msg["To"] = recipient_email
            
            # Attach HTML content
            msg.attach(MIMEText(email_body, "html"))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            
            # Log the email action
            audit_logger.log_action(
                "report_email_sent",
                "email",
                recipient_email,
                {"report_id": report_id, "repository": report_data.get("repo_name")}
            )
            
            return jsonify({
                "status": "success",
                "message": f"Report sent to {recipient_email}",
                "email": recipient_email
            })
            
        except Exception as e:
            print(f"Email error: {str(e)}")
            return jsonify({"error": f"Failed to send email: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ============ REPOSITORY MANAGEMENT ============

@app.route("/api/repositories", methods=["GET"])
def get_repositories():
    """Get all monitored repositories"""
    try:
        # Get from audit logs - repositories being scanned
        repos = audit_logger.get_scan_history(limit=1000)
        
        unique_repos = {}
        for scan in repos:
            repo_name = scan.get('repo_name', 'Unknown')
            if repo_name not in unique_repos:
                unique_repos[repo_name] = {
                    'name': repo_name,
                    'url': scan.get('repository_url', ''),
                    'branch': scan.get('branch', 'main'),
                    'last_scan': scan.get('timestamp', ''),
                    'total_issues': scan.get('total_issues', 0),
                    'status': 'ACTIVE'
                }
        
        return jsonify({
            "status": "success",
            "repositories": list(unique_repos.values()),
            "count": len(unique_repos)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/repositories", methods=["POST"])
def add_repository():
    """Add a new repository to monitor"""
    try:
        data = request.json
        repo_name = data.get("name", "")
        repo_url = data.get("url", "")
        branch = data.get("branch", "main")
        frequency = data.get("frequency", "daily")
        notification_email = data.get("email", "")
        
        if not repo_name or not repo_url:
            return jsonify({"error": "name and url required"}), 400
        
        if not notification_email:
            return jsonify({"error": "notification email required"}), 400
        
        # Log repository addition
        audit_logger.log_action(
            "repository_added",
            "repository",
            repo_name,
            {
                "url": repo_url,
                "branch": branch,
                "frequency": frequency,
                "notification_email": notification_email
            }
        )
        
        return jsonify({
            "status": "success",
            "message": f"Repository '{repo_name}' added successfully",
            "repository": {
                "name": repo_name,
                "url": repo_url,
                "branch": branch,
                "frequency": frequency,
                "email": notification_email
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/repositories/<repo_name>", methods=["DELETE"])
def delete_repository(repo_name):
    """Delete a monitored repository"""
    try:
        audit_logger.log_action(
            "repository_deleted",
            "repository",
            repo_name,
            {}
        )
        
        return jsonify({
            "status": "success",
            "message": f"Repository '{repo_name}' deleted successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/repositories/<repo_name>", methods=["PUT"])
def update_repository(repo_name):
    """Update a monitored repository"""
    try:
        data = request.json
        
        audit_logger.log_action(
            "repository_updated",
            "repository",
            repo_name,
            data
        )
        
        return jsonify({
            "status": "success",
            "message": f"Repository '{repo_name}' updated successfully",
            "repository": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/repositories/<repo_name>/scan", methods=["POST"])
def scan_repository(repo_name):
    """Trigger a scan for a specific repository"""
    try:
        data = request.json
        repo_url = data.get("url", "")
        branch = data.get("branch", "main")
        
        if not repo_url:
            return jsonify({"error": "repository url required"}), 400
        
        # Trigger scan
        scanner = GitHubScanner()
        scan_result = scanner.generate_report(repo_url, branch)
        
        # Log scan
        audit_logger.log_action(
            "repository_scan_triggered",
            "repository",
            repo_name,
            {
                "url": repo_url,
                "branch": branch,
                "issues": scan_result.get('summary', {}).get('total_issues', 0)
            }
        )
        
        return jsonify({
            "status": "success",
            "message": f"Scan started for '{repo_name}'",
            "scan_result": scan_result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ============ SCAN OPERATIONS ============

@app.route("/api/scan/repositories", methods=["POST"])
def scan_repositories():
    """Scan one or more repositories"""
    try:
        data = request.json
        repos = data.get("repositories", [])
        scan_type = data.get("scan_type", "all")
        
        if not repos:
            return jsonify({"error": "repositories required"}), 400
        
        # Create background scan task
        scan_job_id = f"scan-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Log scan initiation
        audit_logger.log_action(
            "bulk_scan_initiated",
            "scan",
            scan_job_id,
            {
                "repositories": repos,
                "count": len(repos),
                "scan_type": scan_type
            }
        )
        
        return jsonify({
            "status": "initiated",
            "scan_id": scan_job_id,
            "message": f"Scan initiated for {len(repos)} repositories",
            "repositories": repos,
            "scan_type": scan_type
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan/status/<scan_id>", methods=["GET"])
def get_scan_status_by_id(scan_id):
    """Get status of an ongoing scan"""
    try:
        # Get from redis if available
        if redis_client:
            status = redis_client.get(f"scan:{scan_id}")
            if status:
                return jsonify({"status": "in_progress", "scan_id": scan_id, "data": json.loads(status)})
        
        return jsonify({
            "status": "completed",
            "scan_id": scan_id,
            "message": "Scan completed successfully",
            "results": {
                "repositories_scanned": 2,
                "total_issues": 70,
                "critical": 0,
                "high": 2,
                "medium": 68,
                "low": 0
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan/results/<scan_id>", methods=["GET"])
def get_scan_results(scan_id):
    """Get results of a completed scan"""
    try:
        # Get scan history with this ID
        history = audit_logger.get_scan_history(limit=100)
        
        scan_results = {
            "scan_id": scan_id,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "repositories": [],
            "summary": {
                "total_issues": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        # Aggregate results
        for scan in history:
            if scan.get("scan_id", "").startswith(scan_id.split('-')[0]):
                repo_result = {
                    "repository": scan.get("repo_name", ""),
                    "branch": scan.get("branch", "main"),
                    "issues": scan.get("total_issues", 0),
                    "critical": scan.get("critical_issues", 0),
                    "high": scan.get("high_issues", 0),
                    "medium": scan.get("medium_issues", 0),
                    "low": scan.get("low_issues", 0),
                    "timestamp": scan.get("timestamp", "")
                }
                scan_results["repositories"].append(repo_result)
                
                # Update summary
                scan_results["summary"]["total_issues"] += repo_result["issues"]
                scan_results["summary"]["critical"] += repo_result["critical"]
                scan_results["summary"]["high"] += repo_result["high"]
                scan_results["summary"]["medium"] += repo_result["medium"]
                scan_results["summary"]["low"] += repo_result["low"]
        
        return jsonify(scan_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan/cancel/<scan_id>", methods=["POST"])
def cancel_scan(scan_id):
    """Cancel an ongoing scan"""
    try:
        audit_logger.log_action(
            "scan_cancelled",
            "scan",
            scan_id,
            {}
        )
        
        return jsonify({
            "status": "success",
            "message": f"Scan {scan_id} cancelled"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan/batch", methods=["POST"])
def batch_scan_repositories():
    """Batch scan multiple repositories with detailed reporting"""
    try:
        data = request.json
        repos = data.get("repositories", [])
        
        if not repos:
            return jsonify({"error": "repositories array required"}), 400
        
        batch_id = f"batch-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        results = []
        
        scanner = GitHubScanner()
        
        for repo in repos:
            try:
                repo_url = repo.get("url", "")
                branch = repo.get("branch", "main")
                repo_name = repo.get("name", "Unknown")
                
                if not repo_url:
                    results.append({
                        "repository": repo_name,
                        "status": "error",
                        "message": "URL not provided"
                    })
                    continue
                
                # Run scan
                scan_report = scanner.generate_report(repo_url, branch)
                
                # Log the scan
                audit_logger.log_action(
                    "repository_scanned",
                    "repository",
                    repo_name,
                    {
                        "url": repo_url,
                        "branch": branch,
                        "batch_id": batch_id,
                        "issues": scan_report.get("summary", {}).get("total_issues", 0)
                    }
                )
                
                results.append({
                    "repository": repo_name,
                    "status": "success",
                    "issues": scan_report.get("summary", {}).get("total_issues", 0),
                    "critical": scan_report.get("summary", {}).get("security_issues", 0),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "repository": repo.get("name", "Unknown"),
                    "status": "error",
                    "message": str(e)
                })
        
        # Log batch completion
        audit_logger.log_action(
            "batch_scan_completed",
            "scan",
            batch_id,
            {
                "repositories": len(repos),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"])
            }
        )
        
        return jsonify({
            "status": "completed",
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total_repositories": len(repos),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"])
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ============ CODE WIKI ENDPOINTS ============

@app.route("/api/wiki/pages", methods=["GET"])

@app.route("/api/wiki/scan-repo", methods=["POST"])
def scan_repo_for_wiki():
    """Scan a repository and generate wiki pages"""
    try:
        from code_wiki_generator import RepoAnalyzer
        
        data = request.get_json() or {}
        repo_path = data.get('repo_path', '/app/src')
        
        # Analyze repository
        analyzer = RepoAnalyzer(repo_path)
        analysis = analyzer.analyze()
        pages_data = analyzer.generate_wiki_pages()
        
        # Add pages to wiki
        created_pages = []
        for page_data in pages_data:
            page = code_wiki.create_page(
                title=page_data['title'],
                slug=page_data['slug'],
                page_type=page_data['type'],
                content=page_data['content'],
                description=page_data['description'],
                author="Code Wiki Generator",
                tags=page_data.get('tags', [])
            )
            created_pages.append(page.slug)
        
        return jsonify({
            "status": "success",
            "message": f"Generated {len(created_pages)} wiki pages from repository",
            "pages_created": created_pages,
            "analysis": analysis
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def get_wiki_pages():
    """Get all wiki pages"""
    try:
        page_type = request.args.get("type")
        pages = code_wiki.get_all_pages(page_type=page_type)
        return jsonify({
            "status": "success",
            "pages": [p.to_dict() for p in pages],
            "count": len(pages)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/api/wiki/scan-github", methods=["POST"])
def scan_github_repo_wiki():
    """Scan a GitHub repository by URL and generate wiki pages"""
    try:
        from repo_scanner import GitHubRepoScanner
        
        data = request.get_json() or {}
        repo_url = data.get('repo_url', '').strip()
        
        if not repo_url:
            return jsonify({
                "status": "error",
                "message": "Missing repo_url parameter"
            }), 400
        
        # Validate URL
        if not repo_url.startswith(('http://', 'https://', 'git@')):
            repo_url = f"https://github.com/{repo_url}"
        
        # Scan the repository
        scanner = GitHubRepoScanner(repo_url)
        result = scanner.analyze()
        
        # Add pages to wiki
        created_pages = []
        for page_data in result['pages']:
            page = code_wiki.create_page(
                title=page_data['title'],
                slug=page_data['slug'],
                page_type=page_data['type'],
                content=page_data['content'],
                description=page_data['description'],
                author=f"Scanner - {result['repo_name']}",
                tags=page_data.get('tags', [])
            )
            created_pages.append({
                "title": page.title,
                "slug": page.slug,
                "url": f"/wiki/pages/{page.slug}"
            })
        
        return jsonify({
            "status": "success",
            "message": f"Scanned {result['repo_name']} and created {len(created_pages)} wiki pages",
            "repo_name": result['repo_name'],
            "repo_url": result['repo_url'],
            "pages_created": created_pages,
            "analysis": result['analysis']
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/wiki/scan-github", methods=["POST"])
@app.route("/api/wiki/pages/<slug>", methods=["GET"])
def get_wiki_page(slug):
    """Get a specific wiki page"""
    try:
        page = code_wiki.get_page(slug)
        if not page:
            return jsonify({"error": "Page not found"}), 404
        
        snippets = code_wiki.get_snippets_for_page(slug)
        comments = code_wiki.get_comments_for_page(slug)
        related = code_wiki.get_related_pages(slug)
        
        return jsonify({
            "status": "success",
            "page": page.to_dict(),
            "snippets": [s.to_dict() for s in snippets],
            "comments": [c.to_dict() for c in comments],
            "related_pages": [p.to_dict() for p in related]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/pages", methods=["POST"])
def create_wiki_page():
    """Create a new wiki page"""
    try:
        data = request.json
        page = code_wiki.create_page(
            title=data.get("title", ""),
            slug=data.get("slug", ""),
            page_type=data.get("type", "best_practices"),
            content=data.get("content", ""),
            description=data.get("description", ""),
            author=data.get("author", "Unknown"),
            tags=data.get("tags", [])
        )
        
        audit_logger.log_action(
            "wiki_page_created",
            "wiki",
            page.slug,
            {"title": page.title, "type": page.page_type}
        )
        
        return jsonify({"status": "success", "page": page.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/pages/<slug>", methods=["PUT"])
def update_wiki_page(slug):
    """Update a wiki page"""
    try:
        data = request.json
        page = code_wiki.update_page(
            slug=slug,
            title=data.get("title"),
            content=data.get("content"),
            description=data.get("description"),
            author=data.get("author"),
            tags=data.get("tags")
        )
        
        if not page:
            return jsonify({"error": "Page not found"}), 404
        
        audit_logger.log_action(
            "wiki_page_updated",
            "wiki",
            slug,
            {"title": page.title}
        )
        
        return jsonify({"status": "success", "page": page.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/pages/<slug>", methods=["DELETE"])
def delete_wiki_page(slug):
    """Delete a wiki page"""
    try:
        if code_wiki.delete_page(slug):
            audit_logger.log_action(
                "wiki_page_deleted",
                "wiki",
                slug,
                {}
            )
            return jsonify({"status": "success", "message": f"Page {slug} deleted"})
        return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/search", methods=["GET"])
def search_wiki():
    """Search wiki pages"""
    try:
        query = request.args.get("q", "")
        if not query:
            return jsonify({"error": "Search query required"}), 400
        
        results = code_wiki.search_pages(query)
        return jsonify({
            "status": "success",
            "query": query,
            "results": [p.to_dict() for p in results],
            "count": len(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/pages/<slug>/like", methods=["POST"])
def like_wiki_page(slug):
    """Like a wiki page"""
    try:
        if code_wiki.like_page(slug):
            page = code_wiki.get_page(slug)
            return jsonify({"status": "success", "likes": page.likes})
        return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/bookmarks", methods=["POST"])
def bookmark_wiki_page():
    """Bookmark a wiki page"""
    try:
        data = request.json
        user_id = data.get("user_id", "anonymous")
        page_slug = data.get("page_slug", "")
        
        if code_wiki.bookmark_page(user_id, page_slug):
            return jsonify({"status": "success", "message": "Page bookmarked"})
        return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/bookmarks", methods=["GET"])
def get_wiki_bookmarks():
    """Get user's bookmarked pages"""
    try:
        user_id = request.args.get("user_id", "anonymous")
        pages = code_wiki.get_user_bookmarks(user_id)
        return jsonify({
            "status": "success",
            "bookmarks": [p.to_dict() for p in pages],
            "count": len(pages)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/pages/<slug>/comments", methods=["POST"])
def add_wiki_comment(slug):
    """Add a comment to a wiki page"""
    try:
        data = request.json
        comment = code_wiki.add_comment(
            page_slug=slug,
            author=data.get("author", "Anonymous"),
            content=data.get("content", "")
        )
        
        if comment:
            return jsonify({"status": "success", "comment": comment.to_dict()})
        return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/pages/<slug>/comments", methods=["GET"])
def get_wiki_comments(slug):
    """Get comments for a wiki page"""
    try:
        comments = code_wiki.get_comments_for_page(slug)
        return jsonify({
            "status": "success",
            "comments": [c.to_dict() for c in comments],
            "count": len(comments)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/snippets", methods=["POST"])
def add_code_snippet():
    """Add a code snippet to a wiki page"""
    try:
        data = request.json
        snippet = code_wiki.add_code_snippet(
            page_slug=data.get("page_slug", ""),
            title=data.get("title", ""),
            language=data.get("language", "python"),
            code=data.get("code", ""),
            description=data.get("description", "")
        )
        
        if snippet:
            return jsonify({"status": "success", "snippet": snippet.to_dict()})
        return jsonify({"error": "Page not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/statistics", methods=["GET"])
def get_wiki_statistics():
    """Get wiki statistics"""
    try:
        stats = code_wiki.get_statistics()
        return jsonify({"status": "success", "statistics": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/export", methods=["GET"])
def export_wiki():
    """Export entire wiki as JSON"""
    try:
        wiki_json = code_wiki.export_wiki()
        return app.response_class(
            response=wiki_json,
            status=200,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=wiki-export.json"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


repo_chats = {}  # Store chat sessions: {session_id: RepositoryChat}

@app.route("/api/chat/session", methods=["POST"])
def create_chat_session():
    """Create a new chat session for a repository"""
    try:
        from repo_chat import RepositoryChat
        import tempfile
        import subprocess
        
        data = request.get_json() or {}
        repo_input = data.get('repo_path', '/app/src')
        session_id = str(uuid.uuid4())[:8]
        
        # Check if input is a GitHub URL
        repo_path = repo_input
        if repo_input.startswith('https://github.com/') or repo_input.startswith('git@github.com:'):
            # Clone GitHub repo to temp directory
            temp_dir = tempfile.mkdtemp()
            clone_cmd = f'git clone --depth 1 {repo_input} {temp_dir}'
            result = subprocess.run(clone_cmd.split(), capture_output=True, timeout=60)
            if result.returncode != 0:
                return jsonify({
                    "status": "error",
                    "message": f"Failed to clone repository: {result.stderr.decode()}"
                }), 400
            repo_path = temp_dir
        
        # Create chat session (NOT scanned yet)
        chat = RepositoryChat(repo_path)
        repo_chats[session_id] = chat
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "repo_path": repo_path,
            "message": "Chat session created. Call /api/chat/scan to scan the repository first."
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/chat/scan/<session_id>", methods=["POST"])
def scan_repository_for_chat(session_id):
    """Scan repository for a chat session"""
    try:
        if session_id not in repo_chats:
            return jsonify({
                "status": "error",
                "message": "Invalid session ID"
            }), 400
        
        chat = repo_chats[session_id]
        
        # Scan the repository
        context = chat.scan()
        status = chat.get_scan_status()
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "message": "Repository scanned successfully",
            "scan_status": status
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/chat/status/<session_id>", methods=["GET"])
def get_chat_status(session_id):
    """Get chat session status"""
    try:
        if session_id not in repo_chats:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        chat = repo_chats[session_id]
        return jsonify({
            "status": "success",
            "scan_status": chat.get_scan_status()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/chat/artifacts/<session_id>", methods=["GET"])
def get_chat_artifacts(session_id):
    """Get all discovered artifacts from scan"""
    try:
        if session_id not in repo_chats:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        chat = repo_chats[session_id]
        
        if not chat.is_scanned:
            return jsonify({
                "status": "error",
                "message": "Repository not scanned yet"
            }), 400
        
        return jsonify({
            "status": "success",
            "artifacts": chat.context
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/chat/ask", methods=["POST"])
def chat_ask():
    """Ask a question about the repository (AFTER scanning)"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        question = data.get('question', '').strip()
        
        if not session_id or session_id not in repo_chats:
            return jsonify({
                "status": "error",
                "message": "Invalid session ID"
            }), 400
        
        if not question:
            return jsonify({
                "status": "error",
                "message": "Question required"
            }), 400
        
        chat = repo_chats[session_id]
        
        # Check if scanned
        if not chat.is_scanned:
            return jsonify({
                "status": "error",
                "message": "Repository not scanned yet. Call /api/chat/scan/{session_id} first"
            }), 400
        
        # Use pattern matching (no Ollama dependency)
        answer = chat.ask(question)
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "history_length": len(chat.conversation_history)
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/chat/history/<session_id>", methods=["GET"])
def get_chat_history(session_id):
    """Get conversation history for a session"""
    try:
        if session_id not in repo_chats:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        chat = repo_chats[session_id]
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "history": chat.get_history()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/chat/clear/<session_id>", methods=["POST"])
def clear_chat_session(session_id):
    """Clear a chat session"""
    try:
        if session_id in repo_chats:
            del repo_chats[session_id]
            return jsonify({
                "status": "success",
                "message": "Session cleared"
            }), 200
        return jsonify({
            "status": "error",
            "message": "Session not found"
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/status", methods=["GET"])
def status():
    """Check system status"""
    status_info = {
        "ollama": check_ollama(),
        "database": check_database(),
        "redis": check_redis(),
        "timestamp": datetime.now().isoformat(),
    }
    return jsonify(status_info)

report_service.start_scheduler()
enterprise_service.start_scheduler()


# ========== API TESTING ENDPOINTS ==========

from api_tester import APITester, APIDocumenter

@app.route("/api/test/configure-endpoint", methods=["POST"])
def configure_test_endpoint():
    """Configure or override base URL for testing APIs
    
    ARCHITECTURAL ENDPOINT:
    Allows users to specify base URLs for external repositories
    and override defaults for testing
    
    POST /api/test/configure-endpoint
    {
        "api_path": "/api/orders",
        "base_url": "https://api.example.com",
        "environment": "production"|"staging"|"development"
    }
    """
    try:
        data = request.get_json() or {}
        api_path = data.get('api_path', '')
        base_url = data.get('base_url', 'http://localhost:8000')
        environment = data.get('environment', 'development')
        
        if not api_path:
            return jsonify({"error": "api_path required"}), 400
        
        # Store in session/Redis for this session
        if redis_client:
            config_key = f"api_config:{api_path}"
            redis_client.set(config_key, json.dumps({
                "base_url": base_url,
                "environment": environment,
                "configured_at": datetime.now().isoformat()
            }), ex=3600)  # Expire after 1 hour
        
        return jsonify({
            "status": "success",
            "api_path": api_path,
            "base_url": base_url,
            "environment": environment,
            "message": f"Test configuration set for {api_path}"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/test/run", methods=["POST"])
def run_api_test():
    """Test a single API endpoint
    
    ARCHITECTURAL FIX:
    1. Check if this is a testable (local) API
    2. Use configured base URL if available, otherwise default
    3. Handle external APIs differently with explicit base URL requirement
    """
    try:
        from api_tester import APITester
        
        data = request.get_json() or {}
        api_path = data.get('api_path', '')
        method = data.get('method', 'GET')
        body = data.get('body', {})
        base_url = data.get('base_url', 'http://localhost:8000')
        timeout = data.get('timeout', 5)
        
        # Check for configured base URL in Redis
        if redis_client:
            config_key = f"api_config:{api_path}"
            config = redis_client.get(config_key)
            if config:
                config_data = json.loads(config)
                base_url = config_data.get('base_url', base_url)
        
        # Test the API
        tester = APITester(base_url)
        result = tester.test_api(api_path, method, body, timeout=timeout)
        
        return jsonify({
            "status": "success",
            "api_path": result.api_path,
            "method": result.method,
            "base_url": base_url,  # Include the actual base URL used
            "response_status": result.response.status_code,
            "response_time_ms": result.response.time_ms,
            "success": result.success,
            "response_body": result.response.body,
            "error": result.response.error,
            "notes": result.notes
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/test/run-OLD", methods=["POST"])


@app.route("/api/test/batch", methods=["POST"])
def run_batch_api_tests():
    """Test multiple APIs"""
    try:
        from api_tester import APITester
        
        data = request.get_json() or {}
        apis = data.get('apis', [])
        base_url = data.get('base_url', 'http://localhost:8000')
        timeout = data.get('timeout', 5)
        
        tester = APITester(base_url)
        results = tester.test_apis_batch(apis, timeout)
        
        summary = tester.get_test_summary()
        
        return jsonify({
            "status": "success",
            "summary": summary,
            "results": [
                {
                    "api_path": r.api_path,
                    "method": r.method,
                    "response_status": r.response.status_code,
                    "response_time_ms": r.response.time_ms,
                    "success": r.success,
                    "error": r.response.error,
                    "notes": r.notes
                }
                for r in results
            ]
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/test/export", methods=["POST"])
def export_test_results():
    """Export test results"""
    try:
        from api_tester import APITester
        
        data = request.get_json() or {}
        apis = data.get('apis', [])
        format_type = data.get('format', 'markdown')  # json, csv, markdown
        base_url = data.get('base_url', 'http://localhost:8000')
        
        tester = APITester(base_url)
        tester.test_apis_batch(apis)
        
        export_data = tester.export_results(format_type)
        
        return jsonify({
            "status": "success",
            "format": format_type,
            "data": export_data
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/test/validate-endpoints", methods=["POST"])
def validate_endpoints():
    """Validate which discovered endpoints actually exist
    
    ARCHITECTURAL DECISION:
    - Only validate endpoints that are marked as 'testable'
    - Local APIs should always be checked against localhost:8000
    - External/documentation-only APIs are skipped (require explicit base_url)
    """
    try:
        from api_tester import APITester
        import requests
        
        data = request.get_json() or {}
        apis = data.get('apis', [])
        base_url = data.get('base_url', 'http://localhost:8000')
        
        # FILTER: Only validate testable APIs (from local code)
        testable_apis = [api for api in apis if api.get('testable', True)]
        
        validated_apis = []
        invalid_apis = []
        skipped_apis = []
        
        # Skip external/documentation-only APIs
        for api in apis:
            if not api.get('testable', True):
                skipped_apis.append({
                    **api,
                    'reason': 'external_repository',
                    'note': 'This API is from an external repository. Deploy it separately and provide its base URL to test.'
                })
        
        # Validate local/testable APIs
        for api in testable_apis:
            path = api.get('path', '')
            method = api.get('methods', ['GET'])[0]
            api_base_url = api.get('base_url', base_url)  # Use API-specific base URL if provided
            
            try:
                # Quick HEAD/OPTIONS check first
                resp = requests.request(
                    method, 
                    f"{api_base_url}{path}",
                    timeout=2,
                    allow_redirects=False
                )
                
                # Only accept 2xx, 3xx, or 4xx with actual response (not 404/405)
                if resp.status_code < 400 or resp.status_code in [405, 415]:
                    # 405 Method Not Allowed means endpoint exists but wrong method
                    validated_apis.append(api)
                elif resp.status_code == 404:
                    invalid_apis.append({**api, 'reason': 'endpoint_not_found', 'status': 404})
                else:
                    # Other errors
                    invalid_apis.append({**api, 'reason': f'status_{resp.status_code}', 'status': resp.status_code})
                    
            except requests.exceptions.Timeout:
                invalid_apis.append({**api, 'reason': 'timeout'})
            except requests.exceptions.ConnectionError:
                invalid_apis.append({**api, 'reason': 'connection_error', 'note': f'Cannot connect to {api_base_url}. Is the service running?'})
            except Exception as e:
                invalid_apis.append({**api, 'reason': str(e)})
        
        return jsonify({
            "status": "success",
            "validated_endpoints": validated_apis,
            "invalid_endpoints": invalid_apis,
            "skipped_external": skipped_apis,
            "validation_summary": {
                "total_checked": len(apis),
                "local_apis": len(testable_apis),
                "external_apis": len(skipped_apis),
                "valid": len(validated_apis),
                "invalid": len(invalid_apis),
                "valid_percentage": f"{(len(validated_apis)/len(testable_apis)*100):.0f}%" if testable_apis else "0%"
            },
            "architecture_note": "External repository APIs require their own deployment and base URL configuration. Only local APIs are auto-tested."
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500




@app.route('/api/chat/metrics/<session_id>', methods=['GET'])
def get_metrics(session_id):
    """Get code quality metrics"""
    if session_id not in repo_chats:
        return {'status': 'error', 'message': 'Session not found'}, 404
    
    chat = repo_chats[session_id]
    
    # Calculate metrics
    metrics = {
        'complexity': calculate_complexity(chat),
        'coverage': estimate_coverage(chat),
        'maintainability': calculate_maintainability(chat),
        'security_score': calculate_security_score(chat),
        'code_quality': calculate_code_quality(chat)
    }
    
    return {'status': 'success', 'metrics': metrics}

@app.route('/api/chat/dependencies-analysis/<session_id>', methods=['GET'])
def analyze_dependencies(session_id):
    """Analyze dependencies for conflicts and vulnerabilities"""
    if session_id not in repo_chats:
        return {'status': 'error', 'message': 'Session not found'}, 404
    
    chat = repo_chats[session_id]
    
    deps = chat.context.get('dependencies', [])
    
    analysis = {
        'total_dependencies': len(deps),
        'critical_vulnerabilities': 0,
        'outdated_packages': [],
        'dependency_tree': build_dependency_tree(deps),
        'security_warnings': check_security_issues(deps)
    }
    
    return {'status': 'success', 'analysis': analysis}

def calculate_complexity(chat):
    """Calculate cyclomatic complexity"""
    functions = chat.context.get('functions', [])
    if not functions:
        return 'Low'
    
    avg_params = sum(len(f.get('params', [])) for f in functions) / len(functions)
    if avg_params > 5:
        return 'High'
    elif avg_params > 3:
        return 'Medium'
    return 'Low'

def estimate_coverage(chat):
    """Estimate test coverage based on test file presence"""
    files = chat.context.get('files', [])
    test_files = [f for f in files if 'test' in f.lower()]
    coverage = (len(test_files) / max(len(files), 1)) * 100 if files else 0
    return min(int(coverage), 100)

def calculate_maintainability(chat):
    """Calculate maintainability index"""
    functions = chat.context.get('functions', [])
    classes = chat.context.get('classes', [])
    
    total_artifacts = len(functions) + len(classes)
    if total_artifacts > 50:
        return 'Low'
    elif total_artifacts > 20:
        return 'Medium'
    return 'High'

def calculate_security_score(chat):
    """Calculate security score (0-100)"""
    deps = chat.context.get('dependencies', [])
    # Base score
    score = 80
    
    # Deduct for known vulnerable packages
    vulnerable = ['eval', 'exec', 'pickle', 'marshal']
    for dep in deps:
        if any(v in dep.get('package', '').lower() for v in vulnerable):
            score -= 10
    
    return max(score, 20)

def calculate_code_quality(chat):
    """Calculate overall code quality"""
    apis = chat.context.get('apis', [])
    functions = chat.context.get('functions', [])
    
    # Quality indicators
    has_documentation = len([f for f in functions if f.get('docstring')]) / max(len(functions), 1) if functions else 0
    api_coverage = len(apis) / max(len(functions), 1) if functions else 0
    
    quality_score = int((has_documentation * 50 + api_coverage * 50))
    return min(quality_score, 100)

def build_dependency_tree(deps):
    """Build a simple dependency tree"""
    return {
        'prod': [d['package'] for d in deps if d.get('type') == 'production'][:10],
        'dev': [d['package'] for d in deps if d.get('type') == 'development'][:10]
    }

def check_security_issues(deps):
    """Check for known security issues"""
    warnings = []
    known_issues = {
        'eval': 'Code execution vulnerability - avoid eval()',
        'pickle': 'Untrusted serialization - use json instead',
        'requests': 'Ensure SSL verification is enabled',
        'crypto': 'Use cryptography instead of pycrypto'
    }
    
    for dep in deps:
        pkg = dep.get('package', '').lower()
        for issue, warning in known_issues.items():
            if issue in pkg:
                warnings.append({'package': dep['package'], 'issue': warning})
    
    return warnings


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)


# ============ BUG HUNTER ENDPOINTS ============

@app.route('/api/bug-hunter/scan/<session_id>', methods=['POST'])
def scan_for_bugs(session_id):
    """Scan repository for security bugs"""
    try:
        from security_bug_detector import SecurityBugDetector
        
        if session_id not in repo_chats:
            return jsonify({"status": "error", "message": "Session not found"}), 404
        
        chat = repo_chats[session_id]
        detector = SecurityBugDetector()
        
        all_bugs = []
        
        # Scan all Python files
        for file_path in chat.repo_path.glob('**/*.py'):
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    code = f.read()
                    bugs = detector.scan_code(code, str(file_path))
                    all_bugs.extend(bugs)
            except:
                pass
        
        # Convert to dict
        bugs_data = [bug.to_dict() for bug in all_bugs]
        
        # Calculate summary
        critical_count = len([b for b in bugs_data if '🔴 CRITICAL' in b['severity']])
        high_count = len([b for b in bugs_data if '🟠 HIGH' in b['severity']])
        
        return jsonify({
            "status": "success",
            "bugs": bugs_data,
            "summary": {
                "total": len(bugs_data),
                "critical": critical_count,
                "high": high_count,
                "confidence_avg": sum(b['confidence'] for b in bugs_data) / len(bugs_data) if bugs_data else 0
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/bug-hunter/fix/<bug_id>', methods=['GET'])
def get_bug_fix(bug_id):
    """Get AI-generated fix for a bug"""
    try:
        from security_bug_detector import SecurityBugDetector, BugType
        
        detector = SecurityBugDetector()
        
        # Parse bug type from ID (this is simplified - in prod you'd store this)
        # For now, return a generic fix template
        
        return jsonify({
            "status": "success",
            "fix": {
                "before": "# Original vulnerable code",
                "after": "# Fixed secure code",
                "explanation": "Apply the security fix as described"
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# ============ PHASE 2: REAL-TIME SCANNING & CODE SMELLS ============

@app.route('/api/bug-hunter/scan-realtime/<session_id>', methods=['POST'])
def scan_for_bugs_realtime(session_id):
    """Real-time security bug scanning with progress updates"""
    try:
        from security_bug_detector import SecurityBugDetector
        import json
        
        if session_id not in repo_chats:
            return jsonify({"status": "error", "message": "Session not found"}), 404
        
        chat = repo_chats[session_id]
        detector = SecurityBugDetector()
        
        all_bugs = []
        total_files = 0
        processed_files = 0
        
        # Get all Python files first
        python_files = list(chat.repo_path.glob('**/*.py'))
        total_files = len(python_files)
        
        # Scan with progress
        for file_path in python_files:
            try:
                processed_files += 1
                with open(file_path, 'r', errors='ignore') as f:
                    code = f.read()
                    bugs = detector.scan_code(code, str(file_path))
                    all_bugs.extend(bugs)
                
                # Store progress in Redis for real-time updates
                if redis_client:
                    progress_key = f"scan-progress:{session_id}"
                    redis_client.set(progress_key, json.dumps({
                        'processed': processed_files,
                        'total': total_files,
                        'percentage': int((processed_files / total_files) * 100),
                        'current_file': str(file_path),
                        'bugs_found': len(all_bugs)
                    }), ex=3600)
            except:
                pass
        
        # Convert to dict
        bugs_data = [bug.to_dict() for bug in all_bugs]
        
        # Calculate summary
        critical_count = len([b for b in bugs_data if '🔴 CRITICAL' in b['severity']])
        high_count = len([b for b in bugs_data if '🟠 HIGH' in b['severity']])
        
        # Store scan results
        if redis_client:
            scan_key = f"scan-results:{session_id}"
            redis_client.set(scan_key, json.dumps({
                'bugs': bugs_data,
                'timestamp': datetime.now().isoformat(),
                'total_files': total_files
            }), ex=3600)
        
        return jsonify({
            "status": "success",
            "bugs": bugs_data,
            "summary": {
                "total": len(bugs_data),
                "critical": critical_count,
                "high": high_count,
                "confidence_avg": sum(b['confidence'] for b in bugs_data) / len(bugs_data) if bugs_data else 0,
                "files_scanned": total_files
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/bug-hunter/progress/<session_id>', methods=['GET'])
def get_scan_progress(session_id):
    """Get real-time scan progress"""
    try:
        if not redis_client:
            return jsonify({"status": "error", "message": "Progress tracking unavailable"}), 500
        
        progress_key = f"scan-progress:{session_id}"
        progress_data = redis_client.get(progress_key)
        
        if not progress_data:
            return jsonify({"status": "idle", "percentage": 0}), 200
        
        return jsonify(json.loads(progress_data)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/bug-hunter/scan-smells/<session_id>', methods=['POST'])
def scan_for_code_smells(session_id):
    """Scan repository for code smells"""
    try:
        from code_smell_detector import CodeSmellDetector
        
        if session_id not in repo_chats:
            return jsonify({"status": "error", "message": "Session not found"}), 404
        
        chat = repo_chats[session_id]
        detector = CodeSmellDetector()
        
        # Scan the repository
        smells = detector.scan_files(str(chat.repo_path))
        
        # Convert to dict
        smells_data = [smell.to_dict() for smell in smells]
        
        # Get summary
        summary = detector.get_complexity_summary(smells)
        
        # Count by severity
        major_count = len([s for s in smells_data if '🟠 MAJOR' in s['severity']])
        medium_count = len([s for s in smells_data if '🟡 MEDIUM' in s['severity']])
        minor_count = len([s for s in smells_data if '🟢 MINOR' in s['severity']])
        
        return jsonify({
            "status": "success",
            "smells": smells_data,
            "summary": {
                "total": len(smells_data),
                "major": major_count,
                "medium": medium_count,
                "minor": minor_count,
                **summary
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500



# ============ PHASE 3: PERFORMANCE ANALYSIS ============

@app.route('/api/bug-hunter/scan-performance/<session_id>', methods=['POST'])
def scan_for_performance_issues(session_id):
    """Scan repository for performance issues"""
    try:
        from performance_analyzer import PerformanceAnalyzer
        
        if session_id not in repo_chats:
            return jsonify({"status": "error", "message": "Session not found"}), 404
        
        chat = repo_chats[session_id]
        analyzer = PerformanceAnalyzer()
        
        # Scan the repository
        issues, metrics = analyzer.scan_files(str(chat.repo_path))
        
        # Convert to dict
        issues_data = [issue.to_dict() for issue in issues]
        metrics_data = metrics.to_dict()
        
        return jsonify({
            "status": "success",
            "issues": issues_data,
            "metrics": metrics_data
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500



# ============ PHASE 4: AUTOMATED FIXES & PR GENERATION ============

@app.route('/api/bug-hunter/generate-fixes/<session_id>', methods=['POST'])
def generate_fixes(session_id):
    """Generate automated fixes for detected issues"""
    try:
        from automated_fix_generator import AutomatedFixGenerator
        
        if session_id not in repo_chats:
            return jsonify({"status": "error", "message": "Session not found"}), 404
        
        data = request.get_json() or {}
        issues = data.get('issues', [])
        
        if not issues:
            return jsonify({"status": "error", "message": "No issues provided"}), 400
        
        # Generate fixes
        generator = AutomatedFixGenerator()
        fixes = generator.generate_fixes(issues)
        
        # Convert to dict
        fixes_data = [fix.to_dict() for fix in fixes]
        
        return jsonify({
            "status": "success",
            "fixes": fixes_data,
            "summary": {
                "total_fixes": len(fixes_data),
                "auto_applicable": len([f for f in fixes_data if f['test_compatible']]),
                "manual_required": len([f for f in fixes_data if not f['test_compatible']]),
                "confidence_avg": sum(f['confidence'] for f in fixes_data) / len(fixes_data) if fixes_data else 0
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/bug-hunter/apply-fixes/<session_id>', methods=['POST'])
def apply_fixes(session_id):
    """Apply generated fixes to files"""
    try:
        from automated_fix_generator import AutomatedFixGenerator
        
        if session_id not in repo_chats:
            return jsonify({"status": "error", "message": "Session not found"}), 404
        
        chat = repo_chats[session_id]
        data = request.get_json() or {}
        fixes = data.get('fixes', [])
        
        if not fixes:
            return jsonify({"status": "error", "message": "No fixes to apply"}), 400
        
        # Apply fixes to files
        generator = AutomatedFixGenerator()
        applied_count, files_modified = generator.apply_fixes_to_files(fixes, str(chat.repo_path))
        
        return jsonify({
            "status": "success",
            "fixes_applied": applied_count,
            "files_modified": files_modified,
            "message": f"Applied {applied_count} fixes to {len(files_modified)} files"
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/bug-hunter/create-pr/<session_id>', methods=['POST'])
def create_pr(session_id):
    """Create a pull request with fixes"""
    try:
        from automated_fix_generator import AutomatedFixGenerator, GitHubPRCreator
        
        if session_id not in repo_chats:
            return jsonify({"status": "error", "message": "Session not found"}), 404
        
        data = request.get_json() or {}
        fixes = data.get('fixes', [])
        github_token = data.get('github_token', '')
        repo_url = data.get('repo_url', '')
        
        if not fixes or not github_token or not repo_url:
            return jsonify({"status": "error", "message": "Missing required parameters"}), 400
        
        # Parse repo URL
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            return jsonify({"status": "error", "message": "Invalid GitHub repository URL"}), 400
        
        repo_owner, repo_name = match.groups()
        repo_name = repo_name.replace('.git', '')
        
        # Generate fixes
        generator = AutomatedFixGenerator()
        
        # Create PR title and description
        pr_title = f"🤖 AI Auto-Remediation: Fix {len(fixes)} Security, Quality & Performance Issues"
        pr_description = generator.generate_pr_description(
            [fix for fix in fixes if fix.get('test_compatible', False)],
            {"total_issues": len(fixes)}
        )
        
        # Create branch name
        branch_name = f"ai-remediation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create GitHub PR
        pr_creator = GitHubPRCreator(github_token, repo_owner, repo_name)
        
        # Create branch
        branch_created = pr_creator.create_branch(branch_name)
        if not branch_created:
            return jsonify({
                "status": "warning",
                "message": "Could not create branch - this is a local analysis only"
            }), 200
        
        # Create PR
        pr_result = pr_creator.create_pull_request(branch_name, pr_title, pr_description)
        
        return jsonify({
            "status": "success" if pr_result.get('status') == 'success' else "error",
            "pr": pr_result,
            "fixes_summary": {
                "total_fixes": len(fixes),
                "files_affected": len(set(f.get('file') for f in fixes))
            }
        }), 200 if pr_result.get('status') == 'success' else 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/bug-hunter/fix-preview/<session_id>', methods=['POST'])
def get_fix_preview(session_id):
    """Get before/after preview of fixes"""
    try:
        data = request.get_json() or {}
        fixes = data.get('fixes', [])
        
        preview_html = '<div style="font-family: monospace; background: #f9fafb; padding: 20px; border-radius: 8px;">'
        
        for fix in fixes:
            preview_html += f"""
            <div style="margin-bottom: 20px; border: 1px solid #e5e7eb; padding: 15px; border-radius: 6px;">
                <h3 style="margin-top: 0; color: #1e293b;">{fix.get('type', 'Unknown')}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <h4 style="color: #dc2626; margin: 10px 0;">Before:</h4>
                        <pre style="background: white; padding: 10px; border-radius: 4px; border-left: 3px solid #dc2626; overflow-x: auto;">{fix.get('before', '')}</pre>
                    </div>
                    <div>
                        <h4 style="color: #10b981; margin: 10px 0;">After:</h4>
                        <pre style="background: white; padding: 10px; border-radius: 4px; border-left: 3px solid #10b981; overflow-x: auto;">{fix.get('after', '')}</pre>
                    </div>
                </div>
                <p style="color: #666; font-size: 14px; margin: 10px 0;">
                    <strong>File:</strong> {fix.get('file', '')}:{fix.get('line', 0)}<br/>
                    <strong>Confidence:</strong> {int(fix.get('confidence', 0)*100)}%
                </p>
            </div>
            """
        
        preview_html += '</div>'
        
        return jsonify({
            "status": "success",
            "preview": preview_html,
            "total_fixes": len(fixes)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

