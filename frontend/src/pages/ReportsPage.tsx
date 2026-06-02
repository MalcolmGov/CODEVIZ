import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSessionStore } from '@/store/sessionStore'
import { reportsService, Schedule } from '@/services/reports'
import {
  FileDown, Mail, Clock, Trash2, Play, Terminal,
  CheckCircle2, XCircle, Plus, RefreshCw, ExternalLink,
} from 'lucide-react'
import clsx from 'clsx'

// ── Design tokens ──────────────────────────────────────────────────────────
const CARD       = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'
const LABEL      = 'text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-1.5 block'
const INPUT      = 'w-full rounded-xl border border-white/[0.08] bg-slate-elevated px-3.5 py-2.5 text-[13px] text-slate-200 placeholder-slate-700 font-mono focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all disabled:opacity-40'
const SELECT_CLS = 'w-full rounded-xl border border-white/[0.08] bg-slate-elevated px-3.5 py-2.5 text-[13px] text-slate-200 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all appearance-none'

const CRON_PRESETS = [
  { label: 'Daily at 6am',    cron: '0 6 * * *'    },
  { label: 'Daily at 9am',    cron: '0 9 * * *'    },
  { label: 'Weekly Mon 8am',  cron: '0 8 * * 1'    },
  { label: 'Every 12 hours',  cron: '0 */12 * * *' },
  { label: 'Custom…',         cron: ''              },
]

// ── Status pill ────────────────────────────────────────────────────────────
function StatusPill({ status }: { status: string | null }) {
  if (!status) return <span className="text-slate-700 text-[10px] font-mono">Never run</span>
  const ok  = status === 'success'
  const err = status.startsWith('error') || status.startsWith('failed')
  return (
    <span className={clsx(
      'text-[10px] font-mono px-2 py-0.5 rounded border',
      ok  ? 'text-emerald-400 bg-emerald-500/[0.08] border-emerald-500/20' :
      err ? 'text-rose-400 bg-rose-500/[0.08] border-rose-500/20' :
            'text-amber-400 bg-amber-500/[0.08] border-amber-500/20'
    )}>
      {ok ? '✓ Success' : err ? '✗ ' + status.slice(0, 40) : status}
    </span>
  )
}

// ── Section header ─────────────────────────────────────────────────────────
function SectionHeader({ icon: Icon, title, desc, accent }: {
  icon: React.ElementType; title: string; desc: string; accent: string
}) {
  return (
    <div className="flex items-start gap-3 pb-5 mb-5 border-b border-white/[0.05]">
      <div className="p-2 rounded-xl border border-white/[0.06] bg-slate-elevated shrink-0 mt-0.5">
        <Icon size={15} style={{ color: accent }} />
      </div>
      <div>
        <h2 className="text-[15px] font-semibold text-slate-200 font-tight">{title}</h2>
        <p className="text-[12px] text-slate-500 mt-0.5">{desc}</p>
      </div>
    </div>
  )
}

