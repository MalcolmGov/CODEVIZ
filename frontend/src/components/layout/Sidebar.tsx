import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { BarChart3, Shield, RefreshCw, Settings, Home, User, Terminal } from 'lucide-react'
import clsx from 'clsx'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const menuItems = [
  { icon: Home, label: 'Dashboard', href: '/' },
  { icon: BarChart3, label: 'Scanner', href: '/scanner' },
  { icon: Shield, label: 'Security', href: '/security' },
  { icon: RefreshCw, label: 'Refactoring', href: '/refactoring' },
  { icon: Settings, label: 'Settings', href: '/settings' },
]

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation()

  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-slate-canvas/60 backdrop-blur-sm lg:hidden z-30" onClick={onClose} />}
      <aside
        className={clsx(
          'fixed left-0 top-16 bottom-0 w-64 bg-slate-surface/40 backdrop-blur-md border-r border-slate-border/40 transition-transform lg:relative lg:top-0 z-40 flex flex-col justify-between',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="absolute inset-0 border-r border-white/5 pointer-events-none" />
        
        <nav className="p-4 space-y-1.5 flex-1 mt-2">
          {menuItems.map(({ icon: Icon, label, href }) => {
            const isActive = location.pathname === href
            return (
              <Link
                key={href}
                to={href}
                onClick={onClose}
                className={clsx(
                  'flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 border font-medium text-sm',
                  isActive
                    ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20 shadow-sm shadow-indigo-500/5'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/30 border-transparent'
                )}
              >
                <Icon size={18} className={clsx(
                  'transition-colors duration-200',
                  isActive ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'
                )} />
                {label}
              </Link>
            )
          })}
        </nav>

        {/* Developer Profile Card */}
        <div className="p-4 border-t border-slate-border/40 bg-slate-950/30">
          <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-900/40 border border-slate-border/20">
            <div className="relative">
              <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
                <User size={18} />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-slate-900 rounded-full" />
            </div>
            <div className="overflow-hidden">
              <h4 className="text-xs font-semibold text-slate-200 truncate font-display">Malcolm Govender</h4>
              <p className="text-[10px] text-slate-500 truncate flex items-center gap-1 font-mono">
                <Terminal size={10} /> developer
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

