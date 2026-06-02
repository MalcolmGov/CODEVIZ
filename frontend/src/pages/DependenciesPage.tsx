import React, { useState, useEffect } from 'react'
import { useSessionStore } from '@/store/sessionStore'
import { dependenciesService } from '@/services/dependencies'
import {
  Package, AlertTriangle, RefreshCw, Terminal, Shield,
  ExternalLink, ChevronDown, ChevronUp, CheckCircle2, X,
} from 'lucide-react'
import clsx from 'clsx'

// ── Design tokens ──────────────────────────────────────────────────────────
const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

const SEV_COLOR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#3b82f6',
}
const SEV_ORDER: Record<string, number> = {
  critical: 0, high: 1, medium: 2, low: 3,
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

// ── Vuln row ───────────────────────────────────────────────────────────────
function VulnRow({ vuln }: { vuln: any }) {
  const [open, setOpen] = useState(false)
  const sevColor = SEV_COLOR[vuln.severity] || '#64748b'

  return (
    <div className={clsx('border-b border-white/[0.04] last:border-b-0', open && 'bg-white/[0.015]')}>
      {/* Summary row */}
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        className="w-full grid grid-cols-12 gap-3 px-5 py-3.5 text-left hover:bg-white/[0.02] transition-colors group"
      >
        {/* Severity */}
        <div className="col-span-2 flex items-center">
          <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border"
            style={{ color: sevColor, backgroundColor: `${sevColor}12`, borderColor: `${sevColor}28` }}>
            {vuln.severity}
          </span>
        </div>

        {/* Package */}
        <div className="col-span-3 flex items-center gap-2 min-w-0">
          <Package size={11} className="text-slate-600 shrink-0" />
          <span className="text-[12px] font-mono text-slate-300 truncate">{vuln.package}</span>
        </div>

        {/* CVE ID */}
        <div className="col-span-3 flex items-center min-w-0">
          <span className="text-[11px] font-mono text-slate-500 truncate">{vuln.cve_id || vuln.osv_id}</span>
        </div>

        {/* CVSS */}
        <div className="col-span-2 flex items-center">
          {vuln.cvss_score != null ? (
            <span className="text-[12px] font-bold font-mono"
              style={{ color: vuln.cvss_score >= 9 ? '#ef4444' : vuln.cvss_score >= 7 ? '#f97316' : vuln.cvss_score >= 4 ? '#eab308' : '#3b82f6' }}>
              {vuln.cvss_score.toFixed(1)}
            </span>
          ) : (
            <span className="text-[11px] text-slate-700">—</span>
          )}
        </div>

        {/* Fixed in */}
        <div className="col-span-1 flex items-center">
          {vuln.fixed_in ? (
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded border border-emerald-500/20 bg-emerald-500/[0.07] text-emerald-400 truncate">
              {vuln.fixed_in}
            </span>
          ) : (
            <span className="text-[10px] text-slate-700">—</span>
          )}
        </div>

        {/* Expand arrow */}
        <div className="col-span-1 flex items-center justify-end">
          {open
            ? <ChevronUp size={12} className="text-slate-500" />
            : <ChevronDown size={12} className="text-slate-700 group-hover:text-slate-500 transition-colors" />}
        </div>
      </button>

      {/* Expanded detail */}
      {open && (
        <div className="px-5 pb-4 space-y-3">
          <p className="text-[12px] text-slate-400 leading-relaxed">{vuln.title}</p>
          <div className="flex flex-wrap gap-3">
            <div>
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-600">Version</span>
              <p className="text-[11px] font-mono text-slate-400 mt-0.5">{vuln.version}</p>
            </div>
            <div>
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-600">Ecosystem</span>
              <p className="text-[11px] text-slate-400 mt-0.5">{vuln.ecosystem}</p>
            </div>
            {vuln.fixed_in && (
              <div>
                <span className="text-[9px] font-bold uppercase tracking-wider text-slate-600">Fix version</span>
                <p className="text-[11px] font-mono text-emerald-400 mt-0.5">→ {vuln.fixed_in}</p>
              </div>
            )}
          </div>
          {vuln.details_url && (
            <a href={vuln.details_url} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-[11px] text-indigo-400 hover:text-indigo-300 transition-colors">
              <ExternalLink size={11} />
              View on OSV.dev
            </a>
          )}
        </div>
      )}
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────
export const DependenciesPage: React.FC = () => {
  const { currentSessionId } = useSessionStore()
  const [vulns, setVulns]       = useState<any[]>([])
  const [summary, setSummary]   = useState<any>(null)
  const [scanned, setScanned]   = useState<number>(0)
  const [affected, setAffected] = useState<number>(0)
  const [loading, setLoading]   = useState(false)
  const [done, setDone]         = useState(false)
  const [filterSev, setFilterSev] = useState('all')

  const runScan = async () => {
    if (!currentSessionId || loading) return
    setLoading(true)
    try {
      const res = await dependenciesService.scan(currentSessionId)
      const d   = (res.data as any).data
      setVulns(d.vulnerabilities || [])
      setSummary(d.summary || {})
      setScanned(d.scanned || 0)
      setAffected(d.affected || 0)
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

  const filtered = vulns.filter(v => filterSev === 'all' || v.severity === filterSev)

  return (
    <div className="space-y-5 animate-fade-in pb-10 select-none">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
        <div>
          <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Dependencies</h1>
          <p className="text-slate-500 text-[13px] mt-1.5">
            {currentSessionId
              ? 'CVE vulnerabilities in your project dependencies via OSV.dev.'
              : 'Scan a repository first to audit dependencies.'}
          </p>
        </div>
        <button onClick={runScan} disabled={!currentSessionId || loading}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all duration-200',
            done
              ? 'border border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200 hover:border-white/[0.14]'
              : 'bg-indigo-500 hover:bg-indigo-600 text-white shadow-sm shadow-indigo-500/30',
            'disabled:opacity-40'
          )}>
          <RefreshCw size={13} className={clsx(loading && 'animate-spin')} />
          {loading ? 'Scanning…' : done ? 'Re-scan' : 'Scan dependencies'}
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
          <RefreshCw size={22} className="text-indigo-400/60 animate-spin mx-auto mb-3" />
          <p className="text-slate-400 text-[13px]">Querying OSV.dev for CVEs…</p>
          <p className="text-slate-600 text-[11px] font-mono mt-1">
            Parsing manifests · batch CVE lookup · CVSS scoring
          </p>
        </div>
      )}

      {/* Results */}
      {done && !loading && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Packages Scanned" value={scanned}
              sub={`${affected} vulnerable packages`}
              accent="#6366f1" icon={Package} />
            <StatCard label="Critical CVEs" value={summary?.critical ?? 0}
              sub={`${summary?.high ?? 0} high severity`}
              accent="#ef4444" icon={AlertTriangle} />
            <StatCard label="Medium CVEs" value={summary?.medium ?? 0}
              sub={`${summary?.low ?? 0} low severity`}
              accent="#eab308" icon={Shield} />
            <StatCard label="Total CVEs" value={vulns.length}
              sub="across all dependencies"
              accent="#22c55e" icon={CheckCircle2} />
          </div>

          {/* Table */}
          {vulns.length > 0 ? (
            <div className={CARD}>
              {/* Filter bar */}
              <div className="flex flex-wrap items-center gap-2 p-4 border-b border-white/[0.05]">
                <span className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mr-1">Filter:</span>
                {(['all', 'critical', 'high', 'medium', 'low'] as const).map(sev => (
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
                    {sev === 'all' ? `All (${vulns.length})` : `${sev.charAt(0).toUpperCase() + sev.slice(1)} (${summary?.[sev] ?? 0})`}
                  </button>
                ))}
              </div>

              {/* Table header */}
              <div className="grid grid-cols-12 gap-3 px-5 py-3 border-b border-white/[0.05] bg-slate-elevated">
                {[['Severity','col-span-2'],['Package','col-span-3'],['CVE','col-span-3'],['CVSS','col-span-2'],['Fixed in','col-span-1'],['','col-span-1']].map(([h,c])=>(
                  <div key={h} className={`${c} text-[9px] font-bold uppercase tracking-[0.12em] text-slate-600`}>{h}</div>
                ))}
              </div>

              {/* Rows */}
              <div className="max-h-[560px] overflow-y-auto scrollbar-none">
                {filtered.length === 0 ? (
                  <div className="py-10 text-center text-slate-600 text-[12px]">
                    No vulnerabilities match the current filter.
                  </div>
                ) : (
                  filtered.map((vuln, i) => <VulnRow key={i} vuln={vuln} />)
                )}
              </div>
            </div>
          ) : (
            <div className={`${CARD} p-10 text-center`}>
              <CheckCircle2 size={24} className="text-emerald-400 mx-auto mb-3" />
              <p className="text-slate-300 text-[14px] font-semibold font-tight">No known CVEs found</p>
              <p className="text-slate-600 text-[12px] mt-1">
                {scanned > 0
                  ? `${scanned} packages scanned — none matched known vulnerabilities in OSV.dev.`
                  : 'No dependency manifests found in this repository.'}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
