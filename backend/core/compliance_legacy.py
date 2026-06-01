"""
Compliance Automation & Dashboard for Move Digital
Track compliance with PCI-DSS, SOC2, HIPAA, ISO27001
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    PCI_DSS = "pci-dss"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"


class ComplianceControl:
    """Represents a single compliance control"""
    
    def __init__(
        self,
        control_id: str,
        framework: ComplianceFramework,
        description: str,
        requirement: str,
        verification_method: str,
        status: str = "not-started"  # not-started, in-progress, completed, failed
    ):
        self.control_id = control_id
        self.framework = framework
        self.description = description
        self.requirement = requirement
        self.verification_method = verification_method
        self.status = status
        self.last_verified = None
        self.evidence = []
    
    def to_dict(self) -> Dict:
        return {
            "control_id": self.control_id,
            "framework": self.framework.value,
            "description": self.description,
            "requirement": self.requirement,
            "verification_method": self.verification_method,
            "status": self.status,
            "last_verified": self.last_verified,
            "evidence": self.evidence
        }


class ComplianceDashboard:
    """Manages compliance tracking and reporting"""
    
    def __init__(self):
        self.controls: Dict[str, ComplianceControl] = {}
        self.audit_logs: List[Dict] = []
        self._initialize_controls()
    
    def _initialize_controls(self):
        """Initialize compliance controls for all frameworks"""
        
        # PCI-DSS Controls (6 key controls for MVP)
        pci_controls = [
            ComplianceControl(
                "PCI-DSS-1.1",
                ComplianceFramework.PCI_DSS,
                "Firewall Configuration",
                "Install and implement firewalls",
                "Network scanning and documentation review"
            ),
            ComplianceControl(
                "PCI-DSS-6.2",
                ComplianceFramework.PCI_DSS,
                "Secure Development Practices",
                "Ensure vulnerability scanning",
                "Automated security scanning results"
            ),
            ComplianceControl(
                "PCI-DSS-8.1",
                ComplianceFramework.PCI_DSS,
                "Access Control",
                "Restrict access by business need",
                "Access control policy review"
            ),
            ComplianceControl(
                "PCI-DSS-10.1",
                ComplianceFramework.PCI_DSS,
                "Audit Logging",
                "Log and monitor access to cardholder data",
                "Audit trail verification"
            ),
        ]
        
        # SOC2 Controls (5 key controls for MVP)
        soc2_controls = [
            ComplianceControl(
                "SOC2-CC1.1",
                ComplianceFramework.SOC2,
                "Change Management",
                "All PR requires code review",
                "Git history and PR documentation"
            ),
            ComplianceControl(
                "SOC2-CC3.1",
                ComplianceFramework.SOC2,
                "Access Restrictions",
                "Restrict system access appropriately",
                "IAM configuration review"
            ),
            ComplianceControl(
                "SOC2-CC6.1",
                ComplianceFramework.SOC2,
                "Vulnerability Management",
                "Identify and address vulnerabilities",
                "Automated scanning and remediation records"
            ),
            ComplianceControl(
                "SOC2-CC7.1",
                ComplianceFramework.SOC2,
                "Security Incident Procedures",
                "Define incident response procedures",
                "Incident response plan documentation"
            ),
        ]
        
        # ISO 27001 Controls (5 key controls for MVP)
        iso_controls = [
            ComplianceControl(
                "ISO-13.1.3",
                ComplianceFramework.ISO27001,
                "Secure Development",
                "Secure development and support processes",
                "Code review and security testing logs"
            ),
            ComplianceControl(
                "ISO-14.1.1",
                ComplianceFramework.ISO27001,
                "Incident Reporting",
                "Information security incident reporting",
                "Incident ticket system audit"
            ),
            ComplianceControl(
                "ISO-9.2.1",
                ComplianceFramework.ISO27001,
                "User Access Management",
                "Control user access rights",
                "Access control list verification"
            ),
            ComplianceControl(
                "ISO-12.1.1",
                ComplianceFramework.ISO27001,
                "Equipment Inventory",
                "Maintain asset inventory",
                "Automated asset discovery"
            ),
        ]
        
        # Add all controls
        for control in pci_controls + soc2_controls + iso_controls:
            self.controls[control.control_id] = control
    
    def get_framework_status(self, framework: ComplianceFramework) -> Dict:
        """Get compliance status for a framework"""
        
        framework_controls = [c for c in self.controls.values() if c.framework == framework]
        
        completed = len([c for c in framework_controls if c.status == "completed"])
        in_progress = len([c for c in framework_controls if c.status == "in-progress"])
        total = len(framework_controls)
        
        percent_complete = (completed / total * 100) if total > 0 else 0
        
        return {
            "framework": framework.value,
            "total_controls": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": total - completed - in_progress,
            "compliance_percent": round(percent_complete, 1),
            "status": "COMPLIANT" if percent_complete >= 80 else "PARTIAL" if percent_complete >= 50 else "NON-COMPLIANT",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_all_frameworks_status(self) -> Dict:
        """Get status of all frameworks"""
        
        frameworks = [
            ComplianceFramework.PCI_DSS,
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001
        ]
        
        return {
            "pci_dss": self.get_framework_status(ComplianceFramework.PCI_DSS),
            "soc2": self.get_framework_status(ComplianceFramework.SOC2),
            "iso27001": self.get_framework_status(ComplianceFramework.ISO27001),
            "timestamp": datetime.now().isoformat()
        }
    
    def update_control_status(
        self,
        control_id: str,
        status: str,
        evidence: Optional[List[str]] = None
    ) -> bool:
        """Update status of a control"""
        
        if control_id not in self.controls:
            return False
        
        control = self.controls[control_id]
        control.status = status
        control.last_verified = datetime.now().isoformat()
        
        if evidence:
            control.evidence.extend(evidence)
        
        # Log audit trail
        self.audit_logs.append({
            "control_id": control_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "evidence_count": len(control.evidence)
        })
        
        return True
    
    def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        format_type: str = "json"  # json, csv, pdf
    ) -> Dict:
        """Generate compliance report"""
        
        status = self.get_framework_status(framework)
        framework_controls = [c for c in self.controls.values() if c.framework == framework]
        
        controls_details = [c.to_dict() for c in framework_controls]
        
        report = {
            "report_type": f"{framework.value}_compliance",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": {
                "compliance_status": status["status"],
                "compliance_percent": status["compliance_percent"],
                "total_controls": status["total_controls"],
                "completed_controls": status["completed"],
                "action_items": status["total_controls"] - status["completed"]
            },
            "detailed_controls": controls_details,
            "audit_trail": self.audit_logs[-20:],  # Last 20 changes
            "next_audit_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "recommendations": self._generate_recommendations(framework, framework_controls)
        }
        
        return report
    
    def _generate_recommendations(
        self,
        framework: ComplianceFramework,
        controls: List[ComplianceControl]
    ) -> List[str]:
        """Generate recommendations for non-compliant controls"""
        
        recommendations = []
        
        for control in controls:
            if control.status != "completed":
                recommendations.append(
                    f"Complete {control.control_id}: {control.requirement}"
                )
        
        return recommendations[:10]  # Top 10 recommendations
    
    def export_audit_trail(self, days: int = 90) -> List[Dict]:
        """Export audit trail for auditors"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        trail = [
            log for log in self.audit_logs
            if datetime.fromisoformat(log["timestamp"]) >= cutoff_date
        ]
        
        return trail


