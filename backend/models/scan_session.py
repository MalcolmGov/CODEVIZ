"""
ScanSession model — persists in-memory repo_chats to SQLite.

Stores: session_id, repo_path, repo_name, scan context (JSON),
        last_accessed, created_at.
On startup, the chat API rehydrates repo_chats from this table so
sessions survive backend restarts.
"""

from extensions import db
from datetime import datetime
import json


class ScanSession(db.Model):
    __tablename__ = 'scan_sessions'

    id           = db.Column(db.Integer, primary_key=True)
    session_id   = db.Column(db.String(64), unique=True, nullable=False, index=True)
    repo_path    = db.Column(db.String(500), nullable=False)
    repo_name    = db.Column(db.String(255))
    repo_url     = db.Column(db.String(500))

    # JSON-serialised scan context (security bugs, dependencies, etc.)
    context_json = db.Column(db.Text, default='{}')

    # Lightweight result caches (JSON) for each analyser
    security_json     = db.Column(db.Text)
    performance_json  = db.Column(db.Text)
    smells_json       = db.Column(db.Text)
    threats_json      = db.Column(db.Text)
    cve_json          = db.Column(db.Text)
    remediation_json  = db.Column(db.Text)

    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_context(self) -> dict:
        try:
            return json.loads(self.context_json or '{}')
        except Exception:
            return {}

    def set_context(self, ctx: dict):
        self.context_json = json.dumps(ctx, default=str)

    def get_cache(self, key: str):
        raw = getattr(self, f'{key}_json', None)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    def set_cache(self, key: str, data):
        setattr(self, f'{key}_json', json.dumps(data, default=str))

    def touch(self):
        self.last_accessed = datetime.utcnow()

    def to_dict(self):
        return {
            'session_id':   self.session_id,
            'repo_path':    self.repo_path,
            'repo_name':    self.repo_name,
            'repo_url':     self.repo_url,
            'created_at':   self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
        }
