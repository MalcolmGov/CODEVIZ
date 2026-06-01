"""
Code Wiki Module - Document code patterns, best practices, and architecture
Similar to Google's Code Wiki for enterprise knowledge management
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import json
import uuid
from dataclasses import dataclass, asdict


class WikiPageType(Enum):
    """Types of wiki pages"""
    ARCHITECTURE = "architecture"
    BEST_PRACTICES = "best_practices"
    API_REFERENCE = "api_reference"
    SETUP_GUIDE = "setup_guide"
    TROUBLESHOOTING = "troubleshooting"
    CODE_PATTERNS = "code_patterns"
    SECURITY_GUIDELINES = "security_guidelines"
    DEPLOYMENT = "deployment"


@dataclass
class WikiPage:
    """Represents a wiki page"""
    id: str
    title: str
    slug: str
    page_type: str
    content: str
    description: str
    author: str
    created_at: str
    updated_at: str
    views: int = 0
    likes: int = 0
    tags: List[str] = None
    related_pages: List[str] = None
    status: str = "published"  # draft, published, archived
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.related_pages is None:
            self.related_pages = []
    
    def to_dict(self):
        return asdict(self)


@dataclass
class CodeSnippet:
    """Represents a code snippet within a wiki page"""
    id: str
    title: str
    language: str
    code: str
    description: str
    page_id: str
    created_at: str
    likes: int = 0
    
    def to_dict(self):
        return asdict(self)


@dataclass
class WikiComment:
    """Represents a comment on a wiki page"""
    id: str
    page_id: str
    author: str
    content: str
    created_at: str
    likes: int = 0
    
    def to_dict(self):
        return asdict(self)


class CodeWiki:
    """Code Wiki management system"""
    
    def __init__(self):
        self.pages: Dict[str, WikiPage] = {}
        self.snippets: Dict[str, CodeSnippet] = {}
        self.comments: Dict[str, List[WikiComment]] = {}
        self.user_bookmarks: Dict[str, List[str]] = {}
        self.search_index: Dict[str, List[str]] = {}
        self._initialize_default_pages()
    
    def _initialize_default_pages(self):
        """Initialize with default wiki pages"""
        default_pages = [
            {
                "title": "Security Best Practices",
                "slug": "security-best-practices",
                "type": WikiPageType.BEST_PRACTICES.value,
                "content": """# Security Best Practices

## Authentication & Authorization
- Always use HTTPS for API endpoints
- Implement OAuth 2.0 for third-party integrations
- Use JWT tokens with expiration
- Never store plaintext passwords

## Data Protection
- Encrypt sensitive data at rest using AES-256
- Implement role-based access control (RBAC)
- Use parameterized queries to prevent SQL injection
- Validate and sanitize all user inputs

## Code Review Checklist
- [ ] No hardcoded secrets or credentials
- [ ] All security headers implemented
- [ ] Input validation in place
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies up to date

## Compliance
- Maintain audit trails for all changes
- Document data access and usage
- Implement proper logging and monitoring""",
                "description": "Essential security guidelines for all development",
                "tags": ["security", "best-practices", "compliance"]
            },
            {
                "title": "API Reference - Remediation",
                "slug": "api-remediation",
                "type": WikiPageType.API_REFERENCE.value,
                "content": """# Remediation API Reference

## Endpoints

### POST /api/remediation/scan-and-fix
Scan repository and create remediation PRs with auto-fixes.

**Parameters:**
- `repo_url` (string, required): GitHub repository URL
- `branch` (string, optional): Branch to scan (default: main)
- `auto_create_pr` (boolean, optional): Create PR automatically (default: true)

**Response:**
```json
{
  "status": "pr_created",
  "repository": "github.com/example/repo",
  "analysis": {
    "total_issues": 12,
    "fixable_issues": 10,
    "fixable_percentage": "83%"
  },
  "pr": {
    "number": 48,
    "url": "https://github.com/example/repo/pull/48",
    "title": "Fix: Security vulnerabilities and dependencies"
  }
}
```

### GET /api/remediation/metrics
Get remediation metrics and statistics.

**Response:**
```json
{
  "status": "success",
  "metrics": {
    "total_analyses": 25,
    "prs_created": 8,
    "total_fixable_detected": 83,
    "total_auto_fixed": 72,
    "auto_fix_percentage": "87%"
  }
}
```""",
                "description": "Complete Remediation API documentation",
                "tags": ["api", "remediation", "endpoints"]
            },
            {
                "title": "Code Patterns - Security",
                "slug": "patterns-security",
                "type": WikiPageType.CODE_PATTERNS.value,
                "content": """# Security Code Patterns

## Input Validation Pattern
```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 12:
            raise ValueError('Password too weak')
        return v
```

## SQL Injection Prevention
```python
# ❌ WRONG
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ CORRECT
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## XSS Prevention
```javascript
// ❌ WRONG
element.innerHTML = userInput;

