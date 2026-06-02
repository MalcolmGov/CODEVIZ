import React, { useState, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useSettingsStore } from '@/store/settingsStore'
import { useSessionStore } from '@/store/sessionStore'
import { settingsService } from '@/services/settings'
import {
  User, Github, Cpu, Bell, SlidersHorizontal,
  Eye, EyeOff, CheckCircle2, XCircle, Loader2,
  ChevronRight, ShieldAlert, RefreshCw, Save, AlertTriangle,
} from 'lucide-react'
import clsx from 'clsx'

const CARD   = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'
const LABEL  = 'text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-1.5 block'
const INPUT  = 'w-full rounded-xl border border-white/[0.08] bg-slate-elevated px-3.5 py-2.5 text-[13px] text-slate-200 placeholder-slate-700 font-mono focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all'
const SELECT_CLS = 'w-full rounded-xl border border-white/[0.08] bg-slate-elevated px-3.5 py-2.5 text-[13px] text-slate-200 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all appearance-none'

function SectionHeader({ icon: Icon, title, desc }: { icon: React.ElementType; title: string; desc: string }) {
  return (
    <div className="flex items-start gap-3 pb-5 mb-5 border-b border-white/[0.05]">
      <div className="p-2 rounded-xl bg-slate-elevated border border-white/[0.06] shrink-0 mt-0.5">
        <Icon size={15} className="text-slate-400" />
      </div>
      <div>
        <h2 className="text-[15px] font-semibold text-slate-200 font-tight">{title}</h2>
        <p className="text-[12px] text-slate-500 mt-0.5">{desc}</p>
      </div>
    </div>
  )
}

function SaveButton({ onClick, saving, saved }: { onClick: () => void; saving: boolean; saved: boolean }) {
  return (
    <button onClick={onClick} disabled={saving}
      className={clsx(
        'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all duration-200',
        saved
          ? 'bg-emerald-500/15 border border-emerald-500/25 text-emerald-400'
          : 'bg-indigo-500/15 border border-indigo-500/25 text-indigo-400 hover:bg-indigo-500/25 disabled:opacity-50'
      )}>
      {saving ? <Loader2 size={13} className="animate-spin" /> : saved ? <CheckCircle2 size={13} /> : <Save size={13} />}
      {saving ? 'Saving…' : saved ? 'Saved' : 'Save changes'}
    </button>
  )
}

type TestState = 'idle' | 'loading' | 'success' | 'error'

function ConnectionBadge({ state, message }: { state: TestState; message: string }) {
  if (state === 'idle') return null
  return (
    <div className={clsx(
      'flex items-center gap-1.5 text-[11px] font-medium px-3 py-1.5 rounded-lg border',
      state === 'loading' ? 'text-slate-400 border-white/[0.07] bg-slate-elevated' :
      state === 'success' ? 'text-emerald-400 border-emerald-500/20 bg-emerald-500/[0.07]' :
                            'text-rose-400 border-rose-500/20 bg-rose-500/[0.07]'
    )}>
      {state === 'loading' ? <Loader2 size={11} className="animate-spin" /> :
       state === 'success' ? <CheckCircle2 size={11} /> : <XCircle size={11} />}
      <span className="truncate max-w-[280px]">{message}</span>
    </div>
  )
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button type="button" role="switch" aria-checked={checked} onClick={() => onChange(!checked)}
      className={clsx(
        'relative inline-flex h-5 w-9 shrink-0 rounded-full border transition-colors duration-200 focus:outline-none',
        checked ? 'bg-indigo-500 border-indigo-500/50' : 'bg-slate-elevated border-white/[0.08]'
      )}>
      <span className={clsx(
        'inline-block h-3.5 w-3.5 rounded-full bg-white shadow-sm mt-[3px] transition-transform duration-200',
        checked ? 'translate-x-4' : 'translate-x-[3px]'
      )} />
    </button>
  )
}

