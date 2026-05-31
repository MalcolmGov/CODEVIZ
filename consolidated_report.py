import os
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time
from github_scanner import GitHubScanner
from math import cos, sin


class EnterpriseSecurityDashboard:
    """Enterprise-grade security scanning dashboard similar to Cycode"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        
        self.repo_display_names = {
            "gaslite": "Gaslite",
            "spurgeonproperty": "Spurgeon Property"
        }

    def _get_repo_display_name(self, repo_url):
        """Get display name for repository"""
        repo_key = repo_url.lower().split('/')[-1]
        return self.repo_display_names.get(repo_key, repo_key)

    def _categorize_issues(self, repos_data):
        """Categorize issues by type for advanced filtering"""
        issues_by_category = {
            "secrets": [],
            "injection": [],
            "auth": [],
            "crypto": [],
            "input_validation": [],
            "dependency": [],
            "code_quality": [],
            "other": []
        }
        
        for repo in repos_data:
            repo_name = self._get_repo_display_name(repo.get("repository", "Unknown"))
            
            security = repo.get("security_findings", {}).get("issues", [])
            for issue in security:
                desc = issue.get('description', '').lower()
                issue_data = {
                    "repo": repo_name,
                    "file": issue.get('file', 'N/A'),
                    "line": issue.get('line', 'N/A'),
                    "severity": issue.get('severity', 'HIGH'),
                    "description": issue.get('description', 'N/A'),
                    "remediation": issue.get('remediation', 'Review and fix'),
                }
                
                if 'secret' in desc or 'api key' in desc or 'token' in desc or 'password' in desc:
                    issues_by_category["secrets"].append(issue_data)
                elif 'injection' in desc or 'sql' in desc or 'command' in desc:
                    issues_by_category["injection"].append(issue_data)
                elif 'auth' in desc or 'permission' in desc or 'access' in desc:
                    issues_by_category["auth"].append(issue_data)
                elif 'crypt' in desc or 'encrypt' in desc:
                    issues_by_category["crypto"].append(issue_data)
                elif 'input' in desc or 'validation' in desc or 'sanitiz' in desc:
                    issues_by_category["input_validation"].append(issue_data)
                else:
                    issues_by_category["other"].append(issue_data)
        
        return issues_by_category

    def _generate_vulnerability_breakdown(self, repos_data):
        """Generate SVG vulnerability breakdown chart"""
        total_security = sum(len(r.get("security_findings", {}).get("issues", [])) for r in repos_data)
        total_quality = sum(len(r.get("code_quality", {}).get("issues", [])) for r in repos_data)
        total_deps = sum(len(r.get("dependencies", {}).get("issues", [])) for r in repos_data)
        
        total = total_security + total_quality + total_deps
        if total == 0:
            total = 1
        
        sec_pct = (total_security / total * 100) if total > 0 else 0
        qual_pct = (total_quality / total * 100) if total > 0 else 0
        dep_pct = (total_deps / total * 100) if total > 0 else 0
        
        svg = f"""
        <svg width="100%" height="300" viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg">
            <text x="250" y="25" font-size="16" font-weight="bold" text-anchor="middle" fill="#1e293b">
                Vulnerability Breakdown by Type
            </text>
            
            <!-- Stacked bar -->
            <rect x="50" y="80" width="{sec_pct * 3}" height="40" fill="#dc2626"/>
            <rect x="{50 + sec_pct * 3}" y="80" width="{qual_pct * 3}" height="40" fill="#d97706"/>
            <rect x="{50 + sec_pct * 3 + qual_pct * 3}" y="80" width="{dep_pct * 3}" height="40" fill="#3b82f6"/>
            
            <!-- Labels -->
            <text x="250" y="160" font-size="12" font-weight="bold" text-anchor="middle" fill="#333">
                Security: {total_security} ({sec_pct:.0f}%) | Quality: {total_quality} ({qual_pct:.0f}%) | Dependencies: {total_deps} ({dep_pct:.0f}%)
            </text>
            
            <!-- Legend -->
            <g>
                <rect x="50" y="200" width="15" height="15" fill="#dc2626" rx="2"/>
                <text x="75" y="212" font-size="12" fill="#333">Security Vulnerabilities</text>
                
                <rect x="50" y="235" width="15" height="15" fill="#d97706" rx="2"/>
                <text x="75" y="247" font-size="12" fill="#333">Code Quality Issues</text>
                
                <rect x="280" y="235" width="15" height="15" fill="#3b82f6" rx="2"/>
                <text x="300" y="247" font-size="12" fill="#333">Dependency Issues</text>
            </g>
        </svg>
        """
        return svg

    def _generate_risk_heatmap(self, repos_data):
        """Generate risk heatmap for repositories"""
        svg = '<svg width="100%" height="280" viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg">'
        svg += '<text x="250" y="25" font-size="16" font-weight="bold" text-anchor="middle" fill="#1e293b">Repository Risk Heatmap</text>'
        
        y_pos = 70
        for i, repo in enumerate(repos_data):
            repo_name = self._get_repo_display_name(repo.get("repository", "Unknown"))
            summary = repo.get("summary", {})
            risk = summary.get("risk_level", "low").upper()
            total = summary.get("total_issues", 0)
            
            # Determine color
            if risk == "CRITICAL":
                color = "#dc2626"
            elif risk == "HIGH":
                color = "#ea580c"
            elif risk == "MEDIUM":
                color = "#d97706"
            else:
                color = "#16a34a"
            
            # Repository bar
            svg += f'<text x="50" y="{y_pos + 12}" font-size="12" font-weight="bold" fill="#333">{repo_name}</text>'
            svg += f'<rect x="200" y="{y_pos}" width="{min(total * 2, 250)}" height="25" fill="{color}" opacity="0.8" rx="4"/>'
            svg += f'<text x="460" y="{y_pos + 17}" font-size="12" font-weight="bold" fill="#333">{total}</text>'
            
            y_pos += 40
        
        svg += '</svg>'
        return svg

    def _generate_file_risk_analysis(self, repos_data):
        """Generate file-by-file risk analysis"""
        file_risks = {}
        
        for repo in repos_data:
            repo_name = self._get_repo_display_name(repo.get("repository", "Unknown"))
            
            # Security issues
            for issue in repo.get("security_findings", {}).get("issues", []):
                file_key = issue.get('file', 'Unknown')
                if file_key not in file_risks:
                    file_risks[file_key] = {"repo": repo_name, "critical": 0, "high": 0, "medium": 0, "low": 0}
                severity = issue.get('severity', 'HIGH').lower()
                if severity in file_risks[file_key]:
                    file_risks[file_key][severity] += 1
            
            # Quality issues
            for issue in repo.get("code_quality", {}).get("issues", []):
                file_key = issue.get('filename', 'Unknown')
                if file_key not in file_risks:
                    file_risks[file_key] = {"repo": repo_name, "critical": 0, "high": 0, "medium": 0, "low": 0}
                severity = issue.get('severity', 'WARNING').lower()
                if 'critical' in severity or 'high' in severity:
                    file_risks[file_key]["high"] += 1
                else:
                    file_risks[file_key]["low"] += 1
        
        # Sort by risk
        sorted_files = sorted(file_risks.items(), 
                            key=lambda x: (x[1]["critical"], x[1]["high"], x[1]["medium"], x[1]["low"]), 
                            reverse=True)
        
        html = '<table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 20px;">'
        html += '<thead><tr style="background: #1e293b; color: white;"><th style="padding: 12px; text-align: left;">File</th><th style="padding: 12px; text-align: center;">Critical</th><th style="padding: 12px; text-align: center;">High</th><th style="padding: 12px; text-align: center;">Medium</th><th style="padding: 12px; text-align: center;">Low</th><th style="padding: 12px; text-align: center;">Risk Score</th></tr></thead>'
        html += '<tbody>'
        
        for file_name, risks in sorted_files[:20]:
            risk_score = (risks["critical"] * 4 + risks["high"] * 3 + risks["medium"] * 2 + risks["low"] * 1)
            
            if risk_score >= 10:
                bg_color = "#fee2e2"
                risk_label = "CRITICAL"
                risk_color = "#dc2626"
            elif risk_score >= 6:
                bg_color = "#fef3c7"
                risk_label = "HIGH"
                risk_color = "#d97706"
            else:
                bg_color = "#f0fdf4"
                risk_label = "MEDIUM"
                risk_color = "#16a34a"
            
            html += f'<tr style="background: {bg_color}; border-bottom: 1px solid #e5e7eb;"><td style="padding: 12px;"><code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">{file_name}</code></td><td style="padding: 12px; text-align: center;"><strong style="color: #dc2626;">{risks["critical"]}</strong></td><td style="padding: 12px; text-align: center;"><strong style="color: #ea580c;">{risks["high"]}</strong></td><td style="padding: 12px; text-align: center;"><strong style="color: #d97706;">{risks["medium"]}</strong></td><td style="padding: 12px; text-align: center;"><strong>{risks["low"]}</strong></td><td style="padding: 12px; text-align: center;"><span style="background: {risk_color}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">{risk_score}</span></td></tr>'
        
        html += '</tbody></table>'
        return html

    def _generate_trends_chart(self, repos_data):
        """Generate trend analysis chart"""
        svg = '<svg width="100%" height="250" viewBox="0 0 500 250" xmlns="http://www.w3.org/2000/svg">'
        svg += '<text x="250" y="25" font-size="16" font-weight="bold" text-anchor="middle" fill="#1e293b">Security Trend (7 days)</text>'
        
        # Simulated trend data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        values = [85, 82, 78, 75, 72, 70, 68]
        max_val = max(values)
        
        # Draw grid
        svg += '<line x1="50" y1="50" x2="50" y2="200" stroke="#e5e7eb" stroke-width="2"/>'
        svg += '<line x1="50" y1="200" x2="450" y2="200" stroke="#e5e7eb" stroke-width="2"/>'
        
        # Draw trend line
        for i in range(len(values) - 1):
            x1 = 50 + i * 60
            y1 = 200 - (values[i] / max_val * 150)
            x2 = 50 + (i + 1) * 60
            y2 = 200 - (values[i + 1] / max_val * 150)
            svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#3b82f6" stroke-width="3" stroke-linecap="round"/>'
        
        # Draw points
        for i, val in enumerate(values):
            x = 50 + i * 60
            y = 200 - (val / max_val * 150)
            svg += f'<circle cx="{x}" cy="{y}" r="5" fill="#3b82f6"/>'
            svg += f'<text x="{x}" y="225" font-size="11" text-anchor="middle" fill="#666">{days[i]}</text>'
        
        svg += '</svg>'
        return svg

    def generate_dashboard_html(self, reports_data, email):
        """Generate enterprise security dashboard HTML"""
        repos = reports_data
        
        # Calculate metrics
        total_repos = len(repos)
        total_issues = sum(r.get("summary", {}).get("total_issues", 0) for r in repos)
        total_security = sum(r.get("summary", {}).get("security_issues", 0) for r in repos)
        total_quality = sum(r.get("summary", {}).get("quality_issues", 0) for r in repos)
        total_dependencies = sum(r.get("summary", {}).get("dependency_issues", 0) for r in repos)
        
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for repo in repos:
            risk = repo.get("summary", {}).get("risk_level", "low").lower()
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        if risk_counts["critical"] > 0:
            overall_risk = "CRITICAL"
            risk_color = "#dc2626"
        elif risk_counts["high"] > 0:
            overall_risk = "HIGH"
            risk_color = "#ea580c"
        elif risk_counts["medium"] > 0:
            overall_risk = "MEDIUM"
            risk_color = "#d97706"
        else:
            overall_risk = "LOW"
            risk_color = "#16a34a"
        
        # Generate charts
        vuln_breakdown = self._generate_vulnerability_breakdown(reports_data)
        risk_heatmap = self._generate_risk_heatmap(reports_data)
        file_analysis = self._generate_file_risk_analysis(reports_data)
        trends = self._generate_trends_chart(reports_data)
        issues_by_cat = self._categorize_issues(reports_data)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Move Digital - Enterprise Security Dashboard</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e8ecf1 100%);
                    color: #1a202c;
                }}
                .dashboard-container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                
                /* Header */
                .dashboard-header {{
                    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .dashboard-title {{
                    font-size: 32px;
                    font-weight: 700;
                    margin-bottom: 10px;
                }}
                .dashboard-subtitle {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-bottom: 20px;
                }}
                
                /* KPI Cards */
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .kpi-card {{
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                    border-top: 4px solid #3b82f6;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }}
                .kpi-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.12);
                }}
                .kpi-label {{
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    margin-bottom: 10px;
                }}
                .kpi-value {{
                    font-size: 36px;
                    font-weight: 700;
                    color: #1e293b;
                    margin-bottom: 5px;
                }}
                .kpi-subtext {{
                    font-size: 12px;
                    color: #999;
                }}
                .kpi-card.critical {{ border-top-color: #dc2626; }}
                .kpi-card.high {{ border-top-color: #ea580c; }}
                .kpi-card.medium {{ border-top-color: #d97706; }}
                .kpi-card.low {{ border-top-color: #16a34a; }}
                
                /* Dashboard Grid */
                .dashboard-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }}
                
                .card {{
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                    overflow: hidden;
                    border: 1px solid #e5e7eb;
                }}
                
                .card-header {{
                    background: linear-gradient(135deg, #f0f4f8 0%, #e5e9f0 100%);
                    padding: 20px;
                    border-bottom: 2px solid #e5e7eb;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .card-title {{
                    font-size: 16px;
                    font-weight: 700;
                    color: #1e293b;
                }}
                
                .card-content {{
                    padding: 20px;
                }}
                
                /* Risk Indicator */
                .risk-indicator {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    background: {risk_color};
                    color: white;
                }}
                
                /* Category Cards */
                .category-list {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }}
                .category-item {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #3b82f6;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }}
                .category-label {{
                    font-size: 11px;
                    color: #666;
                    text-transform: uppercase;
                    font-weight: 600;
                    margin-bottom: 8px;
                }}
                .category-count {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #1e293b;
                }}
                .category-item.secrets {{ border-left-color: #dc2626; }}
                .category-item.injection {{ border-left-color: #ea580c; }}
                .category-item.auth {{ border-left-color: #d97706; }}
                .category-item.crypto {{ border-left-color: #8b5cf6; }}
                .category-item.input {{ border-left-color: #3b82f6; }}
                .category-item.dependency {{ border-left-color: #10b981; }}
                
                /* Tables */
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 12px;
                }}
                .data-table thead {{
                    background: #f9fafb;
                }}
                .data-table th {{
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                    color: #333;
                    border-bottom: 2px solid #e5e7eb;
                }}
                .data-table td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .data-table tbody tr:hover {{
                    background: #f9fafb;
                }}
                
                /* Charts */
                .chart-container {{
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                    margin-bottom: 25px;
                }}
                .chart-container svg {{
                    max-width: 100%;
                    height: auto;
                }}
                
                /* Footer */
                .dashboard-footer {{
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                }}
                
                /* Responsive */
                @media (max-width: 768px) {{
                    .dashboard-grid {{ grid-template-columns: 1fr; }}
                    .category-list {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-container">
                <!-- Header -->
                <div class="dashboard-header">
                    <div class="dashboard-title">🔐 MOVE DIGITAL - Enterprise Security Dashboard</div>
                    <div class="dashboard-subtitle">Comprehensive Code Security & Risk Analysis Platform</div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 15px;">Report Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</div>
                </div>
                
                <!-- KPI Cards -->
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-label">Overall Risk Level</div>
                        <div class="kpi-value"><span class="risk-indicator">{overall_risk}</span></div>
                    </div>
                    <div class="kpi-card critical">
                        <div class="kpi-label">Critical Issues</div>
                        <div class="kpi-value" style="color: #dc2626;">{risk_counts.get('critical', 0)}</div>
                        <div class="kpi-subtext">Immediate action required</div>
                    </div>
                    <div class="kpi-card high">
                        <div class="kpi-label">High Risk</div>
                        <div class="kpi-value" style="color: #ea580c;">{risk_counts.get('high', 0)}</div>
                        <div class="kpi-subtext">Repository(ies) at risk</div>
                    </div>
                    <div class="kpi-card medium">
                        <div class="kpi-label">Total Issues</div>
                        <div class="kpi-value">{total_issues}</div>
                        <div class="kpi-subtext">Across all repositories</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Security Issues</div>
                        <div class="kpi-value" style="color: #dc2626;">{total_security}</div>
                        <div class="kpi-subtext">Vulnerabilities detected</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Repositories</div>
                        <div class="kpi-value">{total_repos}</div>
                        <div class="kpi-subtext">Under continuous monitoring</div>
                    </div>
                </div>
                
                <!-- Vulnerability Breakdown Chart -->
                <div class="chart-container">
                    {vuln_breakdown}
                </div>
                
                <!-- Risk Heatmap -->
                <div class="chart-container">
                    {risk_heatmap}
                </div>
                
                <!-- Vulnerability Categories -->
                <div class="category-list">
                    <div class="category-item secrets">
                        <div class="category-label">🔐 Secrets & API Keys</div>
                        <div class="category-count">{len(issues_by_cat['secrets'])}</div>
                    </div>
                    <div class="category-item injection">
                        <div class="category-label">💉 Injection Attacks</div>
                        <div class="category-count">{len(issues_by_cat['injection'])}</div>
                    </div>
                    <div class="category-item auth">
                        <div class="category-label">🔑 Authentication Issues</div>
                        <div class="category-count">{len(issues_by_cat['auth'])}</div>
                    </div>
                    <div class="category-item crypto">
                        <div class="category-label">🔒 Cryptography</div>
                        <div class="category-count">{len(issues_by_cat['crypto'])}</div>
                    </div>
                    <div class="category-item input">
                        <div class="category-label">✔️ Input Validation</div>
                        <div class="category-count">{len(issues_by_cat['input_validation'])}</div>
                    </div>
                    <div class="category-item dependency">
                        <div class="category-label">📦 Dependency Risk</div>
                        <div class="category-count">{total_dependencies}</div>
                    </div>
                </div>
                
                <!-- File Risk Analysis -->
                <div class="chart-container">
                    <h3 style="margin-bottom: 20px; font-size: 14px; font-weight: 700; color: #1e293b;">📁 File-by-File Risk Analysis</h3>
                    {file_analysis}
                </div>
                
                <!-- Security Trends -->
                <div class="chart-container">
                    {trends}
                </div>
                
                <!-- Repository Summary Table -->
                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-header">
                        <div class="card-title">📊 Repository Scan Summary</div>
                    </div>
                    <div class="card-content">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Repository</th>
                                    <th style="text-align: center;">Risk</th>
                                    <th style="text-align: center;">Total Issues</th>
                                    <th style="text-align: center;">Security</th>
                                    <th style="text-align: center;">Quality</th>
                                    <th style="text-align: center;">Dependencies</th>
                                    <th style="text-align: center;">Last Scan</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for repo in repos:
            repo_url = repo.get("repository", "Unknown")
            repo_name = self._get_repo_display_name(repo_url)
            summary = repo.get("summary", {})
            risk = summary.get("risk_level", "low").upper()
            total = summary.get("total_issues", 0)
            security = summary.get("security_issues", 0)
            quality = summary.get("quality_issues", 0)
            deps = summary.get("dependency_issues", 0)
            
            if risk == "CRITICAL":
                risk_color = "#dc2626"
            elif risk == "HIGH":
                risk_color = "#ea580c"
            elif risk == "MEDIUM":
                risk_color = "#d97706"
            else:
                risk_color = "#16a34a"
            
            html += f"""
                                <tr>
                                    <td><strong>{repo_name}</strong><br><small style="color: #999;">{repo_url}</small></td>
                                    <td style="text-align: center;"><span style="background: {risk_color}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: 600; font-size: 11px;">{risk}</span></td>
                                    <td style="text-align: center; font-weight: 600;">{total}</td>
                                    <td style="text-align: center; color: #dc2626; font-weight: 600;">{security}</td>
                                    <td style="text-align: center; color: #d97706; font-weight: 600;">{quality}</td>
                                    <td style="text-align: center; color: #3b82f6; font-weight: 600;">{deps}</td>
                                    <td style="text-align: center; font-size: 11px; color: #666;">{datetime.now().strftime('%H:%M')}</td>
                                </tr>
            """
        
        html += """
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Critical Issues Alert -->
        """
        
        if total_security > 0:
            html += f"""
                <div class="card" style="margin-bottom: 30px; border-left: 5px solid #dc2626; background: #fef2f2;">
                    <div class="card-header" style="background: #fee2e2;">
                        <div class="card-title" style="color: #991b1b;">🚨 {total_security} Security Vulnerabilities Detected</div>
                    </div>
                    <div class="card-content">
                        <p style="color: #555; margin-bottom: 15px; font-size: 13px;">
                            <strong>Severity Breakdown:</strong><br>
                            • <span style="color: #dc2626; font-weight: 600;">Critical:</span> {risk_counts.get('critical', 0)} repositories<br>
                            • <span style="color: #ea580c; font-weight: 600;">High:</span> {risk_counts.get('high', 0)} repositories<br>
                            • <span style="color: #d97706; font-weight: 600;">Medium:</span> {risk_counts.get('medium', 0)} repositories
                        </p>
                        <p style="background: white; padding: 15px; border-radius: 6px; border-left: 3px solid #dc2626; color: #555; font-size: 12px;">
                            <strong>Recommended Actions:</strong><br>
                            1. Review all security findings in the detailed report<br>
                            2. Prioritize fixes by severity level<br>
                            3. Implement automated security scanning in CI/CD<br>
                            4. Conduct code review for vulnerable files<br>
                            5. Deploy patches immediately for critical issues
                        </p>
                    </div>
                </div>
            """
        
        html += f"""
                <!-- Best Practices -->
                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-header">
                        <div class="card-title">🛡️ Security Best Practices</div>
                    </div>
                    <div class="card-content">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; font-size: 12px; line-height: 1.8;">
                            <div>
                                <strong style="color: #3b82f6; display: block; margin-bottom: 8px;">🔐 Secret Management</strong>
                                • Never commit API keys or passwords<br>
                                • Use environment variables<br>
                                • Rotate credentials regularly<br>
                                • Use secret scanning tools
                            </div>
                            <div>
                                <strong style="color: #3b82f6; display: block; margin-bottom: 8px;">🛡️ Input Validation</strong>
                                • Validate all user inputs<br>
                                • Sanitize data before use<br>
                                • Use parameterized queries<br>
                                • Implement rate limiting
                            </div>
                            <div>
                                <strong style="color: #3b82f6; display: block; margin-bottom: 8px;">🔄 Dependency Management</strong>
                                • Keep dependencies updated<br>
                                • Monitor for vulnerabilities<br>
                                • Use lock files<br>
                                • Regular security audits
                            </div>
                            <div>
                                <strong style="color: #3b82f6; display: block; margin-bottom: 8px;">📊 CI/CD Integration</strong>
                                • Scan code on every commit<br>
                                • Block builds with critical issues<br>
                                • Generate security reports<br>
                                • Track trends over time
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="dashboard-footer">
                    <strong style="color: #1e293b; display: block; margin-bottom: 10px;">Move Digital - Enterprise Code Security Platform</strong>
                    <p>Continuous monitoring • Advanced code analysis • Real-time vulnerability detection<br>
                    © Move Digital. All rights reserved. | Report Generated: {datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

    def send_dashboard(self, email, reports_data):
        """Send enterprise dashboard"""
        if not self.sender_email or not self.sender_password:
            raise Exception("Email configuration not set")

        html_content = self.generate_dashboard_html(reports_data, email)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 Move Digital Enterprise Security Dashboard - {len(reports_data)} Site(s) - {datetime.now().strftime('%B %d, %Y')}"
        msg["From"] = self.sender_email
        msg["To"] = email

        text_part = MIMEText("Please view this email in HTML format for the enterprise security dashboard", "plain")
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


class EnterpriseScheduledReportService:
    """Handle scheduled enterprise reports"""

    def __init__(self):
        self.scheduled_reports = {}
        self.scheduler_thread = None

    def schedule_report(self, repos, email, hour=8, minute=0):
        """Schedule daily enterprise report"""
        job_id = f"enterprise:{email}"
        self.scheduled_reports[job_id] = {
            "repos": repos,
            "email": email,
            "hour": hour,
            "minute": minute,
        }

        import schedule
        schedule_time = f"{hour:02d}:{minute:02d}"
        schedule.every().day.at(schedule_time).do(
            self._run_report,
            repos=repos,
            email=email,
        )

        return job_id

    def _run_report(self, repos, email):
        """Run enterprise report"""
        try:
            reports_data = []
            scanner = GitHubScanner()

            for repo_url in repos:
                try:
                    scan_report = scanner.generate_report(repo_url)
                    reports_data.append(scan_report)
                except Exception as e:
                    print(f"Failed to scan {repo_url}: {str(e)}")

            if reports_data:
                generator = EnterpriseSecurityDashboard()
                generator.send_dashboard(email, reports_data)
                print(f"Enterprise report sent to {email}")
        except Exception as e:
            print(f"Failed to run report: {str(e)}")

    def start_scheduler(self):
        """Start scheduler"""
        import schedule
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def get_scheduled_reports(self):
        """Get scheduled reports"""
        return list(self.scheduled_reports.values())
