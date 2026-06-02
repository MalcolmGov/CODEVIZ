import React, { useState, useEffect } from 'react'
import { useSessionStore } from '@/store/sessionStore'
import { smellsService } from '@/services/smells'
import { AskAIButton } from '@/components/common/AskAIButton'
import {
  FlaskConical, AlertTriangle, RefreshCw, Terminal,
  CheckCircle2, ChevronRight, X, Code2, Copy, GitBranch,
  Layers, Hash, Minimize2, Repeat2, Variable,
} from 'lucide-react'
import clsx from 'clsx'

// ── Design tokens ──────────────────────────────────────────────────────────
const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

const SEV_COLOR: Record<string, string> = {
  major: '#f97316', medium: '#eab308', minor: '#3b82f6',
}
const SEV_ORDER: Record<string, number> = { major: 0, medium: 1, minor: 2 }

const TYPE_ICON: Record<string, React.ElementType> = {
  'Dead Code':                     X,
  'Duplicate Code':                Copy,
  'High Complexity':               GitBranch,
  'Magic Number':                  Hash,
  'Unused Variable':               Variable,
  'Long Method':                   Layers,
  'God Class (Too Many Methods)':  Layers,
  'Deep Nesting':                  Minimize2,
}

const EFFORT_COLOR: Record<string, string> = {
  Low: 'text-emerald-400', Medium: 'text-amber-400', High: 'text-red-400',
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

// ── Type breakdown ─────────────────────────────────────────────────────────
function TypeBreakdown({ byType, total, onFilter, activeType }: {
  byType: Record<string, number>; total: number
  onFilter: (t: string | null) => void; activeType: string | null
}) {
  const sorted = Object.entries(byType).sort(([, a], [, b]) => b - a)
  const max = Math.max(...sorted.map(([, v]) => v), 1)
  return (
    <div className={`${CARD} p-6`}>
      <div className="mb-5">
        <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-600 mb-1">Breakdown</p>
        <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Smells by type</h2>
      </div>
      <div className="space-y-2.5">
        {sorted.map(([type, count]) => {
          const Icon = TYPE_ICON[type] || Code2
          const pct  = Math.round((count / max) * 100)
          const active = activeType === type
          return (
            <button key={type} type="button"
              onClick={() => onFilter(active ? null : type)}
              className={clsx(
                'w-full flex items-center gap-3 p-2.5 rounded-xl transition-all text-left',
                active ? 'bg-indigo-500/10 border border-indigo-500/20' : 'hover:bg-white/[0.025]'
              )}>
              <div className="p-1.5 rounded-lg bg-slate-elevated border border-white/[0.06] shrink-0">
                <Icon size={12} className="text-slate-500" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[12px] text-slate-300 font-medium truncate">{type}</span>
                  <span className="text-[11px] font-bold font-mono text-slate-400 ml-3 shrink-0">{count}</span>
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
  )
}

// ── Smell detail drawer ────────────────────────────────────────────────────
function SmellDrawer({ smell, onClose }: { smell: any; onClose: () => void }) {
  const sevColor = SEV_COLOR[smell.severity] || '#64748b'
  return (
    <div className={`${CARD} p-6 space-y-4`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ backgroundColor: sevColor }} />
          <div>
            <h3 className="text-[15px] font-semibold text-slate-200 font-tight">{smell.type}</h3>
            <p className="text-[11px] font-mono text-slate-600 mt-0.5">
              {smell.file?.split('/').slice(-2).join('/')}
              {smell.line ? ` · line ${smell.line}` : ''}
            </p>
          </div>
        </div>
        <button onClick={onClose} className="text-slate-700 hover:text-slate-400 transition-colors">
          <X size={16} />
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border"
          style={{ color: sevColor, backgroundColor: `${sevColor}12`, borderColor: `${sevColor}28` }}>
          {smell.severity}
        </span>
        {smell.effort && (
          <span className={clsx(
            'text-[9px] font-mono px-2 py-1 rounded-full border border-white/[0.08] bg-white/[0.04]',
            EFFORT_COLOR[smell.effort] || 'text-slate-500'
          )}>
            effort: {smell.effort}
          </span>
        )}
      </div>

      {smell.description && (
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-1">Description</p>
          <p className="text-[12px] text-slate-400 leading-relaxed">{smell.description}</p>
        </div>
      )}

      {smell.impact && (
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-1">Impact</p>
          <p className="text-[12px] text-slate-400 leading-relaxed">{smell.impact}</p>
        </div>
      )}

      {smell.code && (
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-2">Affected code</p>
          <div className="rounded-xl bg-slate-950/80 border border-white/[0.05] overflow-hidden">
            <div className="px-3 py-2 bg-slate-elevated border-b border-white/[0.05]">
              <span className="text-[9px] font-mono text-slate-600 uppercase tracking-wider">
                {smell.file?.split('/').pop()} · line {smell.line}
              </span>
            </div>
            <pre className="p-4 text-[11px] font-mono text-rose-300/80 overflow-x-auto leading-relaxed max-h-[140px]">
              {smell.code}
            </pre>
          </div>
        </div>
      )}

      {smell.refactor && (
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-2">Refactoring suggestion</p>
          <div className="rounded-xl bg-slate-950/80 border border-emerald-500/15 overflow-hidden">
            <div className="flex items-center gap-1.5 px-3 py-2 bg-emerald-500/[0.05] border-b border-emerald-500/10">
              <CheckCircle2 size={11} className="text-emerald-400" />
              <span className="text-[9px] font-mono text-emerald-400/70 uppercase tracking-wider">suggestion</span>
            </div>
            <pre className="p-4 text-[11px] font-mono text-emerald-300/80 overflow-x-auto leading-relaxed max-h-[140px] whitespace-pre-wrap">
              {smell.refactor}
            </pre>
          </div>
        </div>
      )}
      <AskAIButton
        label={smell.type}
        context={`Code smell: ${smell.type} in ${smell.file} line ${smell.line}. Severity: ${smell.severity}. Effort to fix: ${smell.effort || 'unknown'}. Description: ${smell.description || ''}. Impact: ${smell.impact || ''}. ${smell.refactor ? `Suggested refactor: ${smell.refactor}` : ''}`}
      />
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────
export const CodeSmellsPage: React.FC = () => {
  const { currentSessionId } = useSessionStore()
  const [smells, setSmells]     = useState<any[]>([])
  const [metrics, setMetrics]   = useState<any>(null)
  const [loading, setLoading]   = useState(false)
  const [done, setDone]         = useState(false)
  const [selected, setSelected] = useState<any>(null)
  const [filterSev, setFilterSev]   = useState('all')
  const [filterType, setFilterType] = useState<string | null>(null)

  const runScan = async () => {
    if (!currentSessionId || loading) return
    setLoading(true)
    setSelected(null)
    try {
      const res = await smellsService.scan(currentSessionId)
      const d   = (res.data as any).data
      setSmells(d.smells || [])
      setMetrics(d.metrics || null)
      setDone(true)
    } catch {
      setDone(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (currentSessionId && !done) runScan()
  }, [currentSessionId])

  const filtered = smells.filter(s =>
    (filterSev === 'all' || s.severity === filterSev) &&
    (!filterType || s.type === filterType)
  )

  return (
    <div className="space-y-5 animate-fade-in pb-10 select-none">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
        <div>
          <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Code Smells</h1>
          <p className="text-slate-500 text-[13px] mt-1.5">
            {currentSessionId
              ? 'Detects dead code, duplicates, long methods, deep nesting, magic numbers, and more.'
              : 'Scan a repository first to detect code smells.'}
          </p>
        </div>
        <button onClick={runScan} disabled={!currentSessionId || loading}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all duration-200',
            done
              ? 'border border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200 hover:border-white/[0.14]'
              : 'bg-violet-600 hover:bg-violet-500 text-white shadow-sm shadow-violet-500/20',
            'disabled:opacity-40'
          )}>
          <RefreshCw size={13} className={clsx(loading && 'animate-spin')} />
          {loading ? 'Scanning…' : done ? 'Re-scan' : 'Scan for smells'}
        </button>
      </div>

      {/* No session */}
      {!currentSessionId && (
        <div className={`${CARD} p-10 text-center`}>
          <Terminal size={24} className="text-slate-700 mx-auto mb-3" />
          <p className="text-slate-500 text-[14px] font-medium">No active scan session</p>
          <p className="text-slate-700 text-[12px] mt-1">Go to the Scanner page and scan a repository first.</p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className={`${CARD} p-10 text-center`}>
          <FlaskConical size={22} className="text-violet-400/60 animate-pulse mx-auto mb-3" />
          <p className="text-slate-400 text-[13px]">Sniffing for code smells…</p>
          <p className="text-slate-600 text-[11px] font-mono mt-1">
            Dead code · duplicates · long methods · deep nesting · magic numbers
          </p>
        </div>
      )}

      {/* Results */}
      {done && !loading && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Total Smells"    value={metrics?.total ?? smells.length}
              sub={`${metrics?.files_affected ?? 0} files affected`}
              accent="#a855f7" icon={FlaskConical} />
            <StatCard label="Major"           value={metrics?.major ?? 0}
              sub={`${metrics?.medium ?? 0} medium severity`}
              accent="#f97316" icon={AlertTriangle} />
            <StatCard label="Minor"           value={metrics?.minor ?? 0}
              sub="low impact smells"
              accent="#3b82f6" icon={Code2} />
            <StatCard label="Smell Types"     value={Object.keys(metrics?.by_type ?? {}).length}
              sub="distinct categories"
              accent="#22c55e" icon={Repeat2} />
          </div>

          <div className="grid lg:grid-cols-3 gap-5">
            {/* Type breakdown (sidebar) */}
            <div className="lg:col-span-1">
              {metrics?.by_type && Object.keys(metrics.by_type).length > 0 && (
                <TypeBreakdown
                  byType={metrics.by_type}
                  total={smells.length}
                  onFilter={setFilterType}
                  activeType={filterType}
                />
              )}
            </div>

            {/* Issue list */}
            <div className="lg:col-span-2 space-y-5">
              {/* Detail drawer */}
              {selected && <SmellDrawer smell={selected} onClose={() => setSelected(null)} />}

              {smells.length > 0 ? (
                <div className={CARD}>
                  {/* Filter bar */}
                  <div className="flex flex-wrap items-center gap-2 p-4 border-b border-white/[0.05]">
                    <span className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mr-1">Severity:</span>
                    {(['all', 'major', 'medium', 'minor'] as const).map(sev => (
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
                        {sev === 'all' ? `All (${smells.length})` : `${sev.charAt(0).toUpperCase() + sev.slice(1)} (${metrics?.by_severity?.[sev] ?? smells.filter(s => s.severity === sev).length})`}
                      </button>
                    ))}
                    {filterType && (
                      <button type="button" onClick={() => setFilterType(null)}
                        className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-medium border border-indigo-500/25 bg-indigo-500/10 text-indigo-400">
                        <X size={9} /> {filterType}
                      </button>
                    )}
                  </div>

                  {/* Table header */}
                  <div className="grid grid-cols-12 gap-3 px-5 py-3 border-b border-white/[0.05] bg-slate-elevated">
                    {[['Sev','col-span-2'],['Type','col-span-4'],['File','col-span-3'],['Effort','col-span-2'],['','col-span-1']].map(([h,c])=>(
                      <div key={h} className={`${c} text-[9px] font-bold uppercase tracking-[0.12em] text-slate-600`}>{h}</div>
                    ))}
                  </div>

                  {/* Rows */}
                  <div className="divide-y divide-white/[0.04] max-h-[520px] overflow-y-auto scrollbar-none">
                    {filtered.length === 0 ? (
                      <div className="py-10 text-center text-slate-600 text-[12px]">
                        No smells match the current filter.
                      </div>
                    ) : filtered.map((smell, i) => {
                      const sevColor = SEV_COLOR[smell.severity] || '#64748b'
                      const isSelected = selected?.smell_id === smell.smell_id
                      const Icon = TYPE_ICON[smell.type] || Code2
                      return (
                        <div key={i}
                          onClick={() => setSelected(isSelected ? null : smell)}
                          className={clsx(
                            'grid grid-cols-12 gap-3 px-5 py-3.5 cursor-pointer transition-colors group',
                            isSelected ? 'bg-indigo-500/[0.07]' : 'hover:bg-white/[0.02]'
                          )}>
                          <div className="col-span-2 flex items-center">
                            <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border"
                              style={{ color: sevColor, backgroundColor: `${sevColor}12`, borderColor: `${sevColor}28` }}>
                              {smell.severity}
                            </span>
                          </div>
                          <div className="col-span-4 flex items-center gap-2 min-w-0">
                            <Icon size={11} className="text-slate-600 shrink-0" />
                            <span className="text-[12px] text-slate-300 truncate">{smell.type}</span>
                          </div>
                          <div className="col-span-3 flex items-center">
                            <span className="text-[11px] text-slate-600 font-mono truncate">
                              {smell.file?.split('/').slice(-2).join('/')}
                              {smell.line ? `:${smell.line}` : ''}
                            </span>
                          </div>
                          <div className="col-span-2 flex items-center">
                            <span className={clsx('text-[11px] font-mono', EFFORT_COLOR[smell.effort] || 'text-slate-600')}>
                              {smell.effort || '—'}
                            </span>
                          </div>
                          <div className="col-span-1 flex items-center justify-end">
                            <ChevronRight size={12} className={clsx(
                              'transition-all', isSelected ? 'rotate-90 text-indigo-400' : 'text-slate-700 group-hover:text-slate-500'
                            )} />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ) : (
                <div className={`${CARD} p-10 text-center`}>
                  <CheckCircle2 size={24} className="text-emerald-400 mx-auto mb-3" />
                  <p className="text-slate-300 text-[14px] font-semibold font-tight">No code smells detected</p>
                  <p className="text-slate-600 text-[12px] mt-1">
                    The codebase looks clean — no dead code, duplicates, or deeply nested logic found.
                  </p>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
