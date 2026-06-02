import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { useSessionStore } from '@/store/sessionStore'
import { threatsService, ThreatSimulation, KillChainStage, AttackVector } from '@/services/threats'
import { Terminal, RefreshCw, ChevronDown, ChevronUp, Shield, AlertTriangle } from 'lucide-react'
import clsx from 'clsx'

const RISK_COLOR = (r: number) =>
  r >= 7 ? '#ef4444' : r >= 5 ? '#f97316' : r >= 3 ? '#f59e0b' : '#10b981'

const RISK_BG = (r: number) =>
  r >= 7 ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
  : r >= 5 ? 'bg-orange-500/10 border-orange-500/30 text-orange-400'
  : r >= 3 ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
  : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'

const IMPACT_COLOR: Record<string, string> = {
  Critical: 'text-rose-400', High: 'text-orange-400',
  Medium: 'text-amber-400', Low: 'text-emerald-400',
}

// ── Kill Chain SVG ────────────────────────────────────────────────────────────
function KillChainDiagram({ stages }: { stages: KillChainStage[] }) {
  const [hoveredStage, setHoveredStage] = useState<string | null>(null)

  const W = 900, H = 180
  const stageW = W / stages.length
  const boxW = stageW - 16
  const boxH = 100
  const boxY = (H - boxH) / 2

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full min-w-[600px]" style={{ height: H }}>
        {stages.map((stage, i) => {
          const x = i * stageW + 8
          const isCompromised = stage.compromised
          const risk = stage.risk
          const col = RISK_COLOR(risk)
          const isHovered = hoveredStage === stage.stage
          const opacity = hoveredStage ? (isHovered ? 1 : 0.45) : 1

          return (
            <g key={stage.stage} style={{ opacity, cursor: 'pointer', transition: 'opacity .2s' }}
              onMouseEnter={() => setHoveredStage(stage.stage)}
              onMouseLeave={() => setHoveredStage(null)}
            >
              {/* Connector arrow */}
              {i > 0 && isCompromised && (
                <line
                  x1={x - 8} y1={H / 2}
                  x2={x} y2={H / 2}
                  stroke={col} strokeWidth={2}
                  strokeDasharray={isCompromised ? 'none' : '4'}
                  opacity={0.6}
                />
              )}
              {i > 0 && isCompromised && (
                <polygon
                  points={`${x},${H/2-4} ${x+6},${H/2} ${x},${H/2+4}`}
                  fill={col} opacity={0.7}
                />
              )}

              {/* Box */}
              <rect
                x={x} y={boxY} width={boxW} height={boxH}
                rx={8}
                fill={isCompromised ? `${col}22` : 'rgba(15,23,42,0.6)'}
                stroke={isCompromised ? col : 'rgba(51,65,85,0.5)'}
                strokeWidth={isCompromised ? 1.5 : 1}
              />

              {/* Stage name */}
              <text x={x + boxW / 2} y={boxY + 18}
                textAnchor="middle" fontSize={9} fontWeight="600"
                fontFamily="Inter,sans-serif"
                fill={isCompromised ? col : '#64748b'}
                style={{ textTransform: 'uppercase', letterSpacing: '.06em' }}
              >
                {stage.stage.replace('Privilege Escalation', 'Priv. Esc').replace('Defense Evasion', 'Def. Evasion').replace('Lateral Movement', 'Lateral Mvmt')}
              </text>

              {/* Risk score circle */}
              <circle cx={x + boxW / 2} cy={boxY + 50} r={20}
                fill={isCompromised ? `${col}33` : 'rgba(15,23,42,0.8)'}
                stroke={isCompromised ? col : '#334155'}
                strokeWidth={isCompromised ? 2 : 1}
              />
              <text x={x + boxW / 2} y={boxY + 54}
                textAnchor="middle" fontSize={12} fontWeight="800"
                fontFamily="Inter,monospace"
                fill={isCompromised ? col : '#475569'}
              >
                {risk.toFixed(1)}
              </text>

              {/* Vector count */}
              <text x={x + boxW / 2} y={boxY + boxH - 10}
                textAnchor="middle" fontSize={9}
                fontFamily="Inter,sans-serif"
                fill={isCompromised ? col : '#475569'}
              >
                {stage.active_vectors}/{stage.total_vectors} vectors
              </text>
            </g>
          )
        })}
      </svg>

      {/* Hovered stage detail */}
      {hoveredStage && (() => {
        const stage = stages.find(s => s.stage === hoveredStage)!
        return (
          <div className="mt-3 p-3 bg-slate-950/60 border border-slate-border/40 rounded-xl text-xs space-y-1">
            <p className="font-bold text-slate-200 font-display">{stage.stage}</p>
            <div className="flex gap-4">
              <span className="text-slate-400">Exploitability: <span className="font-mono" style={{ color: RISK_COLOR(stage.exploitability) }}>{stage.exploitability}</span></span>
              <span className="text-slate-400">Impact: <span className="font-mono" style={{ color: RISK_COLOR(stage.impact) }}>{stage.impact}</span></span>
              <span className="text-slate-400">Active vectors: <span className="font-mono text-slate-200">{stage.active_vectors}</span></span>
            </div>
          </div>
        )
      })()}
    </div>
  )
}

