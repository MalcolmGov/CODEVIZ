"""
CodeViz Report Generator
Produces professional HTML (email body) + PDF (attachment) reports covering:
  - Scan Summary
  - Multi-Dimensional Risk Score
  - Security Vulnerabilities
  - Compliance (OWASP, SOC2, PCI-DSS, GDPR)
"""

from datetime import datetime
from typing import Dict, Any, Optional
import io


# ─── HTML Email Template ──────────────────────────────────────────────────────

def _score_color(score: float) -> str:
    if score >= 80: return '#10b981'
    if score >= 60: return '#f59e0b'
    return '#ef4444'

def _status_badge(status: str) -> str:
    colors = {
        'pass': ('#10b981', '#052e16'),
        'fail': ('#ef4444', '#1c0606'),
        'warn': ('#f59e0b', '#1c1005'),
        'info': ('#94a3b8', '#0f172a'),
    }
    fg, bg = colors.get(status, colors['info'])
    return (f'<span style="background:{bg};color:{fg};padding:2px 8px;'
            f'border-radius:4px;font-size:11px;font-weight:700;'
            f'font-family:monospace;text-transform:uppercase;">{status}</span>')

def _sev_badge(severity: str) -> str:
    colors = {
        'critical': ('#ef4444', '#1c0606'),
        'high':     ('#f97316', '#1c0a06'),
        'medium':   ('#f59e0b', '#1c1005'),
        'low':      ('#94a3b8', '#0f172a'),
    }
    fg, bg = colors.get(severity, colors['low'])
    return (f'<span style="background:{bg};color:{fg};padding:2px 8px;'
            f'border-radius:4px;font-size:11px;font-weight:700;'
            f'font-family:monospace;text-transform:uppercase;">{severity}</span>')


