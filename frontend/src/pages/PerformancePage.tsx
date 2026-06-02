import React, { useState, useEffect } from 'react'
import { useSessionStore } from '@/store/sessionStore'
import { performanceService } from '@/services/performance'
import { AskAIButton } from '@/components/common/AskAIButton'
import {
  Gauge, AlertTriangle, TrendingDown, TrendingUp,
  ChevronRight, RefreshCw, Terminal, Zap, Clock,
  CheckCircle2, X, Code2,
} from 'lucide-react'
import clsx from 'clsx'

// ── Design tokens ──────────────────────────────────────────────────────────
const CARD   = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

// ── Severity helpers ───────────────────────────────────────────────────────
const SEV_COLOR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#3b82f6',
}
const SEV_ORDER: Record<string, number> = {
  critical: 0, high: 1, medium: 2, low: 3,
}

// Issue type → icon mapping
const TYPE_ICON: Record<string, React.ElementType> = {
  'N+1 Query Problem':         AlertTriangle,
  'Memory Leak':               TrendingDown,
  'Inefficient Algorithm':     Gauge,
  'Synchronous Blocking':      Clock,
  'Async Fire-and-Forget':     Zap,
  'Missing Bulk Operations':   RefreshCw,
  'Lazy Loading Issue':        TrendingDown,
  'Inefficient Loop':          RefreshCw,
}

// ── Stat card ──────────────────────────────────────────────────────────────
function StatCard({ label, value, sub, accent, icon: Icon }: {
  label: string; value: string | number; sub: string
  accent: string; icon: React.ElementType
}) {
  return (
    <div className={`${CARD} p-6`}>
      <div className="h-[3px] w-8 rounded-full mb-5" style={{ backgroundColor: accent }} />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-2">{label}</p>
          <p className="text-[32px] font-black text-white font-tight leading-none tracking-tight">{value}</p>
          <p className="text-[11px] text-slate-500 mt-2 leading-snug">{sub}</p>
        </div>
        <div className="p-2 rounded-xl border border-white/[0.06] bg-slate-elevated">
          <Icon size={15} style={{ color: accent }} />
        </div>
      </div>
    </div>
  )
}

