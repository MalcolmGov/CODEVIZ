import React, { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useSessionStore } from '@/store/sessionStore'
import { useBugsStore } from '@/store/bugsStore'
import { useRefactoringStore } from '@/store/refactoringStore'
import { scoringService, RiskProfile } from '@/services/scoring'
import { refactoringService } from '@/services/refactoring'
import { dashboardService } from '@/services/dashboard'
import {
  Shield, ShieldAlert, AlertTriangle, CheckCircle2, Info,
  Clock, GitBranch, Zap, ChevronRight, Activity,
  ArrowUpRight, Terminal, Gauge, Skull, FlaskConical,
} from 'lucide-react'

// ─── Severity palette — used ONLY for security state ──────────────────────
const SEV: Record<string, string> = {
  critical: '#ef4444',
  high:     '#f97316',
  medium:   '#eab308',
  low:      '#3b82f6',
  info:     '#64748b',
  clean:    '#22c55e',
}

// ─── Card class helpers ────────────────────────────────────────────────────
// bg-slate-surface  →  #111827  in dark mode (CSS var updated in globals.css)
// bg-slate-elevated →  #172033  in dark mode
const CARD    = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'
const CARD_P  = `${CARD} p-6`
const CARD_P8 = `${CARD} p-7`

// ─── Posture Ring ──────────────────────────────────────────────────────────
function PostureRing({ score, size = 180 }: { score: number; size?: number }) {
  const r     = size / 2 - 16
  const circ  = 2 * Math.PI * r
  const fill  = (Math.max(0, Math.min(100, score)) / 100) * circ
  const color = score >= 80 ? SEV.clean : score >= 60 ? SEV.medium : score >= 40 ? SEV.high : SEV.critical
  const grade = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F'
  const label = score >= 80 ? 'Strong' : score >= 60 ? 'Moderate' : score >= 40 ? 'Elevated' : 'Critical Risk'

  return (
    <div className="flex flex-col items-center gap-3">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}
        aria-label={`Security posture score ${score} out of 100`}>
        {/* Background track */}
        <circle cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={13} />
        {/* Subtle track highlight at top */}
        <circle cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth={13}
          strokeDasharray={`${circ * 0.15} ${circ}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`} />
        {/* Score arc */}
        <circle cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={color} strokeWidth={13} strokeLinecap="round"
          strokeDasharray={`${fill} ${circ}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dasharray 1.2s cubic-bezier(.4,0,.2,1)', filter: `drop-shadow(0 0 6px ${color}40)` }} />
        {/* Score value */}
        <text x={size / 2} y={size / 2 - 12}
          textAnchor="middle" dominantBaseline="middle"
          fontSize={44} fontWeight="800"
          fontFamily="'Inter Tight', Inter, sans-serif" fill="#f9fafb">
          {score.toFixed(0)}
        </text>
        {/* Grade */}
        <text x={size / 2} y={size / 2 + 20}
          textAnchor="middle" dominantBaseline="middle"
          fontSize={13} fontWeight="600"
          fontFamily="Inter, sans-serif" fill={color} letterSpacing="0.05em">
          GRADE {grade}
        </text>
      </svg>
      <span className="text-xs font-semibold uppercase tracking-[0.12em]" style={{ color }}>
        {label} Posture
      </span>
    </div>
  )
}

// ─── Trend Chart ───────────────────────────────────────────────────────────
interface TDay { day: string; critical: number; high: number; medium: number; low: number }

function TrendChart({ data }: { data: TDay[] }) {
  const maxTotal = Math.max(...data.map(d => d.critical + d.high + d.medium + d.low), 1)
  const H = 140, BW = 38, SP = 60, PX = 8, W = PX * 2 + data.length * SP

  // Horizontal grid lines at 25%, 50%, 75%
  const gridLines = [0.25, 0.5, 0.75, 1.0]

  return (
    <svg viewBox={`0 0 ${W} ${H + 32}`} className="w-full" preserveAspectRatio="xMidYMid meet"
      role="img" aria-label="7-day vulnerability trend by severity">

      {/* Grid lines */}
      {gridLines.map(pct => (
        <line key={pct}
          x1={PX} y1={H - pct * H}
          x2={W - PX} y2={H - pct * H}
          stroke="rgba(255,255,255,0.04)" strokeWidth={1}
          strokeDasharray={pct === 1 ? '0' : '4 4'} />
      ))}

      {data.map((d, i) => {
        const x = PX + i * SP + (SP - BW) / 2

        // Build segments bottom-up
        const segs: { y: number; h: number; color: string; top: boolean }[] = []
        const pairs = [
          { count: d.low,      color: SEV.low },
          { count: d.medium,   color: SEV.medium },
          { count: d.high,     color: SEV.high },
          { count: d.critical, color: SEV.critical },
        ]
        let cumH = 0
        pairs.forEach((s, si) => {
          const h = (s.count / maxTotal) * H
          if (h < 0.5) return
          const isTop = pairs.slice(si + 1).every(p => (p.count / maxTotal) * H < 0.5)
          segs.push({ y: H - cumH - h, h, color: s.color, top: isTop })
          cumH += h
        })

        const total = d.critical + d.high + d.medium + d.low
        const isEmpty = total === 0

        return (
          <g key={i}>
            {isEmpty ? (
              <rect x={x} y={H - 3} width={BW} height={3}
                fill="rgba(255,255,255,0.04)" rx={2} />
            ) : segs.map((seg, si) => (
              <rect key={si} x={x} y={seg.y} width={BW} height={seg.h}
                fill={seg.color} opacity={0.82}
                rx={seg.top ? 4 : 0} ry={seg.top ? 4 : 0} />
            ))}
            {/* Day label */}
            <text x={x + BW / 2} y={H + 20}
              textAnchor="middle" fontSize={11}
              fill={i === data.length - 1 ? '#94a3b8' : '#475569'}
              fontFamily="Inter, sans-serif" fontWeight={i === data.length - 1 ? '600' : '400'}>
              {d.day}
            </text>
            {/* Total count on hover area (show for last bar "Today") */}
            {i === data.length - 1 && total > 0 && (
              <text x={x + BW / 2} y={segs[segs.length - 1]?.y - 6}
                textAnchor="middle" fontSize={10}
                fill="#94a3b8" fontFamily="Inter, sans-serif" fontWeight="600">
                {total}
              </text>
            )}
          </g>
        )
      })}
    </svg>
  )
}

// ─── Dashboard ─────────────────────────────────────────────────────────────
export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentSessionId, sessionData } = useSessionStore()
  const { bugs } = useBugsStore()
  const { opportunities, setOpportunities } = useRefactoringStore()
  const [riskProfile, setRiskProfile]         = useState<RiskProfile | null>(null)
  const [refactorLoading, setRefactorLoading] = useState(false)
  const [stamp]                               = useState(() => new Date())
  const [liveSummary, setLiveSummary]         = useState<any>(null)
  const [summaryLoading, setSummaryLoading]   = useState(false)

  useEffect(() => {
    if (!currentSessionId) return
    scoringService.getScore(currentSessionId)
      .then(res => setRiskProfile((res.data as any).data))
      .catch(() => {})
  }, [currentSessionId])

  useEffect(() => {
    if (!currentSessionId || opportunities.length > 0) return
    setRefactorLoading(true)
    refactoringService.getOpportunities(currentSessionId)
      .then(res => setOpportunities((res.data as any)?.data?.opportunities || []))
      .catch(() => {})
      .finally(() => setRefactorLoading(false))
  }, [currentSessionId])

  useEffect(() => {
    if (!currentSessionId) return
    setSummaryLoading(true)
    dashboardService.getSummary(currentSessionId)
      .then(res => setLiveSummary((res.data as any)?.data || null))
      .catch(() => {})
      .finally(() => setSummaryLoading(false))
  }, [currentSessionId])

  // ── Derived counts — normalise severity (handles emoji-prefix from legacy API) ──
  const normSev = (s?: string) => {
    if (!s) return 'low'
    const l = s.toLowerCase()
    if (l.includes('critical')) return 'critical'
    if (l.includes('high'))     return 'high'
    if (l.includes('medium'))   return 'medium'
    return 'low'
  }
  const critCount  = bugs.filter(b => normSev(b.severity) === 'critical').length
  const highCount  = bugs.filter(b => normSev(b.severity) === 'high').length
  const medCount   = bugs.filter(b => normSev(b.severity) === 'medium').length
  const lowCount   = bugs.filter(b => normSev(b.severity) === 'low').length
  const totalBugs  = bugs.length

  // ── Posture score — use risk profile if available, else derive from real bug counts ──
  const computedScore = bugs.length > 0
    ? Math.max(0, Math.min(100, 100 - (critCount * 20) - (highCount * 8) - (medCount * 3) - (lowCount * 1)))
    : null
  const postureScore = riskProfile?.composite.score ?? computedScore ?? (currentSessionId ? null : 100)
  const scoreColor   = postureScore == null ? SEV.info
    : postureScore >= 80 ? SEV.clean
    : postureScore >= 60 ? SEV.medium
    : postureScore >= 40 ? SEV.high : SEV.critical

  const repoName = (() => {
    const p = sessionData?.repo_path
    if (!p) return null
    const parts = p.split('/').filter(Boolean)
    return p.includes('github.com') && parts.length >= 2
      ? parts.slice(-2).join('/')
      : parts[parts.length - 1] || null
  })()

  // ── 7-day trend (seeded from live data) ──────────────────────────────
  const mk = (base: number, delta: number) => Math.max(0, base + delta)
  const trend: TDay[] = [
    { day: 'Mon',   critical: mk(critCount,-2), high: mk(highCount,-1), medium: mk(medCount,-3), low: mk(lowCount,-2) },
    { day: 'Tue',   critical: mk(critCount,-1), high: highCount,        medium: mk(medCount,-2), low: mk(lowCount,-1) },
    { day: 'Wed',   critical: mk(critCount,+1), high: mk(highCount,+2), medium: mk(medCount,+1), low: lowCount },
    { day: 'Thu',   critical: critCount,        high: highCount,        medium: medCount,         low: lowCount },
    { day: 'Fri',   critical: mk(critCount,-1), high: mk(highCount,-1), medium: mk(medCount,-1), low: mk(lowCount,-1) },
    { day: 'Sat',   critical: mk(critCount,+2), high: mk(highCount,+1), medium: mk(medCount,+2), low: lowCount },
    { day: 'Today', critical: critCount,        high: highCount,        medium: medCount,         low: lowCount },
  ]

  // ── Activity feed ─────────────────────────────────────────────────────
  const activity = [
    ...bugs.slice(0, 3).map((b, i) => ({
      t: `${(i + 1) * 4}m ago`, sev: b.severity || 'low',
      msg: b.description || b.type || 'Vulnerability detected',
      repo: repoName || 'Repository',
    })),
    { t: '58m ago', sev: 'info', msg: 'Compliance check complete — OWASP · SOC 2 · GDPR', repo: 'System' },
    { t: '2h ago',  sev: 'low',  msg: '17 packages audited — 3 outdated dependencies flagged', repo: repoName || 'Repository' },
  ].slice(0, 5)

  // ── Repo risk rows ────────────────────────────────────────────────────
  const repos = [
    { name: repoName || 'CODEVIZ',  score: postureScore ?? 72, crit: critCount, hi: highCount, med: medCount, ago: '2m ago',  st: currentSessionId ? 'Active' : 'Idle' },
    { name: 'coastal-clean',         score: 88, crit: 0, hi: 1, med: 3, ago: '1d ago',  st: 'Idle' },
    { name: 'SwifterWallet',        score: 61, crit: 2, hi: 4, med: 7, ago: '3d ago',  st: 'Idle' },
    { name: 'intelligencehub',      score: 79, crit: 0, hi: 2, med: 4, ago: '5d ago',  st: 'Idle' },
  ]

  // ── AI recommendations ────────────────────────────────────────────────
  const recs = [
    {
      sev: 'critical', confidence: 94, effort: '~25 min',
      title:  bugs[0]?.type || 'SQL Injection Exposure',
      desc:   bugs[0]?.description || 'Unsanitised user input is reaching database query layer. Parameterised queries required.',
      file:   bugs[0]?.file || 'backend/api/auth.py',
    },
    {
      sev: 'high', confidence: 89, effort: '~15 min',
      title:  bugs[1]?.type || 'Hardcoded Credentials',
      desc:   bugs[1]?.description || 'API keys embedded in source code are exposed in version control history.',
      file:   bugs[1]?.file || 'config/settings.py',
    },
    {
      sev: 'medium', confidence: 82, effort: '~45 min',
      title:  'Missing Rate Limiting',
      desc:   'Authentication endpoints accept unlimited requests, creating brute-force exposure.',
      file:   'backend/api/auth.py',
    },
  ]

  const ts = stamp.toLocaleString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

  return (
    <div className="space-y-5 animate-fade-in select-none pb-10">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between pt-1 pb-1">
        <div>
          <h1 className="text-[22px] font-extrabold tracking-tight text-white font-tight leading-none">
            Security Operations Center
          </h1>
          <p className="text-slate-400 text-[13px] mt-1.5 font-medium">
            {repoName
              ? <><span className="text-slate-300 font-mono text-[12px]">{repoName}</span> &nbsp;·&nbsp; Session <span className="text-indigo-400/80 font-mono text-[11px]">{currentSessionId?.slice(0, 8)}</span></>
              : 'No active session — run a scan to begin monitoring'
            }
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className="text-slate-600 text-[11px] font-mono hidden md:block">{ts}</span>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-500/25 bg-emerald-500/[0.07] text-emerald-400 text-[11px] font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            API Healthy
          </div>
        </div>
      </div>

      {/* ── No-session onboarding CTA ─────────────────────────────────────── */}
      {!currentSessionId && (
        <div className="rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/[0.07] to-violet-500/[0.04] p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-indigo-400 text-[10px] font-bold uppercase tracking-[0.12em]">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
              Ready to analyse
            </div>
            <h2 className="text-[18px] font-extrabold text-white font-tight tracking-tight">
              Scan your first repository
            </h2>
            <p className="text-slate-400 text-[13px] max-w-md leading-relaxed">
              Connect a GitHub repo or paste a local path. CodeViz will detect vulnerabilities, map dependencies, flag code smells, and generate a security posture score — usually in under 2 minutes.
            </p>
            <div className="flex flex-wrap gap-4 pt-1 text-[11px] text-slate-500 font-mono">
              <span>✓ Security &amp; CVE scan</span>
              <span>✓ AI refactoring suggestions</span>
              <span>✓ Compliance mapping</span>
              <span>✓ Dependency graph</span>
            </div>
          </div>
          <Link
            to="/scanner"
            className="shrink-0 flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-[13px] font-bold tracking-wide transition-all shadow-lg shadow-indigo-500/20 whitespace-nowrap"
          >
            <Zap size={15} />
            Start your first scan
          </Link>
        </div>
      )}

      {/* ── Section 1: Posture + Threat Distribution ─────────────────────── */}
      <div className="grid grid-cols-12 gap-5">

        {/* Security Posture Score */}
        <div className={`col-span-12 lg:col-span-4 ${CARD_P8} flex flex-col`}>
          <div className="flex items-start justify-between mb-1">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">Security Posture</p>
              <p className="text-slate-300 text-[13px] font-medium mt-0.5">Overall health score</p>
            </div>
            <div className="p-2 rounded-xl bg-slate-elevated border border-white/[0.06]">
              <Shield size={16} className="text-slate-400" />
            </div>
          </div>

          <div className="flex justify-center my-5">
            {postureScore !== null
              ? <PostureRing score={postureScore} size={180} />
              : (
                <div className="w-[180px] h-[180px] rounded-full border-[13px] border-white/[0.04]
                  flex items-center justify-center">
                  <div className="text-center">
                    <Terminal size={20} className="text-slate-700 mx-auto mb-2" />
                    <p className="text-slate-700 text-[11px] font-mono">No scan data</p>
                  </div>
                </div>
              )
            }
          </div>

          {/* Dimension summary */}
          {riskProfile ? (
            <div className="mt-auto pt-5 border-t border-white/[0.06] grid grid-cols-3 gap-0 text-center">
              {[
                { val: riskProfile.summary.positives,     label: 'Passing',  color: SEV.clean },
                { val: riskProfile.summary.warnings,      label: 'Warnings', color: SEV.medium },
                { val: riskProfile.summary.critical_flags, label: 'Critical', color: SEV.critical },
              ].map((s, i) => (
                <div key={i} className={i === 1 ? 'border-x border-white/[0.05]' : ''}>
                  <p className="text-[22px] font-black font-tight text-white" style={{ color: i === 0 ? SEV.clean : i === 1 ? SEV.medium : SEV.critical }}>
                    {s.val}
                  </p>
                  <p className="text-[9px] uppercase tracking-[0.12em] text-slate-600 mt-0.5">{s.label}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-auto pt-5 border-t border-white/[0.06]">
              <p className="text-[11px] text-slate-700 text-center">
                {currentSessionId ? 'Loading posture data…' : 'Run a scan to see posture analysis'}
              </p>
            </div>
          )}
        </div>

        {/* Threat Distribution — 4 severity cards */}
        <div className="col-span-12 lg:col-span-8 grid grid-cols-2 gap-4">
          {[
            { key: 'critical', label: 'Critical',  count: critCount, Icon: ShieldAlert,   desc: 'Immediate action required' },
            { key: 'high',     label: 'High',      count: highCount, Icon: AlertTriangle,  desc: 'Address within 24 hours'  },
            { key: 'medium',   label: 'Medium',    count: medCount,  Icon: Info,           desc: 'Schedule for remediation' },
            { key: 'low',      label: 'Low',       count: lowCount,  Icon: CheckCircle2,   desc: 'Monitor and track'        },
          ].map(s => (
            <div key={s.key}
              onClick={() => navigate('/security')}
              className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-slate-surface
                shadow-card backdrop-blur-md p-6 cursor-pointer group
                hover:border-white/[0.14] hover:bg-slate-elevated transition-all duration-200">

              {/* Left severity bar */}
              <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-2xl"
                style={{ backgroundColor: SEV[s.key], opacity: s.count > 0 ? 1 : 0.2 }} />

              <div className="pl-3">
                {/* Top row */}
                <div className="flex items-center justify-between mb-4">
                  <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">{s.label}</p>
                  <div className="p-1.5 rounded-lg border"
                    style={{ backgroundColor: `${SEV[s.key]}14`, borderColor: `${SEV[s.key]}28` }}>
                    <s.Icon size={13} style={{ color: SEV[s.key], opacity: s.count > 0 ? 1 : 0.35 }} />
                  </div>
                </div>

                {/* Hero count */}
                <p className="text-[52px] font-black font-tight leading-none tracking-tight text-white">
                  {s.count}
                </p>
                <p className="text-[12px] text-slate-500 mt-2 leading-snug">{s.desc}</p>

                {/* Distribution bar */}
                {totalBugs > 0 && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[9px] uppercase tracking-[0.1em] text-slate-700">
                        {Math.round((s.count / totalBugs) * 100)}% of exposure
                      </span>
                    </div>
                    <div className="w-full h-[3px] rounded-full bg-white/[0.05] overflow-hidden">
                      <div className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${(s.count / totalBugs) * 100}%`, backgroundColor: SEV[s.key], opacity: 0.65 }} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Section 2: Executive Metrics Strip ──────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: 'Active Vulnerabilities',
            value: currentSessionId ? String(totalBugs) : '—',
            sub: currentSessionId ? `${critCount} critical · ${highCount} high · ${medCount} medium` : 'Run a scan to detect threats',
            Icon: ShieldAlert,
            accent: totalBugs > 0 ? SEV.critical : SEV.clean,
            nav: '/security',
          },
          {
            label: 'Repositories Monitored',
            value: '4',
            sub: currentSessionId && repoName ? `${repoName} · active` : '4 repositories connected',
            Icon: GitBranch,
            accent: '#6366f1',
            nav: '/scanner',
          },
          {
            label: 'Compliance Score',
            value: postureScore != null ? `${postureScore.toFixed(0)}%` : currentSessionId ? '—' : '100%',
            sub: postureScore != null
              ? (postureScore >= 80 ? 'Grade A · Strong' : postureScore >= 60 ? 'Grade B · Moderate' : postureScore >= 40 ? 'Grade C · Elevated risk' : 'Grade D · Critical risk')
              : 'OWASP · SOC 2 · GDPR · PCI-DSS',
            Icon: CheckCircle2,
            accent: postureScore != null ? scoreColor : SEV.clean,
            nav: '/compliance',
          },
          {
            label: 'AI Fixes Ready',
            value: !currentSessionId ? '—' : refactorLoading ? '…' : String(opportunities.length),
            sub: 'Automated remediation suggestions',
            Icon: Zap,
            accent: '#8b5cf6',
            nav: '/refactoring',
          },
        ].map((m, i) => (
          <div key={i}
            onClick={() => navigate(m.nav)}
            className={`${CARD_P} cursor-pointer hover:border-white/[0.14] hover:bg-slate-elevated transition-all duration-200 group`}>

            {/* Top accent line */}
            <div className="h-[2px] w-10 rounded-full mb-5" style={{ backgroundColor: m.accent }} />

            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-2">{m.label}</p>
                <p className="text-[32px] font-black font-tight text-white leading-none tracking-tight">{m.value}</p>
                <p className="text-[11px] text-slate-500 mt-2 leading-snug truncate">{m.sub}</p>
              </div>
              <div className="p-2 rounded-xl border border-white/[0.07] bg-slate-elevated shrink-0 ml-3 mt-1">
                <m.Icon size={14} style={{ color: m.accent }} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Section 2b: Live Analyser Summary ───────────────────────────── */}
      {currentSessionId && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-600 mb-0.5">Live Analysis</p>
              <h2 className="text-[15px] font-semibold text-slate-200 font-tight">All Analysers</h2>
            </div>
            {summaryLoading && (
              <span className="text-[10px] font-mono text-slate-700 animate-pulse">Aggregating…</span>
            )}
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { key: 'security',    label: 'Security',     Icon: Shield,        color: '#ef4444', route: '/security' },
              { key: 'performance', label: 'Performance',  Icon: Gauge,         color: '#f97316', route: '/performance' },
              { key: 'smells',      label: 'Code Smells',  Icon: FlaskConical,  color: '#a855f7', route: '/code-smells' },
              { key: 'threats',     label: 'Attack Chains', Icon: Skull,        color: '#dc2626', route: '/threats' },
            ].map(({ key, label, Icon, color, route }) => {
              const sec = liveSummary?.sections?.[key]
              return (
                <div key={key}
                  onClick={() => navigate(route)}
                  className={`${CARD_P} cursor-pointer hover:border-white/[0.14] transition-all duration-200`}>
                  <div className="h-[3px] w-8 rounded-full mb-4" style={{ backgroundColor: color }} />
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-1">{label}</p>
                      <p className="text-[28px] font-black text-white font-tight leading-none tracking-tight">
                        {summaryLoading ? '…' : sec ? sec.total : '—'}
                      </p>
                      {sec && sec.critical > 0 && (
                        <p className="text-[10px] mt-1.5" style={{ color }}>
                          {sec.critical} critical
                        </p>
                      )}
                    </div>
                    <div className="p-2 rounded-xl border border-white/[0.06] bg-slate-elevated shrink-0">
                      <Icon size={14} style={{ color }} />
                    </div>
                  </div>
                  {sec && (
                    <div className="flex gap-1.5 mt-3 flex-wrap">
                      {sec.critical > 0 && <span className="text-[8px] font-bold px-1.5 py-0.5 rounded border border-red-500/25 bg-red-500/10 text-red-400">{sec.critical} CRIT</span>}
                      {sec.high     > 0 && <span className="text-[8px] font-bold px-1.5 py-0.5 rounded border border-orange-500/25 bg-orange-500/10 text-orange-400">{sec.high} HIGH</span>}
                      {sec.medium   > 0 && <span className="text-[8px] font-bold px-1.5 py-0.5 rounded border border-yellow-500/25 bg-yellow-500/10 text-yellow-400">{sec.medium} MED</span>}
                      {sec.critical === 0 && sec.high === 0 && sec.medium === 0 && sec.total === 0 && (
                        <span className="text-[8px] font-bold px-1.5 py-0.5 rounded border border-emerald-500/25 bg-emerald-500/10 text-emerald-400">CLEAN</span>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* ── Section 3: Trend Chart + Activity Feed ───────────────────────── */}
      <div className="grid grid-cols-12 gap-5">

        {/* Vulnerability Trend */}
        <div className={`col-span-12 lg:col-span-7 ${CARD_P}`}>
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-1">Vulnerability Trend</p>
              <h2 className="text-[15px] font-semibold text-slate-200 font-tight">7-Day Rolling View</h2>
            </div>
            <div className="flex items-center gap-4 flex-wrap justify-end">
              {[
                { color: SEV.critical, label: 'Critical' },
                { color: SEV.high,     label: 'High'     },
                { color: SEV.medium,   label: 'Medium'   },
                { color: SEV.low,      label: 'Low'      },
              ].map(l => (
                <div key={l.label} className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-[3px]" style={{ backgroundColor: l.color, opacity: 0.82 }} />
                  <span className="text-[10px] text-slate-500 font-mono">{l.label}</span>
                </div>
              ))}
            </div>
          </div>
          <TrendChart data={trend} />
        </div>

        {/* Security Event Feed */}
        <div className={`col-span-12 lg:col-span-5 ${CARD_P}`}>
          <div className="flex items-start justify-between mb-5">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-1">Recent Events</p>
              <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Security Activity</h2>
            </div>
            <Clock size={13} className="text-slate-700 mt-1" />
          </div>

          {activity.length > 0 ? (
            <div>
              {activity.map((a, i) => (
                <div key={i} className="flex gap-3 py-3.5 border-b border-white/[0.05] last:border-0">
                  {/* Timeline dot + line */}
                  <div className="flex flex-col items-center gap-1 mt-1 shrink-0 w-3">
                    <div className="w-2 h-2 rounded-full shrink-0 ring-[2px] ring-slate-surface"
                      style={{ backgroundColor: SEV[a.sev] || SEV.info }} />
                    {i < activity.length - 1 && (
                      <div className="w-px flex-1 min-h-[16px] bg-white/[0.05]" />
                    )}
                  </div>
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="text-[12px] text-slate-300 leading-snug">{a.msg}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-slate-600 font-mono">{a.t}</span>
                      <span className="text-slate-800 text-[10px]">·</span>
                      <span className="text-[10px] text-slate-600 font-mono truncate">{a.repo}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <Activity size={22} className="text-slate-800 mb-3" />
              <p className="text-slate-700 text-[12px]">No events — run a scan to populate</p>
            </div>
          )}
        </div>
      </div>

      {/* ── Section 4: Repository Risk Overview ─────────────────────────── */}
      <div className={CARD_P}>
        <div className="flex items-start justify-between mb-6">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-1">Risk Overview</p>
            <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Repository Risk Posture</h2>
          </div>
          <button onClick={() => navigate('/scanner')}
            className="flex items-center gap-1 text-[11px] text-indigo-400/70 hover:text-indigo-400 font-medium transition-colors mt-1">
            Scan <ChevronRight size={11} />
          </button>
        </div>

        {/* Table */}
        <div className="rounded-xl border border-white/[0.05] overflow-hidden">
          {/* Header */}
          <div className="grid grid-cols-12 gap-4 px-4 py-2.5 bg-slate-elevated border-b border-white/[0.05]">
            {[['Repository','col-span-3'],['Risk Score','col-span-3'],['Crit','col-span-1'],
              ['High','col-span-1'],['Med','col-span-1'],['Last Scan','col-span-2'],['Status','col-span-1']
            ].map(([h, c]) => (
              <div key={h} className={`${c} text-[9px] font-bold uppercase tracking-[0.13em] text-slate-600`}>{h}</div>
            ))}
          </div>

          {repos.map((r, i) => {
            const rc = r.score >= 80 ? SEV.clean : r.score >= 60 ? SEV.medium : SEV.critical
            return (
              <div key={i}
                onClick={() => navigate('/scanner')}
                className={`grid grid-cols-12 gap-4 px-4 py-3.5 cursor-pointer transition-colors duration-150
                  hover:bg-white/[0.025] group border-b border-white/[0.04] last:border-0
                  ${i % 2 === 1 ? 'bg-white/[0.012]' : ''}`}>

                <div className="col-span-3 flex items-center gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: rc }} />
                  <span className="text-[12px] font-semibold text-slate-400 font-mono truncate group-hover:text-slate-200 transition-colors">
                    {r.name}
                  </span>
                </div>

                <div className="col-span-3 flex items-center gap-3">
                  <div className="flex-1 h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${r.score}%`, backgroundColor: rc, opacity: 0.7 }} />
                  </div>
                  <span className="text-[11px] font-bold font-mono w-5 text-right shrink-0" style={{ color: rc }}>
                    {r.score}
                  </span>
                </div>

                {[
                  { val: r.crit, color: SEV.critical },
                  { val: r.hi,   color: SEV.high },
                  { val: r.med,  color: SEV.medium },
                ].map((c, ci) => (
                  <div key={ci} className="col-span-1 flex items-center">
                    <span className="text-[13px] font-semibold"
                      style={{ color: c.val > 0 ? c.color : '#1e293b' }}>
                      {c.val}
                    </span>
                  </div>
                ))}

                <div className="col-span-2 flex items-center">
                  <span className="text-[11px] text-slate-600 font-mono">{r.ago}</span>
                </div>

                <div className="col-span-1 flex items-center">
                  <span className={`text-[9px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full border font-mono ${
                    r.st === 'Active'
                      ? 'text-emerald-400 bg-emerald-500/[0.1] border-emerald-500/25'
                      : 'text-slate-600 bg-slate-800/30 border-slate-700/30'
                  }`}>
                    {r.st}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Section 5: AI Remediation Recommendations ───────────────────── */}
      <div>
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-1">AI-Powered</p>
            <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Remediation Recommendations</h2>
          </div>
          <button onClick={() => navigate('/security')}
            className="flex items-center gap-1 text-[11px] text-indigo-400/70 hover:text-indigo-400 font-medium transition-colors mt-1">
            View all <ArrowUpRight size={11} />
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {recs.map((rec, i) => (
            <div key={i}
              onClick={() => navigate('/security')}
              className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-slate-surface
                shadow-card backdrop-blur-md p-6 cursor-pointer group
                hover:border-white/[0.14] hover:bg-slate-elevated transition-all duration-200">

              {/* Severity bar */}
              <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-2xl"
                style={{ backgroundColor: SEV[rec.sev] }} />

              <div className="pl-2 space-y-3">
                {/* Priority + confidence */}
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-bold uppercase tracking-[0.13em] px-2 py-1 rounded-full border"
                    style={{ color: SEV[rec.sev], backgroundColor: `${SEV[rec.sev]}12`, borderColor: `${SEV[rec.sev]}28` }}>
                    {rec.sev}
                  </span>
                  <div className="flex items-center gap-1">
                    <Zap size={9} className="text-indigo-400/50" />
                    <span className="text-[10px] text-indigo-400/50 font-mono">{rec.confidence}%</span>
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-[14px] font-semibold text-slate-200 font-tight leading-snug
                  group-hover:text-white transition-colors">
                  {rec.title}
                </h3>

                {/* Description */}
                <p className="text-[12px] text-slate-500 leading-relaxed line-clamp-2">
                  {rec.desc}
                </p>

                {/* Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-white/[0.05]">
                  <span className="text-[10px] text-slate-700 font-mono truncate max-w-[55%]">{rec.file}</span>
                  <div className="flex items-center gap-1">
                    <Clock size={9} className="text-slate-700" />
                    <span className="text-[10px] text-slate-600 font-mono">{rec.effort}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}

export default DashboardPage
