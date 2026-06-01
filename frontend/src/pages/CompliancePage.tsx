import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { useSessionStore } from '@/store/sessionStore'
import { complianceService, ComplianceReport, FrameworkResult, ComplianceControl } from '@/services/compliance'
import { ShieldCheck, AlertTriangle, XCircle, Info, RefreshCw, Terminal, CheckCircle2 } from 'lucide-react'
import clsx from 'clsx'

const STATUS_CONFIG = {
  pass: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20', label: 'Pass' },
  fail: { icon: XCircle,      color: 'text-rose-400',    bg: 'bg-rose-500/10 border-rose-500/20',    label: 'Fail' },
  warn: { icon: AlertTriangle, color: 'text-amber-400',  bg: 'bg-amber-500/10 border-amber-500/20',  label: 'Warn' },
  info: { icon: Info,          color: 'text-slate-400',  bg: 'bg-slate-800/40 border-slate-border/30', label: 'Info' },
}

const SEVERITY_COLOR: Record<string, string> = {
  critical: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
  high:     'text-orange-400 bg-orange-500/10 border-orange-500/20',
  medium:   'text-amber-400 bg-amber-500/10 border-amber-500/20',
  low:      'text-slate-400 bg-slate-800/40 border-slate-border/30',
}

const GRADE_COLOR: Record<string, string> = {
  A: 'text-emerald-400', B: 'text-green-400', C: 'text-amber-400', D: 'text-orange-400', F: 'text-rose-400',
}

const FRAMEWORK_ORDER = ['owasp', 'soc2', 'pcidss', 'gdpr']

function ScoreRing({ score, grade, size = 80 }: { score: number; grade: string; size?: number }) {
  const r = (size / 2) - 6
  const circ = 2 * Math.PI * r
  const dash = (score / 100) * circ
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={5} />
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(99,102,241,0.7)" strokeWidth={5}
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        transform={`rotate(-90 ${size/2} ${size/2})`} />
      <text x={size/2} y={size/2 - 6} textAnchor="middle" dominantBaseline="middle"
        fontSize={size > 60 ? 18 : 13} fontWeight="700" fontFamily="Inter,sans-serif" fill="#e2e8f0">
        {score}
      </text>
      <text x={size/2} y={size/2 + 10} textAnchor="middle" dominantBaseline="middle"
        fontSize={10} fontFamily="Inter,sans-serif" fill="#94a3b8">
        {grade}
      </text>
    </svg>
  )
}

