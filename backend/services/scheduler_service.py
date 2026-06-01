"""
Report Scheduler Service — APScheduler
Runs recurring scan + report + email jobs on a cron schedule.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

# In-memory schedule store (persisted to SQLite in production)
_schedules: Dict[str, dict] = {}
_scheduler: Optional[object] = None


def get_scheduler():
    global _scheduler
    if not SCHEDULER_AVAILABLE:
        return None
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone='UTC')
        _scheduler.start()
    return _scheduler


def _run_scheduled_report(schedule_id: str):
    """Execute a scheduled scan + report + email job."""
    schedule = _schedules.get(schedule_id)
    if not schedule:
        return

    repo_path = schedule['repo_path']
    recipient = schedule['email']

    print(f"[SCHEDULER] Running scheduled report for {repo_path} → {recipient}")

    try:
        # 1. Create a chat session and scan the repo
        from core.scanner_legacy import RepositoryChat
        chat = RepositoryChat(repo_path)
        artifacts = chat.scan()

        # 2. Get risk score
        risk_profile = None
        try:
            from core.scoring import MultiDimensionalScorer
            risk_profile = MultiDimensionalScorer().score(artifacts)
        except Exception as e:
            print(f"[SCHEDULER] Risk score failed: {e}")

        # 3. Get compliance report
        compliance_report = None
        try:
            from core.compliance import ComplianceEngine
            compliance_report = ComplianceEngine().check(artifacts)
        except Exception as e:
            print(f"[SCHEDULER] Compliance check failed: {e}")

        # 4. Generate report
        from core.reporter import build_html_report, build_pdf_report
        repo_name = artifacts.get('repo_name', repo_path.split('/')[-1])
        session_id = f"scheduled-{schedule_id[:8]}"

        html = build_html_report(
            session_id=session_id,
            repo_name=repo_name,
            artifacts=artifacts,
            risk_profile=risk_profile,
            compliance_report=compliance_report,
        )
        pdf = build_pdf_report(
            session_id=session_id,
            repo_name=repo_name,
            artifacts=artifacts,
            risk_profile=risk_profile,
            compliance_report=compliance_report,
        )

        # 5. Send email
        from services.email_service import send_report_email
        now_str = datetime.now().strftime('%Y-%m-%d')
        result = send_report_email(
            to=recipient,
            subject=f'CodeViz Report — {repo_name} ({now_str})',
            html_body=html,
            pdf_bytes=pdf,
            pdf_filename=f'codeviz-{repo_name}-{now_str}.pdf',
        )

        # Update last_run
        _schedules[schedule_id]['last_run'] = datetime.now().isoformat()
        _schedules[schedule_id]['last_status'] = 'success' if result.get('success') else f"failed: {result.get('error')}"
        print(f"[SCHEDULER] Report sent: {result}")

    except Exception as e:
        print(f"[SCHEDULER] Job failed: {e}")
        if schedule_id in _schedules:
            _schedules[schedule_id]['last_status'] = f'error: {str(e)}'


def add_schedule(
    repo_path: str,
    email: str,
    cron_expression: str,        # e.g. "0 6 * * *" for 6am daily
    label: str = '',
    timezone: str = 'UTC',
) -> dict:
    """Add a recurring report schedule. Returns the schedule record."""
    schedule_id = str(uuid.uuid4())[:12]

    schedule = {
        'id': schedule_id,
        'repo_path': repo_path,
        'email': email,
        'cron': cron_expression,
        'label': label or f'Report for {repo_path.split("/")[-1]}',
        'timezone': timezone,
        'created_at': datetime.now().isoformat(),
        'last_run': None,
        'last_status': None,
    }
    _schedules[schedule_id] = schedule

    scheduler = get_scheduler()
    if scheduler and SCHEDULER_AVAILABLE:
        try:
            parts = cron_expression.strip().split()
            if len(parts) == 5:
                minute, hour, day, month, day_of_week = parts
            else:
                minute, hour = '0', '6'
                day = month = day_of_week = '*'

            scheduler.add_job(
                _run_scheduled_report,
                CronTrigger(
                    minute=minute, hour=hour,
                    day=day, month=month,
                    day_of_week=day_of_week,
                    timezone=timezone,
                ),
                args=[schedule_id],
                id=schedule_id,
                replace_existing=True,
                name=schedule['label'],
            )
            schedule['scheduler_status'] = 'active'
        except Exception as e:
            schedule['scheduler_status'] = f'error: {e}'
    else:
        schedule['scheduler_status'] = 'apscheduler_unavailable'

    return schedule


def list_schedules() -> List[dict]:
    return list(_schedules.values())


def get_schedule(schedule_id: str) -> Optional[dict]:
    return _schedules.get(schedule_id)


def remove_schedule(schedule_id: str) -> bool:
    if schedule_id not in _schedules:
        return False
    scheduler = get_scheduler()
    if scheduler and SCHEDULER_AVAILABLE:
        try:
            scheduler.remove_job(schedule_id)
        except Exception:
            pass
    del _schedules[schedule_id]
    return True


def run_now(schedule_id: str) -> dict:
    """Trigger a scheduled job immediately (for testing)."""
    schedule = _schedules.get(schedule_id)
    if not schedule:
        return {'success': False, 'error': 'Schedule not found'}
    try:
        _run_scheduled_report(schedule_id)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}
