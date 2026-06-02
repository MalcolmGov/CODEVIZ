"""
Threat Actor Simulation Engine
Tier 2 Feature: Maps scan artifacts to MITRE ATT&CK tactics,
generates kill chains, exploitability/impact heat maps, and
business impact assessments per threat actor profile.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


# ─── MITRE ATT&CK Kill Chain Stages ──────────────────────────────────────────

KILL_CHAIN_STAGES = [
    'Reconnaissance',
    'Initial Access',
    'Execution',
    'Persistence',
    'Privilege Escalation',
    'Defense Evasion',
    'Lateral Movement',
    'Impact',
]

# ─── Threat Actor Profiles ────────────────────────────────────────────────────

THREAT_ACTORS = {
    'apt': {
        'id': 'apt',
        'name': 'Advanced Persistent Threat',
        'icon': '🎯',
        'description': 'Nation-state or sophisticated criminal group. Patient, well-resourced, targeted. Uses zero-days and custom tooling.',
        'skill_level': 10,
        'motivation': 'Espionage / Data Theft',
        'exploitability_multiplier': 1.2,
    },
    'script_kiddie': {
        'id': 'script_kiddie',
        'name': 'Script Kiddie',
        'icon': '👾',
        'description': 'Opportunistic attacker using publicly available tools and exploits. Targets low-hanging fruit.',
        'skill_level': 3,
        'motivation': 'Notoriety / Vandalism',
        'exploitability_multiplier': 0.7,
    },
    'insider': {
        'id': 'insider',
        'name': 'Malicious Insider',
        'icon': '🕵️',
        'description': 'Current or former employee with legitimate access. Knows the codebase and internal systems.',
        'skill_level': 7,
        'motivation': 'Financial Gain / Sabotage',
        'exploitability_multiplier': 1.5,
    },
    'ransomware': {
        'id': 'ransomware',
        'name': 'Ransomware Operator',
        'icon': '💰',
        'description': 'Financially motivated attacker targeting encryption and extortion. Moves fast once inside.',
        'skill_level': 8,
        'motivation': 'Financial Extortion',
        'exploitability_multiplier': 1.1,
    },
}


# ─── Attack Vector Definitions ────────────────────────────────────────────────

@dataclass
class AttackVector:
    id: str
    name: str
    stage: str                  # MITRE kill chain stage
    tactic: str                 # MITRE tactic ID e.g. TA0001
    technique: str              # MITRE technique e.g. T1190
    description: str
    exploitability: float       # 1-10
    impact: float               # 1-10
    present: bool               # whether this vector was found in the scan
    evidence: str               # what in the artifacts triggered this
    mitigations: List[str] = field(default_factory=list)
    affected_assets: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'stage': self.stage,
            'tactic': self.tactic,
            'technique': self.technique,
            'description': self.description,
            'exploitability': round(self.exploitability, 1),
            'impact': round(self.impact, 1),
            'risk_score': round(self.exploitability * self.impact / 10, 1),
            'present': self.present,
            'evidence': self.evidence,
            'mitigations': self.mitigations,
            'affected_assets': self.affected_assets,
        }


# ─── Detection helpers ────────────────────────────────────────────────────────

def _auth_apis(artifacts):
    return [a for a in artifacts.get('apis', [])
            if any(k in a.get('path','').lower() for k in ['auth','login','token','oauth','session'])]

def _has_auth(artifacts): return len(_auth_apis(artifacts)) > 0
def _has_rate_limit(artifacts):
    return any(any(k in m.get('name','').lower() for k in ['rate','throttle','limit'])
               for m in artifacts.get('middleware', []))

def _has_encryption(artifacts):
    return any(any(k in d.get('package','').lower() for k in ['crypto','bcrypt','jwt','ssl','tls'])
               for d in artifacts.get('dependencies', []))

def _has_logging(artifacts):
    return any(any(k in f.get('name','').lower() for k in ['log','audit','monitor'])
               for f in artifacts.get('functions', []))

def _has_error_handlers(artifacts): return len(artifacts.get('error_handlers', [])) > 0

def _hardcoded_secrets(artifacts):
    return [c for c in artifacts.get('constants', [])
            if any(k in c.get('name','').lower() for k in ['password','secret','key','token','passwd'])
            and str(c.get('value','')).strip().startswith(('"',"'"))]

def _unauth_apis(artifacts):
    auth_paths = {a.get('path','') for a in _auth_apis(artifacts)}
    return [a for a in artifacts.get('apis', []) if a.get('path','') not in auth_paths]

def _dep_count(artifacts): return len(artifacts.get('dependencies', []))
def _api_count(artifacts): return len(artifacts.get('apis', []))
def _model_count(artifacts): return len(artifacts.get('models', []))

def _risky_funcs(artifacts):
    return [f for f in artifacts.get('functions', [])
            if any(k in f.get('name','').lower() for k in ['exec','eval','shell','subprocess','system','query','raw'])]


# ─── Attack Vector Catalogue ──────────────────────────────────────────────────

def _build_vectors(artifacts: Dict) -> List[AttackVector]:
    secrets = _hardcoded_secrets(artifacts)
    unauth = _unauth_apis(artifacts)
    risky_fns = _risky_funcs(artifacts)
    has_auth = _has_auth(artifacts)
    has_rate = _has_rate_limit(artifacts)
    has_enc = _has_encryption(artifacts)
    has_log = _has_logging(artifacts)
    has_err = _has_error_handlers(artifacts)
    api_count = _api_count(artifacts)
    dep_count = _dep_count(artifacts)
    model_count = _model_count(artifacts)

    vectors = [
        # ── Reconnaissance ──────────────────────────────────────────────────
        AttackVector(
            id='recon_api_enum',
            name='API Endpoint Enumeration',
            stage='Reconnaissance',
            tactic='TA0043', technique='T1595',
            description='An attacker can enumerate exposed API endpoints to map the application surface.',
            exploitability=8.5 if api_count > 15 else 6.0,
            impact=5.0,
            present=api_count > 0,
            evidence=f'{api_count} API endpoint(s) detected — large surface increases discoverability.',
            mitigations=['Implement API gateway with endpoint obfuscation', 'Require authentication on all non-public routes', 'Rate limit discovery requests'],
            affected_assets=[a.get('path','') for a in artifacts.get('apis', [])[:5]],
        ),
        AttackVector(
            id='recon_error_info',
            name='Error Message Information Disclosure',
            stage='Reconnaissance',
            tactic='TA0043', technique='T1592',
            description='Unhandled exceptions expose stack traces, file paths, and framework internals to attackers.',
            exploitability=7.0 if not has_err else 2.0,
            impact=4.0,
            present=not has_err,
            evidence='No error handlers detected — raw exception output may leak internal details.' if not has_err else 'Error handlers present — information leakage mitigated.',
            mitigations=['Add global error handlers that return generic messages', 'Log full errors server-side only', 'Disable debug mode in production'],
        ),

        # ── Initial Access ──────────────────────────────────────────────────
        AttackVector(
            id='init_no_auth',
            name='Unauthenticated API Access',
            stage='Initial Access',
            tactic='TA0001', technique='T1190',
            description='API endpoints accessible without authentication allow attackers direct entry into the system.',
            exploitability=9.0 if len(unauth) > 5 else (6.5 if unauth else 1.0),
            impact=8.5,
            present=len(unauth) > 0,
            evidence=f'{len(unauth)} endpoint(s) accessible without authentication detected.' if unauth else 'All endpoints appear to require authentication.',
            mitigations=['Enforce authentication middleware on all routes', 'Apply OAuth2/JWT token validation globally', 'Deny by default — whitelist public routes explicitly'],
            affected_assets=[a.get('path','') for a in unauth[:5]],
        ),
        AttackVector(
            id='init_hardcoded_creds',
            name='Hardcoded Credential Exposure',
            stage='Initial Access',
            tactic='TA0001', technique='T1078',
            description='API keys, passwords, or tokens hardcoded in source are readable by anyone with repo access.',
            exploitability=9.5 if secrets else 1.0,
            impact=9.0,
            present=len(secrets) > 0,
            evidence=f'{len(secrets)} hardcoded credential(s) found in constants.' if secrets else 'No hardcoded credentials detected.',
            mitigations=['Move all secrets to environment variables or a secrets manager (Vault, AWS SSM)', 'Rotate any exposed credentials immediately', 'Add pre-commit hooks to block secret commits'],
            affected_assets=[s.get('name','') for s in secrets[:5]],
        ),
        AttackVector(
            id='init_supply_chain',
            name='Dependency Supply Chain Attack',
            stage='Initial Access',
            tactic='TA0001', technique='T1195',
            description='A compromised dependency can execute malicious code during install or at runtime.',
            exploitability=6.0 if dep_count > 100 else (4.5 if dep_count > 50 else 2.5),
            impact=9.5,
            present=dep_count > 30,
            evidence=f'{dep_count} dependencies — each is a potential supply chain entry point.',
            mitigations=['Pin all dependencies to exact versions', 'Run automated CVE scanning (Snyk, Dependabot)', 'Maintain a software bill of materials (SBOM)', 'Use private mirrors with validated packages'],
        ),

        # ── Execution ───────────────────────────────────────────────────────
        AttackVector(
            id='exec_injection',
            name='Code/Command Injection',
            stage='Execution',
            tactic='TA0002', technique='T1059',
            description='Functions that execute system commands or raw queries without sanitization allow arbitrary code execution.',
            exploitability=8.5 if risky_fns else 3.0,
            impact=10.0,
            present=len(risky_fns) > 0,
            evidence=f'{len(risky_fns)} function(s) with execution/query risk patterns found.' if risky_fns else 'No obvious injection-prone functions detected.',
            mitigations=['Use parameterized queries exclusively', 'Apply allowlist validation on all inputs', 'Sandbox command execution', 'Run static analysis (Bandit, Semgrep) in CI'],
            affected_assets=[f.get('name','') for f in risky_fns[:5]],
        ),

        # ── Persistence ─────────────────────────────────────────────────────
        AttackVector(
            id='persist_no_logging',
            name='Attacker Activity Goes Undetected',
            stage='Persistence',
            tactic='TA0003', technique='T1505',
            description='Without logging and monitoring, attackers can maintain persistent access indefinitely.',
            exploitability=7.0 if not has_log else 2.0,
            impact=8.0,
            present=not has_log,
            evidence='No logging or monitoring detected — attacker activity would go unnoticed.' if not has_log else 'Logging infrastructure detected.',
            mitigations=['Implement structured audit logging for all auth events', 'Set up real-time alerting on anomalies', 'Centralise logs in a SIEM (Splunk, ELK)'],
        ),

        # ── Privilege Escalation ─────────────────────────────────────────────
        AttackVector(
            id='privesc_no_rbac',
            name='Privilege Escalation via Missing RBAC',
            stage='Privilege Escalation',
            tactic='TA0004', technique='T1548',
            description='Without role-based access control, any authenticated user may access admin functions.',
            exploitability=7.5 if has_auth else 9.0,
            impact=9.0,
            present=True,  # always relevant
            evidence='No RBAC middleware detected — privilege boundaries may not be enforced.',
            mitigations=['Implement role-based access control middleware', 'Validate permissions on every protected endpoint', 'Apply principle of least privilege'],
        ),

        # ── Defense Evasion ──────────────────────────────────────────────────
        AttackVector(
            id='evasion_no_rate_limit',
            name='Brute Force / Credential Stuffing',
            stage='Defense Evasion',
            tactic='TA0005', technique='T1110',
            description='Without rate limiting, attackers can attempt unlimited login or API requests without detection.',
            exploitability=8.0 if not has_rate else 2.5,
            impact=7.0,
            present=not has_rate,
            evidence='No rate limiting middleware detected — brute force attacks are uninhibited.' if not has_rate else 'Rate limiting controls detected.',
            mitigations=['Implement rate limiting on authentication endpoints', 'Add CAPTCHA for repeated failures', 'Deploy IP-based throttling at the gateway level'],
        ),

        # ── Lateral Movement ─────────────────────────────────────────────────
        AttackVector(
            id='lateral_unencrypted',
            name='Internal Traffic Interception',
            stage='Lateral Movement',
            tactic='TA0008', technique='T1557',
            description='Unencrypted internal communications allow attackers to intercept credentials and session tokens.',
            exploitability=6.0 if not has_enc else 1.5,
            impact=8.5,
            present=not has_enc,
            evidence='No encryption libraries detected — internal traffic may be unencrypted.' if not has_enc else 'Encryption libraries present.',
            mitigations=['Enforce mTLS for all service-to-service communication', 'Use TLS 1.3 everywhere', 'Encrypt all session tokens'],
        ),

        # ── Impact ───────────────────────────────────────────────────────────
        AttackVector(
            id='impact_data_exfil',
            name='Sensitive Data Exfiltration',
            stage='Impact',
            tactic='TA0010', technique='T1041',
            description='Attackers with database access can exfiltrate all stored personal and business data.',
            exploitability=7.0 if model_count > 0 else 4.0,
            impact=10.0,
            present=model_count > 0,
            evidence=f'{model_count} data model(s) found — database contains exfiltration targets.',
            mitigations=['Encrypt sensitive columns at rest', 'Implement DLP monitoring', 'Apply row-level security and data masking', 'Audit all bulk data access'],
            affected_assets=[m.get('name','') for m in artifacts.get('models', [])[:5]],
        ),
        AttackVector(
            id='impact_dos',
            name='Denial of Service',
            stage='Impact',
            tactic='TA0040', technique='T1499',
            description='Without rate limiting or input size controls, attackers can exhaust server resources.',
            exploitability=7.5 if not has_rate else 3.0,
            impact=7.0,
            present=True,
            evidence='No rate limiting detected — application is vulnerable to resource exhaustion.' if not has_rate else 'Rate limiting partially mitigates DoS risk.',
            mitigations=['Deploy CDN with DDoS protection (Cloudflare)', 'Enforce request size limits', 'Implement circuit breakers'],
        ),
    ]
    return vectors


# ─── Kill Chain Builder ───────────────────────────────────────────────────────

def _build_kill_chain(vectors: List[AttackVector], actor_multiplier: float) -> List[Dict]:
    chain = []
    for stage in KILL_CHAIN_STAGES:
        stage_vectors = [v for v in vectors if v.stage == stage]
        present_vectors = [v for v in stage_vectors if v.present]
        max_exploit = max((v.exploitability * actor_multiplier for v in stage_vectors), default=0)
        max_impact = max((v.impact for v in stage_vectors), default=0)
        chain.append({
            'stage': stage,
            'vectors': [v.to_dict() for v in stage_vectors],
            'active_vectors': len(present_vectors),
            'total_vectors': len(stage_vectors),
            'exploitability': round(min(max_exploit, 10.0), 1),
            'impact': round(max_impact, 1),
            'risk': round(min(max_exploit * actor_multiplier, 10) * max_impact / 10, 1),
            'compromised': any(v.present and v.exploitability * actor_multiplier >= 5 for v in stage_vectors),
        })
    return chain


# ─── Business Impact ─────────────────────────────────────────────────────────

def _business_impact(artifacts: Dict, vectors: List[AttackVector]) -> Dict:
    model_count = _model_count(artifacts)
    api_count = _api_count(artifacts)
    critical_vectors = [v for v in vectors if v.present and v.exploitability >= 8 and v.impact >= 8]

    data_breach_risk = 'Critical' if model_count > 5 and not _has_encryption(artifacts) else \
                       'High' if model_count > 0 else 'Medium'
    service_disruption = 'High' if not _has_rate_limit(artifacts) else 'Low'
    reputational_damage = 'Critical' if len(critical_vectors) >= 3 else \
                          'High' if len(critical_vectors) >= 1 else 'Medium'
    regulatory_exposure = 'Critical' if model_count > 0 and not _has_encryption(artifacts) else 'Medium'

    return {
        'data_breach_risk': data_breach_risk,
        'service_disruption': service_disruption,
        'reputational_damage': reputational_damage,
        'regulatory_exposure': regulatory_exposure,
        'critical_attack_paths': len(critical_vectors),
        'estimated_breach_cost': (
            'High (>$1M)' if len(critical_vectors) >= 3 else
            'Medium ($100K–$1M)' if len(critical_vectors) >= 1 else
            'Low (<$100K)'
        ),
    }


# ─── Main Engine ─────────────────────────────────────────────────────────────

class ThreatSimulator:
    """
    Simulates attack scenarios against a scanned codebase.
    Returns kill chains, heat map data, and business impact per threat actor.
    """

    def simulate(self, artifacts: Dict, actor_id: str = 'apt') -> Dict[str, Any]:
        actor = THREAT_ACTORS.get(actor_id, THREAT_ACTORS['apt'])
        multiplier = actor['exploitability_multiplier']

        vectors = _build_vectors(artifacts)
        kill_chain = _build_kill_chain(vectors, multiplier)
        business_impact = _business_impact(artifacts, vectors)

        present_vectors = [v for v in vectors if v.present]
        critical_vectors = [v for v in present_vectors if v.exploitability * multiplier >= 7 and v.impact >= 7]
        overall_risk = round(
            sum(v.exploitability * multiplier * v.impact / 10 for v in present_vectors) /
            max(len(present_vectors), 1), 1
        )
        overall_risk = min(overall_risk, 10.0)

        return {
            'actor': actor,
            'kill_chain': kill_chain,
            'vectors': [v.to_dict() for v in vectors],
            'heat_map': [
                {
                    'id': v.id,
                    'name': v.name,
                    'stage': v.stage,
                    'exploitability': round(min(v.exploitability * multiplier, 10), 1),
                    'impact': round(v.impact, 1),
                    'present': v.present,
                }
                for v in vectors
            ],
            'business_impact': business_impact,
            'summary': {
                'total_vectors': len(vectors),
                'active_vectors': len(present_vectors),
                'critical_vectors': len(critical_vectors),
                'overall_risk': overall_risk,
                'risk_label': (
                    'Critical' if overall_risk >= 8 else
                    'High' if overall_risk >= 6 else
                    'Medium' if overall_risk >= 4 else 'Low'
                ),
                'stages_compromised': sum(1 for s in kill_chain if s['compromised']),
            },
            'available_actors': THREAT_ACTORS,
        }