# Flask endpoints to add to app.py
COMPLIANCE_ENDPOINTS = """
@app.route("/api/compliance/frameworks", methods=["GET"])
def get_compliance_status():
    '''Get compliance status for all frameworks'''
    try:
        dashboard = ComplianceDashboard()
        status = dashboard.get_all_frameworks_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compliance/report/<framework>", methods=["GET"])
def get_compliance_report(framework):
    '''Generate compliance report for a framework'''
    try:
        dashboard = ComplianceDashboard()
        
        framework_enum = ComplianceFramework(framework)
        report = dashboard.generate_compliance_report(framework_enum)
        
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compliance/audit-trail", methods=["GET"])
def get_audit_trail():
    '''Get compliance audit trail'''
    try:
        dashboard = ComplianceDashboard()
        days = request.args.get("days", 90, type=int)
        
        trail = dashboard.export_audit_trail(days)
        
        return jsonify({
            "audit_trail": trail,
            "count": len(trail),
            "period_days": days
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compliance/control/<control_id>", methods=["PUT"])
def update_compliance_control(control_id):
    '''Update compliance control status'''
    try:
        data = request.json
        dashboard = ComplianceDashboard()
        
        result = dashboard.update_control_status(
            control_id=control_id,
            status=data.get("status", "in-progress"),
            evidence=data.get("evidence", [])
        )
        
        return jsonify({
            "status": "success" if result else "failed",
            "control_id": control_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

if __name__ == "__main__":
    # Test example
    dashboard = ComplianceDashboard()
    
    # Get status
    status = dashboard.get_all_frameworks_status()
    print("Compliance Status:", json.dumps(status, indent=2))
    
    # Generate report
    pci_report = dashboard.generate_compliance_report(ComplianceFramework.PCI_DSS)
    print("\nPCI-DSS Report:", json.dumps(pci_report, indent=2)[:500] + "...")
