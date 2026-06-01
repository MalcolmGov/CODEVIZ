"""
Continuous Compliance Monitoring Engine
Tier 2 Feature: Checks scan artifacts against OWASP Top 10, SOC2, PCI-DSS, GDPR.

Each framework defines a set of controls. Each control maps to one or more
artifact signals. The engine returns pass/fail/warn per control plus an
overall compliance percentage.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class Control:
    id: str           # e.g. "A01", "CC6.1"
    name: str
    description: str
    severity: str     # critical | high | medium | low
    status: str       # pass | fail | warn | info
    finding: str      # human-readable result
    remediation: str  # what to do if failing


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _has_auth(artifacts: Dict) -> bool:
    apis = artifacts.get('apis', [])
    middleware = artifacts.get('middleware', [])
    auth_kw = ['auth', 'login', 'token', 'oauth', 'jwt', 'session', 'verify', 'password']
    api_auth = any(any(k in a.get('path', '').lower() for k in auth_kw) for a in apis)
    mid_auth = any(any(k in m.get('name', '').lower() for k in auth_kw) for m in middleware)
    return api_auth or mid_auth

def _has_input_validation(artifacts: Dict) -> bool:
    funcs = artifacts.get('functions', [])
    val_kw = ['validate', 'sanitize', 'escape', 'clean', 'parse', 'schema']
    return any(any(k in f.get('name', '').lower() for k in val_kw) for f in funcs)

def _has_rate_limiting(artifacts: Dict) -> bool:
    middleware = artifacts.get('middleware', [])
    rate_kw = ['rate', 'throttle', 'limit', 'ratelimit']
    return any(any(k in m.get('name', '').lower() for k in rate_kw) for m in middleware)

def _has_error_handlers(artifacts: Dict) -> bool:
    return len(artifacts.get('error_handlers', [])) > 0

def _has_logging(artifacts: Dict) -> bool:
    funcs = artifacts.get('functions', [])
    consts = artifacts.get('constants', [])
    log_kw = ['log', 'logger', 'logging', 'audit', 'monitor']
    fn_log = any(any(k in f.get('name', '').lower() for k in log_kw) for f in funcs)
    const_log = any(any(k in c.get('name', '').lower() for k in log_kw) for c in consts)
    return fn_log or const_log

def _has_encryption_hints(artifacts: Dict) -> bool:
    deps = artifacts.get('dependencies', [])
    funcs = artifacts.get('functions', [])
    enc_kw = ['crypto', 'encrypt', 'bcrypt', 'hash', 'ssl', 'tls', 'jwt', 'hmac', 'cipher']
    dep_enc = any(any(k in d.get('package', '').lower() for k in enc_kw) for d in deps)
    fn_enc = any(any(k in f.get('name', '').lower() for k in enc_kw) for f in funcs)
    return dep_enc or fn_enc

def _has_cors(artifacts: Dict) -> bool:
    deps = artifacts.get('dependencies', [])
    middleware = artifacts.get('middleware', [])
    return (any('cors' in d.get('package', '').lower() for d in deps) or
            any('cors' in m.get('name', '').lower() for m in middleware))

def _has_hardcoded_secrets(artifacts: Dict) -> bool:
    consts = artifacts.get('constants', [])
    secret_kw = ['password', 'secret', 'api_key', 'apikey', 'token', 'passwd', 'credential']
    risky = [c for c in consts if any(k in c.get('name', '').lower() for k in secret_kw)
             and str(c.get('value', '')).strip().startswith(('"', "'"))]
    return len(risky) > 0

def _has_db_models(artifacts: Dict) -> bool:
    return len(artifacts.get('models', [])) > 0

def _has_https_references(artifacts: Dict) -> bool:
    apis = artifacts.get('apis', [])
    return any('https' in a.get('base_url', '').lower() for a in apis)

def _dependency_count(artifacts: Dict) -> int:
    return len(artifacts.get('dependencies', []))

def _api_count(artifacts: Dict) -> int:
    return len(artifacts.get('apis', []))


# ─── OWASP Top 10 (2021) ─────────────────────────────────────────────────────

def _check_owasp(artifacts: Dict) -> List[Control]:
    controls = []

    # A01 – Broken Access Control
    auth = _has_auth(artifacts)
    controls.append(Control(
        id='A01', name='Broken Access Control',
        description='Restrictions on authenticated users are not properly enforced.',
        severity='critical',
        status='pass' if auth else 'fail',
        finding='Authentication endpoints detected.' if auth else 'No authentication or access control mechanisms found.',
        remediation='Implement role-based access control. Deny by default. Log access control failures.'
    ))

    # A02 – Cryptographic Failures
    enc = _has_encryption_hints(artifacts)
    controls.append(Control(
        id='A02', name='Cryptographic Failures',
        description='Failures related to cryptography exposing sensitive data.',
        severity='critical',
        status='pass' if enc else 'warn',
        finding='Encryption libraries or patterns detected.' if enc else 'No cryptographic library usage detected — verify sensitive data is encrypted at rest and in transit.',
        remediation='Use strong, up-to-date algorithms. Enforce HTTPS. Never store sensitive data in plaintext.'
    ))

    # A03 – Injection
    val = _has_input_validation(artifacts)
    secrets = _has_hardcoded_secrets(artifacts)
    inj_status = 'fail' if secrets else ('pass' if val else 'warn')
    controls.append(Control(
        id='A03', name='Injection',
        description='User-supplied data is not validated, filtered, or sanitized.',
        severity='critical',
        status=inj_status,
        finding='Hardcoded secrets detected — high injection risk.' if secrets else (
            'Input validation functions found.' if val else 'No input validation patterns detected.'),
        remediation='Use parameterized queries. Validate and sanitize all inputs. Apply allowlist validation.'
    ))

    # A04 – Insecure Design
    models = _has_db_models(artifacts)
    controls.append(Control(
        id='A04', name='Insecure Design',
        description='Missing or ineffective control design and threat modeling.',
        severity='high',
        status='pass' if models else 'warn',
        finding='Database models with ORM detected — structured data layer present.' if models else 'No ORM models detected — review data layer for raw queries and design flaws.',
        remediation='Integrate threat modeling in design phase. Use secure design patterns and reference architectures.'
    ))

    # A05 – Security Misconfiguration
    cors = _has_cors(artifacts)
    err_handlers = _has_error_handlers(artifacts)
    misconfig_status = 'pass' if (cors and err_handlers) else ('warn' if (cors or err_handlers) else 'fail')
    controls.append(Control(
        id='A05', name='Security Misconfiguration',
        description='Insecure default configurations, incomplete setups, or misconfigured cloud storage.',
        severity='high',
        status=misconfig_status,
        finding=f"CORS: {'✓' if cors else '✗'}  Error handlers: {'✓' if err_handlers else '✗'}",
        remediation='Configure CORS restrictively. Handle errors without exposing stack traces. Disable unnecessary features.'
    ))

    # A06 – Vulnerable and Outdated Components
    dep_count = _dependency_count(artifacts)
    dep_status = 'fail' if dep_count > 100 else ('warn' if dep_count > 50 else 'pass')
    controls.append(Control(
        id='A06', name='Vulnerable & Outdated Components',
        description='Components with known vulnerabilities used without patching.',
        severity='high',
        status=dep_status,
        finding=f'{dep_count} dependencies detected. {"Large surface — run a CVE audit." if dep_count > 50 else "Manageable dependency footprint."}',
        remediation='Remove unused dependencies. Subscribe to security advisories. Run automated vulnerability scans regularly.'
    ))

    # A07 – Identification and Authentication Failures
    controls.append(Control(
        id='A07', name='Identification & Authentication Failures',
        description='Weaknesses in authentication and session management.',
        severity='critical',
        status='pass' if auth else 'fail',
        finding='Authentication layer present.' if auth else 'No authentication mechanisms detected.',
        remediation='Implement MFA. Use secure session management. Enforce strong password policies.'
    ))

    # A08 – Software and Data Integrity Failures
    controls.append(Control(
        id='A08', name='Software & Data Integrity Failures',
        description='Code and infrastructure that does not protect against integrity violations.',
        severity='high',
        status='warn',
        finding='Unable to verify CI/CD integrity checks from static analysis alone — manual review recommended.',
        remediation='Use digital signatures for updates. Verify integrity of third-party libraries. Implement CI/CD security gates.'
    ))

    # A09 – Security Logging and Monitoring Failures
    logging = _has_logging(artifacts)
    controls.append(Control(
        id='A09', name='Security Logging & Monitoring Failures',
        description='Insufficient logging and monitoring allows attackers to go undetected.',
        severity='medium',
        status='pass' if logging else 'fail',
        finding='Logging functions or constants detected.' if logging else 'No logging or monitoring patterns found.',
        remediation='Log all authentication events and high-value transactions. Set up alerting for suspicious activity.'
    ))

    # A10 – Server-Side Request Forgery
    rate = _has_rate_limiting(artifacts)
    controls.append(Control(
        id='A10', name='Server-Side Request Forgery (SSRF)',
        description='Web application fetches remote resources without validating the URL.',
        severity='high',
        status='warn' if not rate else 'pass',
        finding='Rate limiting detected — partial SSRF mitigation.' if rate else 'No rate limiting or SSRF protection patterns found.',
        remediation='Validate and sanitize all client-supplied URLs. Use allowlists. Disable HTTP redirects where possible.'
    ))

    return controls


# ─── SOC 2 (Trust Services Criteria) ─────────────────────────────────────────

def _check_soc2(artifacts: Dict) -> List[Control]:
    auth = _has_auth(artifacts)
    logging = _has_logging(artifacts)
    enc = _has_encryption_hints(artifacts)
    err_handlers = _has_error_handlers(artifacts)
    rate = _has_rate_limiting(artifacts)

    return [
        Control('CC1.1', 'Control Environment', 'Commitment to integrity and ethical values.',
                'medium', 'warn',
                'Policy enforcement cannot be determined from static analysis.',
                'Document and enforce security policies. Train all staff on security responsibilities.'),
        Control('CC6.1', 'Logical Access Controls', 'Restrict logical access to information assets.',
                'critical', 'pass' if auth else 'fail',
                'Authentication and access controls detected.' if auth else 'No access control mechanisms found.',
                'Implement least-privilege access. Review access rights quarterly.'),
        Control('CC6.6', 'Boundary Protection', 'Restrict external access points.',
                'high', 'pass' if rate else 'warn',
                'Rate limiting controls present.' if rate else 'No boundary protection (rate limiting/CORS) detected.',
                'Deploy WAF, rate limiting, and IP allowlisting at network boundaries.'),
        Control('CC6.7', 'Data Transmission Controls', 'Protect data transmitted over networks.',
                'critical', 'pass' if enc else 'warn',
                'Encryption libraries detected.' if enc else 'No evidence of transport encryption.',
                'Enforce TLS 1.2+ for all data in transit. Use HSTS headers.'),
        Control('CC7.2', 'System Monitoring', 'Monitor for anomalies and security events.',
                'high', 'pass' if logging else 'fail',
                'Logging/monitoring patterns detected.' if logging else 'No monitoring infrastructure found.',
                'Implement centralised logging, SIEM integration, and automated alerting.'),
        Control('CC7.3', 'Incident Response', 'Evaluate and respond to security incidents.',
                'medium', 'pass' if err_handlers else 'warn',
                'Error handling layer present.' if err_handlers else 'No error handling or incident response patterns found.',
                'Define and test an incident response plan. Establish escalation procedures.'),
        Control('CC8.1', 'Change Management', 'Manage changes to infrastructure and software.',
                'medium', 'warn',
                'Change management process cannot be verified from code analysis alone.',
                'Enforce code review, approval workflows, and change documentation for all deployments.'),
        Control('CC9.1', 'Risk Mitigation', 'Identify and mitigate risks from vendors.',
                'high', 'warn' if _dependency_count(artifacts) > 50 else 'pass',
                f"{_dependency_count(artifacts)} dependencies — vendor risk review recommended." if _dependency_count(artifacts) > 50 else 'Manageable third-party footprint.',
                'Assess all third-party vendors. Maintain a software bill of materials (SBOM).'),
    ]


# ─── PCI-DSS (v4.0) ──────────────────────────────────────────────────────────

def _check_pcidss(artifacts: Dict) -> List[Control]:
    enc = _has_encryption_hints(artifacts)
    auth = _has_auth(artifacts)
    logging = _has_logging(artifacts)
    secrets = _has_hardcoded_secrets(artifacts)
    rate = _has_rate_limiting(artifacts)
    err_handlers = _has_error_handlers(artifacts)

    return [
        Control('PCI-2', 'Secure Configurations', 'Do not use vendor-supplied defaults for system passwords.',
                'critical', 'fail' if secrets else 'pass',
                'Hardcoded credentials detected in constants.' if secrets else 'No hardcoded credentials found.',
                'Remove all hardcoded secrets. Use a secrets manager (Vault, AWS Secrets Manager).'),
        Control('PCI-3', 'Cardholder Data Protection', 'Protect stored cardholder data.',
                'critical', 'pass' if enc else 'fail',
                'Encryption implementation detected.' if enc else 'No data encryption detected — cardholder data may be stored in plaintext.',
                'Encrypt all stored sensitive data using AES-256 or equivalent.'),
        Control('PCI-4', 'Data Transmission Encryption', 'Encrypt transmission of cardholder data.',
                'critical', 'pass' if enc else 'fail',
                'Cryptographic libraries present.' if enc else 'No TLS/encryption libraries detected.',
                'Enforce TLS 1.2 or higher for all data transmissions.'),
        Control('PCI-6', 'Secure Systems Development', 'Develop and maintain secure systems and applications.',
                'high', 'pass' if _has_input_validation(artifacts) else 'warn',
                'Input validation patterns detected.' if _has_input_validation(artifacts) else 'No input validation found — injection vulnerabilities possible.',
                'Integrate SAST/DAST in CI/CD. Train developers on secure coding practices.'),
        Control('PCI-7', 'Access Control', 'Restrict access to cardholder data by business need-to-know.',
                'critical', 'pass' if auth else 'fail',
                'Access control mechanisms present.' if auth else 'No access control detected.',
                'Implement role-based access control. Apply principle of least privilege.'),
        Control('PCI-8', 'Unique User IDs', 'Assign a unique ID to each person with computer access.',
                'high', 'pass' if auth else 'warn',
                'User authentication system present.' if auth else 'No user identification system detected.',
                'Ensure every user has a unique account. Prohibit shared credentials.'),
        Control('PCI-10', 'Audit Logging', 'Track and monitor all access to network resources and cardholder data.',
                'high', 'pass' if logging else 'fail',
                'Logging infrastructure detected.' if logging else 'No audit logging found.',
                'Log all access events. Retain logs for at least 12 months. Review daily.'),
        Control('PCI-11', 'Security Testing', 'Regularly test security systems and processes.',
                'medium', 'warn',
                'Automated security testing cannot be confirmed from static analysis.',
                'Run quarterly vulnerability scans and annual penetration tests.'),
        Control('PCI-12', 'Security Policy', 'Maintain an information security policy.',
                'medium', 'warn',
                'Security policy documentation cannot be verified from code analysis.',
                'Document, publish, and annually review a security policy addressing all PCI-DSS requirements.'),
    ]


# ─── GDPR / Privacy ──────────────────────────────────────────────────────────

def _check_gdpr(artifacts: Dict) -> List[Control]:
    enc = _has_encryption_hints(artifacts)
    logging = _has_logging(artifacts)
    models = _has_db_models(artifacts)
    auth = _has_auth(artifacts)

    personal_data_models = [m for m in artifacts.get('models', [])
                            if any(k in m.get('name', '').lower()
                                   for k in ['user', 'person', 'customer', 'profile', 'account', 'member'])]

    return [
        Control('GDPR-5', 'Lawfulness of Processing', 'Personal data must be processed lawfully and transparently.',
                'critical', 'warn',
                'Cannot determine consent mechanisms from static analysis alone.',
                'Implement explicit consent flows. Document legal basis for each data processing activity.'),
        Control('GDPR-17', 'Right to Erasure', 'Data subjects have the right to have their data erased.',
                'high',
                'warn' if personal_data_models else 'info',
                f"{len(personal_data_models)} personal data model(s) detected — ensure deletion APIs exist." if personal_data_models else 'No personal data models detected.',
                'Implement DELETE endpoints for all user data. Cascade deletes across related tables.'),
        Control('GDPR-20', 'Data Portability', 'Data subjects can receive their data in a machine-readable format.',
                'medium', 'warn',
                'Data export functionality cannot be confirmed from static analysis.',
                'Build data export endpoints (JSON/CSV) for all user-owned data.'),
        Control('GDPR-25', 'Data Protection by Design', 'Implement data protection from the design stage.',
                'high', 'pass' if enc else 'fail',
                'Encryption present — data protection by design partially satisfied.' if enc else 'No encryption detected — data protection by design not satisfied.',
                'Pseudonymise personal data by default. Apply encryption at rest and in transit.'),
        Control('GDPR-30', 'Records of Processing', 'Maintain records of processing activities.',
                'medium', 'pass' if logging else 'warn',
                'Logging detected — processing records partially maintained.' if logging else 'No logging found — processing activities may not be recorded.',
                'Maintain a data processing register. Log all access to personal data.'),
        Control('GDPR-32', 'Security of Processing', 'Implement appropriate technical security measures.',
                'critical', 'pass' if (enc and auth) else ('warn' if (enc or auth) else 'fail'),
                f"Encryption: {'✓' if enc else '✗'}  Authentication: {'✓' if auth else '✗'}",
                'Implement encryption, access control, and regular security testing.'),
        Control('GDPR-33', 'Data Breach Notification', 'Report breaches to supervisory authority within 72 hours.',
                'high', 'warn',
                'Breach notification procedures cannot be verified from code — confirm process exists.',
                'Document breach response procedures. Integrate incident alerting and auto-notification workflows.'),
        Control('GDPR-35', 'Data Protection Impact Assessment', 'Conduct DPIA for high-risk processing.',
                'medium', 'warn' if personal_data_models else 'info',
                f"{len(personal_data_models)} personal data model(s) — DPIA recommended." if personal_data_models else 'No high-risk personal data models detected.',
                'Conduct DPIA before processing sensitive personal data. Document findings and mitigations.'),
    ]


# ─── Framework Runner ─────────────────────────────────────────────────────────

FRAMEWORKS = {
    'owasp': {'name': 'OWASP Top 10', 'version': '2021', 'icon': '🛡️'},
    'soc2':  {'name': 'SOC 2',        'version': 'Type II', 'icon': '🏛️'},
    'pcidss': {'name': 'PCI-DSS',      'version': 'v4.0',   'icon': '💳'},
    'gdpr':  {'name': 'GDPR',         'version': '2018',    'icon': '🇪🇺'},
}

FRAMEWORK_CHECKERS = {
    'owasp':  _check_owasp,
    'soc2':   _check_soc2,
    'pcidss': _check_pcidss,
    'gdpr':   _check_gdpr,
}


class ComplianceEngine:
    """
    Runs all compliance frameworks against scan artifacts.
    Returns per-framework results and an overall compliance summary.
    """

    def check(self, artifacts: Dict, frameworks: List[str] = None) -> Dict[str, Any]:
        if not frameworks:
            frameworks = list(FRAMEWORKS.keys())

        results = {}
        for fw_id in frameworks:
            if fw_id not in FRAMEWORK_CHECKERS:
                continue
            controls = FRAMEWORK_CHECKERS[fw_id](artifacts)
            results[fw_id] = self._summarise(fw_id, controls)

        return {
            'frameworks': results,
            'overall': self._overall(results),
            'available_frameworks': FRAMEWORKS,
        }

    def _summarise(self, fw_id: str, controls: List[Control]) -> Dict:
        total = len(controls)
        passed = sum(1 for c in controls if c.status == 'pass')
        failed = sum(1 for c in controls if c.status == 'fail')
        warned = sum(1 for c in controls if c.status == 'warn')
        score = round((passed / total) * 100) if total else 0

        return {
            **FRAMEWORKS[fw_id],
            'id': fw_id,
            'score': score,
            'grade': 'A' if score >= 90 else 'B' if score >= 75 else 'C' if score >= 60 else 'D' if score >= 45 else 'F',
            'controls': [
                {
                    'id': c.id, 'name': c.name, 'description': c.description,
                    'severity': c.severity, 'status': c.status,
                    'finding': c.finding, 'remediation': c.remediation,
                }
                for c in controls
            ],
            'summary': {'total': total, 'passed': passed, 'failed': failed, 'warned': warned},
        }

    def _overall(self, results: Dict) -> Dict:
        if not results:
            return {'score': 0, 'grade': 'F'}
        avg = round(sum(r['score'] for r in results.values()) / len(results))
        return {
            'score': avg,
            'grade': 'A' if avg >= 90 else 'B' if avg >= 75 else 'C' if avg >= 60 else 'D' if avg >= 45 else 'F',
            'frameworks_checked': len(results),
        }
