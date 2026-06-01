"""
Multi-Dimensional Risk Scoring Engine
Tier 2 Feature: Computes Security, Code Quality, Dependency Health,
Architecture, and Business Risk scores from scan artifacts.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DimensionScore:
    name: str
    score: float          # 0-100
    grade: str            # A-F
    label: str            # e.g. "Strong", "Fair", "Critical"
    color: str            # tailwind color token for UI
    findings: list        # list of finding strings (good/bad)
    weight: float         # composite weight (0-1)


def _grade(score: float) -> tuple[str, str, str]:
    """Return (grade, label, color) for a score."""
    if score >= 90:
        return 'A', 'Excellent', 'emerald'
    elif score >= 80:
        return 'B', 'Strong', 'green'
    elif score >= 70:
        return 'C', 'Fair', 'amber'
    elif score >= 60:
        return 'D', 'Weak', 'orange'
    else:
        return 'F', 'Critical', 'rose'


def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, val))


# ─── Dimension 1: Security ───────────────────────────────────────────────────

def _score_security(artifacts: Dict) -> DimensionScore:
    score = 100.0
    findings = []

    apis = artifacts.get('apis', [])
    middleware = artifacts.get('middleware', [])
    error_handlers = artifacts.get('error_handlers', [])
    constants = artifacts.get('constants', [])
    functions = artifacts.get('functions', [])

    # Auth endpoint presence
    auth_keywords = ['auth', 'login', 'token', 'oauth', 'verify', 'session', 'jwt']
    auth_apis = [a for a in apis if any(k in a.get('path', '').lower() for k in auth_keywords)]
    if auth_apis:
        score += 8
        findings.append(f'✅ {len(auth_apis)} authentication endpoint(s) detected')
    else:
        score -= 15
        findings.append('⚠️ No authentication endpoints detected')

    # Security middleware
    sec_middleware = [m for m in middleware if any(
        k in m.get('name', '').lower() for k in ['auth', 'cors', 'csrf', 'helmet', 'rate', 'jwt', 'session']
    )]
    if sec_middleware:
        score += 5
        findings.append(f'✅ Security middleware present ({", ".join(m["name"] for m in sec_middleware[:3])})')
    else:
        score -= 10
        findings.append('⚠️ No security middleware detected')

    # Error handlers (lack = unhandled exceptions = info leakage)
    if error_handlers:
        score += 5
        findings.append(f'✅ {len(error_handlers)} error handler(s) configured')
    else:
        score -= 12
        findings.append('⚠️ No error handlers — exceptions may leak stack traces')

    # Hardcoded secrets in constants
    secret_keywords = ['password', 'secret', 'token', 'key', 'api_key', 'apikey', 'passwd']
    risky_consts = [c for c in constants if any(
        k in c.get('name', '').lower() for k in secret_keywords
    ) and any(
        v.strip().startswith(('"', "'")) for v in [c.get('value', '')]
    )]
    if risky_consts:
        penalty = min(len(risky_consts) * 18, 40)
        score -= penalty
        findings.append(f'🔴 {len(risky_consts)} potential hardcoded secret(s) in constants')
    else:
        findings.append('✅ No hardcoded secrets detected in constants')

    # Unauthenticated API surface (large attack surface)
    if len(apis) > 20:
        score -= 8
        findings.append(f'⚠️ Large API surface: {len(apis)} endpoints increase attack exposure')
    elif len(apis) > 10:
        score -= 3
        findings.append(f'ℹ️ Moderate API surface: {len(apis)} endpoints')

    # SQL injection risk patterns in function names/files
    sql_risk_funcs = [f for f in functions if any(
        k in f.get('name', '').lower() for k in ['execute', 'query', 'raw', 'sql']
    )]
    if sql_risk_funcs:
        score -= min(len(sql_risk_funcs) * 4, 15)
        findings.append(f'⚠️ {len(sql_risk_funcs)} function(s) with raw query indicators — review for injection')

    score = _clamp(score)
    g, lbl, col = _grade(score)
    return DimensionScore('Security', score, g, lbl, col, findings, weight=0.35)


# ─── Dimension 2: Code Quality ────────────────────────────────────────────────

def _score_quality(artifacts: Dict) -> DimensionScore:
    score = 70.0
    findings = []

    stats = artifacts.get('statistics', {})
    functions = artifacts.get('functions', [])
    classes = artifacts.get('classes', [])
    interfaces = artifacts.get('interfaces', [])
    constants = artifacts.get('constants', [])
    error_handlers = artifacts.get('error_handlers', [])
    loc = stats.get('lines_of_code', 0)
    fn_count = len(functions)

    # Average lines per function (complexity proxy)
    if fn_count > 0 and loc > 0:
        avg_lpf = loc / fn_count
        if avg_lpf < 20:
            score += 15
            findings.append(f'✅ Lean functions — avg {avg_lpf:.0f} lines/function')
        elif avg_lpf < 50:
            score += 5
            findings.append(f'ℹ️ Moderate function length — avg {avg_lpf:.0f} lines/function')
        elif avg_lpf < 100:
            score -= 10
            findings.append(f'⚠️ Long functions — avg {avg_lpf:.0f} lines/function (consider splitting)')
        else:
            score -= 20
            findings.append(f'🔴 Very long functions — avg {avg_lpf:.0f} lines/function (high complexity)')
    else:
        findings.append('ℹ️ Unable to compute function complexity')

    # Class count (good OOP structure)
    if len(classes) > 5:
        score += 10
        findings.append(f'✅ {len(classes)} classes — structured OOP design')
    elif len(classes) > 0:
        score += 4
        findings.append(f'ℹ️ {len(classes)} classes detected')
    else:
        score -= 5
        findings.append('⚠️ No classes detected — consider structured design')

    # TypeScript interfaces (type safety)
    if len(interfaces) >= 10:
        score += 12
        findings.append(f'✅ {len(interfaces)} interfaces — strong type safety')
    elif len(interfaces) > 0:
        score += 5
        findings.append(f'ℹ️ {len(interfaces)} interface(s) detected')
    else:
        findings.append('ℹ️ No TypeScript interfaces detected')

    # Constants (avoids magic numbers)
    if len(constants) >= 5:
        score += 5
        findings.append(f'✅ {len(constants)} constants defined — good practice')

    # Error handlers
    if error_handlers:
        score += 5
        findings.append(f'✅ Error handling present')
    else:
        score -= 8
        findings.append('⚠️ No error handlers — unexpected failures may be unhandled')

    score = _clamp(score)
    g, lbl, col = _grade(score)
    return DimensionScore('Code Quality', score, g, lbl, col, findings, weight=0.25)


# ─── Dimension 3: Dependency Health ──────────────────────────────────────────

def _score_dependencies(artifacts: Dict) -> DimensionScore:
    score = 85.0
    findings = []

    deps = artifacts.get('dependencies', [])
    prod_deps = [d for d in deps if d.get('type') not in ('npm_dev',)]
    dev_deps = [d for d in deps if d.get('type') == 'npm_dev']
    total = len(deps)

    if total == 0:
        findings.append('ℹ️ No dependencies detected')
        score = _clamp(score)
        g, lbl, col = _grade(score)
        return DimensionScore('Dependency Health', score, g, lbl, col, findings, weight=0.20)

    # Dependency count thresholds
    if total < 30:
        score += 10
        findings.append(f'✅ Lean dependency tree ({total} total)')
    elif total < 60:
        findings.append(f'ℹ️ Moderate dependency count ({total} total)')
    elif total < 100:
        score -= 12
        findings.append(f'⚠️ Large dependency tree ({total} packages) — increases supply chain risk')
    else:
        score -= 22
        findings.append(f'🔴 Very large dependency tree ({total} packages) — significant supply chain exposure')

    # Dev vs prod ratio
    if len(prod_deps) > 0 and len(dev_deps) > len(prod_deps) * 3:
        score -= 8
        findings.append(f'⚠️ Dev deps ({len(dev_deps)}) far exceed prod deps ({len(prod_deps)}) — review bundling')
    elif len(prod_deps) > 0:
        findings.append(f'✅ Healthy prod/dev split ({len(prod_deps)} prod, {len(dev_deps)} dev)')

    # Known risky package patterns
    risky_patterns = ['eval', 'exec', 'serialize', 'deserialize', 'yaml', 'pickle']
    risky_found = [d for d in deps if any(p in d.get('package', '').lower() for p in risky_patterns)]
    if risky_found:
        score -= min(len(risky_found) * 5, 20)
        findings.append(f'⚠️ {len(risky_found)} dependency(ies) with deserialization/execution risk patterns')
    else:
        findings.append('✅ No high-risk package patterns detected')

    # Python deps (requirements.txt) — check for pinned versions
    python_deps = [d for d in deps if d.get('type') == 'python']
    unpinned = [d for d in python_deps if '==' not in d.get('package', '')]
    if unpinned and len(python_deps) > 0:
        penalty = min(len(unpinned) * 3, 15)
        score -= penalty
        findings.append(f'⚠️ {len(unpinned)} Python dep(s) not pinned to exact versions')
    elif python_deps:
        findings.append(f'✅ Python dependencies use pinned versions')

    score = _clamp(score)
    g, lbl, col = _grade(score)
    return DimensionScore('Dependency Health', score, g, lbl, col, findings, weight=0.20)


# ─── Dimension 4: Architecture ───────────────────────────────────────────────

def _score_architecture(artifacts: Dict) -> DimensionScore:
    score = 55.0
    findings = []

    arch = artifacts.get('architecture', {})
    ux = artifacts.get('ux_architecture', {})
    classes = artifacts.get('classes', [])
    middleware = artifacts.get('middleware', [])
    models = artifacts.get('models', [])
    error_handlers = artifacts.get('error_handlers', [])
    apis = artifacts.get('apis', [])

    # Detected design patterns
    patterns = arch.get('patterns', [])
    if patterns:
        score += min(len(patterns) * 10, 25)
        findings.append(f'✅ Design patterns: {", ".join(patterns)}')
    else:
        findings.append('ℹ️ No structural design patterns detected')

    # Architecture layers
    layers = arch.get('layers', [])
    if layers:
        score += min(len(layers) * 6, 18)
        findings.append(f'✅ Architecture layers: {", ".join(layers)}')

    # External services
    ext_services = arch.get('external_services', [])
    if ext_services:
        score += min(len(ext_services) * 4, 12)
        findings.append(f'✅ Integrations: {", ".join(ext_services[:4])}')

    # Database models (ORM usage = good architecture)
    if models:
        score += 10
        findings.append(f'✅ {len(models)} database model(s) — ORM layer present')
    else:
        score -= 5
        findings.append('ℹ️ No ORM models detected — raw queries may be in use')

    # Middleware (separation of cross-cutting concerns)
    if middleware:
        score += 6
        findings.append(f'✅ {len(middleware)} middleware layer(s) detected')

    # Error handling layer
    if error_handlers:
        score += 5
        findings.append(f'✅ Error handling layer present')

    # Frontend architecture
    fe_framework = ux.get('frontend_framework')
    if fe_framework:
        score += 5
        findings.append(f'✅ Frontend framework: {fe_framework}')

    state_mgmt = ux.get('state_management', [])
    if state_mgmt:
        score += 5
        findings.append(f'✅ State management: {", ".join(state_mgmt)}')

    score = _clamp(score)
    g, lbl, col = _grade(score)
    return DimensionScore('Architecture', score, g, lbl, col, findings, weight=0.15)


# ─── Dimension 5: Business Risk ───────────────────────────────────────────────

def _score_business_risk(artifacts: Dict) -> DimensionScore:
    score = 80.0
    findings = []

    apis = artifacts.get('apis', [])
    models = artifacts.get('models', [])
    arch = artifacts.get('architecture', {})
    ext_services = arch.get('external_services', [])
    middleware = artifacts.get('middleware', [])

    # Authentication reduces business risk
    auth_apis = [a for a in apis if any(
        k in a.get('path', '').lower() for k in ['auth', 'login', 'token', 'oauth']
    )]
    if auth_apis:
        score += 12
        findings.append(f'✅ Authentication gates present ({len(auth_apis)} auth endpoint(s))')
    else:
        score -= 20
        findings.append('🔴 No authentication endpoints — potential open access risk')

    # API surface area (more = more business exposure)
    api_count = len(apis)
    if api_count > 40:
        score -= 18
        findings.append(f'⚠️ Very large attack surface: {api_count} public endpoints')
    elif api_count > 20:
        score -= 10
        findings.append(f'⚠️ Large API surface: {api_count} endpoints')
    elif api_count > 0:
        findings.append(f'✅ Manageable API surface: {api_count} endpoints')

    # Data model exposure risk
    if len(models) > 10:
        score -= 10
        findings.append(f'⚠️ {len(models)} data models — significant data exposure risk if not secured')
    elif len(models) > 0:
        findings.append(f'ℹ️ {len(models)} data model(s) — ensure access controls are in place')

    # External service dependencies = third-party risk
    if len(ext_services) > 5:
        score -= 12
        findings.append(f'⚠️ {len(ext_services)} external integrations increase third-party risk')
    elif ext_services:
        score -= 3
        findings.append(f'ℹ️ {len(ext_services)} external service(s) — review data sharing agreements')

    # Rate limiting / CORS middleware = reduced business risk
    rate_mid = [m for m in middleware if any(
        k in m.get('name', '').lower() for k in ['rate', 'cors', 'throttle', 'limit']
    )]
    if rate_mid:
        score += 8
        findings.append(f'✅ Rate limiting/CORS middleware detected')
    else:
        score -= 5
        findings.append('⚠️ No rate limiting detected — DoS/abuse risk')

    score = _clamp(score)
    g, lbl, col = _grade(score)
    return DimensionScore('Business Risk', score, g, lbl, col, findings, weight=0.05)


# ─── Composite Scorer ─────────────────────────────────────────────────────────

class MultiDimensionalScorer:
    """
    Computes a multi-dimensional risk profile from scan artifacts.

    Dimensions and weights:
      Security          35%
      Code Quality      25%
      Dependency Health 20%
      Architecture      15%
      Business Risk      5%
    """

    def score(self, artifacts: Dict) -> Dict[str, Any]:
        dimensions = [
            _score_security(artifacts),
            _score_quality(artifacts),
            _score_dependencies(artifacts),
            _score_architecture(artifacts),
            _score_business_risk(artifacts),
        ]

        # Weighted composite
        composite = sum(d.score * d.weight for d in dimensions)
        composite = _clamp(composite)
        comp_grade, comp_label, comp_color = _grade(composite)

        return {
            'composite': {
                'score': round(composite, 1),
                'grade': comp_grade,
                'label': comp_label,
                'color': comp_color,
            },
            'dimensions': [
                {
                    'name': d.name,
                    'score': round(d.score, 1),
                    'grade': d.grade,
                    'label': d.label,
                    'color': d.color,
                    'weight': int(d.weight * 100),
                    'findings': d.findings,
                }
                for d in dimensions
            ],
            'summary': {
                'total_findings': sum(len(d.findings) for d in dimensions),
                'critical_flags': sum(
                    sum(1 for f in d.findings if f.startswith('🔴'))
                    for d in dimensions
                ),
                'warnings': sum(
                    sum(1 for f in d.findings if f.startswith('⚠️'))
                    for d in dimensions
                ),
                'positives': sum(
                    sum(1 for f in d.findings if f.startswith('✅'))
                    for d in dimensions
                ),
            }
        }
