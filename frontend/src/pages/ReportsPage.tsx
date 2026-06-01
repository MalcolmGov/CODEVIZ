import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { useSessionStore } from '@/store/sessionStore'
import { reportsService, Schedule } from '@/services/reports'
import {
  FileDown, Mail, Clock, Trash2, Play, Terminal, RefreshCw,
  CheckCircle2, XCircle, AlertTriangle, Plus
} from 'lucide-react'
import clsx from 'clsx'

const CRON_PRESETS = [
  { label: 'Daily at 6am',   cron: '0 6 * * *' },
  { label: 'Daily at 9am',   cron: '0 9 * * *' },
  { label: 'Weekly (Mon 8am)', cron: '0 8 * * 1' },
  { label: 'Every 12 hours', cron: '0 */12 * * *' },
  { label: 'Custom…',        cron: '' },
]

function StatusPill({ status }: { status: string | null }) {
  if (!status) return <span className="text-slate-600 text-xs font-mono">Never run</span>
  const isSuccess = status === 'success'
  const isError = status.startsWith('error') || status.startsWith('failed')
  return (
    <span className={clsx(
      'text-xs font-mono px-2 py-0.5 rounded border',
      isSuccess ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
      isError   ? 'text-rose-400 bg-rose-500/10 border-rose-500/20' :
                  'text-amber-400 bg-amber-500/10 border-amber-500/20'
    )}>
      {isSuccess ? '✓ Success' : isError ? '✗ ' + status.slice(0, 40) : status}
    </span>
  )
}

