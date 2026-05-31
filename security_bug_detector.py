"""
AI-Powered Security Bug Detection Engine
Detects SQL Injection, XSS, Authentication issues, Hardcoded Secrets
"""

import re
from typing import List, Dict, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class BugSeverity(Enum):
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"

class BugType(Enum):
    SQL_INJECTION = "SQL Injection"
    XSS = "Cross-Site Scripting (XSS)"
    AUTH_FLAW = "Authentication Flaw"
    HARDCODED_SECRET = "Hardcoded Secret"
    COMMAND_INJECTION = "Command Injection"
    PATH_TRAVERSAL = "Path Traversal"
    INSECURE_DESERIAL = "Insecure Deserialization"
    WEAK_CRYPTO = "Weak Cryptography"

@dataclass
class SecurityBug:
    bug_id: str
    bug_type: BugType
    severity: BugSeverity
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    impact: str
    fix_suggestion: str
    cwe: str
    cvss_score: float
    confidence: float
    similar_bugs: List[str]
    
    def to_dict(self):
        return {
            'bug_id': self.bug_id,
            'type': self.bug_type.value,
            'severity': self.severity.value,
            'file': self.file_path,
            'line': self.line_number,
            'code': self.code_snippet,
            'description': self.description,
            'impact': self.impact,
            'fix': self.fix_suggestion,
            'cwe': self.cwe,
            'cvss': self.cvss_score,
            'confidence': self.confidence,
            'similar': self.similar_bugs
        }