def build_html_report(
    session_id: str,
    repo_name: str,
    artifacts: Dict,
    risk_profile: Optional[Dict] = None,
    compliance_report: Optional[Dict] = None,
    security_bugs: Optional[list] = None,
) -> str:
    now = datetime.now().strftime('%B %d, %Y at %H:%M')
    stats = artifacts.get('statistics', {})

    # ── Scan summary section ──────────────────────────────────────────────────
    def stat_card(label, value):
        return f'''
        <td style="padding:8px;text-align:center;background:#1e293b;border-radius:8px;margin:4px;">
          <div style="font-size:22px;font-weight:800;color:#e2e8f0;font-family:monospace;">{value}</div>
          <div style="font-size:11px;color:#94a3b8;margin-top:2px;text-transform:uppercase;letter-spacing:.05em;">{label}</div>
        </td>'''

    scan_cards = ''.join([
        stat_card('Files', len(artifacts.get('files', []))),
        stat_card('APIs', len(artifacts.get('apis', []))),
        stat_card('Classes', len(artifacts.get('classes', []))),
        stat_card('Functions', len(artifacts.get('functions', []))),
        stat_card('Models', len(artifacts.get('models', []))),
        stat_card('Dependencies', len(artifacts.get('dependencies', []))),
    ])

    # ── Risk score section ────────────────────────────────────────────────────
    risk_html = ''
    if risk_profile:
        comp = risk_profile.get('composite', {})
        dims = risk_profile.get('dimensions', [])
        color = _score_color(comp.get('score', 0))
        risk_html = f'''
        <tr><td colspan="2">
          <h2 style="color:#e2e8f0;font-size:16px;margin:24px 0 12px;border-bottom:1px solid #334155;padding-bottom:8px;">
            🏆 Multi-Dimensional Risk Score
          </h2>
          <table width="100%" cellpadding="0" cellspacing="8"><tr>
            <td style="text-align:center;padding:16px;background:#1e293b;border-radius:12px;width:120px;">
              <div style="font-size:40px;font-weight:900;color:{color};font-family:monospace;">{comp.get('score', 0):.0f}</div>
              <div style="font-size:24px;font-weight:700;color:{color};">{comp.get('grade','?')}</div>
              <div style="font-size:11px;color:#64748b;margin-top:4px;">Composite</div>
            </td>
            <td style="padding-left:16px;">
              <table width="100%" cellpadding="4">
        '''
        for d in dims:
            dc = _score_color(d['score'])
            bar_w = int(d['score'])
            risk_html += f'''
                <tr>
                  <td style="color:#94a3b8;font-size:12px;width:140px;">{d['name']}</td>
                  <td>
                    <div style="background:#0f172a;border-radius:4px;height:8px;overflow:hidden;">
                      <div style="background:{dc};width:{bar_w}%;height:100%;border-radius:4px;"></div>
                    </div>
                  </td>
                  <td style="color:{dc};font-size:12px;font-weight:700;font-family:monospace;width:50px;text-align:right;">
                    {d['score']:.0f}
                  </td>
                  <td style="color:#64748b;font-size:11px;width:30px;text-align:right;">{d['grade']}</td>
                </tr>'''
        risk_html += '''
              </table>
            </td>
          </tr></table>
        </td></tr>'''

    # ── Compliance section ────────────────────────────────────────────────────
    compliance_html = ''
    if compliance_report:
        frameworks = compliance_report.get('frameworks', {})
        compliance_html = '''
        <tr><td colspan="2">
          <h2 style="color:#e2e8f0;font-size:16px;margin:24px 0 12px;border-bottom:1px solid #334155;padding-bottom:8px;">
            🛡️ Compliance Status
          </h2>
          <table width="100%" cellpadding="8" cellspacing="4">
            <tr>
        '''
        for fw_id, fw in frameworks.items():
            color = _score_color(fw['score'])
            s = fw.get('summary', {})
            compliance_html += f'''
              <td style="text-align:center;background:#1e293b;border-radius:8px;padding:12px;">
                <div style="font-size:11px;color:#94a3b8;margin-bottom:4px;">{fw.get('icon','')} {fw['name']}</div>
                <div style="font-size:28px;font-weight:800;color:{color};font-family:monospace;">{fw['score']}%</div>
                <div style="font-size:11px;color:{color};font-weight:700;">{fw.get('grade','?')}</div>
                <div style="font-size:10px;color:#64748b;margin-top:6px;">
                  <span style="color:#ef4444;">{s.get('failed',0)}F</span> &nbsp;
                  <span style="color:#f59e0b;">{s.get('warned',0)}W</span> &nbsp;
                  <span style="color:#10b981;">{s.get('passed',0)}P</span>
                </div>
              </td>'''
        compliance_html += '</tr></table>'

        # Failed controls detail
        has_failures = any(
            c['status'] == 'fail'
            for fw in frameworks.values()
            for c in fw.get('controls', [])
        )
        if has_failures:
            compliance_html += '''
            <h3 style="color:#ef4444;font-size:13px;margin:16px 0 8px;">Critical Failures Requiring Action</h3>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
              <tr style="background:#1e293b;">
                <th style="padding:8px 12px;text-align:left;font-size:11px;color:#64748b;font-weight:600;">ID</th>
                <th style="padding:8px 12px;text-align:left;font-size:11px;color:#64748b;font-weight:600;">Control</th>
                <th style="padding:8px 12px;text-align:left;font-size:11px;color:#64748b;font-weight:600;">Framework</th>
                <th style="padding:8px 12px;text-align:left;font-size:11px;color:#64748b;font-weight:600;">Severity</th>
              </tr>'''
            row = 0
            for fw_id, fw in frameworks.items():
                for c in fw.get('controls', []):
                    if c['status'] == 'fail':
                        bg = '#0f172a' if row % 2 else '#111827'
                        compliance_html += f'''
              <tr style="background:{bg};border-bottom:1px solid #1e293b;">
                <td style="padding:8px 12px;font-size:12px;color:#94a3b8;font-family:monospace;">{c['id']}</td>
                <td style="padding:8px 12px;font-size:12px;color:#e2e8f0;">{c['name']}</td>
                <td style="padding:8px 12px;font-size:12px;color:#6366f1;">{fw['name']}</td>
                <td style="padding:8px 12px;">{_sev_badge(c['severity'])}</td>
              </tr>'''
                        row += 1
            compliance_html += '</table>'
        compliance_html += '</td></tr>'

    # ── Security bugs section ─────────────────────────────────────────────────
    security_html = ''
    if security_bugs:
        critical_bugs = [b for b in security_bugs if 'CRITICAL' in str(b.get('severity', ''))]
        high_bugs = [b for b in security_bugs if 'HIGH' in str(b.get('severity', ''))]
        security_html = f'''
        <tr><td colspan="2">
          <h2 style="color:#e2e8f0;font-size:16px;margin:24px 0 12px;border-bottom:1px solid #334155;padding-bottom:8px;">
            🔴 Security Vulnerabilities
          </h2>
          <table width="100%" cellpadding="8" cellspacing="4"><tr>
            <td style="background:#1c0606;border-radius:8px;text-align:center;padding:16px;">
              <div style="font-size:28px;font-weight:800;color:#ef4444;font-family:monospace;">{len(critical_bugs)}</div>
              <div style="font-size:11px;color:#fca5a5;">Critical</div>
            </td>
            <td style="background:#1c0a06;border-radius:8px;text-align:center;padding:16px;">
              <div style="font-size:28px;font-weight:800;color:#f97316;font-family:monospace;">{len(high_bugs)}</div>
              <div style="font-size:11px;color:#fdba74;">High</div>
            </td>
            <td style="background:#1e293b;border-radius:8px;text-align:center;padding:16px;">
              <div style="font-size:28px;font-weight:800;color:#e2e8f0;font-family:monospace;">{len(security_bugs)}</div>
              <div style="font-size:11px;color:#94a3b8;">Total</div>
            </td>
          </tr></table>
        </td></tr>'''

    # ── Assemble full HTML ────────────────────────────────────────────────────
    overall_score = risk_profile['composite']['score'] if risk_profile else None
    score_color = _score_color(overall_score) if overall_score is not None else '#94a3b8'

    html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>CodeViz Security Report</title></head>
