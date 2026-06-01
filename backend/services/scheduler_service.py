"""
Report Scheduler Service — APScheduler
Runs recurring scan + report + email jobs on a cron schedule.
Supports multiple repos per schedule.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

_schedules: Dict[str, dict] = {}
_scheduler: Optional[object] = None


# ── Frequency helpers ─────────────────────────────────────────────────────────

FREQUENCY_CRONS = {
    'daily':   '0 {hour} * * *',
    'weekly':  '0 {hour} * * 1',       # Every Monday
    'monthly': '0 {hour} 1 * *',       # 1st of month
}

def frequency_to_cron(frequency: str, hour: int = 6) -> str:
    template = FREQUENCY_CRONS.get(frequency, FREQUENCY_CRONS['daily'])
    return template.format(hour=hour)

def cron_to_human(cron: str, frequency: str, hour: int) -> str:
    labels = {
        'daily':   f'Every day at {hour:02d}:00',
        'weekly':  f'Every Monday at {hour:02d}:00',
        'monthly': f'1st of each month at {hour:02d}:00',
    }
    return labels.get(frequency, cron)

def next_run_estimate(frequency: str, hour: int, timezone: str) -> str:
    """Return an ISO string estimate of the next run."""
    try:
        now = datetime.utcnow()
        if frequency == 'daily':
            candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if candidate <= now:
                candidate += timedelta(days=1)
        elif frequency == 'weekly':
            days_ahead = (0 - now.weekday()) % 7  # 0 = Monday
            candidate = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=0, second=0, microsecond=0)
            if candidate <= now:
                candidate += timedelta(weeks=1)
        elif frequency == 'monthly':
            if now.day == 1 and now.hour < hour:
                candidate = now.replace(day=1, hour=hour, minute=0, second=0, microsecond=0)
            else:
                month = now.month % 12 + 1
                year = now.year + (1 if now.month == 12 else 0)
                candidate = now.replace(year=year, month=month, day=1, hour=hour, minute=0, second=0, microsecond=0)
        else:
            candidate = now + timedelta(days=1)
        return candidate.isoformat()
    except Exception:
        return ''


# ── Job executor ──────────────────────────────────────────────────────────────

def _run_scheduled_report(schedule_id: str):
    """Scan all repos in a schedule, generate and email a combined report."""
    schedule = _schedules.get(schedule_id)
    if not schedule:
        return

    repo_paths = schedule.get('repo_paths', [schedule.get('repo_path', '')])
    recipients = schedule.get('recipients', [schedule.get('email', '')])

    print(f"[SCHEDULER] Running schedule '{schedule.get('label')}' — {len(repo_paths)} repo(s)")
    _schedules[schedule_id]['last_run'] = datetime.now().isoformat()
    _schedules[schedule_id]['last_status'] = 'running'

    try:
        from core.scanner_legacy import RepositoryChat
        from core.scoring import MultiDimensionalScorer
        from core.compliance import ComplianceEngine
        from core.reporter import build_html_report, build_pdf_report
        from services.email_service import send_report_email

        now_str = datetime.now().strftime('%Y-%m-%d')
        errors = []

        for repo_path in repo_paths:
            try:
                repo_name = repo_path.split('/')[-1] if repo_path else 'unknown'
                print(f"[SCHEDULER]   Scanning {repo_name}…")

                chat = RepositoryChat(repo_path)
                artifacts = chat.scan()

                risk_profile = None
                try:
                    risk_profile = MultiDimensionalScorer().score(artifacts)
                except Exception as e:
                    print(f"[SCHEDULER]   Risk score failed: {e}")

                compliance_report = None
                try:
                    compliance_report = ComplianceEngine().check(artifacts)
                except Exception as e:
                    print(f"[SCHEDULER]   Compliance failed: {e}")

                session_id = f"sched-{schedule_id[:6]}-{repo_name[:8]}"
                html = build_html_report(session_id=session_id, repo_name=repo_name,
                                         artifacts=artifacts, risk_profile=risk_profile,
                                         compliance_report=compliance_report)
                pdf = build_pdf_report(session_id=session_id, repo_name=repo_name,
                                       artifacts=artifacts, risk_profile=risk_profile,
                                       compliance_report=compliance_report)

                for recipient in recipients:
                    result = send_report_email(
                        to=recipient,
                        subject=f'CodeViz Report — {repo_name} ({now_str})',
                        html_body=html,
                        pdf_bytes=pdf,
                        pdf_filename=f'codeviz-{repo_name}-{now_str}.pdf',
                    )
                    if not result.get('success'):
                        errors.append(f"{repo_name}: {result.get('error')}")
                    else:
                        print(f"[SCHEDULER]   Sent to {recipient} ✓")

            except Exception as e:
                errors.append(f"{repo_path}: {str(e)[:80]}")
                print(f"[SCHEDULER]   Error on {repo_path}: {e}")

        status = 'success' if not errors else f'partial: {"; ".join(errors[:2])}'
        _schedules[schedule_id]['last_status'] = status
        _schedules[schedule_id]['last_run'] = datetime.now().isoformat()
        print(f"[SCHEDULER] Schedule complete: {status}")

    except Exception as e:
        _schedules[schedule_id]['last_status'] = f'error: {str(e)[:100]}'
        print(f"[SCHEDULER] Fatal error: {e}")


# ── Public API ────────────────────────────────────────────────────────────────

def get_scheduler():
    global _scheduler
    if not SCHEDULER_AVAILABLE:
        return None
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone='UTC')
        _scheduler.start()
    return _scheduler


def add_schedule(
    repo_paths: List[str],
    recipients: List[str],
    frequency: str = 'daily',          # daily | weekly | monthly
    hour: int = 6,
    label: str = '',
    timezone: str = 'UTC',
    cron_expression: str = '',          # overrides frequency if provided
    # legacy compat
    repo_path: str = '',
    email: str = '',
) -> dict:
    # Legacy single-repo compat
    if repo_path and not repo_paths:
        repo_paths = [repo_path]
    if email and not recipients:
        recipients = [email]

    schedule_id = str(uuid.uuid4())[:12]
    cron = cron_expression or frequency_to_cron(frequency, hour)

    schedule = {
        'id': schedule_id,
        'repo_paths': repo_paths,
        'recipients': recipients,
        'frequency': frequency,
        'hour': hour,
        'cron': cron,
        'label': label or f'Auto-scan ({frequency})',
        'timezone': timezone,
        'human_schedule': cron_to_human(cron, frequency, hour),
        'next_run': next_run_estimate(frequency, hour, timezone),
        'created_at': datetime.now().isoformat(),
        'last_run': None,
        'last_status': None,
        # legacy
        'repo_path': repo_paths[0] if repo_paths else '',
        'email': recipients[0] if recipients else '',
    }
    _schedules[schedule_id] = schedule

    scheduler = get_scheduler()
    if scheduler and SCHEDULER_AVAILABLE:
        try:
            parts = cron.strip().split()
            minute, hour_c, day, month, dow = parts if len(parts) == 5 else ('0','6','*','*','*')
            scheduler.add_job(
                _run_scheduled_report,
                CronTrigger(minute=minute, hour=hour_c, day=day,
                            month=month, day_of_week=dow, timezone=timezone),
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
    if schedule_id not in _schedules:
        return {'success': False, 'error': 'Schedule not found'}
    try:
        _run_scheduled_report(schedule_id)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}
