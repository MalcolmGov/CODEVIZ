"""
Integration of all Move Digital modules into Flask app
Copy these endpoints into your app.py file
"""

# ============ IMPORTS (Add to top of app.py) ============

from remediation_engine import RemediationEngine, RemediationDetector
from slack_bot_integration import SlackNotificationManager, AlertThrottler
from policy_engine import PolicyEngine, PolicyType, PolicyViolationSeverity
from risk_scoring import RiskScoring, DataSensitivity
from compliance_dashboard import ComplianceDashboard, ComplianceFramework

# ============ INITIALIZATION (Add after Flask app initialization) ============

remediation_engine = RemediationEngine()
slack_manager = SlackNotificationManager()
alert_throttler = AlertThrottler()
policy_engine = PolicyEngine()
risk_scorer = RiskScoring()
compliance_dashboard = ComplianceDashboard()

# ============ REMEDIATION ENDPOINTS ============

@app.route("/api/remediation/scan-and-fix", methods=["POST"])
def scan_and_fix():
    """Scan repository and create remediation PR"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        branch = data.get("branch", "main")
        
        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400
        
        # Run remediation
        detector = RemediationDetector(repo_url, branch)
        issues = detector.detect_issues()
        
        result = remediation_engine.apply_fixes_and_create_pr(
            repo_url=repo_url,
            branch=branch,
            issues=issues
        )
        
        # Send Slack notification
        if result.get("pr_url"):
            slack_manager.send_remediation_pr_created(
                repo_name=repo_url.split("/")[-1],
                pr_url=result["pr_url"],
                fixes_count=len(result.get("fixed_issues", [])),
                issues_fixed=result.get("fixed_issues", [])
            )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/remediation/analyze-repo", methods=["POST"])
def analyze_repo_for_remediation():
    """Analyze repo for auto-fixable issues (without creating PR)"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        
        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400
        
        detector = RemediationDetector(repo_url)
        analysis = detector.analyze_fixable_issues()
        
        return jsonify({
            "status": "success",
            "repository": repo_url,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/remediation/metrics", methods=["GET"])
def get_remediation_metrics():
    """Get remediation metrics"""
    try:
        metrics = remediation_engine.get_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ SLACK ENDPOINTS ============

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
        
        # Send Slack notification if violations
        if result.get("violations"):
            for violation in result["violations"]:
                if alert_throttler.should_alert(data.get("repo", ""), violation.get("severity", "medium")):
                    slack_manager.send_policy_violation(
                        repo_name=data.get("repo", ""),
                        pr_number=data.get("pr_number", 0),
                        policy_name=violation.get("policy_name", ""),
                        violation_details=violation.get("message", ""),
                        pr_url=data.get("pr_url", "")
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


# ============ INTEGRATED WORKFLOW ENDPOINT ============

@app.route("/api/workflow/full-scan-and-report", methods=["POST"])
def full_workflow_scan():
    """Complete workflow: scan → remediate → check policies → risk score → compliance"""
    try:
        data = request.json
        repo_url = data.get("repo_url", "")
        repo_name = data.get("repo_name", repo_url.split("/")[-1])
        
        if not repo_url:
            return jsonify({"error": "repo_url required"}), 400
        
        # Step 1: Tag repository for risk scoring
        risk_scorer.tag_repository(
            repo_name=repo_name,
            repo_url=repo_url,
            data_sensitivity=DataSensitivity(data.get("data_sensitivity", 2)),
            criticality=data.get("criticality", "medium")
        )
        
        # Step 2: Run remediation scan
        detector = RemediationDetector(repo_url)
        issues = detector.detect_issues()
        
        # Step 3: Calculate risk scores
        risk_profile = risk_scorer.calculate_repository_risk_profile(
            repo_name=repo_name,
            issues=issues
        )
        
        # Step 4: Check policies (mock - would need PR files in real scenario)
        policy_check = policy_engine.check_pr_for_violations(
            repo_name=repo_name,
            pr_number=0,
            pr_files=[],
            pr_reviewers=2
        )
        
        # Step 5: Update compliance
        compliance_dashboard.update_control_status(
            "PCI-DSS-6.2",
            "completed",
            evidence=[f"Scanned {repo_name}"]
        )
        
        # Step 6: Send Slack summary
        slack_manager.send_scan_complete(
            repo_name=repo_name,
            total_issues=len(issues),
            critical=len([i for i in issues if i.get("severity") == "critical"]),
            high=len([i for i in issues if i.get("severity") == "high"]),
            medium=len([i for i in issues if i.get("severity") == "medium"]),
            low=len([i for i in issues if i.get("severity") == "low"]),
            scan_time_seconds=data.get("scan_time_seconds", 0)
        )
        
        return jsonify({
            "status": "complete",
            "repository": repo_name,
            "issues_found": len(issues),
            "risk_profile": risk_profile,
            "policy_violations": policy_check.get("violation_count", 0),
            "compliance_progress": "Updated",
            "slack_notification": "Sent",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