// ── Heat Map SVG ──────────────────────────────────────────────────────────────
function HeatMap({ points }: { points: any[] }) {
  const [hovered, setHovered] = useState<string | null>(null)
  const PAD = 48
  const W = 520, H = 320

  const scaleX = (v: number) => PAD + (v / 10) * (W - PAD * 2)
  const scaleY = (v: number) => H - PAD - (v / 10) * (H - PAD * 2)

  return (
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
        {/* Grid */}
        {[2,4,6,8,10].map(v => (
          <g key={v}>
            <line x1={scaleX(v)} y1={PAD} x2={scaleX(v)} y2={H-PAD}
              stroke="rgba(51,65,85,0.3)" strokeWidth={1} strokeDasharray="4" />
            <line x1={PAD} y1={scaleY(v)} x2={W-PAD} y2={scaleY(v)}
              stroke="rgba(51,65,85,0.3)" strokeWidth={1} strokeDasharray="4" />
            <text x={scaleX(v)} y={H-PAD+14} textAnchor="middle" fontSize={9}
              fill="#475569" fontFamily="Inter,monospace">{v}</text>
            <text x={PAD-8} y={scaleY(v)+4} textAnchor="end" fontSize={9}
              fill="#475569" fontFamily="Inter,monospace">{v}</text>
          </g>
        ))}

        {/* Axis labels */}
        <text x={W/2} y={H-4} textAnchor="middle" fontSize={10} fill="#64748b"
          fontFamily="Inter,sans-serif" fontWeight="600">Exploitability →</text>
        <text x={12} y={H/2} textAnchor="middle" fontSize={10} fill="#64748b"
          fontFamily="Inter,sans-serif" fontWeight="600"
          transform={`rotate(-90, 12, ${H/2})`}>Impact ↑</text>

        {/* Axes */}
        <line x1={PAD} y1={PAD} x2={PAD} y2={H-PAD} stroke="#1e293b" strokeWidth={1.5}/>
        <line x1={PAD} y1={H-PAD} x2={W-PAD} y2={H-PAD} stroke="#1e293b" strokeWidth={1.5}/>

        {/* Risk zones */}
        <rect x={scaleX(5)} y={PAD} width={W-PAD-scaleX(5)} height={scaleY(5)-PAD}
          fill="rgba(239,68,68,0.04)" />
        <text x={W-PAD-8} y={PAD+14} textAnchor="end" fontSize={8}
          fill="rgba(239,68,68,0.4)" fontFamily="Inter,sans-serif">CRITICAL ZONE</text>

        {/* Points */}
        {points.map(p => {
          const cx = scaleX(p.exploitability)
          const cy = scaleY(p.impact)
          const col = RISK_COLOR(p.exploitability * p.impact / 10)
          const r = p.present ? 9 : 5
          const isHov = hovered === p.id
          return (
            <g key={p.id}
              onMouseEnter={() => setHovered(p.id)}
              onMouseLeave={() => setHovered(null)}
              style={{ cursor: 'pointer' }}
            >
              {isHov && <circle cx={cx} cy={cy} r={r + 6} fill={`${col}22`} />}
              <circle cx={cx} cy={cy} r={r}
                fill={p.present ? `${col}55` : 'rgba(15,23,42,0.8)'}
                stroke={col}
                strokeWidth={p.present ? 2 : 1}
                opacity={p.present ? 1 : 0.4}
              />
              {p.present && (
                <circle cx={cx} cy={cy} r={3} fill={col} />
              )}
            </g>
          )
        })}
      </svg>

      {/* Hover tooltip */}
      {hovered && (() => {
        const p = points.find(pt => pt.id === hovered)!
        const risk = (p.exploitability * p.impact / 10).toFixed(1)
        return (
          <div className="absolute bottom-0 left-0 right-0 px-3 py-2 bg-slate-950/80 border-t border-slate-border/30 text-xs">
            <span className="font-bold text-slate-200">{p.name}</span>
            <span className="text-slate-500 mx-2">·</span>
            <span className="text-slate-400">Stage: {p.stage}</span>
            <span className="text-slate-500 mx-2">·</span>
            <span style={{ color: RISK_COLOR(Number(risk)) }} className="font-mono font-bold">
              Risk {risk}
            </span>
            {!p.present && <span className="text-slate-600 ml-2">(not detected)</span>}
          </div>
        )
      })()}
    </div>
  )
}