export const SettingsPage: React.FC = () => {
  const { user } = useAuthStore()
  const { clearSession } = useSessionStore()
  const settings = useSettingsStore()

  const [showToken, setShowToken]     = useState(false)
  const [showWebhook, setShowWebhook] = useState(false)
  const [saving, setSaving]   = useState<Record<string, boolean>>({})
  const [saved, setSaved]     = useState<Record<string, boolean>>({})

  const [ghTest, setGhTest]           = useState<TestState>('idle')
  const [ghMsg, setGhMsg]             = useState('')
  const [ollamaTest, setOllamaTest]   = useState<TestState>('idle')
  const [ollamaMsg, setOllamaMsg]     = useState('')
  const [slackTest, setSlackTest]     = useState<TestState>('idle')
  const [slackMsg, setSlackMsg]       = useState('')

  useEffect(() => {
    settingsService.get()
      .then(res => {
        const d = (res.data as any).data || {}
        if (!settings.githubToken && d.githubToken) settings.set({ githubToken: d.githubToken })
        if (!settings.slackWebhook && d.slackWebhook) settings.set({ slackWebhook: d.slackWebhook })
        if (d.ollamaUrl) settings.set({ ollamaUrl: d.ollamaUrl })
        if (d.ollamaModel) settings.set({ ollamaModel: d.ollamaModel })
      })
      .catch(() => {})
  }, [])

  const saveSection = async (section: string, data: Record<string, unknown>) => {
    setSaving(s => ({ ...s, [section]: true }))
    try { await settingsService.save(data) } catch {}
    settings.set(data as any)
    setSaving(s => ({ ...s, [section]: false }))
    setSaved(s => ({ ...s, [section]: true }))
    setTimeout(() => setSaved(s => ({ ...s, [section]: false })), 2500)
  }

  const testGitHub = async () => {
    setGhTest('loading'); setGhMsg('Verifying token…')
    try {
      const res = await settingsService.testGitHub(settings.githubToken)
      const d = (res.data as any).data
      setGhTest('success')
      setGhMsg(`Connected as @${d.username} · ${d.public_repos} repos · scopes: ${d.scopes}`)
    } catch (e: any) {
      setGhTest('error')
      setGhMsg(e?.response?.data?.message || 'Invalid token or no network access')
    }
  }

  const testOllama = async () => {
    setOllamaTest('loading'); setOllamaMsg('Pinging Ollama…')
    try {
      const res = await settingsService.testOllama(settings.ollamaUrl)
      const d = (res.data as any).data
      setOllamaTest('success')
      setOllamaMsg(`Reachable · ${d.model_count} model(s): ${(d.models || []).slice(0, 3).join(', ')}`)
    } catch {
      setOllamaTest('error')
      setOllamaMsg('Cannot reach Ollama — is it running on the configured URL?')
    }
  }

  const testSlack = async () => {
    setSlackTest('loading'); setSlackMsg('Sending test message…')
    try {
      await settingsService.testSlack(settings.slackWebhook)
      setSlackTest('success'); setSlackMsg('Test message delivered to Slack')
    } catch {
      setSlackTest('error'); setSlackMsg('Webhook rejected — check the URL')
    }
  }

  const OLLAMA_MODELS = ['mistral', 'llama3', 'llama3.2', 'codellama', 'deepseek-coder', 'gemma2', 'phi3', 'qwen2.5-coder']
  const MODEL_TAGS: Record<string, string> = {
    mistral: 'Fast · 7B', llama3: 'General · 8B', 'llama3.2': 'General · 3B',
    codellama: 'Code', 'deepseek-coder': 'Best for code', gemma2: 'Google · 9B',
    phi3: 'Tiny · 3.8B', 'qwen2.5-coder': 'Code · 7B',
  }

  return (
    <div className="max-w-2xl space-y-5 pb-10 animate-fade-in select-none">

      <div className="pt-1">
        <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Settings</h1>
        <p className="text-slate-500 text-[13px] mt-1.5">Configure integrations, AI engine, and scan preferences.</p>
      </div>

      {/* ── 1. Developer Profile ─────────────────────────────────────────── */}
      <div className={`${CARD} p-6`}>
        <SectionHeader icon={User} title="Developer profile"
          desc="Your identity shown in scan reports and staged commits." />
        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <label className={LABEL}>Name</label>
            <input className={INPUT} defaultValue={user?.name || 'Malcolm Govender'}
              readOnly style={{ cursor: 'default', opacity: 0.7 }} />
          </div>
          <div>
            <label className={LABEL}>Email</label>
            <input className={INPUT} defaultValue={user?.email || 'malcolm@moveddigital.com'}
              readOnly style={{ cursor: 'default', opacity: 0.7 }} />
          </div>
        </div>
        <div className="flex items-center justify-between pt-4 border-t border-white/[0.05]">
          <p className="text-[11px] text-slate-700 font-mono">Profile synced from GitHub OAuth.</p>
          <span className="flex items-center gap-1.5 text-[10px] text-emerald-400 bg-emerald-500/[0.08] border border-emerald-500/20 px-2.5 py-1 rounded-full font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Authenticated
          </span>
        </div>
      </div>

      {/* ── 2. GitHub Integration ────────────────────────────────────────── */}
      <div className={`${CARD} p-6`}>
        <SectionHeader icon={Github} title="GitHub integration"
          desc="Personal access token used for repo scanning, PR creation, and CVE dependency lookup." />
        <div className="mb-5">
          <label className={LABEL}>Personal access token</label>
          <div className="relative">
            <input type={showToken ? 'text' : 'password'} className={INPUT + ' pr-10'}
              placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
              value={settings.githubToken}
              onChange={e => settings.set({ githubToken: e.target.value })} />
            <button type="button" onClick={() => setShowToken(v => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400 transition-colors">
              {showToken ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
          </div>
          <p className="text-[10px] text-slate-700 mt-1.5 font-mono">
            Required scopes: <span className="text-slate-500">repo, read:user, read:org</span>
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-white/[0.05]">
          <SaveButton
            onClick={() => saveSection('github', { githubToken: settings.githubToken })}
            saving={!!saving.github} saved={!!saved.github} />
          <button onClick={testGitHub} disabled={!settings.githubToken || ghTest === 'loading'}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/[0.14] transition-all disabled:opacity-40">
            <RefreshCw size={13} className={clsx(ghTest === 'loading' && 'animate-spin')} />
            Test connection
          </button>
          <ConnectionBadge state={ghTest} message={ghMsg} />
        </div>
      </div>

      {/* ── 3. AI Engine ─────────────────────────────────────────────────── */}
      <div className={`${CARD} p-6`}>
        <SectionHeader icon={Cpu} title="AI engine (Ollama)"
          desc="Local LLM powering code Q&A, remediation reasoning, and autonomous fix generation." />
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className={LABEL}>Ollama base URL</label>
            <input className={INPUT} placeholder="http://localhost:11434"
              value={settings.ollamaUrl}
              onChange={e => settings.set({ ollamaUrl: e.target.value })} />
          </div>
          <div>
            <label className={LABEL}>Active model</label>
            <div className="relative">
              <select className={SELECT_CLS}
                value={settings.ollamaModel}
                onChange={e => settings.set({ ollamaModel: e.target.value })}>
                {OLLAMA_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
              <ChevronRight size={12} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 rotate-90 pointer-events-none" />
            </div>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 mb-5">
          {['mistral', 'codellama', 'deepseek-coder', 'llama3'].map(m => (
            <button key={m} type="button" onClick={() => settings.set({ ollamaModel: m })}
              className={clsx(
                'text-[10px] font-mono px-2.5 py-1 rounded-lg border transition-all',
                settings.ollamaModel === m
                  ? 'bg-indigo-500/15 border-indigo-500/30 text-indigo-400'
                  : 'border-white/[0.07] text-slate-600 hover:text-slate-400 hover:border-white/[0.12]'
              )}>
              {m} <span className="opacity-50 ml-1">{MODEL_TAGS[m]}</span>
            </button>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-white/[0.05]">
          <SaveButton
            onClick={() => saveSection('ollama', { ollamaUrl: settings.ollamaUrl, ollamaModel: settings.ollamaModel })}
            saving={!!saving.ollama} saved={!!saved.ollama} />
          <button onClick={testOllama} disabled={ollamaTest === 'loading'}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/[0.14] transition-all disabled:opacity-40">
            <RefreshCw size={13} className={clsx(ollamaTest === 'loading' && 'animate-spin')} />
            Ping Ollama
          </button>
          <ConnectionBadge state={ollamaTest} message={ollamaMsg} />
        </div>
      </div>

      {/* ── 4. Notifications ─────────────────────────────────────────────── */}
      <div className={`${CARD} p-6`}>
        <SectionHeader icon={Bell} title="Notifications"
          desc="Get alerted via Slack or email when scans complete or critical issues are found." />
        <div className="space-y-4 mb-5">

          {/* Slack */}
          <div className="p-4 rounded-xl border border-white/[0.06] bg-slate-elevated space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[13px] font-semibold text-slate-300">Slack alerts</p>
                <p className="text-[11px] text-slate-600 mt-0.5">Posts scan summaries and critical findings to a channel</p>
              </div>
              <Toggle checked={settings.enableSlackNotifications}
                onChange={v => settings.set({ enableSlackNotifications: v })} />
            </div>
            {settings.enableSlackNotifications && (
              <div>
                <label className={LABEL}>Webhook URL</label>
                <div className="relative">
                  <input type={showWebhook ? 'text' : 'password'} className={INPUT + ' pr-10'}
                    placeholder="https://hooks.slack.com/services/..."
                    value={settings.slackWebhook}
                    onChange={e => settings.set({ slackWebhook: e.target.value })} />
                  <button type="button" onClick={() => setShowWebhook(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400 transition-colors">
                    {showWebhook ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
                <div className="flex flex-wrap items-center gap-3 mt-2">
                  <button onClick={testSlack} disabled={!settings.slackWebhook || slackTest === 'loading'}
                    className="flex items-center gap-1.5 text-[11px] font-medium text-indigo-400/70 hover:text-indigo-400 transition-colors disabled:opacity-40">
                    <RefreshCw size={11} className={clsx(slackTest === 'loading' && 'animate-spin')} />
                    Send test message
                  </button>
                  <ConnectionBadge state={slackTest} message={slackMsg} />
                </div>
              </div>
            )}
          </div>

          {/* Email */}
          <div className="p-4 rounded-xl border border-white/[0.06] bg-slate-elevated space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[13px] font-semibold text-slate-300">Email reports</p>
                <p className="text-[11px] text-slate-600 mt-0.5">Scheduled PDF scan summaries delivered to your inbox</p>
              </div>
              <Toggle checked={settings.enableEmailReports}
                onChange={v => settings.set({ enableEmailReports: v })} />
            </div>
            {settings.enableEmailReports && (
              <div>
                <label className={LABEL}>Delivery address</label>
                <input type="email" className={INPUT} placeholder="you@company.com"
                  value={settings.gmailAddress}
                  onChange={e => settings.set({ gmailAddress: e.target.value })} />
              </div>
            )}
          </div>
        </div>
        <div className="pt-4 border-t border-white/[0.05]">
          <SaveButton
            onClick={() => saveSection('notifications', {
              slackWebhook: settings.slackWebhook,
              gmailAddress: settings.gmailAddress,
              enableSlackNotifications: settings.enableSlackNotifications,
              enableEmailReports: settings.enableEmailReports,
            })}
            saving={!!saving.notifications} saved={!!saved.notifications} />
        </div>
      </div>

      {/* ── 5. Scan Preferences ──────────────────────────────────────────── */}
      <div className={`${CARD} p-6`}>
        <SectionHeader icon={SlidersHorizontal} title="Scan preferences"
          desc="Control how the scanner analyses your repositories." />
        <div className="space-y-5 mb-5">

          <div>
            <label className={LABEL}>Default remediation mode</label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 'hitl',       label: 'Human-in-the-loop', desc: 'Review each fix before staging' },
                { id: 'autonomous', label: 'Autonomous',         desc: 'Auto-stage high-confidence fixes' },
              ].map(m => (
                <button key={m.id} type="button"
                  onClick={() => settings.set({ defaultRemediationMode: m.id as any })}
                  className={clsx(
                    'text-left p-3 rounded-xl border transition-all duration-150',
                    settings.defaultRemediationMode === m.id
                      ? 'bg-indigo-500/15 border-indigo-500/30 text-indigo-400'
                      : 'border-white/[0.07] text-slate-500 hover:border-white/[0.12] hover:text-slate-300'
                  )}>
                  <p className="text-[12px] font-semibold">{m.label}</p>
                  <p className="text-[11px] opacity-70 mt-0.5">{m.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className={LABEL}>Scan depth</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'shallow',  label: 'Shallow',  desc: 'Top-level · fastest' },
                { id: 'standard', label: 'Standard', desc: '≤100 files · recommended' },
                { id: 'deep',     label: 'Deep',     desc: 'Full codebase' },
              ].map(d => (
                <button key={d.id} type="button"
                  onClick={() => settings.set({ scanDepth: d.id as any })}
                  className={clsx(
                    'text-left p-3 rounded-xl border transition-all duration-150',
                    settings.scanDepth === d.id
                      ? 'bg-indigo-500/15 border-indigo-500/30 text-indigo-400'
                      : 'border-white/[0.07] text-slate-500 hover:border-white/[0.12] hover:text-slate-300'
                  )}>
                  <p className="text-[12px] font-semibold">{d.label}</p>
                  <p className="text-[11px] opacity-70 mt-0.5">{d.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={LABEL}>Max files per scan</label>
              <input type="number" className={INPUT} min={10} max={1000} step={10}
                value={settings.maxFilesPerScan}
                onChange={e => settings.set({ maxFilesPerScan: Number(e.target.value) })} />
            </div>
            <div>
              <label className={LABEL}>Excluded paths</label>
              <input className={INPUT} placeholder="node_modules, .git, dist"
                value={settings.excludePaths}
                onChange={e => settings.set({ excludePaths: e.target.value })} />
            </div>
          </div>
        </div>
        <div className="pt-4 border-t border-white/[0.05]">
          <SaveButton
            onClick={() => saveSection('scan', {
              defaultRemediationMode: settings.defaultRemediationMode,
              scanDepth: settings.scanDepth,
              maxFilesPerScan: settings.maxFilesPerScan,
              excludePaths: settings.excludePaths,
            })}
            saving={!!saving.scan} saved={!!saved.scan} />
        </div>
      </div>

      {/* ── Danger zone ──────────────────────────────────────────────────── */}
      <div className={`${CARD} p-6 border-rose-500/[0.12]`}>
        <div className="flex items-start gap-3 pb-5 mb-5 border-b border-white/[0.05]">
          <div className="p-2 rounded-xl bg-rose-500/[0.08] border border-rose-500/20 shrink-0 mt-0.5">
            <AlertTriangle size={15} className="text-rose-400" />
          </div>
          <div>
            <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Danger zone</h2>
            <p className="text-[12px] text-slate-500 mt-0.5">Irreversible actions — proceed carefully.</p>
          </div>
        </div>
        <div className="space-y-2.5">
          {[
            {
              label: 'Clear active session',
              desc: 'Resets the current scan session and returns to the scan form',
              action: clearSession,
              btn: 'Clear session',
            },
            {
              label: 'Reset all settings',
              desc: 'Clears all saved configuration and restores defaults',
              action: () => { if (window.confirm('Reset all settings to defaults?')) settings.reset() },
              btn: 'Reset',
            },
          ].map((item, i) => (
            <div key={i} className="flex items-center justify-between p-3.5 rounded-xl border border-white/[0.06] bg-slate-elevated">
              <div>
                <p className="text-[13px] font-medium text-slate-300">{item.label}</p>
                <p className="text-[11px] text-slate-600 mt-0.5">{item.desc}</p>
              </div>
              <button onClick={item.action}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold border border-rose-500/20 text-rose-400 bg-rose-500/[0.07] hover:bg-rose-500/[0.14] transition-colors shrink-0 ml-4">
                <ShieldAlert size={12} /> {item.btn}
              </button>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}
