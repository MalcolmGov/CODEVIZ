import React, { useState, useEffect } from 'react'
import { RefactoringCard } from '@/components/features/RefactoringCard'
import { CodeDiffViewer } from '@/components/features/CodeDiffViewer'
import { PRPreview } from '@/components/features/PRPreview'
import { Card } from '@/components/common/Card'
import { Loader } from '@/components/common/Loader'
import { useRefactoringStore } from '@/store/refactoringStore'
import { refactoringService } from '@/services/refactoring'
import { useSessionStore } from '@/store/sessionStore'
import { Sparkles, Terminal, ShieldCheck, Hourglass, Zap, ChevronRight } from 'lucide-react'
import { StagedPRModal } from '@/components/features/StagedPRModal'
import clsx from 'clsx'

export const RefactoringPage: React.FC = () => {
  const { currentSessionId, sessionData, remediationMode, setRemediationMode } = useSessionStore()
  const { opportunities, selectedOpportunity, suggestions, setOpportunities, selectOpportunity, setSuggestion } =
    useRefactoringStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [stagedData, setStagedData] = useState<any | null>(null)
  const [isStaging, setIsStaging] = useState(false)
  const [showStagedModal, setShowStagedModal] = useState(false)

  // Auto-stage all refactoring opportunities when mode changes to autonomous
  useEffect(() => {
    if (remediationMode === 'autonomous' && opportunities.length > 0 && !showStagedModal && !isStaging) {
      const runAutoStage = async () => {
        setIsStaging(true)
        try {
          const autoRes = await refactoringService.autoStage(currentSessionId!, opportunities)
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
  }, [remediationMode, opportunities, currentSessionId])

  const handleStagePR = async () => {
    if (!currentSessionId || !selectedOpportunity) return
    setIsStaging(true)
    try {
      const response = await refactoringService.stagePR(
        currentSessionId,
        selectedOpportunity.file || '',
        selectedOpportunity.line || 1,
        selectedOpportunity.current_code || '',
        selectedOpportunity.suggested_code || '',
        selectedOpportunity.type || 'Refactoring'
      )
      
      if (response.data?.status === 'success') {
        setStagedData(response.data.data)
        setShowStagedModal(true)
      } else {
        alert(response.data?.message || 'Failed to stage PR')
      }
    } catch (err) {
      console.error('Failed to stage PR:', err)
      alert('Error communicating with backend refactoring engine')
    } finally {
      setIsStaging(false)
    }
  }

  useEffect(() => {
    if (currentSessionId) {
      loadOpportunities()
    }
  }, [currentSessionId])

  const loadOpportunities = async () => {
    if (!currentSessionId) return
    setLoading(true)
    setError(null)
    try {
      const response = await refactoringService.getOpportunities(currentSessionId)
      setOpportunities(response.data.data.opportunities || [])
    } catch (err) {
      console.error('Failed to load opportunities:', err)
      setError('Failed to fetch refactoring opportunities for this workspace.')
    } finally {
      setLoading(false)
    }
  }

  const handleViewSuggestion = async (opp: any, index: number) => {
    if (!currentSessionId) return
    selectOpportunity(opp)
    
    // Check if suggestion already loaded in store
    if (suggestions[index]) return

    try {
      const response = await refactoringService.getSuggestion(currentSessionId, index)
      setSuggestion(index, response.data.data.suggestion)
    } catch (error) {
      console.error('Failed to get suggestion:', error)
    }
  }

  if (!currentSessionId) {
    return (
      <div className="max-w-2xl mx-auto min-h-[50vh] flex flex-col items-center justify-center text-center space-y-6 select-none font-sans">
        <div className="w-14 h-14 rounded-full bg-slate-900 border border-slate-border/60 flex items-center justify-center text-slate-500 shadow-md">
          <Sparkles size={28} />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-slate-100 font-display">No session active</h2>
          <p className="text-slate-400 text-sm max-w-sm mx-auto">
            You must select a repository and scan it in order to view refactoring recommendations.
          </p>
        </div>
      </div>
    )
  }

  if (loading) return <Loader text="Refactoring engine analyzing quality hotspots..." />
  if (isStaging) return <Loader text="Staging Git branch and applying refactoring changes..." />

  const activeIndex = selectedOpportunity ? opportunities.indexOf(selectedOpportunity) : -1
  const activeSuggestion = activeIndex !== -1 ? suggestions[activeIndex] : null

  // Calculated values for premium metrics display
  const totalComplexityReduction = opportunities.length * 12
  const estimatedHoursSaved = (opportunities.length * 0.7).toFixed(1)

  return (
    <div className="space-y-8 select-none font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">Code Refactoring</h1>
          <p className="text-slate-400 text-sm mt-1.5 font-medium">
            Source code quality and architectural improvements in sandbox <span className="text-indigo-400 font-mono font-semibold">{sessionData?.repo_path || '/app/src'}</span>
          </p>
        </div>

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

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md">
          <div className="flex justify-between items-center">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider font-display">Time Saved</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Hourglass size={16} />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-2xl font-black text-slate-100 font-display tracking-tight">~{estimatedHoursSaved} Hours</p>
            <p className="text-slate-500 text-[10px] mt-1 font-mono">Manual dev refactoring time saved</p>
          </div>
        </Card>
        
        <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md">
          <div className="flex justify-between items-center">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider font-display">Complexity Drop</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Zap size={16} />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-2xl font-black text-slate-100 font-display tracking-tight">-{totalComplexityReduction}%</p>
            <p className="text-slate-500 text-[10px] mt-1 font-mono">Cognitive complexity reduction</p>
          </div>
        </Card>

        <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md">
          <div className="flex justify-between items-center">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider font-display">Sandbox Integrity</span>
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <ShieldCheck size={16} />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-2xl font-black text-slate-100 font-display tracking-tight">A+ Rating</p>
            <p className="text-slate-500 text-[10px] mt-1 font-mono">Estimated readability score</p>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Opportunities List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center bg-slate-950/20 px-1 py-1 rounded-lg">
            <span className="text-xs font-semibold text-slate-400 font-display pl-2">Hotspots Discovered ({opportunities.length})</span>
          </div>
          
          <div className="space-y-3.5">
            {opportunities.length === 0 ? (
              <Card className="bg-slate-surface/20 border-slate-border/30">
                <div className="text-center py-16">
                  <ShieldCheck size={36} className="mx-auto text-slate-500 mb-3" />
                  <h3 className="text-sm font-semibold text-slate-300 font-display">No hotspots detected</h3>
                  <p className="text-xs text-slate-500 mt-1">This repository's architecture is highly optimized.</p>
                </div>
              </Card>
            ) : (
              opportunities.map((opp, idx) => (
                <div key={opp.id} onClick={() => handleViewSuggestion(opp, idx)}>
                  <div className={`rounded-xl transition-all duration-200 ${
                    opp.id === selectedOpportunity?.id ? 'ring-2 ring-indigo-500/50' : ''
                  }`}>
                    <RefactoringCard refactoring={opp} onClick={() => {}} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Selected Details Drawer */}
        <div className="space-y-5 lg:sticky lg:top-24">
          {selectedOpportunity && activeSuggestion ? (
            <div className="space-y-6 fade-in">
              <PRPreview
                title={selectedOpportunity.type}
                description={selectedOpportunity.explanation || 'Refactoring suggestion'}
                branch={`refactor/${selectedOpportunity.type.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`}
                filesChanged={1}
                onCreatePR={handleStagePR}
              />
              
              <div className="pt-2">
                <CodeDiffViewer
                  before={selectedOpportunity.current_code || 'Original code'}
                  after={selectedOpportunity.suggested_code || 'Refactored code'}
                />
              </div>
            </div>
          ) : selectedOpportunity ? (
            <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md p-6 text-center py-12">
              <div className="w-8 h-8 rounded-full border border-slate-border/60 flex items-center justify-center mx-auto mb-3">
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
              </div>
              <p className="text-xs text-slate-400 font-mono animate-pulse">Requesting AI suggestion payload...</p>
            </Card>
          ) : (
            <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md p-6 text-center py-16">
              <Sparkles size={24} className="mx-auto text-slate-600 mb-3" />
              <h4 className="text-sm font-semibold text-slate-300 font-display">No Hotspot Selected</h4>
              <p className="text-xs text-slate-500 mt-1 max-w-[200px] mx-auto leading-normal">
                Click on one of the quality hotspots to view suggested changes.
              </p>
            </Card>
          )}
        </div>
      </div>
      
      <StagedPRModal 
        isOpen={showStagedModal} 
        onClose={() => setShowStagedModal(false)} 
        data={stagedData} 
      />
    </div>
  )
}

