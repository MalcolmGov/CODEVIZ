"""
session_store.py — thin persistence layer for in-memory repo_chats.

Usage
-----
    from core.session_store import save_session, load_all_sessions, cache_result, get_cached

save_session(session_id, chat)          # call after creating a chat
cache_result(session_id, key, data)     # call after each analyser run
get_cached(session_id, key)             # returns cached data or None
load_all_sessions()                     # returns dict[session_id → stub] on startup
"""

import json
from datetime import datetime

_app = None  # set in bootstrap


def _db():
    from extensions import db
    return db


def _model():
    from models.scan_session import ScanSession
    return ScanSession


def _repo_path(chat) -> str:
    if hasattr(chat, 'repo_path'):
        return str(chat.repo_path)
    if isinstance(chat, dict):
        return chat.get('repo_path', '')
    return ''


def _repo_name(chat) -> str:
    if hasattr(chat, '_original_url'):
        url = chat._original_url
        if url:
            return url.rstrip('/').split('/')[-1]
    path = _repo_path(chat)
    return path.rstrip('/').split('/')[-1] if path else ''


def save_session(session_id: str, chat):
    """Upsert a session record from a live chat object."""
    try:
        from flask import current_app
        with current_app.app_context():
            db = _db()
            ScanSession = _model()
            rec = ScanSession.query.filter_by(session_id=session_id).first()
            if not rec:
                rec = ScanSession(session_id=session_id)
                db.session.add(rec)
            rec.repo_path = _repo_path(chat)
            rec.repo_name = _repo_name(chat)
            rec.repo_url  = getattr(chat, '_original_url', None)
            rec.touch()
            db.session.commit()
    except Exception as e:
        print(f"⚠️  session_store.save_session: {e}")


def cache_result(session_id: str, key: str, data):
    """Persist an analyser result (JSON-serialisable) against a session."""
    try:
        from flask import current_app
        with current_app.app_context():
            db = _db()
            ScanSession = _model()
            rec = ScanSession.query.filter_by(session_id=session_id).first()
            if rec:
                rec.set_cache(key, data)
                rec.touch()
                db.session.commit()
    except Exception as e:
        print(f"⚠️  session_store.cache_result({key}): {e}")


def get_cached(session_id: str, key: str):
    """Return cached analyser result, or None."""
    try:
        from flask import current_app
        with current_app.app_context():
            ScanSession = _model()
            rec = ScanSession.query.filter_by(session_id=session_id).first()
            if rec:
                return rec.get_cache(key)
    except Exception as e:
        print(f"⚠️  session_store.get_cached({key}): {e}")
    return None


def delete_session(session_id: str):
    """Remove a persisted session."""
    try:
        from flask import current_app
        with current_app.app_context():
            db = _db()
            ScanSession = _model()
            rec = ScanSession.query.filter_by(session_id=session_id).first()
            if rec:
                db.session.delete(rec)
                db.session.commit()
    except Exception as e:
        print(f"⚠️  session_store.delete_session: {e}")


def load_all_sessions() -> dict:
    """
    On startup: load all persisted sessions from DB.
    Returns a dict of session_id → lightweight stub (dict with repo_path/context).
    Callers can use this to rehydrate repo_chats.
    """
    stubs = {}
    try:
        from flask import current_app
        with current_app.app_context():
            ScanSession = _model()
            records = ScanSession.query.order_by(ScanSession.last_accessed.desc()).limit(100).all()
            for rec in records:
                stubs[rec.session_id] = {
                    'repo_path':  rec.repo_path,
                    'repo_name':  rec.repo_name,
                    'is_scanned': True,
                    'context':    rec.get_context(),
                    '_persisted': True,
                }
            print(f"✅ Restored {len(stubs)} scan sessions from DB")
    except Exception as e:
        print(f"⚠️  session_store.load_all_sessions: {e}")
    return stubs


def list_sessions() -> list:
    """Return a list of all persisted sessions (for API use)."""
    try:
        from flask import current_app
        with current_app.app_context():
            ScanSession = _model()
            return [r.to_dict() for r in
                    ScanSession.query.order_by(ScanSession.last_accessed.desc()).limit(50).all()]
    except Exception as e:
        print(f"⚠️  session_store.list_sessions: {e}")
        return []