function ControlRow({ control }: { control: ComplianceControl }) {
  const [open, setOpen] = useState(false)
  const cfg = STATUS_CONFIG[control.status] || STATUS_CONFIG.info
  const Icon = cfg.icon
  return (
    <div className="border border-slate-border/30 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-800/20 transition-colors"
      >
        <Icon size={15} className={clsx('shrink-0', cfg.color)} />
        <span className="font-mono text-xs text-slate-300 shrink-0 w-16">{control.id}</span>
        <span className="text-sm text-slate-200 font-medium flex-1">{control.name}</span>
        <span className={clsx('text-[10px] font-bold px-2 py-0.5 rounded border font-mono uppercase shrink-0', SEVERITY_COLOR[control.severity])}>
          {control.severity}
        </span>
        <span className={clsx('text-[10px] font-bold px-2 py-0.5 rounded border font-mono uppercase shrink-0', cfg.bg, cfg.color)}>
          {cfg.label}
        </span>
        <span className="text-slate-600 text-xs ml-1">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="px-4 pb-4 pt-1 bg-slate-950/30 space-y-3 border-t border-slate-border/20">
          <p className="text-xs text-slate-400 leading-relaxed">{control.finding}</p>
          {control.status !== 'pass' && (
            <div className="flex gap-2 items-start">
              <span className="text-[10px] font-bold text-indigo-400 font-mono uppercase shrink-0 mt-0.5">Fix</span>
              <p className="text-xs text-slate-400 leading-relaxed">{control.remediation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function FrameworkPanel({ fw }: { fw: FrameworkResult }) {
  const failedControls = fw.controls.filter(c => c.status === 'fail')
  const warnControls = fw.controls.filter(c => c.status === 'warn')
  const passControls = fw.controls.filter(c => c.status === 'pass')

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <ScoreRing score={fw.score} grade={fw.grade} size={72} />
          <div>
            <h2 className="text-xl font-black text-slate-100 font-display">{fw.icon} {fw.name}</h2>
            <p className="text-slate-400 text-xs mt-0.5 font-mono">Version: {fw.version}</p>
            <div className="flex gap-3 mt-2">
              <span className="text-xs text-emerald-400 font-mono">{fw.summary.passed} passed</span>
              <span className="text-xs text-rose-400 font-mono">{fw.summary.failed} failed</span>
              <span className="text-xs text-amber-400 font-mono">{fw.summary.warned} warnings</span>
            </div>
          </div>
        </div>

        {/* Score bar */}
        <div className="flex-1 min-w-[200px]">
          <div className="flex justify-between text-[10px] font-mono text-slate-500 mb-1">
            <span>Compliance score</span>
            <span>{fw.score}%</span>
          </div>
          <div className="w-full bg-slate-950/60 rounded-full h-2 overflow-hidden">
            <div
              className={clsx('h-full rounded-full transition-all duration-700',
                fw.score >= 80 ? 'bg-emerald-500' : fw.score >= 60 ? 'bg-amber-500' : 'bg-rose-500'
              )}
              style={{ width: `${fw.score}%` }}
            />
          </div>
        </div>
      </div>

      {/* Controls grouped by status */}
      {failedControls.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider font-mono">
            Failed ({failedControls.length})
          </h3>
          {failedControls.map(c => <ControlRow key={c.id} control={c} />)}
        </div>
      )}
      {warnControls.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono">
            Warnings ({warnControls.length})
          </h3>
          {warnControls.map(c => <ControlRow key={c.id} control={c} />)}
        </div>
      )}
      {passControls.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider font-mono">
            Passing ({passControls.length})
          </h3>
          {passControls.map(c => <ControlRow key={c.id} control={c} />)}
        </div>
      )}
    </div>
  )
}

export const CompliancePage: React.FC = () => {
  const navigate = useNavigate()
  const { currentSessionId } = useSessionStore()
  const [report, setReport] = useState<ComplianceReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeFramework, setActiveFramework] = useState('owasp')
  const [error, setError] = useState<string | null>(null)

  const fetchReport = async (sessionId: string) => {
    setLoading(true)
    setError(null)
    try {
      const res = await complianceService.getReport(sessionId)
      setReport((res.data as any).data)
    } catch (e: any) {
      setError(e?.response?.data?.message || 'Failed to load compliance report')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (currentSessionId) fetchReport(currentSessionId)
  }, [currentSessionId])

  if (!currentSessionId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Terminal size={40} className="text-slate-600" />
        <h2 className="text-xl font-bold text-slate-300 font-display">No active scan</h2>
        <p className="text-slate-500 text-sm text-center max-w-xs">
          Run a repository scan first to generate a compliance report.
        </p>
        <Button onClick={() => navigate('/scanner')} size="sm">Go to Scanner</Button>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] gap-3 text-slate-400 font-mono text-sm">
        <RefreshCw size={18} className="animate-spin text-indigo-400" />
        Running compliance checks across all frameworks...
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <XCircle size={36} className="text-rose-400" />
        <p className="text-slate-400 text-sm">{error}</p>
        <Button onClick={() => fetchReport(currentSessionId!)} size="sm" variant="secondary">Retry</Button>
      </div>
    )
  }

  if (!report) return null

  const orderedFrameworks = FRAMEWORK_ORDER.filter(id => report.frameworks[id])
  const activefw = report.frameworks[activeFramework]

  return (
    <div className="space-y-6 select-none animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">Compliance Monitor</h1>
          <p className="text-slate-400 text-sm mt-1 font-medium">
            Session: <span className="text-indigo-400 font-mono">{currentSessionId}</span>
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => fetchReport(currentSessionId!)}
          className="border-slate-border/80 hover:bg-slate-800 flex items-center gap-2"
        >
          <RefreshCw size={14} />
          Re-run checks
        </Button>
      </div>

      {/* Overall + framework score cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {/* Overall */}
        <Card className="col-span-2 md:col-span-1 flex flex-col items-center justify-center py-5 bg-slate-surface/30 border-slate-border/40">
          <ScoreRing score={report.overall.score} grade={report.overall.grade} size={80} />
          <p className="text-slate-400 text-[10px] font-mono mt-2 uppercase tracking-wider">Overall</p>
        </Card>

        {/* Per-framework */}
        {orderedFrameworks.map(fwId => {
          const fw = report.frameworks[fwId]
          return (
            <Card
              key={fwId}
              hover
              onClick={() => setActiveFramework(fwId)}
              className={clsx(
                'flex flex-col items-center justify-center py-5 cursor-pointer transition-all duration-200',
                activeFramework === fwId
                  ? 'bg-indigo-500/10 border-indigo-500/40'
                  : 'bg-slate-surface/30 border-slate-border/40 hover:border-slate-border/70'
              )}
            >
              <ScoreRing score={fw.score} grade={fw.grade} size={64} />
              <p className="text-slate-300 text-[10px] font-mono mt-2 font-bold">{fw.icon} {fw.name}</p>
              <div className="flex gap-2 mt-1">
                <span className="text-[9px] text-rose-400 font-mono">{fw.summary.failed}F</span>
                <span className="text-[9px] text-amber-400 font-mono">{fw.summary.warned}W</span>
                <span className="text-[9px] text-emerald-400 font-mono">{fw.summary.passed}P</span>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Framework detail */}
      {activefw && (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <FrameworkPanel fw={activefw} />
        </Card>
      )}
    </div>
  )
}
