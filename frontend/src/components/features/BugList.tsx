import React from 'react'
import { Badge } from '@/components/common/Badge'
import { Card } from '@/components/common/Card'
import { Issue } from '@/types'
import { AlertOctagon, Code, ShieldAlert, Cpu } from 'lucide-react'
import clsx from 'clsx'

interface BugListProps {
  bugs: Issue[]
  onSelectBug: (bug: Issue) => void
}

export const BugList: React.FC<BugListProps> = ({ bugs, onSelectBug }) => (
  <div className="space-y-4">
    {bugs.length === 0 ? (
      <Card className="bg-slate-surface/20 border-slate-border/30">
        <div className="text-center py-16">
          <ShieldAlert size={36} className="mx-auto text-slate-500 mb-3" />
          <h3 className="text-sm font-semibold text-slate-300 font-display">No threats detected</h3>
          <p className="text-xs text-slate-500 mt-1">This repository is free of immediate static vulnerability threats.</p>
        </div>
      </Card>
    ) : (
      bugs.map((bug) => {
        const sevClass = bug.severity?.toLowerCase() || 'medium'
        const isCritical = sevClass.includes('critical')
        const isHigh = sevClass.includes('high')
        const isMedium = sevClass.includes('medium')
        
        return (
          <Card 
            key={bug.id || bug.bug_id} 
            hover 
            onClick={() => onSelectBug(bug)}
            className="cursor-pointer border-slate-border/40 hover:border-indigo-500/30 bg-slate-surface/30 backdrop-blur-md transition-all duration-200"
          >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <span className={clsx(
                    'px-2 py-0.5 rounded text-[10px] font-bold font-mono tracking-wide border uppercase',
                    isCritical && 'bg-rose-500/10 text-rose-450 border-rose-500/20 text-rose-400',
                    isHigh && 'bg-amber-500/10 text-amber-450 border-amber-500/20 text-amber-450 text-amber-405 text-amber-400',
                    isMedium && 'bg-yellow-500/10 text-yellow-450 border-yellow-500/20 text-yellow-400',
                    (!isCritical && !isHigh && !isMedium) && 'bg-emerald-500/10 text-emerald-450 border-emerald-500/20 text-emerald-400'
                  )}>
                    {bug.severity?.replace(/[^a-zA-Z]/g, '') || 'LOW'}
                  </span>
                  
                  {bug.cwe && (
                    <span className="text-[10px] text-slate-500 font-mono">
                      {bug.cwe}
                    </span>
                  )}
                </div>
                
                <h4 className="text-sm font-bold text-slate-100 font-display line-clamp-2">
                  {bug.message}
                </h4>
                
                <div className="flex items-center gap-4 text-[11px] text-slate-500 font-mono">
                  <span className="flex items-center gap-1">
                    <Code size={12} />
                    <span>{(bug.file || '').split('/').pop() || 'Unknown'}:{bug.line}</span>
                  </span>
                  {bug.cvss !== undefined && (
                    <span className="flex items-center gap-1">
                      <Cpu size={12} />
                      <span>CVSS: {bug.cvss}</span>
                    </span>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-2 md:self-center">
                <div className="text-xs text-slate-400 font-mono bg-slate-900 border border-slate-border/50 px-2 py-1 rounded-lg">
                  {Math.round((bug.confidence || 0.8) * 100)}% Match
                </div>
              </div>
            </div>
          </Card>
        )
      })
    )}
  </div>
)

