import React, { useState, useEffect } from 'react'
import { useSessionStore } from '@/store/sessionStore'
import { threatsService } from '@/services/threats'
import { AskAIButton } from '@/components/common/AskAIButton'
import {
  Skull, AlertTriangle, Shield, ChevronRight, RefreshCw,
  Terminal, ArrowRight, X, Target, Zap, TrendingUp,
} from 'lucide-react'
import clsx from 'clsx'

// ── Design tokens ──────────────────────────────────────────────────────────
const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

// ── Colour maps ────────────────────────────────────────────────────────────
const SEV_COLOR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#3b82f6',
}
const HEAT_BG: Record<string, string> = {
  0:  'bg-transparent',
  1:  'bg-blue-500/10',
  2:  'bg-amber-500/15',
  3:  'bg-orange-500/20',
  4:  'bg-red-500/25',
}
const HEAT_TEXT: Record<string, string> = {
  0:  'text-slate-700',
  1:  'text-blue-400',
  2:  'text-amber-400',
  3:  'text-orange-400',
  4:  'text-red-400',
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

// ── Kill chain diagram ─────────────────────────────────────────────────────
function KillChain({ chain, onSelect, selected }: {
  chain: any; onSelect: () => void; selected: boolean
}) {
  const sevColor = SEV_COLOR[chain.severity] || '#64748b'
  return (
    <div
      onClick={onSelect}
      className={clsx(
        CARD, 'p-5 cursor-pointer transition-all duration-200',
        selected ? 'ring-1 ring-inset' : 'hover:border-white/[0.14]',
      )}
      style={selected ? { ringColor: sevColor } : {}}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-slate-elevated border border-white/[0.06] shrink-0 mt-0.5">
            <Skull size={13} style={{ color: sevColor }} />
          </div>
          <div>
            <p className="text-[12px] font-semibold text-slate-200 font-tight leading-tight">
              {chain.file.split('/').slice(-2).join('/')}
            </p>
            <p className="text-[10px] text-slate-600 font-mono mt-0.5">
              {chain.stage_count} stages · {chain.issue_count} issues · risk {chain.risk_score}
            </p>
          </div>
        </div>
        <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border shrink-0"
          style={{ color: sevColor, backgroundColor: `${sevColor}12`, borderColor: `${sevColor}28` }}>
          {chain.severity}
        </span>
      </div>

      {/* Stage pills */}
      <div className="flex flex-wrap items-center gap-1.5">
        {chain.stages.map((stage: string, i: number) => {
          const step = chain.steps[i]
          const c = SEV_COLOR[step?.severity] || '#64748b'
          return (
            <React.Fragment key={stage}>
              <div className="flex items-center gap-1 px-2 py-1 rounded-lg border text-[9px] font-semibold"
                style={{ color: c, backgroundColor: `${c}10`, borderColor: `${c}22` }}>
                <div className="w-1 h-1 rounded-full" style={{ backgroundColor: c }} />
                {stage}
              </div>
              {i < chain.stages.length - 1 && (
                <ArrowRight size={9} className="text-slate-700 shrink-0" />
              )}
            </React.Fragment>
          )
        })}
      </div>
    </div>
  )
}

// ── Chain detail drawer ────────────────────────────────────────────────────
function ChainDrawer({ chain, onClose }: { chain: any; onClose: () => void }) {
  return (
    <div className={`${CARD} p-6 space-y-4`}>
      <div className="flex items-center justify-between">
        <h3 className="text-[15px] font-semibold text-slate-200 font-tight">Attack Path Detail</h3>
        <button onClick={onClose} className="text-slate-700 hover:text-slate-400 transition-colors">
          <X size={16} />
        </button>
      </div>
      <p className="text-[11px] font-mono text-slate-600">{chain.file}</p>

      <div className="space-y-3">
        {chain.steps.map((step: any, i: number) => {
          const c = SEV_COLOR[step.severity] || '#64748b'
          return (
            <div key={i} className="flex gap-3">
              {/* Timeline line */}
              <div className="flex flex-col items-center shrink-0">
                <div className="w-6 h-6 rounded-full border-2 flex items-center justify-center text-[9px] font-bold"
                  style={{ borderColor: c, color: c, backgroundColor: `${c}10` }}>
                  {i + 1}
                </div>
                {i < chain.steps.length - 1 && (
                  <div className="w-px flex-1 mt-1" style={{ backgroundColor: `${c}30` }} />
                )}
              </div>

              {/* Content */}
              <div className="pb-4 flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="text-[12px] font-semibold text-slate-200">{step.stage}</span>
                  <span className="text-[9px] font-mono text-slate-600">{step.tactic}</span>
                  <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border"
                    style={{ color: c, backgroundColor: `${c}12`, borderColor: `${c}28` }}>
                    {step.severity}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mb-1">{step.impact}</p>
                <p className="text-[11px] text-slate-600">
                  <span className="text-slate-500 font-medium">{step.issue_type}</span>
                  {step.file && (
                    <span className="font-mono ml-2 text-slate-700">
                      {step.file.split('/').slice(-1)[0]}:{step.line}
                    </span>
                  )}
                </p>
                {step.description && (
                  <p className="text-[11px] text-slate-700 mt-1 leading-relaxed line-clamp-2">{step.description}</p>
                )}
              </div>
            </div>
          )
        })}
      </div>
      <AskAIButton
        label={`${chain.severity} kill chain`}
        context={`Attack chain in ${chain.file} — ${chain.stage_count} MITRE ATT&CK stages: ${chain.stages.join(' → ')}. Severity: ${chain.severity}. Risk score: ${chain.risk_score}. Exploits ${chain.issue_count} vulnerabilities.`}
      />
    </div>
  )
}

// ── Heat map ───────────────────────────────────────────────────────────────
const STAGES = [
  'Reconnaissance', 'Initial Access', 'Execution', 'Persistence',
  'Privilege Escalation', 'Defense Evasion', 'Credential Access',
  'Lateral Movement', 'Exfiltration',
]
const SEVS = ['critical', 'high', 'medium', 'low']

function HeatMap({ cells }: { cells: any[] }) {
  const cellMap: Record<string, Record<string, any>> = {}
  for (const cell of cells) {
    if (!cellMap[cell.stage]) cellMap[cell.stage] = {}
    cellMap[cell.stage][cell.severity] = cell
  }

  const maxCount = Math.max(...cells.map(c => c.count), 1)

  return (
    <div className={`${CARD} p-6`}>
      <div className="mb-5">
        <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-600 mb-1">Attack Surface</p>
        <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Threat Heat Map</h2>
        <p className="text-[11px] text-slate-600 mt-1">MITRE ATT&CK stages × vulnerability severity</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left" style={{ borderCollapse: 'separate', borderSpacing: 0 }}>
          <thead>
            <tr>
              <th className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-600 pb-3 pr-4 whitespace-nowrap">
                Stage
              </th>
              {SEVS.map(sev => (
                <th key={sev} className="text-[9px] font-bold uppercase tracking-[0.12em] pb-3 px-2 text-center whitespace-nowrap"
                  style={{ color: SEV_COLOR[sev] }}>
                  {sev}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {STAGES.map((stage, si) => (
              <tr key={stage}>
                <td className={clsx(
                  'text-[11px] text-slate-400 pr-4 py-1.5 whitespace-nowrap font-medium',
                  si < STAGES.length - 1 ? 'border-b border-white/[0.04]' : ''
                )}>
                  {stage}
                </td>
                {SEVS.map(sev => {
                  const cell = cellMap[stage]?.[sev]
                  const count = cell?.count ?? 0
                  const intensity = count === 0 ? 0 : Math.ceil((count / maxCount) * 4)
                  return (
                    <td key={sev} className={clsx(
                      'px-2 py-1.5 text-center',
                      si < STAGES.length - 1 ? 'border-b border-white/[0.04]' : ''
                    )}>
                      <div className={clsx(
                        'mx-auto w-10 h-7 rounded-lg flex items-center justify-center text-[11px] font-bold transition-all',
                        count > 0 ? HEAT_BG[intensity] : 'bg-transparent',
                        count > 0 ? HEAT_TEXT[intensity] : 'text-slate-800',
                      )}>
                        {count > 0 ? count : '·'}
                      </div>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-5 pt-4 border-t border-white/[0.05]">
        <span className="text-[9px] text-slate-700 uppercase tracking-wider font-bold">Intensity:</span>
        {[
          { label: 'None', bg: 'bg-transparent', text: 'text-slate-700' },
          { label: 'Low', bg: 'bg-blue-500/10', text: 'text-blue-400' },
          { label: 'Med', bg: 'bg-amber-500/15', text: 'text-amber-400' },
          { label: 'High', bg: 'bg-orange-500/20', text: 'text-orange-400' },
          { label: 'Critical', bg: 'bg-red-500/25', text: 'text-red-400' },
        ].map(({ label, bg, text }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className={clsx('w-5 h-4 rounded', bg, text === 'text-slate-700' ? 'border border-white/[0.06]' : '')} />
            <span className={clsx('text-[9px] font-medium', text)}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────
export const ThreatPage: React.FC = () => {
  const { currentSessionId } = useSessionStore()
  const [chains, setChains]     = useState<any[]>([])
  const [heatMap, setHeatMap]   = useState<any[]>([])
  const [metrics, setMetrics]   = useState<any>(null)
  const [loading, setLoading]   = useState(false)
  const [scanned, setScanned]   = useState(false)
  const [selected, setSelected] = useState<any>(null)

  const runSim = async () => {
    if (!currentSessionId || loading) return
    setLoading(true)
    setSelected(null)
    try {
      const res = await threatsService.simulate(currentSessionId)
      const d   = (res.data as any).data
      setChains(d.chains || [])
      setHeatMap(d.heat_map || [])
      setMetrics(d.metrics || null)
      setScanned(true)
    } catch {
      setScanned(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (currentSessionId && !scanned) runSim()
  }, [currentSessionId])

  return (
    <div className="space-y-5 animate-fade-in pb-10 select-none">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
        <div>
          <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Threat Simulation</h1>
          <p className="text-slate-500 text-[13px] mt-1.5">
            {currentSessionId
              ? 'MITRE ATT&CK kill chains and heat map generated from your vulnerabilities.'
              : 'Scan a repository first to simulate attack paths.'}
          </p>
        </div>
        <button onClick={runSim} disabled={!currentSessionId || loading}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all duration-200',
            scanned
              ? 'border border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200 hover:border-white/[0.14]'
              : 'bg-red-500/80 hover:bg-red-500 text-white shadow-sm shadow-red-500/25',
            'disabled:opacity-40'
          )}>
          <RefreshCw size={13} className={clsx(loading && 'animate-spin')} />
          {loading ? 'Simulating…' : scanned ? 'Re-simulate' : 'Simulate threats'}
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
          <Skull size={22} className="text-red-400/60 animate-pulse mx-auto mb-3" />
          <p className="text-slate-400 text-[13px]">Simulating attacker behaviour…</p>
          <p className="text-slate-600 text-[11px] font-mono mt-1">
            Chaining vulnerabilities → mapping MITRE ATT&CK stages → scoring blast radius
          </p>
        </div>
      )}

      {/* Results */}
      {scanned && !loading && (
        <>
          {/* Metric cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Attack Chains"     value={metrics?.total_chains ?? chains.length}
              sub={`${metrics?.critical_chains ?? 0} critical paths`}
              accent="#ef4444" icon={Skull} />
            <StatCard label="Stages Exposed"    value={metrics?.stages_exposed ?? 0}
              sub="of 9 MITRE ATT&CK tactics"
              accent="#f97316" icon={Target} />
            <StatCard label="Blast Radius"
              value={metrics?.blast_radius_pct != null ? `${metrics.blast_radius_pct}%` : '—'}
              sub="of kill chain covered"
              accent="#a855f7" icon={Zap} />
            <StatCard label="Critical Vulns"
              value={metrics?.by_severity?.critical ?? 0}
              sub={`${metrics?.by_severity?.high ?? 0} high severity`}
              accent="#eab308" icon={TrendingUp} />
          </div>

          {/* Stage coverage badges */}
          {metrics?.stage_coverage?.length > 0 && (
            <div className={`${CARD} px-6 py-4`}>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-600 mr-1 shrink-0">
                  Exposed tactics:
                </span>
                {metrics.stage_coverage.map((stage: string) => (
                  <span key={stage}
                    className="text-[10px] font-medium px-2.5 py-1 rounded-full border border-red-500/20 bg-red-500/[0.07] text-red-400">
                    {stage}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Heat map */}
          {heatMap.length > 0 && <HeatMap cells={heatMap} />}

          {/* Kill chains */}
          {chains.length > 0 ? (
            <>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-600 mb-3">
                  Kill Chains — ordered by risk score
                </p>
                <div className="space-y-3">
                  {chains.map((chain: any) => (
                    <KillChain
                      key={chain.chain_id}
                      chain={chain}
                      selected={selected?.chain_id === chain.chain_id}
                      onSelect={() => setSelected(
                        selected?.chain_id === chain.chain_id ? null : chain
                      )}
                    />
                  ))}
                </div>
              </div>

              {/* Detail drawer */}
              {selected && (
                <ChainDrawer chain={selected} onClose={() => setSelected(null)} />
              )}
            </>
          ) : (
            <div className={`${CARD} p-10 text-center`}>
              <Shield size={24} className="text-emerald-400 mx-auto mb-3" />
              <p className="text-slate-300 text-[14px] font-semibold font-tight">No viable attack chains found</p>
              <p className="text-slate-600 text-[12px] mt-1">
                Vulnerabilities detected don't form multi-stage kill chains. Keep it that way.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