// ── Issue detail drawer ────────────────────────────────────────────────────
function IssueDrawer({ issue, onClose }: { issue: any; onClose: () => void }) {
  const sevColor = SEV_COLOR[issue.severity] || '#64748b'
  return (
    <div className={`${CARD} p-6 space-y-4`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ backgroundColor: sevColor }} />
          <div>
            <h3 className="text-[15px] font-semibold text-slate-200 font-tight">{issue.type}</h3>
            <p className="text-[11px] font-mono text-slate-600 mt-0.5">
              {issue.file?.split('/').slice(-2).join('/')} · line {issue.line}
            </p>
          </div>
        </div>
        <button onClick={onClose} className="text-slate-700 hover:text-slate-400 transition-colors">
          <X size={16} />
        </button>
      </div>

      {/* Severity + slowdown */}
      <div className="flex flex-wrap gap-2">
        <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border"
          style={{ color: sevColor, backgroundColor: `${sevColor}12`, borderColor: `${sevColor}28` }}>
          {issue.severity}
        </span>
        {issue.slowdown && (
          <span className="text-[9px] font-mono px-2 py-1 rounded-full border border-amber-500/25 bg-amber-500/[0.08] text-amber-400">
            {issue.slowdown}
          </span>
        )}
        {issue.improvement && (
          <span className="text-[9px] font-mono px-2 py-1 rounded-full border border-emerald-500/25 bg-emerald-500/[0.08] text-emerald-400">
            ↑ {issue.improvement}
          </span>
        )}
      </div>

      {/* Description + impact */}
      <div className="space-y-3">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-1">Description</p>
          <p className="text-[12px] text-slate-400 leading-relaxed">{issue.description}</p>
        </div>
        {issue.impact && (
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-1">Impact</p>
            <p className="text-[12px] text-slate-400 leading-relaxed">{issue.impact}</p>
          </div>
        )}
      </div>

      {/* Code snippet */}
      {issue.code && (
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-2">Affected code</p>
          <div className="rounded-xl bg-slate-950/80 border border-white/[0.05] overflow-hidden">
            <div className="flex items-center justify-between px-3 py-2 bg-slate-elevated border-b border-white/[0.05]">
              <span className="text-[9px] font-mono text-slate-600 uppercase tracking-wider">
                {issue.file?.split('/').pop()} · line {issue.line}
              </span>
            </div>
            <pre className="p-4 text-[11px] font-mono text-rose-300/80 overflow-x-auto leading-relaxed max-h-[160px]">
              {issue.code}
            </pre>
          </div>
        </div>
      )}

      {/* Fix suggestion */}
      {issue.fix && (
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-2">Recommended fix</p>
          <div className="rounded-xl bg-slate-950/80 border border-emerald-500/15 overflow-hidden">
            <div className="flex items-center gap-1.5 px-3 py-2 bg-emerald-500/[0.05] border-b border-emerald-500/10">
              <CheckCircle2 size={11} className="text-emerald-400" />
              <span className="text-[9px] font-mono text-emerald-400/70 uppercase tracking-wider">optimised</span>
            </div>
            <pre className="p-4 text-[11px] font-mono text-emerald-300/80 overflow-x-auto leading-relaxed max-h-[160px]">
              {issue.fix}
            </pre>
          </div>
        </div>
      )}
      <AskAIButton
        label={issue.type}
        context={`Performance issue: ${issue.type} in ${issue.file} line ${issue.line}. Severity: ${issue.severity}. Slowdown: ${issue.slowdown || 'unknown'}. Description: ${issue.description || ''}. ${issue.fix ? `Fix: ${issue.fix}` : ''}`}
      />
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────
export const PerformancePage: React.FC = () => {
  const { currentSessionId } = useSessionStore()

  const [issues, setIssues]       = useState<any[]>([])
  const [metrics, setMetrics]     = useState<any>(null)
  const [loading, setLoading]     = useState(false)
  const [scanned, setScanned]     = useState(false)
  const [selected, setSelected]   = useState<any>(null)
  const [filterSev, setFilterSev] = useState<string>('all')
  const [filterType, setFilterType] = useState<string>('all')

  const runScan = async () => {
    if (!currentSessionId || loading) return
    setLoading(true)
    setSelected(null)
    try {
      const res = await performanceService.scan(currentSessionId)
      const d   = (res.data as any).data
      setIssues(d.issues || [])
      setMetrics(d.metrics || null)
      setScanned(true)
    } catch {
      setScanned(true)
    } finally {
      setLoading(false)
    }
  }

  // Auto-run if session exists and haven't scanned yet
  useEffect(() => {
    if (currentSessionId && !scanned) runScan()
  }, [currentSessionId])

  // Derived
  const issueTypes = [...new Set(issues.map(i => i.type))].sort()
  const filtered   = issues.filter(i =>
    (filterSev  === 'all' || i.severity === filterSev) &&
    (filterType === 'all' || i.type === filterType)
  )

  const critCount = issues.filter(i => i.severity === 'critical').length
  const highCount = issues.filter(i => i.severity === 'high').length

  // Type breakdown for the bar chart
  const byType = metrics?.by_type || {}
  const maxTypeCount = Math.max(...Object.values(byType).map(Number), 1)

  return (
    <div className="space-y-5 animate-fade-in pb-10 select-none">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
        <div>
          <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Performance Analysis</h1>
          <p className="text-slate-500 text-[13px] mt-1.5">
            {currentSessionId
              ? 'Detects N+1 queries, memory leaks, blocking I/O, and inefficient algorithms.'
              : 'Run a scan first to analyse performance.'}
          </p>
        </div>
        <button onClick={runScan} disabled={!currentSessionId || loading}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all duration-200',
            scanned
              ? 'border border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200 hover:border-white/[0.14]'
              : 'bg-indigo-500 hover:bg-indigo-600 text-white shadow-sm shadow-indigo-500/30',
            'disabled:opacity-40'
          )}>
          <RefreshCw size={13} className={clsx(loading && 'animate-spin')} />
          {loading ? 'Scanning…' : scanned ? 'Re-scan' : 'Scan for issues'}
        </button>
      </div>

      {/* ── No session state ─────────────────────────────────────────────── */}
      {!currentSessionId && (
        <div className={`${CARD} p-10 text-center`}>
          <Terminal size={24} className="text-slate-700 mx-auto mb-3" />
          <p className="text-slate-500 text-[14px] font-medium">No active scan session</p>
          <p className="text-slate-700 text-[12px] mt-1">Go to the Scanner page and scan a repository first.</p>
        </div>
      )}

      {/* ── Loading state ────────────────────────────────────────────────── */}
      {loading && (
        <div className={`${CARD} p-10 text-center`}>
          <RefreshCw size={22} className="text-indigo-400/60 animate-spin mx-auto mb-3" />
          <p className="text-slate-400 text-[13px]">Analysing code for performance issues…</p>
          <p className="text-slate-600 text-[11px] font-mono mt-1">
            Checking N+1 queries · memory leaks · blocking I/O · inefficient loops
          </p>
        </div>
      )}

      {/* ── Results ──────────────────────────────────────────────────────── */}
      {scanned && !loading && (
        <>
          {/* Metric cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Total Issues"     value={metrics?.total_issues ?? issues.length}
              sub={`${metrics?.files_affected ?? 0} files affected`}
              accent="#6366f1" icon={Gauge} />
            <StatCard label="Critical Issues"  value={critCount}
              sub={`${highCount} high priority`}
              accent="#ef4444" icon={AlertTriangle} />
            <StatCard label="Est. Slowdown"
              value={metrics?.estimated_slowdown_percent ? `${metrics.estimated_slowdown_percent}%` : '—'}
              sub="vs optimised baseline"
              accent="#f97316" icon={TrendingDown} />
            <StatCard label="Potential Gain"
              value={metrics?.estimated_improvement_percent ? `${metrics.estimated_improvement_percent}%` : '—'}
              sub="if all issues fixed"
              accent="#22c55e" icon={TrendingUp} />
          </div>

          {/* Issue type breakdown + filter */}
          {Object.keys(byType).length > 0 && (
            <div className={`${CARD} p-6`}>
              <div className="flex items-start justify-between mb-5">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-600 mb-1">Breakdown</p>
                  <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Issues by type</h2>
                </div>
                <span className="text-[10px] text-slate-700 font-mono mt-1">{issues.length} total</span>
              </div>
              <div className="space-y-2.5">
                {Object.entries(byType)
                  .sort(([, a], [, b]) => Number(b) - Number(a))
                  .map(([type, count]) => {
                    const Icon = TYPE_ICON[type] || Code2
                    const pct  = Math.round((Number(count) / maxTypeCount) * 100)
                    return (
                      <button key={type} type="button"
                        onClick={() => setFilterType(filterType === type ? 'all' : type)}
                        className={clsx(
                          'w-full flex items-center gap-3 p-2.5 rounded-xl transition-all text-left',
                          filterType === type ? 'bg-indigo-500/10 border border-indigo-500/20' : 'hover:bg-white/[0.025]'
                        )}>
                        <div className="p-1.5 rounded-lg bg-slate-elevated border border-white/[0.06] shrink-0">
                          <Icon size={12} className="text-slate-500" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[12px] text-slate-300 font-medium truncate">{type}</span>
                            <span className="text-[11px] font-bold font-mono text-slate-400 ml-3 shrink-0">{String(count)}</span>
                          </div>
                          <div className="w-full h-1.5 rounded-full bg-white/[0.05] overflow-hidden">
                            <div className="h-full rounded-full bg-indigo-500/60 transition-all duration-500"
                              style={{ width: `${pct}%` }} />
                          </div>
                        </div>
                      </button>
                    )
                  })}
              </div>
            </div>
          )}

          {/* Detail drawer (when issue selected) */}
          {selected && (
            <IssueDrawer issue={selected} onClose={() => setSelected(null)} />
          )}

          {/* Issue list */}
          {issues.length > 0 ? (
            <div className={CARD}>
              {/* Filters */}
              <div className="flex flex-wrap items-center gap-2 p-4 border-b border-white/[0.05]">
                <span className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mr-1">Filter:</span>
                {['all', 'critical', 'high', 'medium', 'low'].map(sev => (
                  <button key={sev} type="button"
                    onClick={() => setFilterSev(sev)}
                    className={clsx(
                      'px-3 py-1 rounded-full text-[10px] font-semibold transition-all border',
                      filterSev === sev
                        ? sev === 'all'
                          ? 'bg-slate-700/50 border-white/[0.14] text-slate-200'
                          : 'border-current text-white'
                        : 'border-white/[0.07] text-slate-600 hover:text-slate-400'
                    )}
                    style={filterSev === sev && sev !== 'all' ? {
                      backgroundColor: `${SEV_COLOR[sev]}18`,
                      borderColor:     `${SEV_COLOR[sev]}40`,
                      color:           SEV_COLOR[sev],
                    } : {}}>
                    {sev === 'all' ? `All (${issues.length})` : `${sev.charAt(0).toUpperCase() + sev.slice(1)} (${issues.filter(i => i.severity === sev).length})`}
                  </button>
                ))}
                {filterType !== 'all' && (
                  <button type="button" onClick={() => setFilterType('all')}
                    className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-medium border border-indigo-500/25 bg-indigo-500/10 text-indigo-400">
                    <X size={9} /> {filterType}
                  </button>
                )}
              </div>

              {/* Table header */}
              <div className="grid grid-cols-12 gap-3 px-5 py-3 border-b border-white/[0.05] bg-slate-elevated">
                {[['Severity','col-span-2'],['Type','col-span-4'],['File','col-span-3'],['Slowdown','col-span-2'],['','col-span-1']].map(([h,c])=>(
                  <div key={h} className={`${c} text-[9px] font-bold uppercase tracking-[0.12em] text-slate-600`}>{h}</div>
                ))}
              </div>

              {/* Rows */}
              <div className="divide-y divide-white/[0.04] max-h-[560px] overflow-y-auto scrollbar-none">
                {filtered.length === 0 ? (
                  <div className="py-10 text-center text-slate-600 text-[12px]">
                    No issues match the current filter.
                  </div>
                ) : filtered.map((issue, i) => {
                  const sevColor = SEV_COLOR[issue.severity] || '#64748b'
                  const isSelected = selected?.issue_id === issue.issue_id
                  return (
                    <div key={i} onClick={() => setSelected(isSelected ? null : issue)}
                      className={clsx(
                        'grid grid-cols-12 gap-3 px-5 py-3.5 cursor-pointer transition-colors group',
                        isSelected ? 'bg-indigo-500/[0.07]' : 'hover:bg-white/[0.02]'
                      )}>

                      {/* Severity */}
                      <div className="col-span-2 flex items-center">
                        <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border"
                          style={{ color: sevColor, backgroundColor: `${sevColor}12`, borderColor: `${sevColor}28` }}>
                          {issue.severity}
                        </span>
                      </div>

                      {/* Type */}
                      <div className="col-span-4 flex items-center gap-2">
                        <span className="text-[12px] text-slate-300 truncate">{issue.type}</span>
                      </div>

                      {/* File */}
                      <div className="col-span-3 flex items-center">
                        <span className="text-[11px] text-slate-600 font-mono truncate">
                          {issue.file?.split('/').slice(-2).join('/')}
                          {issue.line ? `:${issue.line}` : ''}
                        </span>
                      </div>

                      {/* Slowdown */}
                      <div className="col-span-2 flex items-center">
                        <span className="text-[11px] font-mono text-amber-400/70">{issue.slowdown || '—'}</span>
                      </div>

                      {/* Arrow */}
                      <div className="col-span-1 flex items-center justify-end">
                        <ChevronRight size={12}
                          className={clsx('transition-all', isSelected ? 'rotate-90 text-indigo-400' : 'text-slate-700 group-hover:text-slate-500')} />
                      </div>

                    </div>
                  )
                })}
              </div>
            </div>
          ) : (
            <div className={`${CARD} p-10 text-center`}>
              <CheckCircle2 size={24} className="text-emerald-400 mx-auto mb-3" />
              <p className="text-slate-300 text-[14px] font-semibold font-tight">No performance issues detected</p>
              <p className="text-slate-600 text-[12px] mt-1">
                The analyser found no N+1 queries, memory leaks, or blocking I/O in the scanned files.
              </p>
            </div>
          )}
        </>
      )}

    </div>
  )
}
