import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { Table } from '@/components/common/Table'
import { Badge } from '@/components/common/Badge'
import { useSessionStore } from '@/store/sessionStore'
import { useBugsStore } from '@/store/bugsStore'
import { Shield, BarChart3, RefreshCw, Terminal, CheckCircle2, ChevronRight, Activity } from 'lucide-react'

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentSessionId, sessionData } = useSessionStore()
  const { bugs } = useBugsStore()

  const criticalBugs = bugs.filter(b => b.severity === 'critical' || b.severity === 'high').length
  const totalBugs = bugs.length

  const stats = [
    { 
      label: 'Repositories Scanned', 
      value: currentSessionId ? '1' : '0', 
      icon: Terminal, 
      desc: 'Active developer environments',
      cardClass: 'border-indigo-500/20 dark:border-indigo-500/40 hover:border-indigo-500/40 dark:hover:border-indigo-500/60 bg-gradient-to-br from-indigo-50/60 via-indigo-50/20 to-slate-surface dark:from-indigo-950/60 dark:via-indigo-900/30 dark:to-slate-950/40 shadow-md dark:shadow-lg shadow-indigo-500/5 dark:shadow-indigo-500/20 hover:shadow-lg dark:hover:shadow-indigo-500/30',
      iconClass: 'text-indigo-600 dark:text-indigo-300 bg-indigo-500/10 dark:bg-indigo-500/30 border-indigo-500/20 dark:border-indigo-400/40',
      glowClass: 'bg-indigo-500/10 dark:bg-indigo-500/30 blur-3xl',
      valClass: 'bg-gradient-to-r from-indigo-600 via-indigo-500 to-indigo-700 dark:from-indigo-100 dark:via-indigo-200 dark:to-indigo-300 text-transparent bg-clip-text drop-shadow-[0_2px_8px_rgba(99,102,241,0.15)] dark:drop-shadow-[0_2px_8px_rgba(99,102,241,0.3)]'
    },
    { 
      label: 'Critical Threats', 
      value: currentSessionId ? String(criticalBugs) : '0', 
      icon: Shield, 
      desc: 'Requires immediate action',
      cardClass: 'border-rose-500/20 dark:border-rose-500/40 hover:border-rose-500/40 dark:hover:border-rose-500/60 bg-gradient-to-br from-rose-50/60 via-rose-50/20 to-slate-surface dark:from-rose-950/60 dark:via-rose-900/30 dark:to-slate-950/40 shadow-md dark:shadow-lg shadow-rose-500/5 dark:shadow-rose-500/20 hover:shadow-lg dark:hover:shadow-rose-500/30',
      iconClass: 'text-rose-600 dark:text-rose-300 bg-rose-500/10 dark:bg-rose-500/30 border-rose-500/20 dark:border-rose-400/40',
      glowClass: 'bg-rose-500/10 dark:bg-rose-500/30 blur-3xl',
      valClass: 'bg-gradient-to-r from-rose-600 via-rose-500 to-rose-700 dark:from-rose-100 dark:via-rose-200 dark:to-rose-300 text-transparent bg-clip-text drop-shadow-[0_2px_8px_rgba(244,63,94,0.15)] dark:drop-shadow-[0_2px_8px_rgba(244,63,94,0.3)]'
    },
    { 
      label: 'Refactor Opportunities', 
      value: currentSessionId ? '8' : '0', 
      icon: RefreshCw, 
      desc: 'Redundancies & quality issues',
      cardClass: 'border-amber-500/20 dark:border-amber-500/40 hover:border-amber-500/40 dark:hover:border-amber-500/60 bg-gradient-to-br from-amber-50/60 via-amber-50/20 to-slate-surface dark:from-amber-950/60 dark:via-amber-900/30 dark:to-slate-950/40 shadow-md dark:shadow-lg shadow-amber-500/5 dark:shadow-amber-500/20 hover:shadow-lg dark:hover:shadow-amber-500/30',
      iconClass: 'text-amber-600 dark:text-amber-300 bg-amber-500/10 dark:bg-amber-500/30 border-amber-500/20 dark:border-amber-400/40',
      glowClass: 'bg-amber-500/10 dark:bg-amber-500/30 blur-3xl',
      valClass: 'bg-gradient-to-r from-amber-600 via-amber-500 to-amber-700 dark:from-amber-100 dark:via-amber-200 dark:to-amber-300 text-transparent bg-clip-text drop-shadow-[0_2px_8px_rgba(245,158,11,0.15)] dark:drop-shadow-[0_2px_8px_rgba(245,158,11,0.3)]'
    },
    { 
      label: 'Global Security Score', 
      value: currentSessionId ? (totalBugs > 0 ? `${Math.max(40, 100 - totalBugs * 5)}%` : '98%') : '100%', 
      icon: CheckCircle2, 
      desc: 'Based on threat exposure',
      cardClass: 'border-emerald-500/20 dark:border-emerald-500/40 hover:border-emerald-500/40 dark:hover:border-emerald-500/60 bg-gradient-to-br from-emerald-50/60 via-emerald-50/20 to-slate-surface dark:from-emerald-950/60 dark:via-emerald-900/30 dark:to-slate-950/40 shadow-md dark:shadow-lg shadow-emerald-500/5 dark:shadow-emerald-500/20 hover:shadow-lg dark:hover:shadow-emerald-500/30',
      iconClass: 'text-emerald-600 dark:text-emerald-300 bg-emerald-500/10 dark:bg-emerald-500/30 border-emerald-500/20 dark:border-emerald-400/40',
      glowClass: 'bg-emerald-500/10 dark:bg-emerald-500/30 blur-3xl',
      valClass: 'bg-gradient-to-r from-emerald-600 via-emerald-500 to-emerald-700 dark:from-emerald-100 dark:via-emerald-200 dark:to-emerald-300 text-transparent bg-clip-text drop-shadow-[0_2px_8px_rgba(16,185,129,0.15)] dark:drop-shadow-[0_2px_8px_rgba(16,185,129,0.3)]'
    },
  ]

  const recentScansData = currentSessionId ? [
    {
      repo: sessionData?.repo_path || '/app/src',
      id: currentSessionId,
      vulnerabilities: `${totalBugs} issues`,
      status: totalBugs > 0 ? 'Threats Found' : 'Clean',
      timestamp: 'Just now'
    }
  ] : []

  return (
    <div className="space-y-8 select-none">
      {/* Header section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">Security Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1.5 font-medium">
            Welcome, Malcolm Govender. Your development sandboxes are monitored.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-slate-900/50 border border-slate-border/30 rounded-xl px-4 py-2 text-xs font-semibold text-slate-300 font-mono">
          <Activity size={14} className="text-emerald-400 animate-pulse" />
          <span>VULNERABILITY ENGINE ACTIVE</span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {stats.map((stat, idx) => (
          <Card key={idx} hover className={`relative overflow-hidden transition-all duration-300 ${stat.cardClass}`}>
            {/* Ambient Corner Glow */}
            <div className={`absolute -top-8 -right-8 w-24 h-24 rounded-full blur-2xl pointer-events-none transition-opacity duration-300 ${stat.glowClass}`} />
            
            <div className="flex justify-between items-start relative z-10">
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider font-display">
                {stat.label}
              </span>
              <div className={`p-2 rounded-lg border transition-colors duration-300 ${stat.iconClass}`}>
                <stat.icon size={18} />
              </div>
            </div>
            <div className="mt-4 relative z-10">
              <p className={`text-3xl font-black font-display tracking-tight ${stat.valClass}`}>
                {stat.value}
              </p>
              <p className="text-slate-500 text-[11px] mt-1 font-mono">{stat.desc}</p>
            </div>
          </Card>
        ))}
      </div>

      {/* Main split sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scans table */}
        <Card className="lg:col-span-2 border-slate-500/30 bg-gradient-to-br from-slate-800/50 via-slate-850/40 to-slate-900/50 backdrop-blur-md flex flex-col justify-between shadow-lg">
          <div>
            <h2 className="text-lg font-bold text-slate-100 mb-2 font-display">Active Repository Scans</h2>
            <p className="text-slate-400 text-xs mb-6 font-medium">Verify recent scanning logs and active session threats.</p>
            
            {recentScansData.length > 0 ? (
              <Table 
                columns={[
                  { key: 'repo', label: 'Repository Location' },
                  { key: 'vulnerabilities', label: 'Threats Discovered' },
                  { 
                    key: 'status', 
                    label: 'Engine Status',
                    render: (row) => (
                      <Badge severity={row.status === 'Clean' ? 'low' : 'critical'}>
                        {row.status}
                      </Badge>
                    )
                  },
                  { key: 'timestamp', label: 'Scanned At' }
                ]}
                data={recentScansData}
                onRowClick={() => navigate('/security')}
              />
            ) : (
              <div className="text-center py-12 border border-dashed border-slate-border/50 rounded-xl bg-slate-900/10">
                <Terminal size={32} className="mx-auto text-slate-600 mb-3" />
                <h3 className="text-sm font-semibold text-slate-300 font-display">No scan sessions active</h3>
                <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
                  Execute code scanner analysis on your repository to view security vulnerabilities.
                </p>
                <Button 
                  onClick={() => navigate('/scanner')} 
                  variant="secondary" 
                  size="sm" 
                  className="mt-4 border-slate-border/80 hover:bg-slate-800"
                >
                  Configure scan path
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Quick actions panel */}
        <Card className="border-slate-500/30 bg-gradient-to-br from-slate-800/50 via-slate-850/40 to-slate-900/50 backdrop-blur-md flex flex-col justify-between shadow-lg">
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-slate-100 font-display">Engine Controls</h2>
            <p className="text-slate-400 text-xs font-medium">Quick navigation links to perform scan commands.</p>
            
            <div className="space-y-2.5 pt-2">
              {[
                { 
                  title: 'Scanner Engine', 
                  desc: 'Initiate file scanner & parse codebase AST structure',
                  href: '/scanner',
                  icon: BarChart3
                },
                { 
                  title: 'Security Center', 
                  desc: 'Review security bugs and recommended fix patches',
                  href: '/security',
                  icon: Shield
                },
                { 
                  title: 'Refactor Pipeline', 
                  desc: 'Generate pull request recommendations',
                  href: '/refactoring',
                  icon: RefreshCw
                }
              ].map((act, i) => (
                <button
                  key={i}
                  onClick={() => navigate(act.href)}
                  className="w-full text-left p-3.5 rounded-xl bg-slate-950/40 border border-slate-border/40 hover:border-indigo-500/30 hover:bg-indigo-500/5 transition-all duration-200 group flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-border/60 text-slate-400 group-hover:text-indigo-400 group-hover:border-indigo-500/20 transition-all duration-200">
                      <act.icon size={16} />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-200 group-hover:text-indigo-300 font-display">
                        {act.title}
                      </h4>
                      <p className="text-[10px] text-slate-500 mt-0.5 max-w-[170px] truncate">{act.desc}</p>
                    </div>
                  </div>
                  <ChevronRight size={14} className="text-slate-600 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
                </button>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

