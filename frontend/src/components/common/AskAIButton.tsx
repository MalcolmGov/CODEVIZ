/**
 * AskAIButton — inline "Ask AI about this finding" button.
 *
 * Calls /api/chat/ask with the current session and a pre-formed question
 * built from the finding, then renders the response in a collapsible panel
 * directly below the trigger — no navigation required.
 *
 * Usage:
 *   <AskAIButton
 *     label="SQL Injection"
 *     context="SQL Injection in backend/api/auth.py line 42: f-string SQL query. Impact: attacker can dump the database."
 *   />
 */

import React, { useState } from 'react'
import { useSessionStore } from '@/store/sessionStore'
import { chatService } from '@/services/chat'
import { Bot, ChevronDown, ChevronUp, RefreshCw, X } from 'lucide-react'
import clsx from 'clsx'

interface AskAIButtonProps {
  /** Short label shown in the button, e.g. "SQL Injection" */
  label?: string
  /** Full context string sent to the LLM */
  context: string
  /** Optional override question. Defaults to a standard prompt. */
  question?: string
  className?: string
}

export const AskAIButton: React.FC<AskAIButtonProps> = ({
  label, context, question, className,
}) => {
  const { currentSessionId } = useSessionStore()
  const [open, setOpen]       = useState(false)
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer]   = useState<string | null>(null)
  const [error, setError]     = useState<string | null>(null)

  const ask = async () => {
    if (!currentSessionId) return
    setLoading(true)
    setError(null)
    setOpen(true)

    const q = question || (
      `You are a senior security engineer reviewing a code finding. Here is the finding:\n\n` +
      `${context}\n\n` +
      `Please explain this issue clearly, describe the real-world risk, and give a concise code-level fix. ` +
      `Be specific and practical. Keep your answer under 200 words.`
    )

    try {
      const res = await chatService.ask(currentSessionId, q)
      setAnswer((res.data as any)?.data?.response || (res.data as any)?.response || 'No response from AI.')
    } catch (e: any) {
      setError(e?.response?.data?.error || 'AI service unavailable — is Ollama running?')
    } finally {
      setLoading(false)
    }
  }

  const handleClick = () => {
    if (open && answer) {
      setOpen(false)
    } else if (!answer && !loading) {
      ask()
    } else {
      setOpen(o => !o)
    }
  }

  return (
    <div className={clsx('inline-block', className)}>
      <button
        type="button"
        onClick={handleClick}
        disabled={!currentSessionId}
        className={clsx(
          'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-semibold transition-all duration-150 border',
          open
            ? 'border-indigo-500/30 bg-indigo-500/10 text-indigo-300'
            : 'border-white/[0.08] bg-slate-elevated text-slate-500 hover:text-indigo-400 hover:border-indigo-500/20',
          'disabled:opacity-30 disabled:cursor-not-allowed',
        )}
        title={currentSessionId ? 'Ask AI about this finding' : 'No active scan session'}
      >
        {loading
          ? <RefreshCw size={10} className="animate-spin text-indigo-400" />
          : <Bot size={10} />}
        Ask AI
        {open ? <ChevronUp size={9} /> : <ChevronDown size={9} />}
      </button>

      {open && (
        <div className="mt-2 rounded-xl border border-indigo-500/15 bg-slate-950/80 overflow-hidden w-full max-w-xl">
          {/* Header */}
          <div className="flex items-center justify-between px-3 py-2 bg-indigo-500/[0.07] border-b border-indigo-500/10">
            <div className="flex items-center gap-1.5">
              <Bot size={11} className="text-indigo-400" />
              <span className="text-[9px] font-mono text-indigo-400/70 uppercase tracking-wider">
                AI analysis{label ? ` · ${label}` : ''}
              </span>
            </div>
            <button onClick={() => setOpen(false)} className="text-slate-700 hover:text-slate-400 transition-colors">
              <X size={12} />
            </button>
          </div>

          {/* Body */}
          <div className="p-3">
            {loading && (
              <div className="flex items-center gap-2 py-2">
                <RefreshCw size={11} className="animate-spin text-indigo-400/60 shrink-0" />
                <span className="text-[11px] text-slate-600 font-mono">Thinking…</span>
              </div>
            )}
            {error && (
              <p className="text-[11px] text-red-400 leading-relaxed">{error}</p>
            )}
            {answer && !loading && (
              <p className="text-[12px] text-slate-300 leading-relaxed whitespace-pre-wrap">{answer}</p>
            )}
          </div>

          {/* Re-ask */}
          {answer && !loading && (
            <div className="px-3 pb-3">
              <button onClick={ask}
                className="text-[10px] text-indigo-400/60 hover:text-indigo-400 transition-colors flex items-center gap-1">
                <RefreshCw size={9} /> Regenerate
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