<body style="margin:0;padding:0;background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;">
    <tr><td align="center" style="padding:24px 16px;">
      <table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;">

        <!-- Header -->
        <tr><td style="background:#1e293b;border-radius:12px 12px 0 0;padding:28px 32px;">
          <table width="100%"><tr>
            <td>
              <div style="font-size:22px;font-weight:900;color:#e2e8f0;">
                Code<span style="color:#6366f1;font-weight:500;">Viz</span>
              </div>
              <div style="font-size:13px;color:#64748b;margin-top:4px;">Security & Compliance Report</div>
            </td>
            <td style="text-align:right;">
              {'<div style="font-size:36px;font-weight:900;color:' + score_color + ';font-family:monospace;">' + f"{overall_score:.0f}" + '</div><div style="font-size:11px;color:#64748b;">Overall Score</div>' if overall_score is not None else ''}
            </td>
          </tr></table>
        </td></tr>

        <!-- Meta -->
        <tr><td style="background:#162032;padding:12px 32px;">
          <table width="100%"><tr>
            <td style="font-size:12px;color:#64748b;">Repository: <span style="color:#94a3b8;">{repo_name}</span></td>
            <td style="font-size:12px;color:#64748b;text-align:right;">Generated: <span style="color:#94a3b8;">{now}</span></td>
          </tr></table>
        </td></tr>

        <!-- Body -->
        <tr><td style="background:#0f172a;border-radius:0 0 12px 12px;padding:24px 32px;">
          <table width="100%" cellpadding="0" cellspacing="0">

            <!-- Scan summary -->
            <tr><td colspan="2">
              <h2 style="color:#e2e8f0;font-size:16px;margin:0 0 12px;border-bottom:1px solid #334155;padding-bottom:8px;">
                📊 Scan Summary
              </h2>
              <table width="100%" cellspacing="8"><tr>{scan_cards}</tr></table>
            </td></tr>

            {risk_html}
            {compliance_html}
            {security_html}

            <!-- Footer -->
            <tr><td colspan="2" style="padding-top:32px;border-top:1px solid #1e293b;margin-top:24px;">
              <p style="font-size:11px;color:#334155;margin:0;">
                This report was generated automatically by CodeViz · Session ID: {session_id}
              </p>
            </td></tr>

          </table>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>'''
    return html


# ─── PDF Generator ────────────────────────────────────────────────────────────

def build_pdf_report(
    session_id: str,
    repo_name: str,
    artifacts: Dict,
    risk_profile: Optional[Dict] = None,
    compliance_report: Optional[Dict] = None,
    security_bugs: Optional[list] = None,
) -> bytes:
    """Generate a professional PDF report and return as bytes."""
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        now = datetime.now().strftime('%B %d, %Y at %H:%M')

        # ── Header ────────────────────────────────────────────────────────────
        pdf.set_fill_color(30, 41, 59)   # slate-800
        pdf.rect(0, 0, 210, 40, 'F')

        pdf.set_xy(10, 8)
        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_text_color(226, 232, 240)
        pdf.cell(0, 10, 'CodeViz Security Report', ln=True)

        pdf.set_x(10)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 6, f'Repository: {repo_name}   |   Generated: {now}', ln=True)

        pdf.set_y(48)

        def section_title(title):
            pdf.set_fill_color(15, 23, 42)
            pdf.set_text_color(99, 102, 241)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_x(10)
            pdf.cell(0, 8, title, ln=True)
            pdf.set_draw_color(51, 65, 85)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)

        def row(label, value, indent=10):
            pdf.set_x(indent)
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(148, 163, 184)
            pdf.cell(60, 6, label)
            pdf.set_text_color(226, 232, 240)
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 6, str(value), ln=True)

        # ── Scan Summary ──────────────────────────────────────────────────────
        section_title('Scan Summary')
        stats_data = [
            ('Files scanned', len(artifacts.get('files', []))),
            ('API endpoints', len(artifacts.get('apis', []))),
            ('Classes', len(artifacts.get('classes', []))),
            ('Functions', len(artifacts.get('functions', []))),
            ('Database models', len(artifacts.get('models', []))),
            ('Dependencies', len(artifacts.get('dependencies', []))),
        ]
        for label, val in stats_data:
            row(label, val)
        pdf.ln(6)

        # ── Risk Score ────────────────────────────────────────────────────────
        if risk_profile:
            section_title('Multi-Dimensional Risk Score')
            comp = risk_profile.get('composite', {})
            row('Composite Score', f"{comp.get('score', 0):.0f} / 100")
            row('Grade', comp.get('grade', '?'))
            pdf.ln(2)
            for d in risk_profile.get('dimensions', []):
                row(d['name'], f"{d['score']:.0f}  ({d['grade']})  — Weight: {d['weight']}%", indent=18)
            pdf.ln(6)

        # ── Compliance ────────────────────────────────────────────────────────
        if compliance_report:
            section_title('Compliance Status')
            for fw_id, fw in compliance_report.get('frameworks', {}).items():
                s = fw.get('summary', {})
                row(f"{fw.get('icon','')} {fw['name']} {fw.get('version','')}",
                    f"{fw['score']}%  Grade: {fw.get('grade','?')}  "
                    f"({s.get('passed',0)} passed / {s.get('failed',0)} failed / {s.get('warned',0)} warned)")
            pdf.ln(4)

            # Failed controls
            all_failures = [
                (fw['name'], c)
                for fw in compliance_report.get('frameworks', {}).values()
                for c in fw.get('controls', []) if c['status'] == 'fail'
            ]
            if all_failures:
                pdf.set_x(10)
                pdf.set_font('Helvetica', 'B', 10)
                pdf.set_text_color(239, 68, 68)
                pdf.cell(0, 7, 'Critical Failures:', ln=True)
                for fw_name, c in all_failures:
                    pdf.set_x(18)
                    pdf.set_font('Helvetica', '', 9)
                    pdf.set_text_color(226, 232, 240)
                    pdf.cell(20, 5, c['id'])
                    pdf.set_text_color(148, 163, 184)
                    pdf.cell(80, 5, c['name'][:40])
                    pdf.set_text_color(100, 116, 139)
                    pdf.cell(0, 5, f'[{fw_name}]  Severity: {c["severity"]}', ln=True)
            pdf.ln(6)

        # ── Security Bugs ─────────────────────────────────────────────────────
        if security_bugs:
            section_title('Security Vulnerabilities')
            critical = sum(1 for b in security_bugs if 'CRITICAL' in str(b.get('severity', '')))
            high = sum(1 for b in security_bugs if 'HIGH' in str(b.get('severity', '')))
            row('Total issues', len(security_bugs))
            row('Critical', critical)
            row('High', high)
            pdf.ln(6)

        # ── Footer ────────────────────────────────────────────────────────────
        pdf.set_y(-20)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(0, 6, f'CodeViz Report  |  Session: {session_id}  |  {now}', align='C')

        return pdf.output()

    except ImportError:
        # Fallback: return a minimal text-based PDF placeholder
        return b'%PDF-1.4\n% fpdf2 not installed\n'
