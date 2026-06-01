import React from 'react'
import { Card } from '@/components/common/Card'

interface CodeDiffViewerProps {
  before: string
  after: string
}

export const CodeDiffViewer: React.FC<CodeDiffViewerProps> = ({ before, after }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-5 select-none">
    <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md flex flex-col justify-between">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-display">Original Code</h4>
        <span className="w-2 h-2 rounded-full bg-rose-500" />
      </div>
      <pre className="bg-[#0e0406] p-4 border border-rose-950/50 rounded-xl text-xs font-mono overflow-x-auto text-rose-300 border-l-4 border-l-rose-500/80 leading-relaxed max-h-[300px]">
        <code>{before}</code>
      </pre>
    </Card>
    
    <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md flex flex-col justify-between">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-display">AI Refactored Code</h4>
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
      </div>
      <pre className="bg-[#040d0e] p-4 border border-emerald-950/50 rounded-xl text-xs font-mono overflow-x-auto text-emerald-300 border-l-4 border-l-emerald-500/80 leading-relaxed max-h-[300px]">
        <code>{after}</code>
      </pre>
    </Card>
  </div>
)

