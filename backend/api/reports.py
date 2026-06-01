"""
Reports API Blueprint
POST /api/reports/generate/<session_id>   — generate + return PDF
POST /api/reports/email/<session_id>      — generate + email report
GET  /api/reports/schedules               — list schedules
POST /api/reports/schedules               — create schedule
DELETE /api/reports/schedules/<id>        — delete schedule
POST /api/reports/schedules/<id>/run      — trigger now
"""

from flask import request, Response
from . import reports_bp
from utils import format_success_response, format_error_response
from datetime import datetime


def _gather_data(session_id: str):
    """Collect artifacts, risk profile, compliance, and bugs for a session."""
    from api.chat import repo_chats
    if session_id not in repo_chats:
        return None, 'Session not found — scan a repository first'

    chat = repo_chats[session_id]
    artifacts = (chat.context if hasattr(chat, 'context') and chat.context
                 else chat.get('context', {}) if isinstance(chat, dict) else {})

    if not artifacts:
        return None, 'No scan data found'

    # Risk score
    risk_profile = None
    try:
        from core.scoring import MultiDimensionalScorer
        risk_profile = MultiDimensionalScorer().score(artifacts)
    except Exception:
        pass

    # Compliance
    compliance_report = None
    try:
        from core.compliance import ComplianceEngine
        compliance_report = ComplianceEngine().check(artifacts)
    except Exception:
        pass

    return {
        'session_id': session_id,
        'repo_name': artifacts.get('repo_name', session_id),
        'artifacts': artifacts,
        'risk_profile': risk_profile,
        'compliance_report': compliance_report,
        'security_bugs': [],  # extend when security scanner integrated
    }, None


@reports_bp.route('/generate/<session_id>', methods=['GET', 'POST'])
def generate_report(session_id):
    """Generate and stream a PDF report for download."""
    data, err = _gather_data(session_id)
    if err:
        return format_error_response(err)[0], 404

    try:
        from core.reporter import build_pdf_report
        pdf = build_pdf_report(
            session_id=data['session_id'],
            repo_name=data['repo_name'],
            artifacts=data['artifacts'],
            risk_profile=data['risk_profile'],
            compliance_report=data['compliance_report'],
            security_bugs=data['security_bugs'],
        )
        now = datetime.now().strftime('%Y-%m-%d')
        filename = f"codeviz-{data['repo_name']}-{now}.pdf"
        return Response(
            pdf,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'application/pdf',
            }
        )
    except Exception as e:
        return format_error_response(str(e))[0], 500


@reports_bp.route('/preview/<session_id>', methods=['GET'])
def preview_report(session_id):
    """Return the HTML report body (for in-browser preview)."""
    data, err = _gather_data(session_id)
    if err:
        return format_error_response(err)[0], 404

    try:
        from core.reporter import build_html_report
        html = build_html_report(
            session_id=data['session_id'],
            repo_name=data['repo_name'],
            artifacts=data['artifacts'],
            risk_profile=data['risk_profile'],
            compliance_report=data['compliance_report'],
            security_bugs=data['security_bugs'],
        )
        return Response(html, mimetype='text/html')
    except Exception as e:
        return format_error_response(str(e))[0], 500


@reports_bp.route('/email/<session_id>', methods=['POST'])
def email_report(session_id):
    """Generate and email a report for a session."""
    data, err = _gather_data(session_id)
    if err:
        return format_error_response(err)[0], 404

    body = request.get_json() or {}
    recipient = body.get('email', '').strip()
    if not recipient:
        return format_error_response('email field is required')[0], 400

    try:
        from core.reporter import build_html_report, build_pdf_report
        from services.email_service import send_report_email

        html = build_html_report(**{k: data[k] for k in
                                    ['session_id', 'repo_name', 'artifacts',
                                     'risk_profile', 'compliance_report', 'security_bugs']})
        pdf = build_pdf_report(**{k: data[k] for k in
                                  ['session_id', 'repo_name', 'artifacts',
                                   'risk_profile', 'compliance_report', 'security_bugs']})

        now = datetime.now().strftime('%Y-%m-%d')
        result = send_report_email(
            to=recipient,
            subject=f"CodeViz Security Report — {data['repo_name']} ({now})",
            html_body=html,
            pdf_bytes=pdf,
            pdf_filename=f"codeviz-{data['repo_name']}-{now}.pdf",
        )

        if result.get('success'):
            return format_success_response({'sent_to': recipient}, 'Report emailed')[0], 200
        return format_error_response(result.get('error', 'Email failed'))[0], 500

    except Exception as e:
        return format_error_response(str(e))[0], 500


@reports_bp.route('/schedules', methods=['GET'])
def list_schedules():
    from services.scheduler_service import list_schedules as _list
    return format_success_response({'schedules': _list()})[0], 200


@reports_bp.route('/schedules', methods=['POST'])
def create_schedule():
    """Create a recurring report schedule."""
    body = request.get_json() or {}

    # Support both legacy single and new multi-repo payloads
    repo_paths = body.get('repo_paths') or ([body['repo_path']] if body.get('repo_path') else [])
    recipients = body.get('recipients') or ([body['email']] if body.get('email') else [])
    frequency = body.get('frequency', 'daily').strip()
    hour = int(body.get('hour', 6))
    label = body.get('label', '').strip()
    timezone = body.get('timezone', 'UTC').strip()
    cron = body.get('cron', '').strip()

    if not repo_paths or not recipients:
        return format_error_response('repo_paths and recipients are required')[0], 400

    try:
        from services.scheduler_service import add_schedule
        schedule = add_schedule(
            repo_paths=repo_paths,
            recipients=recipients,
            frequency=frequency,
            hour=hour,
            label=label,
            timezone=timezone,
            cron_expression=cron,
        )
        return format_success_response(schedule, 'Schedule created')[0], 201
    except Exception as e:
        return format_error_response(str(e))[0], 500


@reports_bp.route('/schedules/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    from services.scheduler_service import remove_schedule
    if remove_schedule(schedule_id):
        return format_success_response(None, 'Schedule deleted')[0], 200
    return format_error_response('Schedule not found')[0], 404


@reports_bp.route('/schedules/<schedule_id>/run', methods=['POST'])
def run_schedule_now(schedule_id):
    """Trigger a scheduled report immediately."""
    from services.scheduler_service import run_now
    result = run_now(schedule_id)
    if result.get('success'):
        return format_success_response(None, 'Report triggered')[0], 200
    return format_error_response(result.get('error', 'Failed'))[0], 500
