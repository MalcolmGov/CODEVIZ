import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useSessionStore } from '@/store/sessionStore'
import { apisService } from '@/services/apis'
import {
  Globe, RefreshCw, Terminal, CheckCircle2, AlertTriangle,
  Clock, Zap, ChevronDown, ChevronUp,
} from 'lucide-react'
import clsx from 'clsx'

const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

const METHOD_COLOR: Record<string, string> = {
  GET:    '#3b82f6', POST:   '#22c55e', PUT:    '#f97316',
  PATCH:  '#a855f7', DELETE: '#ef4444', OPTIONS: '#64748b',
}

function StatCard({ label, value, sub, accent, icon: Icon }: any) {
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

function EndpointRow({ ep, probed }: { ep: any; probed?: any }) {
  const [open, setOpen] = useState(false)
  const mc = METHOD_COLOR[ep.method?.toUpperCase() || 'GET'] || '#64748b'
  const latency = probed?.latency
  const status  = probed?.status
  const ok      = probed?.ok

  return (
    <div className="border-b border-white/[0.04] last:border-0">
      <button type="button" onClick={() => setOpen(o => !o)}
        className="w-full grid grid-cols-12 gap-3 px-5 py-3.5 text-left hover:bg-white/[0.02] transition-colors group">
        {/* Method */}
        <div className="col-span-2 flex items-center">
          <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded font-mono"
            style={{ color: mc, backgroundColor: `${mc}15` }}>
            {ep.method || 'GET'}
          </span>
        </div>
        {/* Path */}
        <div className="col-span-5 flex items-center min-w-0">
          <span className="text-[12px] font-mono text-slate-300 truncate">{ep.path}</span>
        </div>
        {/* Description */}
        <div className="col-span-3 flex items-center min-w-0">
          <span className="text-[11px] text-slate-600 truncate">{ep.description || ep.handler || '—'}</span>
        </div>
        {/* Status */}
        <div className="col-span-1 flex items-center">
          {probed ? (
            <span className={clsx('text-[11px] font-mono font-bold', ok ? 'text-emerald-400' : 'text-red-400')}>
              {status ?? 'ERR'}
            </span>
          ) : <span className="text-[10px] text-slate-700">—</span>}
        </div>
        {/* Latency + expand */}
        <div className="col-span-1 flex items-center justify-end gap-2">
          {latency && <span className="text-[10px] font-mono text-slate-600">{latency}ms</span>}
          {open ? <ChevronUp size={11} className="text-slate-500" />
                : <ChevronDown size={11} className="text-slate-700 group-hover:text-slate-500 transition-colors" />}
        </div>
      </button>

      {open && (
        <div className="px-5 pb-4 space-y-2">
          {ep.file && (
            <p className="text-[11px] font-mono text-slate-600">
              Defined in: <span className="text-slate-400">{ep.file}</span>
              {ep.line ? `:${ep.line}` : ''}
            </p>
          )}
          {probed?.error && (
            <p className="text-[11px] text-red-400">Error: {probed.error}</p>
          )}
          {ep.auth_required !== undefined && (
            <p className="text-[11px] text-slate-500">
              Auth: <span className={ep.auth_required ? 'text-emerald-400' : 'text-amber-400'}>
                {ep.auth_required ? 'Required' : 'Public'}
              </span>
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export const ApiAnalyzerPage: React.FC = () => {
  const { currentSessionId } = useSessionStore()
  const [endpoints, setEndpoints] = useState<any[]>([])
  const [probeResults, setProbeResults] = useState<Record<string, any>>({})
  const [probeBase, setProbeBase] = useState('http://localhost:8000')
  const [loading, setLoading]   = useState(false)
  const [probing,      setProbing]      = useState(false)
  const [done,         setDone]         = useState(false)
  const [error,        setError]        = useState<string | null>(null)
  const [probeError,   setProbeError]   = useState<string | null>(null)
  const [summary,      setSummary]      = useState<any>(null)
  const [filterMethod, setFilterMethod] = useState('all')

  const load = async () => {
    if (!currentSessionId || loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await apisService.endpoints(currentSessionId)
      const d   = (res.data as any).data
      setEndpoints(d.endpoints || [])
      setDone(true)
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || 'Failed to load endpoints'
      setError(msg)
      setDone(true)
    } finally { setLoading(false) }
  }

  const runProbe = async () => {
    if (!currentSessionId || probing || endpoints.length === 0) return
    setProbing(true)
    setProbeError(null)
    try {
      const res = await apisService.probe(currentSessionId, probeBase)
      const d   = (res.data as any).data
      const map: Record<string, any> = {}
      ;(d.results || []).forEach((r: any, i: number) => { map[r.path ?? i] = r })
      setProbeResults(map)
      setSummary(d.summary)
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || 'Probe failed'
      setProbeError(msg)
    } finally { setProbing(false) }
  }

  useEffect(() => { if (currentSessionId && !done) load() }, [currentSessionId])

  const methods = ['all', ...new Set(endpoints.map(e => e.method?.toUpperCase() || 'GET'))]
  const filtered = endpoints.filter(e => filterMethod === 'all' || (e.method || 'GET').toUpperCase() === filterMethod)

  return (
    <div className="space-y-5 animate-fade-in pb-10 select-none">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
        <div>
          <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">API Analyzer</h1>
          <p className="text-slate-500 text-[13px] mt-1.5">
            {currentSessionId ? 'Discovered endpoints from your codebase. Probe live for health and latency.' : 'Scan a repository first.'}
          </p>
        </div>
        <button onClick={load} disabled={!currentSessionId || loading}
          className={clsx('flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all',
            done ? 'border border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200'
                 : 'bg-indigo-500 hover:bg-indigo-600 text-white shadow-sm shadow-indigo-500/30',
            'disabled:opacity-40')}>
          <RefreshCw size={13} className={clsx(loading && 'animate-spin')} />
          {loading ? 'Loading…' : done ? 'Refresh' : 'Load endpoints'}
        </button>
      </div>

      {!currentSessionId && (
        <div className={`${CARD} p-10 text-center`}>
          <Terminal size={24} className="text-slate-700 mx-auto mb-3" />
          <p className="text-slate-500 text-[14px] font-medium">No active scan session</p>
          <Link to="/scanner"
            className="mt-3 inline-block text-[12px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
            Go to Scanner →
          </Link>
        </div>
      )}

      {/* Load error */}
      {done && !loading && error && (
        <div className={`${CARD} p-8 text-center`}>
          <AlertTriangle size={22} className="text-amber-400 mx-auto mb-3" />
          <p className="text-slate-400 text-[13px] mb-1">Failed to load endpoints</p>
          <p className="text-slate-600 text-[11px] font-mono">{error}</p>
          <button onClick={load}
            className="mt-4 text-[12px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
            Retry
          </button>
        </div>
      )}

      {done && !loading && !error && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Endpoints" value={endpoints.length} sub="discovered in codebase" accent="#6366f1" icon={Globe} />
            <StatCard label="Passing"   value={summary?.ok ?? '—'} sub="responded successfully" accent="#22c55e" icon={CheckCircle2} />
            <StatCard label="Failing"   value={summary?.failed ?? '—'} sub="errors or timeouts" accent="#ef4444" icon={AlertTriangle} />
            <StatCard label="Avg latency" value={summary?.avg_latency ? `${summary.avg_latency}ms` : '—'} sub="across probed endpoints" accent="#f97316" icon={Clock} />
          </div>

          {/* Probe bar */}
          <div className={`${CARD} px-6 py-4`}>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <div className="flex items-center gap-2 flex-1">
                <Globe size={13} className="text-slate-600 shrink-0" />
                <input
                  value={probeBase}
                  onChange={e => setProbeBase(e.target.value)}
                  className="flex-1 bg-slate-elevated border border-white/[0.08] rounded-lg px-3 py-1.5 text-[12px] font-mono text-slate-300 focus:outline-none focus:border-indigo-500/40"
                  placeholder="http://localhost:8000"
                />
              </div>
              <button onClick={runProbe} disabled={probing || endpoints.length === 0}
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all disabled:opacity-40 shrink-0">
                <Zap size={12} className={clsx(probing && 'animate-pulse')} />
                {probing ? 'Probing…' : 'Probe all'}
              </button>
            </div>
            {probeError && (
              <p className="text-[11px] text-red-400 font-mono mt-1 px-1">{probeError}</p>
            )}
          </div>

          {endpoints.length > 0 ? (
            <div className={CARD}>
              {/* Method filter */}
              <div className="flex flex-wrap items-center gap-2 p-4 border-b border-white/[0.05]">
                <span className="text-[10px] font-bold uppercase tracking-[0.1em] text-slate-600 mr-1">Method:</span>
                {methods.map(m => (
                  <button key={m} type="button" onClick={() => setFilterMethod(m)}
                    className={clsx('px-3 py-1 rounded-full text-[10px] font-semibold font-mono transition-all border',
                      filterMethod === m
                        ? 'bg-slate-700/50 border-white/[0.14] text-slate-200'
                        : 'border-white/[0.07] text-slate-600 hover:text-slate-400')}>
                    {m === 'all' ? `All (${endpoints.length})` : m}
                  </button>
                ))}
              </div>

              {/* Table header */}
              <div className="grid grid-cols-12 gap-3 px-5 py-3 border-b border-white/[0.05] bg-slate-elevated">
                {[['Method','col-span-2'],['Path','col-span-5'],['Handler','col-span-3'],['Status','col-span-1'],['','col-span-1']].map(([h,c])=>(
                  <div key={h} className={`${c} text-[9px] font-bold uppercase tracking-[0.12em] text-slate-600`}>{h}</div>
                ))}
              </div>

              <div className="max-h-[560px] overflow-y-auto scrollbar-none">
                {filtered.map((ep, i) => (
                  <EndpointRow key={i} ep={ep} probed={probeResults[ep.path]} />
                ))}
              </div>
            </div>
          ) : (
            <div className={`${CARD} p-10 text-center`}>
              <Globe size={24} className="text-slate-700 mx-auto mb-3" />
              <p className="text-slate-400 text-[14px] font-medium">No endpoints discovered</p>
              <p className="text-slate-600 text-[12px] mt-1">Run a full scan on the Scanner page first to populate the API map.</p>
              <Link to="/scanner"
                className="mt-3 inline-block text-[12px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
                Go to Scanner →
              </Link>
            </div>
          )}
        </>
      )}
    </div>
  )
}
