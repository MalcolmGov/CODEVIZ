"""
Slack Bot Integration for Move Digital
Real-time security alerts and notifications
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlackNotificationManager:
    """Manages Slack notifications for security findings"""
    
    def __init__(self, webhook_url: Optional[str] = None, bot_token: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.channel = os.getenv("SLACK_CHANNEL", "#security-alerts")
        
    def send_raw_message(self, payload: Dict) -> bool:
        """Send raw Slack message"""
        try:
            if not self.webhook_url:
                logger.warning("Slack webhook not configured")
                return False
                
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Slack message failed: {e}")
            return False
    
    def send_vulnerability_alert(
        self,
        repo_name: str,
        severity: str,
        findings: List[Dict],
        branch: str = "main"
    ) -> bool:
        """Send vulnerability alert to Slack"""
        
        # Color based on severity
        severity_colors = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#d97706",
            "low": "#16a34a"
        }
        
        color = severity_colors.get(severity.lower(), "#6b7280")
        
        # Build findings summary
        findings_text = ""
        for i, finding in enumerate(findings[:5], 1):
            findings_text += f"\n{i}. {finding.get('title', 'Unknown')}"
            if finding.get('cve'):
                findings_text += f" ({finding['cve']})"
        
        if len(findings) > 5:
            findings_text += f"\n... and {len(findings) - 5} more"
        
        payload = {
            "channel": self.channel,
            "attachments": [
                {
                    "color": color,
                    "title": f"🔐 {severity.upper()} Security Alert",
                    "fields": [
                        {
                            "title": "Repository",
                            "value": f"`{repo_name}`",
                            "short": True
                        },
                        {
                            "title": "Branch",
                            "value": branch,
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": severity.upper(),
                            "short": True
                        },
                        {
                            "title": "Issue Count",
                            "value": str(len(findings)),
                            "short": True
                        },
                        {
                            "title": "Findings",
                            "value": findings_text,
                            "short": False
                        }
                    ],
                    "footer": "Move Digital Security Platform",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        return self.send_raw_message(payload)
    
    def send_remediation_pr_created(
        self,
        repo_name: str,
        pr_url: str,
        fixes_count: int,
        issues_fixed: List[str]
    ) -> bool:
        """Notify when remediation PR is created"""
        
        issues_summary = "\n".join([f"• {issue}" for issue in issues_fixed[:5]])
        if len(issues_fixed) > 5:
            issues_summary += f"\n• ... and {len(issues_fixed) - 5} more"
        
        payload = {
            "channel": self.channel,
            "attachments": [
                {
                    "color": "#10b981",
                    "title": "✅ Remediation PR Created",
                    "fields": [
                        {
                            "title": "Repository",
                            "value": f"`{repo_name}`",
                            "short": True
                        },
                        {
                            "title": "Issues Fixed",
                            "value": str(fixes_count),
                            "short": True
                        },
                        {
                            "title": "Fixed Issues",
                            "value": issues_summary,
                            "short": False
                        }
                    ],
                    "actions": [
                        {
                            "type": "button",
                            "text": "View PR",
                            "url": pr_url,
                            "style": "primary"
                        }
                    ],
                    "footer": "Move Digital Remediation Engine",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        return self.send_raw_message(payload)
    
    def send_scan_complete(
        self,
        repo_name: str,
        total_issues: int,
        critical: int,
        high: int,
        medium: int,
        low: int,
        scan_time_seconds: float
    ) -> bool:
        """Notify when scan completes"""
        
        payload = {
            "channel": self.channel,
            "attachments": [
                {
                    "color": "#3b82f6",
                    "title": "📊 Security Scan Complete",
                    "fields": [
                        {
                            "title": "Repository",
                            "value": f"`{repo_name}`",
                            "short": True
                        },
                        {
                            "title": "Total Issues",
                            "value": str(total_issues),
                            "short": True
                        },
                        {
                            "title": "🔴 Critical",
                            "value": str(critical),
                            "short": True
                        },
                        {
                            "title": "🟠 High",
                            "value": str(high),
                            "short": True
                        },
                        {
                            "title": "🟡 Medium",
                            "value": str(medium),
                            "short": True
                        },
                        {
                            "title": "🟢 Low",
                            "value": str(low),
                            "short": True
                        },
                        {
                            "title": "Scan Time",
                            "value": f"{scan_time_seconds:.2f}s",
                            "short": True
                        }
                    ],
                    "footer": "Move Digital Security Platform",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        return self.send_raw_message(payload)
    
    def send_policy_violation(
        self,
        repo_name: str,
        pr_number: int,
        policy_name: str,
        violation_details: str,
        pr_url: str
    ) -> bool:
        """Notify when policy is violated"""
        
        payload = {
            "channel": self.channel,
            "attachments": [
                {
                    "color": "#dc2626",
                    "title": "⚠️ Policy Violation",
                    "fields": [
                        {
                            "title": "Repository",
                            "value": f"`{repo_name}`",
                            "short": True
                        },
                        {
                            "title": "PR #",
                            "value": str(pr_number),
                            "short": True
                        },
                        {
                            "title": "Policy",
                            "value": policy_name,
                            "short": False
                        },
                        {
                            "title": "Details",
                            "value": violation_details,
                            "short": False
                        }
                    ],
                    "actions": [
                        {
                            "type": "button",
                            "text": "View PR",
                            "url": pr_url,
                            "style": "danger"
                        }
                    ],
                    "footer": "Move Digital Policy Engine",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        return self.send_raw_message(payload)
    
    def send_compliance_status(
        self,
        pci_dss_percent: int,
        soc2_percent: int,
        hipaa_percent: int,
        iso27001_percent: int
    ) -> bool:
        """Send compliance status update"""
        
        def get_emoji(percent):
            if percent >= 90:
                return "🟢"
            elif percent >= 75:
                return "🟡"
            else:
                return "🔴"
        
        payload = {
            "channel": self.channel,
            "attachments": [
                {
                    "color": "#3b82f6",
                    "title": "📋 Compliance Status",
                    "fields": [
                        {
                            "title": f"{get_emoji(pci_dss_percent)} PCI-DSS",
                            "value": f"{pci_dss_percent}%",
                            "short": True
                        },
                        {
                            "title": f"{get_emoji(soc2_percent)} SOC2",
                            "value": f"{soc2_percent}%",
                            "short": True
                        },
                        {
                            "title": f"{get_emoji(hipaa_percent)} HIPAA",
                            "value": f"{hipaa_percent}%",
                            "short": True
                        },
                        {
                            "title": f"{get_emoji(iso27001_percent)} ISO 27001",
                            "value": f"{iso27001_percent}%",
                            "short": True
                        }
                    ],
                    "footer": "Move Digital Compliance Engine",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        return self.send_raw_message(payload)


class AlertThrottler:
    """Prevents alert fatigue by grouping/deduplicating alerts"""
    
    def __init__(self, time_window_seconds: int = 3600):
        self.time_window = time_window_seconds
        self.alert_history = {}
    
    def should_alert(self, repo_name: str, severity: str) -> bool:
        """Determine if alert should be sent (alert fatigue management)"""
        
        key = f"{repo_name}:{severity}"
        now = datetime.now().timestamp()
        
        if key in self.alert_history:
            last_alert_time = self.alert_history[key]
            if now - last_alert_time < self.time_window:
                return False
        
        self.alert_history[key] = now
        return True


# Flask endpoints to add to app.py
SLACK_ENDPOINTS = """
@app.route("/api/slack/alerts", methods=["POST"])
def send_slack_alert():
    '''Send security alert to Slack'''
    try:
        data = request.json
        manager = SlackNotificationManager()
        
        alert_type = data.get("type", "vulnerability")
        
        if alert_type == "vulnerability":
            result = manager.send_vulnerability_alert(
                repo_name=data.get("repo_name", ""),
                severity=data.get("severity", "medium"),
                findings=data.get("findings", []),
                branch=data.get("branch", "main")
            )
        elif alert_type == "remediation_pr":
            result = manager.send_remediation_pr_created(
                repo_name=data.get("repo_name", ""),
                pr_url=data.get("pr_url", ""),
                fixes_count=data.get("fixes_count", 0),
                issues_fixed=data.get("issues_fixed", [])
            )
        elif alert_type == "scan_complete":
            result = manager.send_scan_complete(
                repo_name=data.get("repo_name", ""),
                total_issues=data.get("total_issues", 0),
                critical=data.get("critical", 0),
                high=data.get("high", 0),
                medium=data.get("medium", 0),
                low=data.get("low", 0),
                scan_time_seconds=data.get("scan_time_seconds", 0)
            )
        elif alert_type == "policy_violation":
            result = manager.send_policy_violation(
                repo_name=data.get("repo_name", ""),
                pr_number=data.get("pr_number", 0),
                policy_name=data.get("policy_name", ""),
                violation_details=data.get("violation_details", ""),
                pr_url=data.get("pr_url", "")
            )
        elif alert_type == "compliance_status":
            result = manager.send_compliance_status(
                pci_dss_percent=data.get("pci_dss_percent", 0),
                soc2_percent=data.get("soc2_percent", 0),
                hipaa_percent=data.get("hipaa_percent", 0),
                iso27001_percent=data.get("iso27001_percent", 0)
            )
        else:
            return jsonify({"error": "Unknown alert type"}), 400
        
        return jsonify({
            "status": "success" if result else "failed",
            "message": "Slack alert sent"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/slack/test", methods=["POST"])
def test_slack():
    '''Test Slack integration'''
    try:
        manager = SlackNotificationManager()
        result = manager.send_vulnerability_alert(
            repo_name="test-repo",
            severity="high",
            findings=[
                {"title": "SQL Injection in query builder", "cve": "CVE-2024-1234"},
                {"title": "Hardcoded API key", "cve": None}
            ]
        )
        return jsonify({"status": "success" if result else "failed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

if __name__ == "__main__":
    # Test example
    manager = SlackNotificationManager()
    
    # Test vulnerability alert
    manager.send_vulnerability_alert(
        repo_name="spurgeon-property",
        severity="high",
        findings=[
            {"title": "SQL Injection in payment handler", "cve": "CVE-2024-XXXX"},
            {"title": "Hardcoded AWS credentials", "cve": None}
        ]
    )
    
    print("Slack bot integration ready!")