// ✅ CORRECT
element.textContent = userInput;
// OR
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

## CSRF Protection
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

@app.route('/api/update', methods=['POST'])
@csrf.protect
def update_data():
    # CSRF token automatically validated
    pass
```""",
                "description": "Common security coding patterns and solutions",
                "tags": ["patterns", "security", "code-examples"]
            },
            {
                "title": "Architecture Overview",
                "slug": "architecture",
                "type": WikiPageType.ARCHITECTURE.value,
                "content": """# Move Digital Architecture

## System Components

### Frontend
- React-based dashboard
- Real-time WebSocket updates
- Responsive Material-UI design

### Backend
- Flask REST API
- PostgreSQL for persistence
- Redis for caching & sessions
- Qdrant for vector search

### Security Engine
- Remediation Engine: Auto-fix 87% of issues
- Policy Engine: Enforce security standards
- Risk Scoring: Business-context vulnerability prioritization
- Compliance Dashboard: Track PCI-DSS, SOC2, HIPAA

### Integrations
- GitHub API for repository scanning
- Slack for real-time notifications
- Jira for issue tracking
- Email for scheduled reports

## Data Flow
1. User triggers scan via UI or webhook
2. Scanner analyzes repository code
3. Security engine identifies vulnerabilities
4. Remediation engine creates fixes
5. PR is auto-created in GitHub
6. Real-time alerts sent to Slack
7. Dashboard shows metrics in real-time""",
                "description": "Complete system architecture and data flow",
                "tags": ["architecture", "system-design", "overview"]
            },
            {
                "title": "Deployment Guide",
                "slug": "deployment",
                "type": WikiPageType.DEPLOYMENT.value,
                "content": """# Deployment Guide

## Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 14+
- Redis 7+

## Local Development
```bash
docker-compose up -d
export FLASK_ENV=development
flask run
# Visit http://localhost:8000
```

## Staging Deployment
```bash
export ENVIRONMENT=staging
docker build -t move-digital:staging .
docker push move-digital:staging
kubectl apply -f k8s/staging/
```

## Production Deployment
```bash
# 1. Build production image
docker build -f Dockerfile.prod -t move-digital:latest .

# 2. Push to registry
docker push move-digital:latest

# 3. Deploy to Kubernetes
kubectl apply -f k8s/production/