// ── Schedule modal ─────────────────────────────────────────────────────────
function ScheduleModal({
  repoPath, onClose, onCreated,
}: { repoPath: string; onClose: () => void; onCreated: () => void }) {
  const [email,          setEmail]          = useState('')
  const [selectedPreset, setSelectedPreset] = useState(0)
  const [customCron,     setCustomCron]     = useState('')
  const [label,          setLabel]          = useState('')
  const [timezone,       setTimezone]       = useState('UTC')
  const [loading,        setLoading]        = useState(false)
  const [error,          setError]          = useState<string | null>(null)

  const cron = CRON_PRESETS[selectedPreset].cron || customCron

  const handleCreate = async () => {
    if (!email || !cron) { setError('Email and schedule are required'); return }
    setLoading(true); setError(null)
    try {
      await reportsService.createSchedule({ repo_path: repoPath, email, cron, label, timezone })
      onCreated(); onClose()
    } catch (e: any) {
      setError(e?.response?.data?.message || 'Failed to create schedule')
    } finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className={`${CARD} w-full max-w-md p-6 space-y-5`}>
        <div className="flex items-center justify-between">
          <h3 className="text-[16px] font-bold text-slate-200 font-tight">Schedule report</h3>
          <button onClick={onClose}
            className="text-slate-700 hover:text-slate-400 transition-colors text-lg leading-none">×</button>
        </div>

        <div>
          <label className={LABEL}>Repository</label>
          <div className="font-mono text-[12px] text-indigo-400 bg-indigo-500/[0.08] border border-indigo-500/20 rounded-xl px-3.5 py-2.5">
            {repoPath}
          </div>
        </div>

        <div>
          <label className={LABEL}>Email recipient</label>
          <input type="email" placeholder="you@company.com" value={email}
            onChange={e => setEmail(e.target.value)} className={INPUT} />
        </div>

        <div>
          <label className={LABEL}>Frequency</label>
          <div className="grid grid-cols-2 gap-2">
            {CRON_PRESETS.map((p, i) => (
              <button key={i} type="button" onClick={() => setSelectedPreset(i)}
                className={clsx(
                  'px-3 py-2 rounded-xl text-[11px] font-medium border transition-all text-left',
                  selectedPreset === i
                    ? 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300'
                    : 'border-white/[0.07] text-slate-500 hover:text-slate-300 hover:border-white/[0.12]'
                )}>
                {p.label}
              </button>
            ))}
          </div>
          {selectedPreset === CRON_PRESETS.length - 1 && (
            <input type="text" placeholder="e.g. 0 6 * * *"
              value={customCron} onChange={e => setCustomCron(e.target.value)}
              className={INPUT + ' mt-2'} />
          )}
          {cron && <p className="mt-1 text-[10px] text-slate-600 font-mono">cron: {cron}</p>}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={LABEL}>Label (optional)</label>
            <input type="text" placeholder="Daily security scan" value={label}
              onChange={e => setLabel(e.target.value)} className={INPUT} />
          </div>
          <div>
            <label className={LABEL}>Timezone</label>
            <select value={timezone} onChange={e => setTimezone(e.target.value)} className={SELECT_CLS}>
              <option value="UTC">UTC</option>
              <option value="Africa/Johannesburg">SAST (UTC+2)</option>
              <option value="America/New_York">EST</option>
              <option value="America/Los_Angeles">PST</option>
              <option value="Europe/London">GMT</option>
              <option value="Asia/Dubai">GST (UTC+4)</option>
            </select>
          </div>
        </div>

        {error && <p className="text-[11px] text-rose-400 font-mono">{error}</p>}

        <div className="flex gap-3 pt-1">
          <button type="button" onClick={onClose}
            className="flex-1 py-2.5 rounded-xl text-[12px] font-semibold border border-white/[0.08] text-slate-400 hover:text-slate-200 transition-all">
            Cancel
          </button>
          <button type="button" onClick={handleCreate} disabled={loading}
            className="flex-1 py-2.5 rounded-xl text-[12px] font-semibold bg-indigo-500 hover:bg-indigo-600 text-white transition-all disabled:opacity-50 flex items-center justify-center gap-2">
            {loading
              ? <><RefreshCw size={12} className="animate-spin" /> Creating…</>
              : 'Create schedule'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────
export const ReportsPage: React.FC = () => {
  const { currentSessionId, sessionData } = useSessionStore()
  const [schedules,    setSchedules]    = useState<Schedule[]>([])
  const [showModal,    setShowModal]    = useState(false)
  const [emailTo,      setEmailTo]      = useState('')
  const [emailSending, setEmailSending] = useState(false)
  const [emailStatus,  setEmailStatus]  = useState<{ ok: boolean; msg: string } | null>(null)
  const [downloading,  setDownloading]  = useState(false)

  const fetchSchedules = async () => {
    try {
      const res = await reportsService.listSchedules()
      setSchedules((res.data as any).data?.schedules || [])
    } catch {}
  }

  useEffect(() => { fetchSchedules() }, [])

  const handleDownload = async () => {
    if (!currentSessionId) return
    setDownloading(true)
    try {
      const res = await reportsService.downloadPdf(currentSessionId)
      const blob = new Blob([res.data as any], { type: 'application/pdf' })
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href = url
      a.download = `codeviz-report-${currentSessionId}.pdf`
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (e) {
      console.error('Download failed:', e)
    } finally { setDownloading(false) }
  }

  const handleEmail = async () => {
    if (!currentSessionId || !emailTo) return
    setEmailSending(true); setEmailStatus(null)
    try {
      await reportsService.emailReport(currentSessionId, emailTo)
      setEmailStatus({ ok: true, msg: `Report sent to ${emailTo}` })
    } catch (e: any) {
      setEmailStatus({ ok: false, msg: e?.response?.data?.message || 'Failed to send email' })
    } finally { setEmailSending(false) }
  }

  const handleDelete = async (id: string) => {
    await reportsService.deleteSchedule(id)
    fetchSchedules()
  }

  const handleRunNow = async (id: string) => {
    await reportsService.runNow(id)
    setTimeout(fetchSchedules, 2000)
  }

  const repoPath = (sessionData as any)?.repo_path || ''

  return (
    <div className="space-y-5 animate-fade-in pb-10 select-none">

      {showModal && (
        <ScheduleModal repoPath={repoPath} onClose={() => setShowModal(false)} onCreated={fetchSchedules} />
      )}

      {/* Page header */}
      <div className="pt-1">
        <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Reports</h1>
        <p className="text-slate-500 text-[13px] mt-1.5">On-demand PDF export and recurring scheduled delivery.</p>
      </div>

      {/* On-demand row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Download PDF */}
        <div className={`${CARD} p-6`}>
          <SectionHeader icon={FileDown} title="Download PDF" accent="#6366f1"
            desc="Full report — compliance, risk score, scan summary." />

          {!currentSessionId ? (
            <div className="text-center py-6 space-y-3">
              <Terminal size={24} className="mx-auto text-slate-700" />
              <p className="text-slate-500 text-[13px]">No active scan session.</p>
              <Link to="/scanner"
                className="text-[12px] text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors">
                Go to Scanner →
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-[11px] text-slate-600 font-mono">
                Session: <span className="text-indigo-400">{currentSessionId}</span>
              </p>
              <button onClick={handleDownload} disabled={downloading}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-[13px] font-semibold bg-indigo-500 hover:bg-indigo-600 text-white transition-all disabled:opacity-50 shadow-sm shadow-indigo-500/25">
                {downloading
                  ? <><RefreshCw size={13} className="animate-spin" /> Generating…</>
                  : <><FileDown size={13} /> Download Report PDF</>}
              </button>
              <a href={reportsService.previewUrl(currentSessionId)} target="_blank" rel="noopener noreferrer"
                className="flex items-center justify-center gap-1.5 text-[11px] text-indigo-400 hover:text-indigo-300 transition-colors">
                <ExternalLink size={11} /> Preview in browser
              </a>
            </div>
          )}
        </div>

        {/* Email report */}
        <div className={`${CARD} p-6`}>
          <SectionHeader icon={Mail} title="Email report now" accent="#22c55e"
            desc="Send HTML + PDF attachment via Gmail." />

          <div className="space-y-3">
            <div>
              <label className={LABEL}>Recipient</label>
              <input type="email" placeholder="recipient@company.com"
                value={emailTo} onChange={e => setEmailTo(e.target.value)}
                disabled={!currentSessionId} className={INPUT} />
            </div>
            <button onClick={handleEmail} disabled={!currentSessionId || !emailTo || emailSending}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-[13px] font-semibold border border-emerald-500/30 bg-emerald-500/[0.08] text-emerald-300 hover:bg-emerald-500/[0.15] transition-all disabled:opacity-40">
              {emailSending
                ? <><RefreshCw size={13} className="animate-spin" /> Sending…</>
                : <><Mail size={13} /> Send report</>}
            </button>

            {emailStatus && (
              <div className={clsx(
                'flex items-center gap-2 text-[11px] px-3 py-2 rounded-xl border font-mono',
                emailStatus.ok
                  ? 'bg-emerald-500/[0.07] border-emerald-500/20 text-emerald-400'
                  : 'bg-rose-500/[0.07] border-rose-500/20 text-rose-400'
              )}>
                {emailStatus.ok ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                {emailStatus.msg}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Scheduled reports */}
      <div className={`${CARD} p-6`}>
        <div className="flex items-start justify-between pb-5 mb-5 border-b border-white/[0.05]">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl border border-white/[0.06] bg-slate-elevated shrink-0 mt-0.5">
              <Clock size={15} className="text-amber-400" />
            </div>
            <div>
              <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Scheduled reports</h2>
              <p className="text-[12px] text-slate-500 mt-0.5">Auto-scan and email on a recurring schedule.</p>
            </div>
          </div>
          <button onClick={() => setShowModal(true)} disabled={!repoPath}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/[0.14] transition-all disabled:opacity-40">
            <Plus size={13} /> New schedule
          </button>
        </div>

        {!repoPath && (
          <p className="text-slate-600 text-[12px] italic text-center py-4">
            Run a scan first to enable scheduled reports.
          </p>
        )}

        {schedules.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-white/[0.05] rounded-xl">
            <Clock size={24} className="mx-auto text-slate-700 mb-2" />
            <p className="text-slate-600 text-[12px]">No schedules configured yet.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {schedules.map(s => (
              <div key={s.id}
                className="flex items-center gap-4 p-4 bg-slate-elevated/60 border border-white/[0.06] rounded-xl">
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-semibold text-slate-200 truncate">
                    {s.label || 'Untitled schedule'}
                  </p>
                  <p className="text-[11px] text-slate-600 font-mono mt-0.5 truncate">{s.repo_path}</p>
                  <div className="flex gap-2 mt-1.5 flex-wrap">
                    <span className="text-[10px] text-indigo-400 font-mono bg-indigo-500/[0.08] border border-indigo-500/20 px-2 py-0.5 rounded">
                      {s.cron}
                    </span>
                    <span className="text-[10px] text-slate-600 font-mono">{s.timezone}</span>
                    <span className="text-[10px] text-slate-500 font-mono">{s.email}</span>
                  </div>
                </div>

                <div className="text-right space-y-1 shrink-0">
                  <StatusPill status={s.last_status} />
                  {s.last_run && (
                    <p className="text-[10px] text-slate-700 font-mono">
                      {new Date(s.last_run).toLocaleString()}
                    </p>
                  )}
                </div>

                <div className="flex gap-2 shrink-0">
                  <button onClick={() => handleRunNow(s.id)} title="Run now"
                    className="p-2 rounded-lg border border-white/[0.07] text-slate-600 hover:text-emerald-400 hover:border-emerald-500/20 hover:bg-emerald-500/[0.07] transition-all">
                    <Play size={12} />
                  </button>
                  <button onClick={() => handleDelete(s.id)} title="Delete schedule"
                    className="p-2 rounded-lg border border-white/[0.07] text-slate-600 hover:text-rose-400 hover:border-rose-500/20 hover:bg-rose-500/[0.07] transition-all">
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  )
}