// ── Vector Row ────────────────────────────────────────────────────────────────
function VectorRow({ v }: { v: AttackVector }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-slate-border/30 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-800/20 transition-colors"
      >
        <span className={clsx(
          'w-2 h-2 rounded-full shrink-0',
          v.present ? (v.risk_score >= 7 ? 'bg-rose-500 animate-pulse' : v.risk_score >= 5 ? 'bg-orange-500' : 'bg-amber-500') : 'bg-slate-600'
        )} />
        <span className="font-mono text-[10px] text-slate-500 shrink-0 w-14">{v.technique}</span>
        <span className="text-sm text-slate-200 font-medium flex-1">{v.name}</span>
        <span className="text-[10px] text-slate-500 font-mono shrink-0">{v.stage}</span>
        <span className={clsx('text-xs font-bold font-mono px-2 py-0.5 rounded border shrink-0', RISK_BG(v.risk_score))}>
          {v.risk_score.toFixed(1)}
        </span>
        {open ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
      </button>
      {open && (
        <div className="px-4 pb-4 pt-1 bg-slate-950/30 space-y-3 border-t border-slate-border/20">
          <p className="text-xs text-slate-400 leading-relaxed">{v.description}</p>
          <p className="text-xs"><span className="text-slate-500">Evidence: </span><span className="text-slate-300">{v.evidence}</span></p>
          {v.affected_assets.length > 0 && (
            <p className="text-xs"><span className="text-slate-500">Affected: </span>
              <span className="font-mono text-indigo-400">{v.affected_assets.join(', ')}</span></p>
          )}
          {v.mitigations.length > 0 && (
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Mitigations</p>
              <ul className="space-y-0.5">
                {v.mitigations.map((m, i) => (
                  <li key={i} className="text-xs text-slate-400 flex gap-1.5">
                    <span className="text-indigo-500 shrink-0">→</span>{m}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export const ThreatPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentSessionId } = useSessionStore()
  const [simulation, setSimulation] = useState<ThreatSimulation | null>(null)
  const [activeActor, setActiveActor] = useState('apt')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runSimulation = async (actorId: string) => {
    if (!currentSessionId) return
    setLoading(true)
    setError(null)
    try {
      const res = await threatsService.simulate(currentSessionId, actorId)
      setSimulation((res.data as any).data)
    } catch (e: any) {
      setError(e?.response?.data?.message || 'Simulation failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (currentSessionId) runSimulation(activeActor)
  }, [currentSessionId])

  const switchActor = (id: string) => {
    setActiveActor(id)
    runSimulation(id)
  }

  if (!currentSessionId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Terminal size={40} className="text-slate-600" />
        <h2 className="text-xl font-bold text-slate-300 font-display">No active scan</h2>
        <p className="text-slate-500 text-sm text-center max-w-xs">
          Scan a repository first to simulate threat scenarios.
        </p>
        <Button onClick={() => navigate('/scanner')} size="sm">Go to Scanner</Button>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] gap-3 text-slate-400 font-mono text-sm">
        <RefreshCw size={18} className="animate-spin text-rose-400" />
        Running threat simulation…
      </div>
    )
  }

  if (error || !simulation) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <AlertTriangle size={36} className="text-amber-400" />
        <p className="text-slate-400 text-sm">{error || 'No simulation data'}</p>
        <Button onClick={() => runSimulation(activeActor)} size="sm" variant="secondary">Retry</Button>
      </div>
    )
  }

  const { actor, kill_chain, vectors, heat_map, business_impact, summary, available_actors } = simulation
  const activeVectors = vectors.filter(v => v.present)

  return (
    <div className="space-y-6 select-none animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">
            Threat Actor Simulation
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Session: <span className="text-indigo-400 font-mono">{currentSessionId}</span>
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => runSimulation(activeActor)}
          className="flex items-center gap-2 border-slate-border/80">
          <RefreshCw size={14} />
          Re-simulate
        </Button>
      </div>

      {/* Threat actor selector */}
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Threat Actor Profile</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.values(available_actors).map(a => (
            <button
              key={a.id}
              onClick={() => switchActor(a.id)}
              className={clsx(
                'px-4 py-3 rounded-xl border text-left transition-all duration-200',
                activeActor === a.id
                  ? 'bg-rose-500/10 border-rose-500/30'
                  : 'bg-slate-950/40 border-slate-border/30 hover:border-slate-border/60'
              )}
            >
              <p className="text-lg mb-1">{a.icon}</p>
              <p className={clsx('text-xs font-bold', activeActor === a.id ? 'text-rose-300' : 'text-slate-300')}>
                {a.name}
              </p>
              <p className="text-[10px] text-slate-500 mt-0.5">{a.motivation}</p>
              <div className="mt-2 flex gap-1">
                {Array.from({ length: 10 }).map((_, i) => (
                  <div key={i} className={clsx(
                    'h-1 flex-1 rounded-full',
                    i < a.skill_level ? (activeActor === a.id ? 'bg-rose-500' : 'bg-indigo-600') : 'bg-slate-800'
                  )} />
                ))}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Summary hero */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Overall Risk', value: summary.overall_risk.toFixed(1), sub: summary.risk_label,
            color: RISK_COLOR(summary.overall_risk) },
          { label: 'Active Vectors', value: summary.active_vectors, sub: `of ${summary.total_vectors} total`,
            color: '#f97316' },
          { label: 'Critical Paths', value: summary.critical_vectors, sub: 'high exploit + impact',
            color: '#ef4444' },
          { label: 'Stages Exposed', value: `${summary.stages_compromised}/8`, sub: 'kill chain stages',
            color: '#f59e0b' },
        ].map(card => (
          <Card key={card.label} className="bg-slate-surface/30 border-slate-border/40 text-center py-5">
            <div style={{ color: card.color }} className="text-3xl font-black font-display">
              {card.value}
            </div>
            <div className="text-slate-300 text-xs font-bold mt-1">{card.label}</div>
            <div className="text-slate-600 text-[10px] mt-0.5 font-mono">{card.sub}</div>
          </Card>
        ))}
      </div>

      {/* Kill chain diagram */}
      <Card className="bg-slate-surface/30 border-slate-border/40 space-y-4">
        <div>
          <h2 className="font-bold text-slate-100 font-display text-base">
            {actor.icon} {actor.name} — Attack Kill Chain
          </h2>
          <p className="text-slate-500 text-xs mt-0.5">{actor.description}</p>
        </div>
        <KillChainDiagram stages={kill_chain} />
        <div className="flex gap-4 text-[10px] text-slate-500 font-mono">
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-rose-500" />Compromised stage</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-slate-700" />Not exposed</span>
          <span className="text-slate-600">Hover stages for details · Score = exploitability × impact</span>
        </div>
      </Card>

      {/* Heat map + business impact */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-slate-surface/30 border-slate-border/40 space-y-3">
          <h2 className="font-bold text-slate-100 font-display text-base">
            Exploitability vs Impact Heat Map
          </h2>
          <p className="text-slate-500 text-xs">Filled = present in your codebase · Hover for details</p>
          <HeatMap points={heat_map} />
        </Card>

        <Card className="bg-slate-surface/30 border-slate-border/40 space-y-4">
          <h2 className="font-bold text-slate-100 font-display text-base">Business Impact Assessment</h2>
          <div className="space-y-3">
            {[
              { label: 'Data Breach Risk', value: business_impact.data_breach_risk },
              { label: 'Service Disruption', value: business_impact.service_disruption },
              { label: 'Reputational Damage', value: business_impact.reputational_damage },
              { label: 'Regulatory Exposure', value: business_impact.regulatory_exposure },
            ].map(row => (
              <div key={row.label} className="flex justify-between items-center py-2 border-b border-slate-border/20 last:border-0">
                <span className="text-sm text-slate-400">{row.label}</span>
                <span className={clsx('text-sm font-bold', IMPACT_COLOR[row.value] || 'text-slate-300')}>
                  {row.value}
                </span>
              </div>
            ))}
            <div className="pt-2 flex justify-between items-center bg-slate-950/40 rounded-xl px-4 py-3">
              <span className="text-xs text-slate-400 font-semibold">Estimated Breach Cost</span>
              <span className="text-sm font-black text-rose-400">{business_impact.estimated_breach_cost}</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Attack vectors list */}
      <Card className="bg-slate-surface/30 border-slate-border/40 space-y-3">
        <div className="flex justify-between items-center">
          <h2 className="font-bold text-slate-100 font-display text-base">
            Attack Vectors ({activeVectors.length} active)
          </h2>
          <span className="text-[10px] text-slate-500 font-mono">Click to expand findings + mitigations</span>
        </div>
        <div className="space-y-2">
          {vectors
            .sort((a, b) => b.risk_score - a.risk_score)
            .map(v => <VectorRow key={v.id} v={v} />)}
        </div>
      </Card>
    </div>
  )
}