function ScheduleModal({
  repoPath, onClose, onCreated
}: { repoPath: string; onClose: () => void; onCreated: () => void }) {
  const [email, setEmail] = useState('')
  const [selectedPreset, setSelectedPreset] = useState(0)
  const [customCron, setCustomCron] = useState('')
  const [label, setLabel] = useState('')
  const [timezone, setTimezone] = useState('UTC')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const cron = CRON_PRESETS[selectedPreset].cron || customCron

  const handleCreate = async () => {
    if (!email || !cron) { setError('Email and schedule are required'); return }
    setLoading(true)
    setError(null)
    try {
      await reportsService.createSchedule({ repo_path: repoPath, email, cron, label, timezone })
      onCreated()
      onClose()
    } catch (e: any) {
      setError(e?.response?.data?.message || 'Failed to create schedule')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-slate-surface border-slate-border/60 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-slate-100 font-display text-lg">Schedule Report</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 text-xl">×</button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Repository
            </label>
            <div className="font-mono text-xs text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-lg px-3 py-2">
              {repoPath}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Email Recipient
            </label>
            <input
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full bg-slate-950/60 border border-slate-border/50 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Frequency
            </label>
            <div className="grid grid-cols-2 gap-2">
              {CRON_PRESETS.map((p, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedPreset(i)}
                  className={clsx(
                    'px-3 py-2 rounded-lg text-xs font-medium border transition-all text-left',
                    selectedPreset === i
                      ? 'bg-indigo-500/15 border-indigo-500/40 text-indigo-300'
                      : 'bg-slate-950/40 border-slate-border/40 text-slate-400 hover:border-slate-border/70'
                  )}
                >
                  {p.label}
                </button>
              ))}
            </div>
            {selectedPreset === CRON_PRESETS.length - 1 && (
              <input
                type="text"
                placeholder="cron expression e.g. 0 6 * * *"
                value={customCron}
                onChange={e => setCustomCron(e.target.value)}
                className="mt-2 w-full bg-slate-950/60 border border-slate-border/50 rounded-lg px-3 py-2 text-slate-100 text-sm font-mono placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
              />
            )}
            {cron && (
              <p className="mt-1 text-[10px] text-slate-500 font-mono">Cron: {cron}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                Label (optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Daily security scan"
                value={label}
                onChange={e => setLabel(e.target.value)}
                className="w-full bg-slate-950/60 border border-slate-border/50 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                Timezone
              </label>
              <select
                value={timezone}
                onChange={e => setTimezone(e.target.value)}
                className="w-full bg-slate-950/60 border border-slate-border/50 rounded-lg px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-indigo-500/50"
              >
                <option value="UTC">UTC</option>
                <option value="Africa/Johannesburg">SAST (UTC+2)</option>
                <option value="America/New_York">EST</option>
                <option value="America/Los_Angeles">PST</option>
                <option value="Europe/London">GMT</option>
                <option value="Asia/Dubai">GST (UTC+4)</option>
              </select>
            </div>
          </div>
        </div>

        {error && (
          <p className="text-xs text-rose-400 font-mono">{error}</p>
        )}

        <div className="flex gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} className="flex-1">Cancel</Button>
          <Button onClick={handleCreate} loading={loading} className="flex-1">
            Create Schedule
          </Button>
        </div>
      </Card>
    </div>
  )
}

export const ReportsPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentSessionId, sessionData } = useSessionStore()
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [showModal, setShowModal] = useState(false)
  const [emailTo, setEmailTo] = useState('')
  const [emailSending, setEmailSending] = useState(false)
  const [emailStatus, setEmailStatus] = useState<{ ok: boolean; msg: string } | null>(null)
  const [downloading, setDownloading] = useState(false)

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
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `codeviz-report-${currentSessionId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Download failed:', e)
    } finally {
      setDownloading(false)
    }
  }

  const handleEmail = async () => {
    if (!currentSessionId || !emailTo) return
    setEmailSending(true)
    setEmailStatus(null)
    try {
      await reportsService.emailReport(currentSessionId, emailTo)
      setEmailStatus({ ok: true, msg: `Report sent to ${emailTo}` })
    } catch (e: any) {
      setEmailStatus({ ok: false, msg: e?.response?.data?.message || 'Failed to send email' })
    } finally {
      setEmailSending(false)
    }
  }

  const handleDelete = async (id: string) => {
    await reportsService.deleteSchedule(id)
    fetchSchedules()
  }

  const handleRunNow = async (id: string) => {
    await reportsService.runNow(id)
    setTimeout(fetchSchedules, 2000)
  }

  const repoPath = sessionData?.repo_path || ''

  return (
    <div className="space-y-6 select-none animate-fade-in">
      {showModal && (
        <ScheduleModal
          repoPath={repoPath}
          onClose={() => setShowModal(false)}
          onCreated={fetchSchedules}
        />
      )}

      <div>
        <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">Reports</h1>
        <p className="text-slate-400 text-sm mt-1">On-demand PDF reports and recurring scheduled delivery.</p>
      </div>

      {/* On-demand section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Download PDF */}
        <Card className="bg-slate-surface/30 border-slate-border/40 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
              <FileDown size={20} className="text-indigo-400" />
            </div>
            <div>
              <h2 className="font-bold text-slate-100 font-display">Download PDF</h2>
              <p className="text-slate-500 text-xs">Full report — compliance, risk, scan summary</p>
            </div>
          </div>

          {!currentSessionId ? (
            <div className="text-center py-6 space-y-2">
              <Terminal size={28} className="mx-auto text-slate-600" />
              <p className="text-slate-500 text-xs">No active scan. Run a scan first.</p>
              <Button size="sm" variant="secondary" onClick={() => navigate('/scanner')}>Go to Scanner</Button>
            </div>
          ) : (
            <>
              <p className="text-xs text-slate-400 font-mono">
                Session: <span className="text-indigo-400">{currentSessionId}</span>
              </p>
              <Button
                onClick={handleDownload}
                loading={downloading}
                className="w-full flex items-center justify-center gap-2"
              >
                <FileDown size={15} />
                {downloading ? 'Generating PDF…' : 'Download Report PDF'}
              </Button>
              <a
                href={reportsService.previewUrl(currentSessionId)}
                target="_blank"
                rel="noopener noreferrer"
                className="block text-center text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                Preview in browser →
              </a>
            </>
          )}
        </Card>

        {/* Email report */}
        <Card className="bg-slate-surface/30 border-slate-border/40 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
              <Mail size={20} className="text-emerald-400" />
            </div>
            <div>
              <h2 className="font-bold text-slate-100 font-display">Email Report Now</h2>
              <p className="text-slate-500 text-xs">Send HTML + PDF attachment via Gmail</p>
            </div>
          </div>

          <div className="space-y-3">
            <input
              type="email"
              placeholder="recipient@company.com"
              value={emailTo}
              onChange={e => setEmailTo(e.target.value)}
              disabled={!currentSessionId}
              className="w-full bg-slate-950/60 border border-slate-border/50 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 disabled:opacity-40"
            />
            <Button
              onClick={handleEmail}
              loading={emailSending}
              disabled={!currentSessionId || !emailTo}
              variant="secondary"
              className="w-full border-emerald-500/30 hover:bg-emerald-500/10 hover:text-emerald-300"
            >
              <Mail size={14} className="mr-2" />
              {emailSending ? 'Sending…' : 'Send Report'}
            </Button>

            {emailStatus && (
              <div className={clsx(
                'flex items-center gap-2 text-xs px-3 py-2 rounded-lg border font-mono',
                emailStatus.ok
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                  : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
              )}>
                {emailStatus.ok ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
                {emailStatus.msg}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Scheduled reports */}
      <Card className="bg-slate-surface/30 border-slate-border/40 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20">
              <Clock size={20} className="text-amber-400" />
            </div>
            <div>
              <h2 className="font-bold text-slate-100 font-display">Scheduled Reports</h2>
              <p className="text-slate-500 text-xs">Auto-scan and email on a recurring schedule</p>
            </div>
          </div>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setShowModal(true)}
            disabled={!repoPath}
            className="flex items-center gap-2"
          >
            <Plus size={14} />
            New Schedule
          </Button>
        </div>

        {!repoPath && (
          <p className="text-slate-500 text-xs italic text-center py-4">
            Run a scan first to enable scheduled reports.
          </p>
        )}

        {schedules.length === 0 ? (
          <div className="text-center py-8 border border-dashed border-slate-border/30 rounded-xl">
            <Clock size={28} className="mx-auto text-slate-600 mb-2" />
            <p className="text-slate-500 text-xs">No schedules configured yet.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {schedules.map(s => (
              <div
                key={s.id}
                className="flex items-center gap-4 p-4 bg-slate-950/40 border border-slate-border/30 rounded-xl"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-200 truncate">{s.label}</p>
                  <p className="text-xs text-slate-500 font-mono mt-0.5 truncate">{s.repo_path}</p>
                  <div className="flex gap-3 mt-1.5 flex-wrap">
                    <span className="text-[10px] text-indigo-400 font-mono bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded">
                      {s.cron}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">{s.timezone}</span>
                    <span className="text-[10px] text-slate-400 font-mono">{s.email}</span>
                  </div>
                </div>

                <div className="text-right space-y-1.5 shrink-0">
                  <StatusPill status={s.last_status} />
                  {s.last_run && (
                    <p className="text-[10px] text-slate-600 font-mono">
                      Last: {new Date(s.last_run).toLocaleString()}
                    </p>
                  )}
                </div>

                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => handleRunNow(s.id)}
                    className="p-2 rounded-lg bg-slate-900 border border-slate-border/40 text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/20 transition-all"
                    title="Run now"
                  >
                    <Play size={13} />
                  </button>
                  <button
                    onClick={() => handleDelete(s.id)}
                    className="p-2 rounded-lg bg-slate-900 border border-slate-border/40 text-slate-500 hover:bg-rose-500/10 hover:text-rose-400 hover:border-rose-500/20 transition-all"
                    title="Delete schedule"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Gmail setup note */}
      <Card className="bg-amber-500/5 border-amber-500/20 space-y-2">
        <div className="flex items-start gap-3">
          <AlertTriangle size={15} className="text-amber-400 mt-0.5 shrink-0" />
          <div>
            <p className="text-xs font-semibold text-amber-400">Gmail App Password Required</p>
            <p className="text-xs text-slate-400 mt-1">
              Email delivery uses <span className="font-mono text-slate-300">GMAIL_ADDRESS</span> and <span className="font-mono text-slate-300">GMAIL_PASSWORD</span> from your <span className="font-mono text-slate-300">.env</span>.
              Gmail requires an <strong className="text-slate-200">App Password</strong> (not your account password).
              Generate one at: Gmail → Settings → Security → 2-Step Verification → App Passwords.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