# 4. Verify deployment
kubectl get pods -n production
```

## Environment Variables
```
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
GITHUB_TOKEN=ghp_xxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/xxxx
```""",
                "description": "Complete deployment instructions",
                "tags": ["deployment", "devops", "kubernetes"]
            }
        ]
        
        for page_data in default_pages:
            page = WikiPage(
                id=str(uuid.uuid4()),
                title=page_data["title"],
                slug=page_data["slug"],
                page_type=page_data["type"],
                content=page_data["content"],
                description=page_data["description"],
                author="Move Digital",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=page_data.get("tags", [])
            )
            self.pages[page.slug] = page
            self._update_search_index(page)
    
    def create_page(self, title: str, slug: str, page_type: str, content: str, 
                   description: str, author: str, tags: List[str] = None) -> WikiPage:
        """Create a new wiki page"""
        page = WikiPage(
            id=str(uuid.uuid4()),
            title=title,
            slug=slug,
            page_type=page_type,
            content=content,
            description=description,
            author=author,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=tags or []
        )
        self.pages[slug] = page
        self._update_search_index(page)
        return page
    
    def get_page(self, slug: str) -> Optional[WikiPage]:
        """Get a wiki page by slug"""
        page = self.pages.get(slug)
        if page:
            page.views += 1
        return page
    
    def update_page(self, slug: str, title: str = None, content: str = None, 
                   description: str = None, author: str = None, 
                   tags: List[str] = None) -> Optional[WikiPage]:
        """Update an existing wiki page"""
        page = self.pages.get(slug)
        if not page:
            return None
        
        if title:
            page.title = title
        if content:
            page.content = content
        if description:
            page.description = description
        if author:
            page.author = author
        if tags is not None:
            page.tags = tags
        
        page.updated_at = datetime.now().isoformat()
        self._update_search_index(page)
        return page
    
    def delete_page(self, slug: str) -> bool:
        """Delete a wiki page"""
        if slug in self.pages:
            del self.pages[slug]
            return True
        return False
    
    def add_code_snippet(self, page_slug: str, title: str, language: str, 
                        code: str, description: str) -> Optional[CodeSnippet]:
        """Add a code snippet to a page"""
        if page_slug not in self.pages:
            return None
        
        snippet = CodeSnippet(
            id=str(uuid.uuid4()),
            title=title,
            language=language,
            code=code,
            description=description,
            page_id=page_slug,
            created_at=datetime.now().isoformat()
        )
        self.snippets[snippet.id] = snippet
        return snippet
    
    def get_snippets_for_page(self, page_slug: str) -> List[CodeSnippet]:
        """Get all snippets for a page"""
        return [s for s in self.snippets.values() if s.page_id == page_slug]
    
    def add_comment(self, page_slug: str, author: str, content: str) -> Optional[WikiComment]:
        """Add a comment to a page"""
        if page_slug not in self.pages:
            return None
        
        comment = WikiComment(
            id=str(uuid.uuid4()),
            page_id=page_slug,
            author=author,
            content=content,
            created_at=datetime.now().isoformat()
        )
        
        if page_slug not in self.comments:
            self.comments[page_slug] = []
        self.comments[page_slug].append(comment)
        return comment
    
    def get_comments_for_page(self, page_slug: str) -> List[WikiComment]:
        """Get all comments for a page"""
        return self.comments.get(page_slug, [])
    
    def like_page(self, slug: str) -> bool:
        """Like a wiki page"""
        page = self.pages.get(slug)
        if page:
            page.likes += 1
            return True
        return False
    
    def bookmark_page(self, user_id: str, page_slug: str) -> bool:
        """Bookmark a page for a user"""
        if user_id not in self.user_bookmarks:
            self.user_bookmarks[user_id] = []
        
        if page_slug not in self.user_bookmarks[user_id]:
            self.user_bookmarks[user_id].append(page_slug)
        return True
    
    def get_user_bookmarks(self, user_id: str) -> List[WikiPage]:
        """Get all bookmarked pages for a user"""
        slugs = self.user_bookmarks.get(user_id, [])
        return [self.pages[slug] for slug in slugs if slug in self.pages]
    
    def search_pages(self, query: str) -> List[WikiPage]:
        """Search wiki pages by title, content, or tags"""
        query_lower = query.lower()
        results = []
        
        for page in self.pages.values():
            if (query_lower in page.title.lower() or 
                query_lower in page.description.lower() or
                query_lower in page.content.lower() or
                any(query_lower in tag.lower() for tag in page.tags)):
                results.append(page)
        
        return sorted(results, key=lambda p: p.views, reverse=True)
    
    def get_all_pages(self, page_type: str = None, limit: int = 100) -> List[WikiPage]:
        """Get all wiki pages, optionally filtered by type"""
        pages = list(self.pages.values())
        
        if page_type:
            pages = [p for p in pages if p.page_type == page_type]
        
        # Sort by views (popularity)
        pages = sorted(pages, key=lambda p: p.views, reverse=True)
        return pages[:limit]
    
    def get_related_pages(self, page_slug: str, limit: int = 5) -> List[WikiPage]:
        """Get related pages based on tags"""
        page = self.pages.get(page_slug)
        if not page:
            return []
        
        related = {}
        for other_page in self.pages.values():
            if other_page.slug == page_slug:
                continue
            
            # Calculate relevance based on shared tags
            shared_tags = set(page.tags) & set(other_page.tags)
            if shared_tags:
                relevance = len(shared_tags)
                related[other_page.slug] = (other_page, relevance)
        
        # Sort by relevance
        sorted_related = sorted(related.items(), key=lambda x: x[1][1], reverse=True)
        return [page for page, _ in sorted_related[:limit]]
    
    def get_statistics(self) -> Dict:
        """Get wiki statistics"""
        return {
            "total_pages": len(self.pages),
            "total_views": sum(p.views for p in self.pages.values()),
            "total_likes": sum(p.likes for p in self.pages.values()),
            "pages_by_type": self._count_by_type(),
            "most_viewed": [p.to_dict() for p in sorted(
                self.pages.values(), 
                key=lambda p: p.views, 
                reverse=True
            )[:5]],
            "most_liked": [p.to_dict() for p in sorted(
                self.pages.values(), 
                key=lambda p: p.likes, 
                reverse=True
            )[:5]]
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count pages by type"""
        counts = {}
        for page in self.pages.values():
            counts[page.page_type] = counts.get(page.page_type, 0) + 1
        return counts
    
    def _update_search_index(self, page: WikiPage):
        """Update search index for a page"""
        keywords = set()
        
        # Add title words
        keywords.update(page.title.lower().split())
        
        # Add description words
        keywords.update(page.description.lower().split())
        
        # Add tags
        keywords.update(page.tags)
        
        for keyword in keywords:
            if keyword not in self.search_index:
                self.search_index[keyword] = []
            if page.slug not in self.search_index[keyword]:
                self.search_index[keyword].append(page.slug)
    
    def export_wiki(self) -> str:
        """Export entire wiki as JSON"""
        wiki_data = {
            "pages": [p.to_dict() for p in self.pages.values()],
            "snippets": [s.to_dict() for s in self.snippets.values()],
            "exported_at": datetime.now().isoformat()
        }
        return json.dumps(wiki_data, indent=2)
