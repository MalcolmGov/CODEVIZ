import React from 'react'
import { Card } from '@/components/common/Card'
import { Badge } from '@/components/common/Badge'
import { Refactoring } from '@/types'
import { Code2, Sparkles } from 'lucide-react'

interface RefactoringCardProps {
  refactoring: Refactoring
  onClick: () => void
}

export const RefactoringCard: React.FC<RefactoringCardProps> = ({ refactoring, onClick }) => (
  <Card 
    hover 
    onClick={onClick}
    className="cursor-pointer border-slate-border/40 hover:border-indigo-500/30 bg-slate-surface/30 backdrop-blur-md p-5 select-none"
  >
    <div className="space-y-3.5">
      <div className="flex justify-between items-start gap-4">
        <div className="space-y-1">
          <h3 className="font-bold text-slate-100 font-display text-sm tracking-tight flex items-center gap-1.5">
            <Sparkles size={14} className="text-indigo-400 shrink-0" />
            {refactoring.type}
          </h3>
          <p className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
            <Code2 size={12} />
            <span>{(refactoring.file || '').split('/').pop() || 'Unknown'}:{refactoring.line}</span>
          </p>
        </div>
        <div className="flex gap-1.5">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono tracking-wide border border-slate-border/50 bg-slate-900 text-slate-300">
            Priority: {refactoring.priority}/10
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono tracking-wide border border-indigo-500/20 bg-indigo-500/10 text-indigo-400">
            {Math.round((refactoring.confidence || 0.8) * 100)}% Match
          </span>
        </div>
      </div>
      <p className="text-xs text-slate-400 font-sans leading-relaxed line-clamp-2 bg-slate-950/20 p-3 rounded-lg border border-slate-border/20">
        {refactoring.explanation}
      </p>
    </div>
  </Card>
)

