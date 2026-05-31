"""
Advanced Risk Scoring Algorithm for Move Digital
Calculate business-contextual risk scores for security findings
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import math


class DataSensitivity(Enum):
    """Data sensitivity levels for asset tagging"""
    PUBLIC = 1
    INTERNAL = 2
    CONFIDENTIAL = 3
    SECRET = 4  # PII, Financial data, etc.


class RiskScoring:
    """Calculate comprehensive risk scores based on multiple factors"""
    
    def __init__(self):
        self.repositories = {}
        self.risk_history = []
    
    def tag_repository(
        self,
        repo_name: str,
        repo_url: str,
        data_sensitivity: DataSensitivity,
        criticality: str = "medium",  # low, medium, high, critical
        tags: List[str] = None
    ) -> Dict:
        """Tag a repository with business context"""
        
        if tags is None:
            tags = []
        
        repo_context = {
            "name": repo_name,
            "url": repo_url,
            "data_sensitivity": data_sensitivity.value,
            "data_sensitivity_name": data_sensitivity.name,
            "criticality": criticality,
            "tags": tags,
            "tagged_at": datetime.now().isoformat()
        }
        
        self.repositories[repo_name] = repo_context
        return repo_context
    
    def calculate_risk_score(
        self,
        repo_name: str,
        severity: str,  # critical, high, medium, low
        exploitability: str = "medium",  # low, medium, high, critical
        affected_files: List[str] = None,
        cvss_score: float = 0.0
    ) -> Dict:
        """Calculate business-contextual risk score"""
        
        if affected_files is None:
            affected_files = []
        
        # Get repository context
        repo_context = self.repositories.get(repo_name, {})
        data_sensitivity = repo_context.get("data_sensitivity", DataSensitivity.INTERNAL.value)
        criticality = repo_context.get("criticality", "medium")
        
        # Severity score (0-40 points)
        severity_scores = {
            "critical": 40,
            "high": 30,
            "medium": 20,
            "low": 10
        }
        severity_score = severity_scores.get(severity.lower(), 10)
        
        # Exploitability score (0-30 points)
        exploitability_scores = {
            "critical": 30,
            "high": 22,
            "medium": 15,
            "low": 8
        }
        exploitability_score = exploitability_scores.get(exploitability.lower(), 15)
        
        # Data sensitivity impact (0-20 points)
        sensitivity_multiplier = data_sensitivity / 4.0
        data_impact = 20 * sensitivity_multiplier
        
        # Criticality impact (0-10 points)
        criticality_scores = {
            "low": 2,
            "medium": 5,
            "high": 7,
            "critical": 10
        }
        criticality_score = criticality_scores.get(criticality.lower(), 5)
        
        # CVSS score override (0-100)
        if cvss_score > 0:
            base_score = cvss_score
        else:
            base_score = severity_score + exploitability_score + data_impact + criticality_score
        
        # Normalize to 0-100 scale
        final_score = min(base_score, 100)
        
        # Determine risk level
        if final_score >= 85:
            risk_level = "CRITICAL"
        elif final_score >= 70:
            risk_level = "HIGH"
        elif final_score >= 50:
            risk_level = "MEDIUM"
        elif final_score >= 25:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        risk_data = {
            "repository": repo_name,
            "severity": severity,
            "exploitability": exploitability,
            "data_sensitivity": repo_context.get("data_sensitivity_name", "INTERNAL"),
            "criticality": criticality,
            "affected_files": affected_files,
            "affected_file_count": len(affected_files),
            "severity_score": severity_score,
            "exploitability_score": exploitability_score,
            "data_impact_score": data_impact,
            "criticality_score": criticality_score,
            "cvss_score": cvss_score,
            "final_risk_score": round(final_score, 1),
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat(),
            "recommendation": self._get_recommendation(risk_level, final_score)
        }
        
        self.risk_history.append(risk_data)
        return risk_data
    
    def _get_recommendation(self, risk_level: str, score: float) -> str:
        """Generate recommendation based on risk level"""
        
        recommendations = {
            "CRITICAL": f"Fix immediately within 24 hours (Risk: {score}). This issue can directly impact business operations.",
            "HIGH": f"Fix within 1 week (Risk: {score}). Prioritize in your sprint planning.",
            "MEDIUM": f"Fix within 2 weeks (Risk: {score}). Plan for next iteration.",
            "LOW": f"Fix when possible (Risk: {score}). Include in backlog.",
            "MINIMAL": f"Monitor (Risk: {score}). Address in regular maintenance cycles."
        }
        
        return recommendations.get(risk_level, "Review and prioritize accordingly.")
    
    def calculate_repository_risk_profile(self, repo_name: str, issues: List[Dict]) -> Dict:
        """Calculate overall risk profile for a repository"""
        
        if not issues:
            return {
                "repository": repo_name,
                "total_issues": 0,
                "overall_risk_score": 0,
                "risk_level": "MINIMAL",
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "weighted_average_score": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        scores = []
        risk_levels = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "MINIMAL": 0}
        
        for issue in issues:
            score = self.calculate_risk_score(
                repo_name=repo_name,
                severity=issue.get("severity", "medium"),
                exploitability=issue.get("exploitability", "medium"),
                affected_files=issue.get("files", []),
                cvss_score=issue.get("cvss_score", 0.0)
            )
            scores.append(score["final_risk_score"])
            risk_levels[score["risk_level"]] += 1
        
        # Calculate weighted average (higher scores weighted more)
        weighted_sum = sum(s ** 1.5 for s in scores)
        weight_count = len(scores)
        weighted_average = (weighted_sum / weight_count) ** (1/1.5) if weight_count > 0 else 0
        
        # Determine overall risk level
        if risk_levels["CRITICAL"] > 0:
            overall_level = "CRITICAL"
        elif risk_levels["HIGH"] > 2 or (risk_levels["HIGH"] > 0 and weighted_average >= 70):
            overall_level = "HIGH"
        elif risk_levels["MEDIUM"] > 5 or (risk_levels["MEDIUM"] > 0 and weighted_average >= 50):
            overall_level = "MEDIUM"
        elif risk_levels["LOW"] > 0:
            overall_level = "LOW"
        else:
            overall_level = "MINIMAL"
        
        return {
            "repository": repo_name,
            "total_issues": len(issues),
            "overall_risk_score": round(weighted_average, 1),
            "risk_level": overall_level,
            "critical_count": risk_levels["CRITICAL"],
            "high_count": risk_levels["HIGH"],
            "medium_count": risk_levels["MEDIUM"],
            "low_count": risk_levels["LOW"],
            "minimal_count": risk_levels["MINIMAL"],
            "weighted_average_score": round(weighted_average, 1),
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_roi_savings(self, repo_name: str, risk_score: float) -> Dict:
        """Calculate estimated ROI from fixing an issue"""
        
        # Estimation model:
        # Critical issue fixed = prevents avg $50k in incident costs
        # High = prevents avg $10k
        # Medium = prevents avg $2k
        # Low = prevents avg $500
        
        if risk_score >= 85:
            incident_cost = 50000
            fix_time_hours = 8
        elif risk_score >= 70:
            incident_cost = 10000
            fix_time_hours = 4
        elif risk_score >= 50:
            incident_cost = 2000
            fix_time_hours = 2
        else:
            incident_cost = 500
            fix_time_hours = 1
        
        hourly_rate = 100  # Standard rate
        fix_cost = fix_time_hours * hourly_rate
        
        roi = incident_cost - fix_cost
        roi_percentage = (roi / fix_cost * 100) if fix_cost > 0 else 0
        
        return {
            "repository": repo_name,
            "risk_score": risk_score,
            "estimated_incident_cost": f"${incident_cost:,.0f}",
            "fix_time_hours": fix_time_hours,
            "fix_cost": f"${fix_cost:,.0f}",
            "estimated_roi": f"${roi:,.0f}",
            "roi_percentage": f"{roi_percentage:.0f}%",
            "message": f"Fixing this issue saves approximately ${roi:,.0f} in potential incident costs"
        }


# Flask endpoints to add to app.py
RISK_SCORING_ENDPOINTS = """
@app.route("/api/risk/tag-repository", methods=["POST"])
def tag_repository():
    '''Tag a repository with business context'''
    try:
        data = request.json
        scorer = RiskScoring()
        
        result = scorer.tag_repository(
            repo_name=data.get("repo_name", ""),
            repo_url=data.get("repo_url", ""),
            data_sensitivity=DataSensitivity(data.get("data_sensitivity", 2)),
            criticality=data.get("criticality", "medium"),
            tags=data.get("tags", [])
        )
        
        return jsonify({
            "status": "success",
            "repository_context": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/risk/calculate", methods=["POST"])
def calculate_risk():
    '''Calculate risk score for an issue'''
    try:
        data = request.json
        scorer = RiskScoring()
        
        result = scorer.calculate_risk_score(
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
def get_repo_risk_profile():
    '''Get risk profile for a repository'''
    try:
        data = request.json
        scorer = RiskScoring()
        
        result = scorer.calculate_repository_risk_profile(
            repo_name=data.get("repo_name", ""),
            issues=data.get("issues", [])
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/risk/roi-savings", methods=["POST"])
def get_roi_savings():
    '''Calculate ROI from fixing an issue'''
    try:
        data = request.json
        scorer = RiskScoring()
        
        result = scorer.calculate_roi_savings(
            repo_name=data.get("repo_name", ""),
            risk_score=data.get("risk_score", 0)
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

if __name__ == "__main__":
    # Test example
    scorer = RiskScoring()
    
    # Tag repositories
    scorer.tag_repository(
        "spurgeon-property",
        "github.com/MalcolmGov/SpurgeonProperty",
        DataSensitivity.SECRET,  # Processes payments
        criticality="critical",
        tags=["payment-processing", "production", "pci-dss"]
    )
    
    # Calculate risk for an issue
    risk = scorer.calculate_risk_score(
        repo_name="spurgeon-property",
        severity="high",
        exploitability="high",
        affected_files=["payment_handler.py", "api/checkout.py"],
        cvss_score=7.5
    )
    
    print("Risk Score:", json.dumps(risk, indent=2))
    
    # Calculate ROI
    roi = scorer.calculate_roi_savings("spurgeon-property", risk["final_risk_score"])
    print("\nROI Savings:", json.dumps(roi, indent=2))
