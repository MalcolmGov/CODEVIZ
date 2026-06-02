import React, { useState } from 'react'
import { Modal } from '@/components/common/Modal'
import { CheckCircle2, Copy, Check, Terminal, FolderGit2, GitBranch } from 'lucide-react'

interface StagedPRModalProps {
  isOpen: boolean
  onClose: () => void
  data: {
    branch: string
    file_patched: string
    commit: string
    is_git: boolean
  } | null
}

export const StagedPRModal: React.FC<StagedPRModalProps> = ({ isOpen, onClose, data }) => {
  const [copiedCmd, setCopiedCmd] = useState<number | null>(null)

  if (!data) return null

  const checkoutCmd = `git checkout ${data.branch}`
  const diffCmd = `git diff main`

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedCmd(index)
    setTimeout(() => setCopiedCmd(null), 2000)
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Pull Request Staged" size="lg">
      <div className="space-y-6 select-none font-sans py-2">
        {/* Success Banner */}
        <div className="flex flex-col items-center justify-center text-center space-y-3 pb-2">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <CheckCircle2 size={24} />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 font-display">Branch Staged Successfully</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              The AI recommended fixes have been merged into a new sandboxed branch and committed to your repository workspace.
            </p>
          </div>
        </div>

        {/* PR Staged Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950/40 border border-slate-border/20 rounded-xl p-4 font-mono text-xs">
          <div className="space-y-1">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Staged Branch</p>
            <p className="text-indigo-400 flex items-center gap-1.5 font-bold">
              <GitBranch size={13} />
              {data.branch}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Patched File</p>
            <p className="text-slate-200 truncate flex items-center gap-1.5" title={data.file_patched}>
              <FolderGit2 size={13} className="text-slate-400" />
              {data.file_patched}
            </p>
          </div>
          <div className="md:col-span-2 space-y-1 pt-2 border-t border-slate-border/20">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Local Commit Message</p>
            <p className="text-slate-300 italic">
              "{data.commit}"
            </p>
          </div>
        </div>

        {/* Terminal Instructions */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold text-slate-200 font-display flex items-center gap-1.5">
            <Terminal size={14} className="text-indigo-400" />
            Inspect Changes locally
          </h4>
          <div className="bg-slate-950 border border-slate-border/40 rounded-xl p-4 space-y-3 font-mono text-[11px] text-slate-300">
            <div className="flex justify-between items-center bg-slate-900/60 p-2 rounded-lg border border-slate-border/20">
              <div className="flex-1 truncate mr-2">
                <span className="text-slate-500 mr-2">$</span>
                <span className="text-indigo-300 font-bold">{checkoutCmd}</span>
              </div>
              <button
                type="button"
                onClick={() => handleCopy(checkoutCmd, 1)}
                className="text-[10px] text-slate-400 hover:text-slate-200 shrink-0 font-sans border border-slate-border/30 hover:border-slate-border/60 bg-slate-950 px-2.5 py-1 rounded transition-all"
              >
                {copiedCmd === 1 ? (
                  <span className="text-emerald-400 font-bold flex items-center gap-1"><Check size={10} /> Copied</span>
                ) : 'Copy'}
              </button>
            </div>
            
            <div className="flex justify-between items-center bg-slate-900/60 p-2 rounded-lg border border-slate-border/20">
              <div className="flex-1 truncate mr-2">
                <span className="text-slate-500 mr-2">$</span>
                <span className="text-indigo-300 font-bold">{diffCmd}</span>
              </div>
              <button
                type="button"
                onClick={() => handleCopy(diffCmd, 2)}
                className="text-[10px] text-slate-400 hover:text-slate-200 shrink-0 font-sans border border-slate-border/30 hover:border-slate-border/60 bg-slate-950 px-2.5 py-1 rounded transition-all"
              >
                {copiedCmd === 2 ? (
                  <span className="text-emerald-400 font-bold flex items-center gap-1"><Check size={10} /> Copied</span>
                ) : 'Copy'}
              </button>
            </div>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-white bg-indigo-500 hover:bg-indigo-600 rounded-xl transition-all"
          >
            Got it, close
          </button>
        </div>
      </div>
    </Modal>
  )
}
