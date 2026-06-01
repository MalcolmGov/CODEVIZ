"""
Database Models for CodeViz

Using SQLAlchemy ORM for all data persistence.
"""

from extensions import db
from datetime import datetime
import enum


class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    avatar_url = db.Column(db.String(500))
    github_token = db.Column(db.String(500))  # Should be encrypted in production
    
    # Relationships
    repositories = db.relationship('Repository', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'github_id': self.github_id,
            'created_at': self.created_at.isoformat()
        }


class Repository(db.Model):
    """Repository model"""
    __tablename__ = 'repositories'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    github_url = db.Column(db.String(500), nullable=False)
    default_branch = db.Column(db.String(100), default='main')
    
    last_scanned = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')  # active, archived, scanning
    
    # Relationships
    scans = db.relationship('Scan', backref='repository', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('owner_id', 'name', name='unique_owner_repo'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'github_url': self.github_url,
            'default_branch': self.default_branch,
            'last_scanned': self.last_scanned.isoformat() if self.last_scanned else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Scan(db.Model):
    """Repository scan model"""
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    
    branch = db.Column(db.String(100), default='main')
    commit_hash = db.Column(db.String(40))
    
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    total_issues = db.Column(db.Integer, default=0)
    
    # Relationships
    issues = db.relationship('Issue', backref='scan', lazy=True, cascade='all, delete-orphan')
    refactorings = db.relationship('Refactoring', backref='scan', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'branch': self.branch,
            'commit_hash': self.commit_hash,
            'status': self.status,
            'total_issues': self.total_issues,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class IssueSeverity(enum.Enum):
    """Issue severity levels"""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class IssueType(enum.Enum):
    """Issue types"""
    SECURITY = 'security'
    QUALITY = 'quality'
    PERFORMANCE = 'performance'
    SMELL = 'code_smell'


class Issue(db.Model):
    """Code issue model"""
    __tablename__ = 'issues'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    
    type = db.Column(db.Enum(IssueType), nullable=False)
    severity = db.Column(db.Enum(IssueSeverity), nullable=False)
    
    file = db.Column(db.String(500))
    line = db.Column(db.Integer)
    code = db.Column(db.Text)
    message = db.Column(db.Text, nullable=False)
    
    cve = db.Column(db.String(100))  # CVE reference if applicable
    confidence = db.Column(db.Float, default=1.0)  # 0.0 to 1.0
    
    fixed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'type': self.type.value,
            'severity': self.severity.value,
            'file': self.file,
            'line': self.line,
            'message': self.message,
            'cve': self.cve,
            'confidence': self.confidence,
            'fixed': self.fixed
        }


class Refactoring(db.Model):
    """Refactoring opportunity model"""
    __tablename__ = 'refactorings'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    
    type = db.Column(db.String(100), nullable=False)  # extract_method, simplify_conditional, etc
    priority = db.Column(db.Integer, default=5)  # 1-10 scale
    
    file = db.Column(db.String(500))
    line = db.Column(db.Integer)
    
    current_code = db.Column(db.Text)
    suggested_code = db.Column(db.Text)
    tests = db.Column(db.Text)
    
    explanation = db.Column(db.Text)
    confidence = db.Column(db.Float, default=1.0)  # 0.0 to 1.0
    
    applied = db.Column(db.Boolean, default=False)
    
    # Relationship to PR if created
    pr_id = db.Column(db.Integer, db.ForeignKey('pull_requests.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'type': self.type,
            'priority': self.priority,
            'file': self.file,
            'line': self.line,
            'explanation': self.explanation,
            'confidence': self.confidence,
            'applied': self.applied
        }


class PullRequest(db.Model):
    """Pull request model"""
    __tablename__ = 'pull_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    
    github_pr_number = db.Column(db.Integer)
    github_pr_url = db.Column(db.String(500))
    github_branch = db.Column(db.String(100))
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    status = db.Column(db.String(50), default='draft')  # draft, open, merged, closed
    
    # Relationships
    refactorings = db.relationship('Refactoring', backref='pull_request', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    merged_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'title': self.title,
            'status': self.status,
            'github_pr_number': self.github_pr_number,
            'github_pr_url': self.github_pr_url,
            'created_at': self.created_at.isoformat(),
            'merged_at': self.merged_at.isoformat() if self.merged_at else None
        }
