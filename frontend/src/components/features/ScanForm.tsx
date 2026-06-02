import React, { useState, useEffect, useMemo } from 'react'
import { Button } from '@/components/common/Button'
import { useSessionStore } from '@/store/sessionStore'
import { chatService } from '@/services/chat'
import { repositoriesService, GitHubRepository } from '@/services/repositories'
import { reportsService, Schedule } from '@/services/reports'
import { authService } from '@/services/auth'
import { historyService } from '@/services/history'
import { notificationsService } from '@/services/apis'
import { useSettingsStore } from '@/store/settingsStore'
import {
  Search, CheckSquare, Square, Clock, Zap, Calendar,
  Mail, Trash2, Play, Plus, ChevronDown, Globe, Lock,
  RefreshCw, CheckCircle2, XCircle, Github,
} from 'lucide-react'
import clsx from 'clsx'

const FREQUENCIES = [
  { id: 'daily',   label: 'Daily',   desc: 'Every day' },
  { id: 'weekly',  label: 'Weekly',  desc: 'Every Monday' },
  { id: 'monthly', label: 'Monthly', desc: '1st of month' },
]

const HOURS = Array.from({ length: 24 }, (_, i) => ({
  value: i,
  label: `${String(i).padStart(2, '0')}:00`,
}))

const TIMEZONES = [
  { value: 'UTC',                    label: 'UTC' },
  { value: 'Africa/Johannesburg',    label: 'SAST (UTC+2)' },
  { value: 'America/New_York',       label: 'EST (UTC-5)' },
  { value: 'America/Los_Angeles',    label: 'PST (UTC-8)' },
  { value: 'Europe/London',          label: 'GMT (UTC+0)' },
  { value: 'Europe/Paris',           label: 'CET (UTC+1)' },
  { value: 'Asia/Dubai',             label: 'GST (UTC+4)' },
  { value: 'Asia/Singapore',         label: 'SGT (UTC+8)' },
]

function StatusPill({ status }: { status: string | null }) {
  if (!status) return <span className="text-slate-600 text-[10px] font-mono">Never run</span>
  const ok = status === 'success'
  const err = status.startsWith('error') || status.startsWith('partial')
  return (
    <span className={clsx(
      'text-[10px] font-mono px-1.5 py-0.5 rounded border',
      ok  ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
      err ? 'text-rose-400 bg-rose-500/10 border-rose-500/20' :
            'text-amber-400 bg-amber-500/10 border-amber-500/20'
    )}>
      {ok ? '✓ OK' : err ? '✗ ' + status.slice(0, 30) : status}
    </span>
  )
}

