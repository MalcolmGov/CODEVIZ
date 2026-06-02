import React, { useState, useEffect } from 'react'
import { useSessionStore } from '@/store/sessionStore'
import { remediationService, TestGenResult } from '@/services/remediation'
import { api } from '@/services/api'
import {
  Wrench, AlertTriangle, RefreshCw, Terminal,
  CheckCircle2, ChevronRight, Package, Key,
  Code2, ShieldAlert, X, Zap, GitPullRequest, ExternalLink, FlaskConical,
} from 'lucide-react'
import clsx from 'clsx'

// ── Design tokens ──────────────────────────────────────────────────────────
const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

const SEV_COLOR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#3b82f6',
}

const CAT_ICON: Record<string, React.ElementType> = {
  'outdated_dependencies':     Package,
  'hardcoded_secrets':         Key,
  'code_formatting':           Code2,
  'security_misconfigurations': ShieldAlert,
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

// ── Category summary card ──────────────────────────────────────────────────
function CategoryCard({ category, label, count, onClick, active }: {
  category: string; label: string; count: number
  onClick: () => void; active: boolean
}) {
  const Icon = CAT_ICON[category] || Wrench
  return (
    <button type="button" onClick={onClick}
      className={clsx(
        CARD, 'p-5 text-left w-full transition-all duration-200 hover:border-white/[0.14]',
        active && 'ring-1 ring-inset ring-indigo-500/40 border-indigo-500/20',
      )}>
      <div className="flex items-center justify-between mb-3">
        <div className="p-2 rounded-lg bg-slate-elevated border border-white/[0.06]">
          <Icon size={14} className={active ? 'text-indigo-400' : 'text-slate-500'} />
        </div>
        <span className={clsx(
          'text-[11px] font-bold font-mono',
          count > 0 ? 'text-amber-400' : 'text-emerald-400'
        )}>{count}</span>
      </div>
      <p className="text-[12px] font-semibold text-slate-200 font-tight">{label}</p>
      <p className="text-[10px] text-slate-600 mt-0.5">
        {count > 0 ? `${count} issue${count > 1 ? 's' : ''} detected` : 'No issues found'}
      </p>
    </button>
  )
}

// ── Issue row ──────────────────────────────────────────────────────────────
function IssueRow({ issue, onSelect, selected }: {
  issue: any; onSelect: () => void; selected: boolean
}) {
  const sevColor = SEV_COLOR[issue.severity] || '#64748b'
  const Icon = CAT_ICON[issue.category] || Wrench
  return (
    <div
      onClick={onSelect}
      className={clsx(
        'grid grid-cols-12 gap-3 px-5 py-3.5 cursor-pointer transition-colors border-b border-white/[0.04] last:border-b-0',
        selected ? 'bg-indigo-500/[0.07]' : 'hover:bg-white/[0.02]'
      )}>
      <div className="col-span-2 flex items-center">
        <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border"
          style={{ color: sevColor, backgroundColor: `${sevColor}12`, borderColor: `${sevColor}28` }}>
          {issue.severity}
        </span>
      </div>
      <div className="col-span-3 flex items-center gap-2 min-w-0">
        <Icon size={11} className="text-slate-600 shrink-0" />
        <span className="text-[11px] text-slate-400 truncate">{issue.category_label}</span>
      </div>
      <div className="col-span-5 flex items-center min-w-0">
        <span className="text-[12px] text-slate-300 truncate">{issue.description || issue.fix || '—'}</span>
      </div>
      <div className="col-span-1 flex items-center">
        {(issue.fix || issue.auto_fixable) && (
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded border border-emerald-500/20 bg-emerald-500/[0.07] text-emerald-400">
            auto
          </span>
        )}
      </div>
      <div className="col-span-1 flex items-center justify-end">
        <ChevronRight size={12} className={clsx(
          'transition-all', selected ? 'rotate-90 text-indigo-400' : 'text-slate-700'
        )} />
      </div>
    </div>
  )
}

// ── Issue detail ───────────────────────────────────────────────────────────
function IssueDetail({ issue, onClose }: { issue: any; onClose: () => void }) {
  const sevColor = SEV_COLOR[issue.severity] || '#64748b'
  const [genLoading, setGenLoading] = useState(false)
  const [genResult,  setGenResult]  = useState<TestGenResult | null>(null)
  const [genError,   setGenError]   = useState<string | null>(null)
  const [copied,     setCopied]     = useState(false)

  const generateTest = async () => {
    setGenLoading(true)
    setGenError(null)
    try {
      const res = await remediationService.generateTests({
        issue_type:    issue.category_label || issue.category || 'Security Issue',
        file_path:     issue.file || 'unknown',
        description:   issue.description || '',
        original_code: issue.original_code || issue.code || '# not available',
        fixed_code:    issue.fix || '# not available',
      })
      setGenResult((res.data as any).data)
    } catch (err: any) {
      setGenError(err?.response?.data?.message || 'Test generation failed')
    } finally {
      setGenLoading(false) }
  }

  const copyTest = () => {
    if (!genResult) return
    navigator.clipboard.writeText(genResult.test_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`${CARD} p-6 space-y-4`}>
      <div className="flex items-start justify-between">
        <div>
          <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border"
            style={{ color: sevColor, backgroundColor: `${sevColor}12`, borderColor: `${sevColor}28` }}>
            {issue.severity}
          </span>
          <h3 className="text-[14px] font-semibold text-slate-200 font-tight mt-2">{issue.category_label}</h3>
          {issue.file && (
            <p className="text-[11px] font-mono text-slate-600 mt-0.5">
              {issue.file.split('/').slice(-2).join('/')}
              {issue.line ? `:${issue.line}` : ''}
            </p>
          )}
        </div>
        <button onClick={onClose} className="text-slate-700 hover:text-slate-400 transition-colors">
          <X size={16} />
        </button>
      </div>

      {issue.description && (
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-1">Issue</p>
          <p className="text-[12px] text-slate-400 leading-relaxed">{issue.description}</p>
        </div>
      )}

      {issue.fix && (
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mb-2">Recommended fix</p>
          <div className="rounded-xl bg-slate-950/80 border border-emerald-500/15 overflow-hidden">
            <div className="flex items-center gap-1.5 px-3 py-2 bg-emerald-500/[0.05] border-b border-emerald-500/10">
              <CheckCircle2 size={11} className="text-emerald-400" />
              <span className="text-[9px] font-mono text-emerald-400/70 uppercase tracking-wider">fix</span>
            </div>
            <pre className="p-4 text-[11px] font-mono text-emerald-300/80 overflow-x-auto leading-relaxed max-h-[160px] whitespace-pre-wrap">
              {issue.fix}
            </pre>
          </div>
        </div>
      )}

      {/* Generate Test */}
      <div className="pt-1">
        <div className="flex items-center justify-between mb-2">
          <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600">AI Test Generation</p>
          <button
            onClick={generateTest}
            disabled={genLoading}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold transition-all duration-200',
              'border border-violet-500/30 bg-violet-500/[0.08] text-violet-300 hover:bg-violet-500/[0.15] hover:border-violet-500/50',
              'disabled:opacity-40 disabled:cursor-not-allowed'
            )}>
            {genLoading
              ? <><RefreshCw size={10} className="animate-spin" /> Generating…</>
              : <><FlaskConical size={10} /> Generate Test</>}
          </button>
        </div>

        {genError && (
          <p className="text-[11px] text-red-400 bg-red-500/[0.06] border border-red-500/20 rounded-lg px-3 py-2">
            {genError}
          </p>
        )}

        {genResult && (
          <div className="rounded-xl bg-slate-950/80 border border-violet-500/15 overflow-hidden">
            <div className="flex items-center justify-between px-3 py-2 bg-violet-500/[0.05] border-b border-violet-500/10">
              <div className="flex items-center gap-1.5">
                <FlaskConical size={11} className="text-violet-400" />
                <span className="text-[9px] font-mono text-violet-400/70 uppercase tracking-wider">
                  {genResult.suggested_filename}
                </span>
                {genResult.llm_used && (
                  <span className="text-[8px] px-1.5 py-0.5 rounded border border-violet-500/20 bg-violet-500/[0.08] text-violet-400/70">
                    AI
                  </span>
                )}
              </div>
              <button
                onClick={copyTest}
                className="text-[9px] text-slate-500 hover:text-slate-300 transition-colors font-mono">
                {copied ? '✓ copied' : 'copy'}
              </button>
            </div>
            <pre className="p-4 text-[11px] font-mono text-violet-300/80 overflow-x-auto leading-relaxed max-h-[200px] whitespace-pre-wrap">
              {genResult.test_code}
            </pre>
          </div>
        )}
      </div>

      {/* Extra fields */}
      <div className="flex flex-wrap gap-4 pt-2">
        {issue.package && (
          <div>
            <p className="text-[9px] font-bold uppercase tracking-wider text-slate-600">Package</p>
            <p className="text-[11px] font-mono text-slate-400 mt-0.5">{issue.package}</p>
          </div>
        )}
        {issue.current_version && (
          <div>
            <p className="text-[9px] font-bold uppercase tracking-wider text-slate-600">Current</p>
            <p className="text-[11px] font-mono text-slate-400 mt-0.5">{issue.current_version}</p>
          </div>
        )}
        {issue.latest_version && (
          <div>
            <p className="text-[9px] font-bold uppercase tracking-wider text-slate-600">Latest</p>
            <p className="text-[11px] font-mono text-emerald-400 mt-0.5">{issue.latest_version}</p>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────
export const RemediationPage: React.FC = () => {
  const { currentSessionId } = useSessionStore()
  const [issues, setIssues]     = useState<any[]>([])
  const [metrics, setMetrics]   = useState<any>(null)
  const [loading, setLoading]   = useState(false)
  const [done, setDone]         = useState(false)
  const [selected, setSelected] = useState<any>(null)
  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const [prLoading, setPrLoading] = useState(false)
  const [prResult, setPrResult]   = useState<any>(null)
  const [prError, setPrError]     = useState<string | null>(null)

  const runScan = async () => {
    if (!currentSessionId || loading) return
    setLoading(true)
    setSelected(null)
    try {
      const res = await remediationService.scan(currentSessionId)
      const d   = (res.data as any).data
      setIssues(d.issues || [])
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

  const categories = [
    { key: 'outdated_dependencies',     label: 'Outdated Dependencies' },
    { key: 'hardcoded_secrets',         label: 'Hardcoded Secrets' },
    { key: 'code_formatting',           label: 'Code Formatting' },
    { key: 'security_misconfigurations', label: 'Security Misconfigs' },
  ]

  const catCounts = (key: string) =>
    issues.filter(i => i.category === key).length

  const filtered = activeCategory
    ? issues.filter(i => i.category === activeCategory)
    : issues

  return (
    <div className="space-y-5 animate-fade-in pb-10 select-none">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
        <div>
          <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Auto-Remediation</h1>
          <p className="text-slate-500 text-[13px] mt-1.5">
            {currentSessionId
              ? 'Detects outdated dependencies, hardcoded secrets, formatting issues, and misconfigurations.'
              : 'Scan a repository first to detect fixable issues.'}
          </p>
        </div>
        <button onClick={runScan} disabled={!currentSessionId || loading}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all duration-200',
            done
              ? 'border border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200 hover:border-white/[0.14]'
              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-500/20',
            'disabled:opacity-40'
          )}>
          <RefreshCw size={13} className={clsx(loading && 'animate-spin')} />
          {loading ? 'Scanning…' : done ? 'Re-scan' : 'Scan for issues'}
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
          <Wrench size={22} className="text-emerald-400/60 animate-pulse mx-auto mb-3" />
          <p className="text-slate-400 text-[13px]">Scanning for fixable issues…</p>
          <p className="text-slate-600 text-[11px] font-mono mt-1">
            Checking dependencies · secrets · formatting · misconfigurations
          </p>
        </div>
      )}

      {/* Results */}
      {done && !loading && (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Total Issues"    value={metrics?.total ?? issues.length}
              sub="across all categories"
              accent="#6366f1" icon={Wrench} />
            <StatCard label="Auto-fixable"    value={metrics?.auto_fixable ?? 0}
              sub="can be fixed automatically"
              accent="#22c55e" icon={Zap} />
            <StatCard label="Critical / High" value={(metrics?.by_severity?.critical ?? 0) + (metrics?.by_severity?.high ?? 0)}
              sub={`${metrics?.by_severity?.medium ?? 0} medium priority`}
              accent="#ef4444" icon={AlertTriangle} />
            <StatCard label="Categories"
              value={metrics?.categories_with_issues?.length ?? 0}
              sub="issue types detected"
              accent="#f97316" icon={ShieldAlert} />
          </div>

          {/* Category overview */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {categories.map(({ key, label }) => (
              <CategoryCard
                key={key}
                category={key}
                label={label}
                count={catCounts(key)}
                active={activeCategory === key}
                onClick={() => {
                  setActiveCategory(activeCategory === key ? null : key)
                  setSelected(null)
                }}
              />
            ))}
          </div>

          {/* Active category filter pill */}
          {activeCategory && (
            <div className="flex items-center gap-2">
              <button type="button" onClick={() => { setActiveCategory(null); setSelected(null) }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-medium border border-indigo-500/25 bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/15 transition-colors">
                <X size={10} />
                {categories.find(c => c.key === activeCategory)?.label}
              </button>
            </div>
          )}

          {/* Issue detail */}
          {selected && (
            <IssueDetail issue={selected} onClose={() => setSelected(null)} />
          )}

          {/* Issue list */}
          {issues.length > 0 ? (
            <div className={CARD}>
              <div className="grid grid-cols-12 gap-3 px-5 py-3 border-b border-white/[0.05] bg-slate-elevated">
                {[['Severity','col-span-2'],['Category','col-span-3'],['Description','col-span-5'],['Fix','col-span-1'],['','col-span-1']].map(([h,c])=>(
                  <div key={h} className={`${c} text-[9px] font-bold uppercase tracking-[0.12em] text-slate-600`}>{h}</div>
                ))}
              </div>
              <div className="max-h-[560px] overflow-y-auto scrollbar-none">
                {filtered.length === 0 ? (
                  <div className="py-10 text-center text-slate-600 text-[12px]">No issues in this category.</div>
                ) : (
                  filtered.map((issue, i) => (
                    <IssueRow
                      key={i}
                      issue={issue}
                      selected={selected === issue}
                      onSelect={() => setSelected(selected === issue ? null : issue)}
                    />
                  ))
                )}
              </div>
            </div>
          ) : (
            <div className={`${CARD} p-10 text-center`}>
              <CheckCircle2 size={24} className="text-emerald-400 mx-auto mb-3" />
              <p className="text-slate-300 text-[14px] font-semibold font-tight">No fixable issues detected</p>
              <p className="text-slate-600 text-[12px] mt-1">
                Dependencies are up to date, no hardcoded secrets found, and no misconfigurations detected.
              </p>
            </div>
          )}

          {/* GitHub PR Panel */}
          {issues.length > 0 && (
            <div className={`${CARD} p-6`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-3">
                  <div className="p-1.5 rounded-lg bg-slate-elevated border border-white/[0.06] shrink-0 mt-0.5">
                    <GitPullRequest size={13} className="text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-[13px] font-semibold text-slate-200">Create Remediation PR</p>
                    <p className="text-[11px] text-slate-600 mt-0.5 leading-relaxed">
                      Apply all auto-fixable issues and open a GitHub pull request.
                      Requires <span className="font-mono text-slate-500">GITHUB_TOKEN</span> and a GitHub repo URL.
                    </p>
                  </div>
                </div>
                <button
                  onClick={async () => {
                    if (!currentSessionId || prLoading) return
                    setPrLoading(true); setPrError(null); setPrResult(null)
                    try {
                      const res = await api.post(`/remediation/create-pr/${currentSessionId}`, { branch: 'main' })
                      setPrResult((res.data as any)?.data || {})
                    } catch (e: any) {
                      setPrError(e?.response?.data?.error || e?.message || 'PR creation failed')
                    } finally {
                      setPrLoading(false)
                    }
                  }}
                  disabled={prLoading || !currentSessionId}
                  className={clsx(
                    'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all duration-200 shrink-0',
                    'bg-indigo-500 hover:bg-indigo-600 text-white shadow-sm shadow-indigo-500/25 disabled:opacity-40'
                  )}>
                  {prLoading
                    ? <><RefreshCw size={12} className="animate-spin" /> Creating…</>
                    : <><GitPullRequest size={12} /> Create PR</>}
                </button>
              </div>

              {/* Result */}
              {prResult && (
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/[0.06] p-4 flex items-start gap-3">
                  <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-[12px] font-semibold text-emerald-300">
                      {prResult.message || 'Pull request created!'}
                    </p>
                    {prResult.pr_url && (
                      <a href={prResult.pr_url} target="_blank" rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-[11px] text-indigo-400 hover:text-indigo-300 mt-1">
                        <ExternalLink size={10} /> View PR on GitHub
                      </a>
                    )}
                  </div>
                </div>
              )}

              {/* Error */}
              {prError && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/[0.06] p-4 flex items-start gap-3">
                  <AlertTriangle size={14} className="text-red-400 shrink-0 mt-0.5" />
                  <p className="text-[12px] text-red-400">{prError}</p>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
