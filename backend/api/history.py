"""
Scan History API

Persists a lightweight snapshot after every scan so CodeViz can:
  - Show posture score trends over time
  - Compare scans across repos
  - Drive the "Recent Scans" table on the dashboard

Storage: SQLite (same DB as repo cache, no extra dependencies).

Endpoints
---------
POST /api/history/record/<session_id>   Save snapshot for this session
GET  /api/history/recent                Last 20 scans (all repos)
GET  /api/history/repo/<repo_name>      All scans for one repo (trend data)
DELETE /api/history/<record_id>         Remove a single record
"""

import json
import sqlite3
import os
from datetime import datetime

from flask import request
from . import history_bp
from utils import format_success_response, format_error_response, get_repo_path, get_session_context


# ── DB helpers ───────────────────────────────────────────────────────────────

def _db_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'instance', 'codeviz.db')


def _get_conn():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name   TEXT    NOT NULL,
            repo_name        TEXT    NOT NULL,
            session_id       TEXT,
            scanned_at       TEXT    NOT NULL,
            posture_score    REAL    DEFAULT 0,
            critical_count   INTEGER DEFAULT 0,
            high_count       INTEGER DEFAULT 0,
            medium_count     INTEGER DEFAULT 0,
            low_count        INTEGER DEFAULT 0,
            total_issues     INTEGER DEFAULT 0,
            refactor_count   INTEGER DEFAULT 0,
            smell_count      INTEGER DEFAULT 0,
            perf_count       INTEGER DEFAULT 0,
            compliance_score REAL    DEFAULT 0,
            extra_json       TEXT    DEFAULT '{}'
        )
    """)
    conn.commit()


def _row_to_dict(row) -> dict:
    d = dict(row)
    try:
        d['extra'] = json.loads(d.pop('extra_json', '{}') or '{}')
    except Exception:
        d['extra'] = {}
    return d


# ── Internal: build snapshot from session context ────────────────────────────

def _build_snapshot(session_id: str) -> dict | None:
    """
    Pull live data from the session context and return a snapshot dict.
    Returns None if the session doesn't exist.
    """
    try:
        from api.chat import repo_chats
        if session_id not in repo_chats:
            return None

        chat      = repo_chats[session_id]
        context   = get_session_context(chat)
        repo_path = get_repo_path(chat)
        repo_name = (repo_path or '').rstrip('/').split('/')[-1] if repo_path else 'unknown'
        repo_full = context.get('repo_full_name') or f'local/{repo_name}'

        # Security counts
        sec_issues = context.get('security_issues') or []
        sev_map    = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for issue in sec_issues:
            s = str(issue.get('severity', 'low')).lower()
            for lvl in ('critical', 'high', 'medium', 'low'):
                if lvl in s:
                    sev_map[lvl] += 1
                    break

        # Posture score (from scoring context if available)
        posture = context.get('posture_score') or context.get('composite_score') or 0
        if not posture:
            # Derive a rough score from issue counts
            raw = sev_map['critical'] * 15 + sev_map['high'] * 5 + sev_map['medium'] * 2
            posture = max(0, min(100, 100 - raw))

        # Other counts
        refactor_count   = len(context.get('refactoring_opportunities') or [])
        smell_count      = len(context.get('code_smells') or [])
        perf_issues      = context.get('performance_issues') or []
        perf_count       = len(perf_issues) if isinstance(perf_issues, list) else 0
        compliance_score = context.get('compliance_score') or 0

        return {
            'repo_full_name':  repo_full,
            'repo_name':       repo_name,
            'session_id':      session_id,
            'posture_score':   round(float(posture), 1),
            'critical_count':  sev_map['critical'],
            'high_count':      sev_map['high'],
            'medium_count':    sev_map['medium'],
            'low_count':       sev_map['low'],
            'total_issues':    len(sec_issues),
            'refactor_count':  refactor_count,
            'smell_count':     smell_count,
            'perf_count':      perf_count,
            'compliance_score': round(float(compliance_score), 1),
        }
    except Exception as e:
        print(f"[history] snapshot build error: {e}")
        return None


# ── Routes ───────────────────────────────────────────────────────────────────

@history_bp.route('/record/<session_id>', methods=['POST'])
def record_scan(session_id):
    """
    Save a scan snapshot for this session.
    Accepts an optional JSON body to override individual fields
    (e.g. posture_score if the frontend has a more accurate value).
    """
    try:
        snapshot = _build_snapshot(session_id)
        if snapshot is None:
            return format_error_response('Session not found')[0], 404

        # Allow frontend overrides (e.g. posture_score from the scoring service)
        body = request.get_json(silent=True) or {}
        for key in ('posture_score', 'repo_full_name', 'compliance_score'):
            if key in body:
                snapshot[key] = body[key]

        conn = _get_conn()
        _ensure_table(conn)
        conn.execute("""
            INSERT INTO scan_history
                (repo_full_name, repo_name, session_id, scanned_at,
                 posture_score, critical_count, high_count, medium_count, low_count,
                 total_issues, refactor_count, smell_count, perf_count,
                 compliance_score, extra_json)
            VALUES
                (:repo_full_name, :repo_name, :session_id, :scanned_at,
                 :posture_score, :critical_count, :high_count, :medium_count, :low_count,
                 :total_issues, :refactor_count, :smell_count, :perf_count,
                 :compliance_score, :extra_json)
        """, {
            **snapshot,
            'scanned_at':  datetime.utcnow().isoformat(),
            'extra_json':  '{}',
        })
        conn.commit()
        record_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()

        print(f"[history] Recorded scan #{record_id} for {snapshot['repo_full_name']} "
              f"(score={snapshot['posture_score']})")
        return format_success_response({
            'record_id':    record_id,
            'repo':         snapshot['repo_full_name'],
            'posture_score': snapshot['posture_score'],
        }, 'Scan recorded')[0], 201

    except Exception as e:
        return format_error_response(str(e))[0], 500


@history_bp.route('/recent', methods=['GET'])
def recent_scans():
    """Return the last N scans across all repos."""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        conn  = _get_conn()
        _ensure_table(conn)
        rows  = conn.execute("""
            SELECT * FROM scan_history
            ORDER BY scanned_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return format_success_response({
            'scans': [_row_to_dict(r) for r in rows],
            'count': len(rows),
        })[0], 200
    except Exception as e:
        return format_error_response(str(e))[0], 500