export const ScanForm: React.FC<{ onScanComplete: (sessionId: string) => void }> = ({ onScanComplete }) => {
  const { createSession } = useSessionStore()
  const slackSettings = useSettingsStore(s => ({
    enabled: s.enableSlackNotifications,
    webhook: s.slackWebhook,
  }))

  // Shared state
  const REPO_CACHE_KEY = 'codeviz_cached_repos'

  // Built-in fallback — always visible even with backend offline + empty cache.
  // Update this list to match your real repos.
  const DEFAULT_REPOS: GitHubRepository[] = [
    { id: '101', name: 'CODEVIZ',         full_name: 'MalcolmGov/CODEVIZ',         url: 'https://github.com/MalcolmGov/CODEVIZ',         clone_url: 'https://github.com/MalcolmGov/CODEVIZ.git',         description: 'AI-Powered Code Analysis Platform', private: false, branch: 'main', local_path: '/Users/malcolmgovender/codeviz-proper' },
    { id: '102', name: 'coastal-clean',   full_name: 'MalcolmGov/coastal-clean',   url: 'https://github.com/MalcolmGov/coastal-clean',   clone_url: 'https://github.com/MalcolmGov/coastal-clean.git',   description: 'Coastal environmental data monitor', private: true,  branch: 'main' },
    { id: '103', name: 'SwifterWallet',   full_name: 'MalcolmGov/SwifterWallet',   url: 'https://github.com/MalcolmGov/SwifterWallet',   clone_url: 'https://github.com/MalcolmGov/SwifterWallet.git',   description: 'iOS Swift finance wallet',           private: false, branch: 'main' },
    { id: '104', name: 'intelligencehub', full_name: 'MalcolmGov/intelligencehub', url: 'https://github.com/MalcolmGov/intelligencehub', clone_url: 'https://github.com/MalcolmGov/intelligencehub.git', description: 'AI models hosting aggregator',       private: true,  branch: 'main' },
  ]

  const saveRepoCache = (list: GitHubRepository[]) => {
    try { localStorage.setItem(REPO_CACHE_KEY, JSON.stringify(list)) } catch {}
  }
  const loadRepoCache = (): GitHubRepository[] => {
    try {
      const stored = JSON.parse(localStorage.getItem(REPO_CACHE_KEY) || '[]')
      return stored.length > 0 ? stored : DEFAULT_REPOS
    } catch { return DEFAULT_REPOS }
  }

  const [repos, setRepos] = useState<GitHubRepository[]>(() => loadRepoCache())
  const [loadingRepos, setLoadingRepos] = useState(true)
  const [usingCache, setUsingCache] = useState(false)
  const [mode, setMode] = useState<'scan' | 'schedule'>('scan')
  const [error, setError] = useState<string>()

  // Scan Now state
  const [selectedScanRepo, setSelectedScanRepo] = useState<string>('')
  const [scanning, setScanning] = useState(false)

  // Schedule state
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRepoIds, setSelectedRepoIds] = useState<Set<string>>(new Set())
  const [frequency, setFrequency] = useState('daily')
  const [hour, setHour] = useState(6)
  const [timezone, setTimezone] = useState('UTC')
  const [recipients, setRecipients] = useState([''])
  const [scheduleLabel, setScheduleLabel] = useState('')
  const [creating, setCreating] = useState(false)
  const [scheduleSuccess, setScheduleSuccess] = useState(false)

  // Schedules list
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [runningId, setRunningId] = useState<string | null>(null)

  // Load repos + schedules on mount
  useEffect(() => {
    // Pre-populate from cache immediately so the dropdown is never blank
    const cached = loadRepoCache()
    if (cached.length > 0) {
      setRepos(cached)
      setSelectedScanRepo(prev => prev || cached[0].id)
    }

    repositoriesService.listGitHubRepos()
      .then(res => {
        const list = res.data.data?.repositories || []
        if (list.length > 0) {
          setRepos(list)
          saveRepoCache(list)
          setSelectedScanRepo(prev => prev || list[0].id)
          setUsingCache(false)
        } else if (cached.length > 0) {
          setUsingCache(true)
        }
      })
      .catch(() => {
        // Backend offline — repos already pre-loaded from cache or defaults
        setUsingCache(true)
      })
      .finally(() => setLoadingRepos(false))
    fetchSchedules()
  }, [])

  const fetchSchedules = () => {
    reportsService.listSchedules()
      .then(res => setSchedules((res.data as any).data?.schedules || []))
      .catch(() => {})
  }

  // Filtered repos for schedule mode
  const filteredRepos = useMemo(() =>
    repos.filter(r =>
      r.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.description || '').toLowerCase().includes(searchQuery.toLowerCase())
    ), [repos, searchQuery])

  const allSelected = filteredRepos.length > 0 && filteredRepos.every(r => selectedRepoIds.has(r.id))

  const toggleRepo = (id: string) => {
    setSelectedRepoIds(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const toggleAll = () => {
    if (allSelected) {
      setSelectedRepoIds(new Set())
    } else {
      setSelectedRepoIds(new Set(filteredRepos.map(r => r.id)))
    }
  }

  // Scan Now handler
  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedScanRepo) { setError('Select a repository to scan'); return }
    const repo = repos.find(r => r.id === selectedScanRepo)
    if (!repo) { setError('Repository not found'); return }
    setScanning(true)
    setError(undefined)
    try {
      const path = (repo as any).local_path || repo.clone_url
      const sessionId = await createSession(path)
      await chatService.scan(sessionId)
      // Persist scan history (fire-and-forget)
      historyService.record(sessionId, {
        repo_full_name: repo.full_name,
      }).catch(() => {})

      // Auto Slack alert if enabled and webhook is configured
      if (slackSettings.enabled && slackSettings.webhook) {
        notificationsService.slackAlert(sessionId, slackSettings.webhook)
          .catch(() => {}) // non-critical
      }

      onScanComplete(sessionId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed')
    } finally {
      setScanning(false)
    }
  }

  // Create schedule handler
  const handleCreateSchedule = async () => {
    const selectedPaths = repos
      .filter(r => selectedRepoIds.has(r.id))
      .map(r => (r as any).local_path || r.clone_url)
    const validRecipients = recipients.filter(e => e.trim())

    if (selectedPaths.length === 0) { setError('Select at least one repository'); return }
    if (validRecipients.length === 0) { setError('Add at least one email recipient'); return }

    setCreating(true)
    setError(undefined)
    try {
      await reportsService.createSchedule({
        repo_paths: selectedPaths,
        recipients: validRecipients,
        frequency,
        hour,
        label: scheduleLabel || `Auto-scan (${frequency})`,
        timezone,
      } as any)
      setScheduleSuccess(true)
      setSelectedRepoIds(new Set())
      setRecipients([''])
      setScheduleLabel('')
      fetchSchedules()
      setTimeout(() => setScheduleSuccess(false), 3000)
    } catch (e: any) {
      setError(e?.response?.data?.message || 'Failed to create schedule')
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteSchedule = async (id: string) => {
    await reportsService.deleteSchedule(id)
    fetchSchedules()
  }

  const handleRunNow = async (id: string) => {
    setRunningId(id)
    try {
      await reportsService.runNow(id)
      setTimeout(fetchSchedules, 2000)
    } finally {
      setRunningId(null)
    }
  }

  const inputCls = 'w-full bg-slate-950/60 border border-slate-border/50 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all'
  const labelCls = 'text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5'

  return (
    <div className="space-y-6">
      {/* Mode toggle */}
      <div className="flex gap-1 p-1 bg-slate-950/60 border border-slate-border/40 rounded-xl w-fit">
        <button
          onClick={() => { setMode('scan'); setError(undefined) }}
          className={clsx(
            'flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200',
            mode === 'scan'
              ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/20'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Zap size={15} />
          Scan Now
        </button>
        <button
          onClick={() => { setMode('schedule'); setError(undefined) }}
          className={clsx(
            'flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200',
            mode === 'schedule'
              ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/20'
              : 'text-slate-400 hover:text-slate-200'
          )}
        >
          <Calendar size={15} />
          Schedule Automation
        </button>
      </div>

      {/* ── SCAN NOW ── */}
      {mode === 'scan' && (
        <form onSubmit={handleScan} className="space-y-4">
          <div>
            <label className={labelCls}>Select Repository</label>
            {loadingRepos ? (
              <div className="flex items-center gap-2 text-slate-500 text-sm py-2">
                <RefreshCw size={14} className="animate-spin" /> Loading repos…
              </div>
            ) : repos.length === 0 ? (
              <div className="flex items-center gap-3 py-2">
                <select value="custom" onChange={() => {}} className={inputCls}>
                  <option value="custom">📁 Custom path / URL…</option>
                </select>
                <button
                  type="button"
                  onClick={() => {
                    setLoadingRepos(true)
                    setError(undefined)
                    repositoriesService.listGitHubRepos()
                      .then(res => {
                        const list = res.data.data?.repositories || []
                        setRepos(list)
                        if (list.length > 0) setSelectedScanRepo(list[0].id)
                      })
                      .catch((err) => {
                        const msg = err?.response?.data?.message || err?.message || 'Failed to load repositories'
                        setError(`Repos: ${msg}`)
                      })
                      .finally(() => setLoadingRepos(false))
                  }}
                  className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 border border-indigo-500/30 rounded-lg px-3 py-2 transition-colors whitespace-nowrap"
                >
                  <RefreshCw size={12} /> Retry
                </button>
              </div>
            ) : (
              <div className="space-y-1.5">
                <select
                  value={selectedScanRepo}
                  onChange={e => setSelectedScanRepo(e.target.value)}
                  className={inputCls}
                >
                  {repos.map(r => (
                    <option key={r.id} value={r.id}>
                      {r.full_name} ({r.private ? '🔒 Private' : '🌐 Public'})
                    </option>
                  ))}
                  <option value="custom">📁 Custom path / URL…</option>
                </select>
                {usingCache && (
                  <div className="flex items-center justify-between gap-3 px-3 py-2 rounded-lg bg-amber-500/[0.07] border border-amber-500/20">
                    <p className="text-[11px] text-amber-400/80 font-mono">
                      ⚡ Showing cached repos — backend offline
                    </p>
                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          const res = await authService.getGitHubLoginUrl()
                          const url = res.data.data?.auth_url
                          if (url) window.location.href = url
                        } catch {
                          /* backend still down, do nothing */
                        }
                      }}
                      className="flex items-center gap-1.5 text-[11px] font-semibold text-amber-300 hover:text-white whitespace-nowrap transition-colors"
                    >
                      <Github size={11} /> Re-authorize
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {selectedScanRepo === 'custom' && (
            <div>
              <label className={labelCls}>Repository Path or URL</label>
              <input
                type="text"
                placeholder="/path/to/local/repo or https://github.com/user/repo"
                className={inputCls}
              />
            </div>
          )}

          {error && <p className="text-rose-400 text-xs font-mono">{error}</p>}

          <Button type="submit" loading={scanning} size="lg" className="w-full sm:w-auto">
            🚀 Scan Repository
          </Button>
        </form>
      )}

      {/* ── SCHEDULE AUTOMATION ── */}
      {mode === 'schedule' && (
        <div className="space-y-6">
          {/* Repo selection */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className={labelCls}>Select Repositories</label>
              <span className="text-xs text-slate-500 font-mono">
                {selectedRepoIds.size} of {repos.length} selected
              </span>
            </div>

            {/* Search */}
            <div className="relative mb-3">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
              <input
                type="text"
                placeholder="Search repositories…"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className={clsx(inputCls, 'pl-9')}
              />
            </div>

            {/* Select all row */}
            <button
              onClick={toggleAll}
              className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg bg-slate-950/40 border border-slate-border/30 hover:border-indigo-500/30 mb-2 transition-all"
            >
              {allSelected
                ? <CheckSquare size={16} className="text-indigo-400 shrink-0" />
                : <Square size={16} className="text-slate-500 shrink-0" />}
              <span className="text-sm font-semibold text-slate-300">
                {allSelected ? 'Deselect all' : `Select all (${filteredRepos.length})`}
              </span>
            </button>

            {/* Repo list */}
            <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
              {loadingRepos ? (
                <div className="flex items-center gap-2 text-slate-500 text-sm py-4 justify-center">
                  <RefreshCw size={14} className="animate-spin" /> Loading…
                </div>
              ) : filteredRepos.map(repo => {
                const checked = selectedRepoIds.has(repo.id)
                return (
                  <button
                    key={repo.id}
                    onClick={() => toggleRepo(repo.id)}
                    className={clsx(
                      'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg border text-left transition-all duration-150',
                      checked
                        ? 'bg-indigo-500/10 border-indigo-500/30'
                        : 'bg-slate-950/30 border-slate-border/30 hover:border-slate-border/60'
                    )}
                  >
                    {checked
                      ? <CheckSquare size={15} className="text-indigo-400 shrink-0" />
                      : <Square size={15} className="text-slate-600 shrink-0" />}
                    <div className="flex-1 min-w-0">
                      <p className={clsx('text-sm font-medium truncate', checked ? 'text-indigo-300' : 'text-slate-300')}>
                        {repo.full_name}
                      </p>
                      {repo.description && (
                        <p className="text-[10px] text-slate-500 truncate mt-0.5">{repo.description}</p>
                      )}
                    </div>
                    <span className="shrink-0">
                      {repo.private
                        ? <Lock size={11} className="text-slate-600" />
                        : <Globe size={11} className="text-slate-600" />}
                    </span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Frequency + time */}
          <div>
            <label className={labelCls}>Scan Frequency</label>
            <div className="grid grid-cols-3 gap-2 mb-3">
              {FREQUENCIES.map(f => (
                <button
                  key={f.id}
                  onClick={() => setFrequency(f.id)}
                  className={clsx(
                    'px-3 py-3 rounded-xl border text-left transition-all duration-150',
                    frequency === f.id
                      ? 'bg-indigo-500/15 border-indigo-500/40'
                      : 'bg-slate-950/40 border-slate-border/30 hover:border-slate-border/60'
                  )}
                >
                  <p className={clsx('text-sm font-bold', frequency === f.id ? 'text-indigo-300' : 'text-slate-300')}>
                    {f.label}
                  </p>
                  <p className="text-[10px] text-slate-500 mt-0.5">{f.desc}</p>
                </button>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelCls}>Time</label>
                <select
                  value={hour}
                  onChange={e => setHour(Number(e.target.value))}
                  className={inputCls}
                >
                  {HOURS.map(h => (
                    <option key={h.value} value={h.value}>{h.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className={labelCls}>Timezone</label>
                <select
                  value={timezone}
                  onChange={e => setTimezone(e.target.value)}
                  className={inputCls}
                >
                  {TIMEZONES.map(tz => (
                    <option key={tz.value} value={tz.value}>{tz.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Email recipients */}
          <div>
            <label className={labelCls}>Email Report To</label>
            <div className="space-y-2">
              {recipients.map((email, i) => (
                <div key={i} className="flex gap-2">
                  <div className="relative flex-1">
                    <Mail size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
                    <input
                      type="email"
                      placeholder="recipient@company.com"
                      value={email}
                      onChange={e => {
                        const next = [...recipients]
                        next[i] = e.target.value
                        setRecipients(next)
                      }}
                      className={clsx(inputCls, 'pl-8')}
                    />
                  </div>
                  {recipients.length > 1 && (
                    <button
                      onClick={() => setRecipients(recipients.filter((_, j) => j !== i))}
                      className="p-2 text-slate-600 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => setRecipients([...recipients, ''])}
                className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
              >
                <Plus size={13} /> Add recipient
              </button>
            </div>
          </div>

          {/* Label */}
          <div>
            <label className={labelCls}>Schedule Name <span className="text-slate-600 normal-case font-normal">(optional)</span></label>
            <input
              type="text"
              placeholder={`${frequency.charAt(0).toUpperCase() + frequency.slice(1)} security scan`}
              value={scheduleLabel}
              onChange={e => setScheduleLabel(e.target.value)}
              className={inputCls}
            />
          </div>

          {error && <p className="text-rose-400 text-xs font-mono">{error}</p>}
          {scheduleSuccess && (
            <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium">
              <CheckCircle2 size={15} /> Schedule created successfully
            </div>
          )}

          {/* Summary pill */}
          {selectedRepoIds.size > 0 && recipients.filter(e => e.trim()).length > 0 && (
            <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl px-4 py-3 text-xs text-slate-400 font-mono">
              Scan <span className="text-indigo-300 font-bold">{selectedRepoIds.size} repo{selectedRepoIds.size > 1 ? 's' : ''}</span>{' '}
              {frequency === 'daily' ? 'every day' : frequency === 'weekly' ? 'every Monday' : 'on the 1st'}{' '}
              at <span className="text-indigo-300 font-bold">{String(hour).padStart(2,'0')}:00 {timezone}</span>{' '}
              → email to <span className="text-indigo-300 font-bold">{recipients.filter(e=>e.trim()).join(', ')}</span>
            </div>
          )}

          <Button
            onClick={handleCreateSchedule}
            loading={creating}
            disabled={selectedRepoIds.size === 0}
            size="lg"
            className="w-full sm:w-auto"
          >
            <Calendar size={15} className="mr-2" />
            Create Schedule
          </Button>
        </div>
      )}

      {/* ── Active Schedules ── */}
      {schedules.length > 0 && (
        <div className="pt-4 border-t border-slate-border/30">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Clock size={13} /> Active Schedules ({schedules.length})
          </h3>
          <div className="space-y-2">
            {schedules.map(s => (
              <div
                key={s.id}
                className="flex items-center gap-3 px-4 py-3 bg-slate-950/40 border border-slate-border/30 rounded-xl"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-semibold text-slate-200 truncate">{s.label}</p>
                    <StatusPill status={s.last_status} />
                  </div>
                  <p className="text-[10px] text-indigo-400 font-mono mt-0.5">
                    {(s as any).human_schedule || s.cron} · {(s as any).recipients?.join(', ') || s.email}
                  </p>
                  <p className="text-[10px] text-slate-600 font-mono mt-0.5">
                    {((s as any).repo_paths?.length || 1)} repo{((s as any).repo_paths?.length || 1) > 1 ? 's' : ''}
                    {s.last_run ? ` · Last: ${new Date(s.last_run).toLocaleString()}` : ''}
                  </p>
                </div>
                <div className="flex gap-1.5 shrink-0">
                  <button
                    onClick={() => handleRunNow(s.id)}
                    disabled={runningId === s.id}
                    className="p-1.5 rounded-lg bg-slate-900 border border-slate-border/40 text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/20 transition-all disabled:opacity-40"
                    title="Run now"
                  >
                    {runningId === s.id
                      ? <RefreshCw size={12} className="animate-spin" />
                      : <Play size={12} />}
                  </button>
                  <button
                    onClick={() => handleDeleteSchedule(s.id)}
                    className="p-1.5 rounded-lg bg-slate-900 border border-slate-border/40 text-slate-500 hover:bg-rose-500/10 hover:text-rose-400 hover:border-rose-500/20 transition-all"
                    title="Delete"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