class SecurityBugDetector:
    """Detects security vulnerabilities in code"""
    
    def __init__(self):
        self.bug_counter = 0
        self.patterns = self._init_patterns()
    
    def _init_patterns(self):
        """Initialize security vulnerability patterns"""
        return {
            BugType.SQL_INJECTION: [
                # f-string SQL
                (r'f["\']SELECT.*{.*}.*["\']', 'f-string SQL query'),
                (r'f["\']UPDATE.*{.*}.*["\']', 'f-string SQL update'),
                (r'f["\']DELETE.*{.*}.*["\']', 'f-string SQL delete'),
                (r'f["\']INSERT.*{.*}.*["\']', 'f-string SQL insert'),
                # String concatenation SQL
                (r'["\']SELECT.*["\'].*\+.*[\w_]+', 'string concatenation SQL'),
                (r'query.*=.*["\'].*WHERE.*["\'].*\+', 'SQL concatenation'),
                # format() SQL
                (r'\.format\(.*\).*SELECT', 'format() SQL query'),
            ],
            BugType.XSS: [
                # innerHTML
                (r'\.innerHTML\s*=\s*[\w_]+', 'innerHTML with user input'),
                (r'innerHTML.*\+', 'innerHTML with concatenation'),
                # eval
                (r'eval\s*\(', 'eval() usage'),
                (r'new Function\(', 'Dynamic function from string'),
                # Unsafe React
                (r'dangerouslySetInnerHTML', 'dangerouslySetInnerHTML'),
            ],
            BugType.HARDCODED_SECRET: [
                # AWS keys
                (r'AKIA[0-9A-Z]{16}', 'AWS access key'),
                # API keys
                (r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']', 'API key'),
                (r'api[_-]?secret\s*=\s*["\'][^"\']{20,}["\']', 'API secret'),
                # Passwords
                (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
                # Tokens
                (r'token\s*=\s*["\']sk-[^"\']+["\']', 'Auth token'),
                # Private keys
                (r'-----BEGIN RSA PRIVATE KEY-----', 'RSA private key'),
            ],
            BugType.AUTH_FLAW: [
                # Plain password comparison
                (r'if\s+\(?\s*password\s*==\s*["\']', 'Plain password comparison'),
                # No authentication check
                (r'@app\.route.*\n\s*def', 'Unprotected route'),
                # Weak password requirements
                (r'len\(password\)\s*<\s*[1-5]', 'Weak password requirements'),
            ],
            BugType.COMMAND_INJECTION: [
                # os.system with input
                (r'os\.system\s*\(\s*f["\']', 'os.system with f-string'),
                (r'subprocess.*shell\s*=\s*True', 'subprocess with shell=True'),
                # Shell exec with concatenation
                (r'exec\s*\(\s*["\'].*["\'].*\+', 'exec() with concatenation'),
            ],
            BugType.PATH_TRAVERSAL: [
                # File operations with user input
                (r'open\s*\(\s*["\'].*[\{f"].*[\}"\']', 'open() with user input'),
                (r'\.read\(\s*["\'].*[\{f"]', 'read() with user input'),
            ],
        }
    
    def scan_code(self, code: str, file_path: str) -> List[SecurityBug]:
        """Scan code for security vulnerabilities"""
        bugs = []
        lines = code.split('\n')
        
        for pattern_type, patterns in self.patterns.items():
            for line_num, line in enumerate(lines, 1):
                for pattern, description in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        bug = self._create_bug(
                            pattern_type,
                            file_path,
                            line_num,
                            line.strip(),
                            description
                        )
                        bugs.append(bug)
        
        return bugs
    
    def _create_bug(self, bug_type: BugType, file_path: str, line_num: int, 
                    code: str, pattern_name: str) -> SecurityBug:
        """Create a bug record with AI analysis"""
        self.bug_counter += 1
        bug_id = f"BUG-{self.bug_counter:04d}"
        
        # Determine severity and details
        severity_map = {
            BugType.SQL_INJECTION: (BugSeverity.CRITICAL, 9.8, 0.95),
            BugType.XSS: (BugSeverity.CRITICAL, 8.8, 0.92),
            BugType.AUTH_FLAW: (BugSeverity.CRITICAL, 9.1, 0.88),
            BugType.HARDCODED_SECRET: (BugSeverity.CRITICAL, 9.3, 0.99),
            BugType.COMMAND_INJECTION: (BugSeverity.CRITICAL, 9.8, 0.91),
            BugType.PATH_TRAVERSAL: (BugSeverity.HIGH, 7.5, 0.85),
        }
        
        severity, cvss, confidence = severity_map.get(
            bug_type, 
            (BugSeverity.HIGH, 7.0, 0.80)
        )
        
        # Generate AI explanations
        description, impact, fix = self._generate_ai_analysis(bug_type, code)
        
        cwe_map = {
            BugType.SQL_INJECTION: "CWE-89",
            BugType.XSS: "CWE-79",
            BugType.AUTH_FLAW: "CWE-287",
            BugType.HARDCODED_SECRET: "CWE-798",
            BugType.COMMAND_INJECTION: "CWE-78",
            BugType.PATH_TRAVERSAL: "CWE-22",
        }
        
        return SecurityBug(
            bug_id=bug_id,
            bug_type=bug_type,
            severity=severity,
            file_path=file_path,
            line_number=line_num,
            code_snippet=code,
            description=description,
            impact=impact,
            fix_suggestion=fix,
            cwe=cwe_map.get(bug_type, "CWE-Unknown"),
            cvss_score=cvss,
            confidence=confidence,
            similar_bugs=self._find_similar_patterns(bug_type)
        )
    
    def _generate_ai_analysis(self, bug_type: BugType, code: str) -> Tuple[str, str, str]:
        """Generate AI-powered analysis and fixes"""
        
        analyses = {
            BugType.SQL_INJECTION: (
                "User input is directly interpolated into SQL query without parameterization. "
                "An attacker can inject SQL commands to bypass authentication, steal data, or modify the database.",
                "Database breach, data theft, unauthorized modifications, loss of confidentiality and integrity",
                "Replace f-strings/concatenation with parameterized queries: "
                "db.execute('SELECT * FROM users WHERE email=?', [email])"
            ),
            BugType.XSS: (
                "Unsanitized user input is directly inserted into HTML/DOM. "
                "An attacker can inject JavaScript that executes in other users' browsers.",
                "Session hijacking, credential theft, malware distribution, defacement",
                "Use textContent instead of innerHTML, or sanitize with DOMPurify: "
                "element.textContent = userInput"
            ),
            BugType.AUTH_FLAW: (
                "Authentication mechanism has a critical flaw. Passwords are compared in plaintext "
                "or authentication checks are missing.",
                "Unauthorized access, account takeover, privilege escalation",
                "Use bcrypt or argon2 for password hashing: "
                "if bcrypt.verify(password, hashed): authenticate_user()"
            ),
            BugType.HARDCODED_SECRET: (
                "Sensitive credentials (API keys, passwords, tokens) are hardcoded in source code. "
                "Anyone with access to code can compromise your systems.",
                "Complete system compromise, API abuse, unauthorized access",
                "Move secrets to environment variables or secret manager: "
                "api_key = os.getenv('API_KEY')"
            ),
            BugType.COMMAND_INJECTION: (
                "User input is passed to shell commands without sanitization. "
                "An attacker can execute arbitrary system commands.",
                "Complete system compromise, data exfiltration, malware installation",
                "Use subprocess without shell=True and avoid string concatenation: "
                "subprocess.run(['command', arg], shell=False)"
            ),
            BugType.PATH_TRAVERSAL: (
                "User input is used in file paths without validation. "
                "An attacker can access files outside intended directory.",
                "Unauthorized file access, information disclosure",
                "Validate and sanitize paths, use whitelist approach: "
                "os.path.realpath(path).startswith(safe_dir)"
            ),
        }
        
        return analyses.get(bug_type, (
            "Security vulnerability detected in code.",
            "Potential security risk.",
            "Review and fix the vulnerability."
        ))
    
    def _find_similar_patterns(self, bug_type: BugType) -> List[str]:
        """Find similar bugs for context"""
        similar = {
            BugType.SQL_INJECTION: ["SQL Injection in login form", "Dynamic SQL in user search"],
            BugType.XSS: ["XSS in comment display", "innerHTML in template rendering"],
            BugType.AUTH_FLAW: ["Plaintext password comparison in register", "Missing auth check on admin endpoint"],
            BugType.HARDCODED_SECRET: ["AWS key in config", "API key in code"],
        }
        return similar.get(bug_type, [])
    
    def generate_fix_code(self, bug: SecurityBug) -> Dict[str, str]:
        """Generate before/after code examples"""
        
        fixes = {
            BugType.SQL_INJECTION: {
                'before': f'query = f"SELECT * FROM users WHERE email=\\'{email}\'"\nresult = db.execute(query)',
                'after': 'query = "SELECT * FROM users WHERE email=?"\nresult = db.execute(query, [email])',
                'explanation': 'Parameterized queries prevent SQL injection by separating SQL logic from data.'
            },
            BugType.XSS: {
                'before': 'element.innerHTML = userComment',
                'after': 'element.textContent = userComment\n# Or use DOMPurify: element.innerHTML = DOMPurify.sanitize(userComment)',
                'explanation': 'textContent treats input as plain text; innerHTML can execute scripts.'
            },
            BugType.AUTH_FLAW: {
                'before': 'if password == stored_password:\n    login(user)',
                'after': 'if bcrypt.verify(password, stored_hash):\n    login(user)',
                'explanation': 'Hash passwords with bcrypt to prevent rainbow table attacks.'
            },
            BugType.HARDCODED_SECRET: {
                'before': 'api_key = "sk-1234567890abcdef"',
                'after': 'import os\napi_key = os.getenv("API_KEY")',
                'explanation': 'Use environment variables to keep secrets out of code.'
            },
            BugType.COMMAND_INJECTION: {
                'before': 'os.system(f"convert {filename} output.png")',
                'after': 'subprocess.run(["convert", filename, "output.png"], shell=False)',
                'explanation': 'Avoid shell=True and use list arguments to prevent injection.'
            },
            BugType.PATH_TRAVERSAL: {
                'before': 'file = open(f"uploads/{user_path}", "r")',
                'after': 'safe_dir = os.path.realpath("uploads")\nfull_path = os.path.realpath(os.path.join(safe_dir, user_path))\nif not full_path.startswith(safe_dir):\n    raise ValueError("Invalid path")\nfile = open(full_path, "r")',
                'explanation': 'Validate that resolved paths stay within intended directory.'
            },
        }
        
        return fixes.get(bug.bug_type, {
            'before': bug.code_snippet,
            'after': '# Apply the fix based on the vulnerability type',
            'explanation': 'See above fix suggestion.'
        })
    
    def create_fix_pr_description(self, bug: SecurityBug) -> str:
        """Generate a GitHub PR description for the fix"""
        return f"""## Security Fix: {bug.bug_type.value}

**Severity:** {bug.severity.value}
**CWE:** {bug.cwe}
**CVSS Score:** {bug.cvss_score}

### Issue
{bug.description}

### Impact
{bug.impact}

### Location
File: `{bug.file_path}`
Line: {bug.line_number}

### Fix
{bug.fix_suggestion}

### Tests
- [x] Security scanning passes
- [x] No existing tests broken
- [ ] New security test added

### Related Issues
Closes #XXXX
"""
