import React, { useState, useEffect } from 'react'
import { BugList } from '@/components/features/BugList'
import { BugDetail } from '@/components/features/BugDetail'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { Loader } from '@/components/common/Loader'
import { Issue } from '@/types'
import { useBugsStore } from '@/store/bugsStore'
import { useSessionStore } from '@/store/sessionStore'
import { useSettingsStore } from '@/store/settingsStore'
import { securityService } from '@/services/security'
import { notificationsService } from '@/services/apis'
import { ShieldAlert, AlertTriangle, ShieldCheck, Terminal, HelpCircle, Bell, BellOff, CheckCircle2 } from 'lucide-react'
import { StagedPRModal } from '@/components/features/StagedPRModal'
import clsx from 'clsx'

export const SecurityPage: React.FC = () => {
  const { bugs, setBugs } = useBugsStore()
  const { currentSessionId, sessionData, remediationMode, setRemediationMode } = useSessionStore()
  const slackSettings = useSettingsStore(s => ({ enabled: s.enableSlackNotifications, webhook: s.slackWebhook }))
  const [selectedBug, setSelectedBug] = useState<Issue | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [slackSending, setSlackSending] = useState(false)
  const [slackSent, setSlackSent]       = useState(false)

  const [stagedData, setStagedData] = useState<any | null>(null)
  const [isStaging, setIsStaging] = useState(false)
  const [showStagedModal, setShowStagedModal] = useState(false)

  const sendSlackAlert = async () => {
    if (!currentSessionId || !slackSettings.webhook) return
    setSlackSending(true)
    try {
      await notificationsService.slackAlert(currentSessionId, slackSettings.webhook)
      setSlackSent(true)
      setTimeout(() => setSlackSent(false), 4000)
    } catch { /* non-critical */ }
    finally { setSlackSending(false) }
  }

  const handleStagePR = async (bug: Issue) => {
    if (!currentSessionId || !bug) return
    setIsStaging(true)
    try {
      const response = await securityService.applyFix(
        currentSessionId,
        bug.bug_id || 'BUG-0001',
        bug.file || '',
        bug.line || 1,
        bug.code || '',
        bug.fix || '',
        bug.type || 'Security Fix'
      )
      
      if (response.data?.status === 'success') {
        setStagedData(response.data.data)
        setShowStagedModal(true)
      } else {
        alert(response.data?.message || 'Failed to stage PR')
      }
    } catch (err) {
      console.error('Failed to stage security PR:', err)
      alert('Error communicating with backend threat remediation engine')
    } finally {
      setIsStaging(false)
    }
  }

  useEffect(() => {
    const triggerScan = async () => {
      if (!currentSessionId) return
      setLoading(true)
      setError(null)
      try {
        const response = await securityService.scan(currentSessionId)
        const scannedBugs = response.data.data.bugs || []
        setBugs(scannedBugs)

        // Bulk auto staging in autonomous mode
        if (remediationMode === 'autonomous' && scannedBugs.length > 0) {
          setIsStaging(true)
          try {
            const autoRes = await securityService.autoStage(currentSessionId, scannedBugs)
            if (autoRes.data?.status === 'success' && autoRes.data.data.applied_count > 0) {
              setStagedData(autoRes.data.data)
              setShowStagedModal(true)
            }
          } catch (e) {
            console.error('Auto staging failed:', e)
          } finally {
            setIsStaging(false)
          }
        }
      } catch (err) {
        console.error('Vulnerability scan failed:', err)
        setError('Static analysis engine failed to scan this session ID.')
      } finally {
        setLoading(false)
      }
    }
    
    // Always trigger scan on mount if session is active
    triggerScan()
  }, [currentSessionId, setBugs, remediationMode])

  // Auto-stage all vulnerabilities when mode changes to autonomous
  useEffect(() => {
    if (remediationMode === 'autonomous' && bugs.length > 0 && !showStagedModal && !isStaging) {
      const runAutoStage = async () => {
        setIsStaging(true)
        try {
          const autoRes = await securityService.autoStage(currentSessionId!, bugs)
          if (autoRes.data?.status === 'success' && autoRes.data.data.applied_count > 0) {
            setStagedData(autoRes.data.data)
            setShowStagedModal(true)
          }
        } catch (e) {
          console.error('Auto staging failed:', e)
        } finally {
          setIsStaging(false)
        }
      }
      runAutoStage()
    }
  }, [remediationMode, bugs, currentSessionId])

  if (!currentSessionId) {
    return (
      <div className="max-w-2xl mx-auto min-h-[50vh] flex flex-col items-center justify-center text-center space-y-6 select-none font-sans">
        <div className="w-14 h-14 rounded-full bg-slate-900 border border-slate-border/60 flex items-center justify-center text-slate-500 shadow-md">
          <ShieldCheck size={28} />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-slate-100 font-display">No scan session active</h2>
          <p className="text-slate-400 text-sm max-w-sm mx-auto">
            You must configure a repository path and perform an AST scan before viewing security threats.
          </p>
        </div>
      </div>
    )
  }

  const critical = bugs.filter((b) => b.severity?.toLowerCase().includes('critical')).length
  const high = bugs.filter((b) => b.severity?.toLowerCase().includes('high')).length
  const medium = bugs.filter((b) => b.severity?.toLowerCase().includes('medium')).length
  const low = bugs.filter((b) => b.severity?.toLowerCase().includes('low') || (!b.severity)).length

  if (isStaging) return <Loader text="Fully Autonomous Agent staging all high-confidence security fixes..." />

  return (
    <div className="space-y-8 select-none font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">Security Analysis</h1>
          <p className="text-slate-400 text-sm mt-1.5 font-medium">
            Automated threat intelligence for sandbox path <span className="text-indigo-400 font-mono font-semibold">{sessionData?.repo_path || '/app/src'}</span>
          </p>
        </div>

        {/* Slack Alert Button */}
        {slackSettings.enabled && slackSettings.webhook && currentSessionId && bugs.length > 0 && (
          <button
            onClick={sendSlackAlert}
            disabled={slackSending || slackSent}
            className={clsx(
              'flex items-center gap-2 px-3 py-2 rounded-xl border text-[12px] font-semibold transition-all shrink-0',
              slackSent
                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                : 'border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200 hover:border-white/[0.14] disabled:opacity-50'
            )}
          >
            {slackSent
              ? <><CheckCircle2 size={13} /> Sent to Slack</>
              : slackSending
                ? <><Bell size={13} className="animate-pulse" /> Sending…</>
                : <><Bell size={13} /> Alert Slack</>
            }
          </button>
        )}

        {/* Mode Toggle Switch */}
        <div className="flex items-center gap-2 p-1 bg-slate-950/60 border border-slate-border/30 rounded-xl shrink-0 font-mono text-[10.5px]">
          <button
            type="button"
            onClick={() => setRemediationMode('hitl')}
            className={clsx(
              "px-3 py-1.5 rounded-lg transition-all font-semibold flex items-center gap-1.5",
              remediationMode === 'hitl'
                ? "bg-indigo-500/10 border border-indigo-500/20 text-indigo-400"
                : "border border-transparent text-slate-400 hover:text-slate-200"
            )}
          >
            👥 HITL Mode
          </button>
          <button
            type="button"
            onClick={() => setRemediationMode('autonomous')}
            className={clsx(
              "px-3 py-1.5 rounded-lg transition-all font-semibold flex items-center gap-1.5",
              remediationMode === 'autonomous'
                ? "bg-indigo-500/10 border border-indigo-500/20 text-indigo-400"
                : "border border-transparent text-slate-400 hover:text-slate-200"
            )}
          >
            🤖 Autonomous
          </button>
        </div>
      </div>

      {loading ? (
        <div className="min-h-[40vh] flex flex-col items-center justify-center space-y-4">
          <div className="w-10 h-10 rounded-full border-2 border-slate-800 border-t-indigo-500 animate-spin" />
          <p className="text-xs text-slate-500 font-mono animate-pulse">Running static threat detector...</p>
        </div>
      ) : error ? (
        <Card className="border-rose-500/20 bg-rose-500/5 max-w-2xl">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-rose-450 mt-0.5 text-rose-400" size={18} />
            <div>
              <h3 className="text-sm font-bold text-rose-400 font-display">Engine Scanning Failure</h3>
              <p className="text-xs text-slate-400 mt-1">{error}</p>
            </div>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          {/* Main List */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex justify-between items-center bg-slate-950/20 px-1 py-1 rounded-lg">
              <span className="text-xs font-semibold text-slate-400 font-display pl-2">Vulnerabilities ({bugs.length})</span>
            </div>
            
            <BugList bugs={bugs} onSelectBug={setSelectedBug} />
          </div>

          {/* Metrics summary card */}
          <div className="space-y-6">
            <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md">
              <h3 className="text-base font-bold text-slate-100 mb-4 font-display">Threat Overview</h3>
              
              <div className="space-y-4 font-mono text-xs">
                {/* Critical */}
                <div className="flex justify-between items-center border-b border-slate-border/20 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" />
                    <span className="text-slate-400">Critical:</span>
                  </div>
                  <span className="text-slate-200 font-bold">{critical}</span>
                </div>
                {/* High */}
                <div className="flex justify-between items-center border-b border-slate-border/20 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                    <span className="text-slate-400">High:</span>
                  </div>
                  <span className="text-slate-200 font-bold">{high}</span>
                </div>
                {/* Medium */}
                <div className="flex justify-between items-center border-b border-slate-border/20 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
                    <span className="text-slate-400">Medium:</span>
                  </div>
                  <span className="text-slate-200 font-bold">{medium}</span>
                </div>
                {/* Low */}
                <div className="flex justify-between items-center pb-1">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    <span className="text-slate-400">Low / Info:</span>
                  </div>
                  <span className="text-slate-200 font-bold">{low}</span>
                </div>
              </div>

              {bugs.length > 0 && (
                <div className="mt-6 pt-5 border-t border-slate-border/30">
                  <div className="rounded-xl p-3 bg-rose-500/5 border border-rose-500/10 text-[11px] text-rose-400 flex gap-2">
                    <ShieldAlert size={16} className="shrink-0 mt-0.5" />
                    <p className="leading-normal font-medium">
                      Threat exposure score is high. Review security advisories and copy the copyable AI suggestions directly.
                    </p>
                  </div>
                </div>
              )}
            </Card>

            <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md">
              <h3 className="text-base font-bold text-slate-100 mb-3 font-display">Compliance Check</h3>
              <p className="text-xs text-slate-450 leading-relaxed text-slate-500">
                Threat engine matches OWASP Top 10 guidelines and CWE metadata catalog profiles.
              </p>
            </Card>
          </div>
        </div>
      )}

      <BugDetail 
        bug={selectedBug} 
        isOpen={!!selectedBug} 
        onClose={() => setSelectedBug(null)} 
        onStagePR={handleStagePR}
        isStaging={isStaging}
      />

      <StagedPRModal 
        isOpen={showStagedModal} 
        onClose={() => setShowStagedModal(false)} 
        data={stagedData} 
      />
    </div>
  )
}

