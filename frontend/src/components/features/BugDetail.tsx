import React from 'react'
import { Modal } from '@/components/common/Modal'
import { Issue } from '@/types'
import { Badge } from '@/components/common/Badge'
import { AlertOctagon, Terminal, Copy, Check, GitPullRequest } from 'lucide-react'
import { AskAIButton } from '@/components/common/AskAIButton'

interface BugDetailProps {
  bug: Issue | null
  isOpen: boolean
  onClose: () => void
  onStagePR?: (bug: Issue) => void
  isStaging?: boolean
}

export const BugDetail: React.FC<BugDetailProps> = ({ bug, isOpen, onClose, onStagePR, isStaging }) => {
  const [copied, setCopied] = React.useState(false)
  if (!bug) return null

  const handleCopy = () => {
    if (bug.fix) {
      navigator.clipboard.writeText(bug.fix)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const sevClass = bug.severity?.toLowerCase() || 'medium'
  const severityBadge = sevClass.includes('critical') ? 'critical' : sevClass.includes('high') ? 'high' : sevClass.includes('medium') ? 'medium' : 'low'

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Vulnerability Report Details" size="xl">
      <div className="space-y-6 select-none font-sans">
        {/* Top Info Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-slate-950/40 border border-slate-border/20 rounded-xl p-4">
          <div>
            <h4 className="text-[10px] uppercase font-bold tracking-wider text-slate-500 font-mono mb-1">Threat Level</h4>
            <Badge severity={severityBadge}>
              {bug.severity?.replace(/[^a-zA-Z]/g, '') || 'LOW'}
            </Badge>
          </div>
          <div>
            <h4 className="text-[10px] uppercase font-bold tracking-wider text-slate-500 font-mono mb-1">CWE Reference</h4>
            <span className="text-xs text-slate-300 font-mono font-semibold">{bug.cwe || 'CWE-Unknown'}</span>
          </div>
          {bug.cvss !== undefined && (
            <div>
              <h4 className="text-[10px] uppercase font-bold tracking-wider text-slate-500 font-mono mb-1">CVSS Base</h4>
              <span className="text-xs font-mono font-bold text-rose-450 text-rose-400">{bug.cvss} / 10.0</span>
            </div>
          )}
          <div>
            <h4 className="text-[10px] uppercase font-bold tracking-wider text-slate-500 font-mono mb-1">Engine Match</h4>
            <span className="text-xs text-slate-300 font-mono font-semibold">{Math.round((bug.confidence || 0.8) * 100)}% Confidence</span>
          </div>
        </div>

        {/* Threat Description */}
        <div className="space-y-2">
          <h3 className="text-sm font-bold text-slate-200 font-display">Vulnerability Description</h3>
          <p className="text-sm text-slate-350 text-slate-400 leading-relaxed bg-slate-900/40 p-4 border border-slate-border/20 rounded-xl">
            {bug.message}
          </p>
        </div>

        {/* Location */}
        <div className="space-y-2">
          <h3 className="text-sm font-bold text-slate-200 font-display">Vulnerable Source Code</h3>
          <p className="text-xs text-slate-500 font-mono">File: <span className="text-indigo-400">{bug.file}</span> (Line: {bug.line})</p>
          {bug.code && (
            <div className="relative">
              <pre className="bg-slate-950 p-4 border border-slate-border/50 rounded-xl overflow-x-auto text-xs font-mono text-slate-300 border-l-4 border-l-rose-500/80">
                <code>{bug.code}</code>
              </pre>
            </div>
          )}
        </div>

        {/* Ask AI */}
        <AskAIButton
          label={bug.type || 'Security Finding'}
          context={`${bug.type || 'Security issue'} in ${bug.file} line ${bug.line}. Severity: ${bug.severity}. CWE: ${bug.cwe || 'unknown'}. Description: ${bug.message}. ${bug.fix ? `Suggested fix: ${bug.fix}` : ''}`}
          className="w-full"
        />

        {/* Suggested Solution */}
        {bug.fix && (
          <div className="space-y-2.5">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold text-slate-200 font-display">AI Recommended Fix</h3>
              <button 
                onClick={handleCopy}
                className="text-[10px] text-slate-400 hover:text-slate-200 font-mono flex items-center gap-1.5 px-2 py-1 rounded bg-slate-900 border border-slate-border/40 transition-colors"
              >
                {copied ? (
                  <>
                    <Check size={11} className="text-emerald-400" />
                    <span className="text-emerald-400">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy size={11} />
                    <span>Copy Code</span>
                  </>
                )}
              </button>
            </div>
            <pre className="bg-[#040d0e] p-4 border border-emerald-950/60 rounded-xl overflow-x-auto text-xs font-mono text-emerald-400 border-l-4 border-l-emerald-500/80">
              <code>{bug.fix}</code>
            </pre>

            {onStagePR && (
              <button
                type="button"
                disabled={isStaging}
                onClick={() => onStagePR(bug)}
                className="w-full mt-3 flex items-center justify-center gap-2 py-2 px-4 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 disabled:from-slate-800 disabled:to-slate-800 transition-all border border-transparent shadow-sm"
              >
                {isStaging ? (
                  <>
                    <div className="w-3.5 h-3.5 rounded-full border-2 border-slate-600 border-t-white animate-spin" />
                    <span>Staging Security Patch...</span>
                  </>
                ) : (
                  <>
                    <GitPullRequest size={14} />
                    <span>Stage Pull Request</span>
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </Modal>
  )
}