@history_bp.route('/repo/<path:repo_name>', methods=['GET'])
def repo_history(repo_name):
    """Return all scans for a specific repo (used for trend charts)."""
    try:
        limit = min(int(request.args.get('limit', 30)), 200)
        conn  = _get_conn()
        _ensure_table(conn)
        rows  = conn.execute("""
            SELECT * FROM scan_history
            WHERE repo_full_name = ? OR repo_name = ?
            ORDER BY scanned_at ASC
            LIMIT ?
        """, (repo_name, repo_name, limit)).fetchall()
        conn.close()

        scans = [_row_to_dict(r) for r in rows]

        # Compute trend direction
        trend = None
        if len(scans) >= 2:
            delta = scans[-1]['posture_score'] - scans[-2]['posture_score']
            trend = 'improving' if delta > 1 else 'declining' if delta < -1 else 'stable'

        return format_success_response({
            'repo':  repo_name,
            'scans': scans,
            'count': len(scans),
            'trend': trend,
            'latest_score': scans[-1]['posture_score'] if scans else None,
        })[0], 200
    except Exception as e:
        return format_error_response(str(e))[0], 500


@history_bp.route('/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Remove a single history record."""
    try:
        conn = _get_conn()
        _ensure_table(conn)
        conn.execute('DELETE FROM scan_history WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        return format_success_response(None, f'Record {record_id} deleted')[0], 200
    except Exception as e:
        return format_error_response(str(e))[0], 500


@history_bp.route('/stats', methods=['GET'])
def global_stats():
    """Aggregate stats across all scan history (used for landing page / overview)."""
    try:
        conn = _get_conn()
        _ensure_table(conn)
        row = conn.execute("""
            SELECT
                COUNT(*)                    AS total_scans,
                COUNT(DISTINCT repo_full_name) AS repos_scanned,
                AVG(posture_score)          AS avg_posture,
                SUM(critical_count)         AS total_criticals_fixed,
                MAX(scanned_at)             AS last_scan_at
            FROM scan_history
        """).fetchone()
        conn.close()
        return format_success_response(dict(row) if row else {})[0], 200
    except Exception as e:
        return format_error_response(str(e))[0], 500
