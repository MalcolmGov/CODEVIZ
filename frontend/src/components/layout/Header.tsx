import React, { useState, useEffect, useRef } from 'react'
import { Menu, LogOut, Shield, RefreshCw, Sun, Moon } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/auth'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '@/services/api'
import clsx from 'clsx'

interface HealthServiceStatus {
  status: string
  type: string
  error?: string
}

interface HealthData {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'checking' | 'unknown'
  services: {
    app?: HealthServiceStatus
    database?: HealthServiceStatus
    cache?: HealthServiceStatus
    ollama?: HealthServiceStatus
  }
}

export const Header: React.FC<{ onMenuClick: () => void }> = ({ onMenuClick }) => {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const [healthStatus, setHealthStatus] = useState<HealthData>({
    status: 'checking',
    services: {}
  })
  const [popoverOpen, setPopoverOpen] = useState(false)
  const popoverRef = useRef<HTMLDivElement>(null)

  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    try {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme === 'light' || savedTheme === 'dark') {
        return savedTheme
      }
    } catch (e) {
      console.warn('localStorage not available', e)
    }
    return 'dark' // default to dark
  })

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.remove('dark')
      document.documentElement.classList.add('light')
    } else {
      document.documentElement.classList.remove('light')
      document.documentElement.classList.add('dark')
    }
    try {
      localStorage.setItem('theme', theme)
    } catch (e) {
      console.warn('localStorage not available', e)
    }
  }, [theme])

  const checkHealth = async () => {
    try {
      const response = await api.get('/health')
      setHealthStatus({
        status: response.data.status === 'healthy' ? 'healthy' : 'degraded',
        services: response.data.services || {}
      })
    } catch (err: any) {
      if (err.response?.status === 503 && err.response?.data) {
        setHealthStatus({
          status: err.response.data.status || 'unhealthy',
          services: err.response.data.services || {}
        })
      } else {
        setHealthStatus({
          status: 'unhealthy',
          services: {
            app: { status: 'unhealthy', type: 'Flask' }
          }
        })
      }
    }
  }

  useEffect(() => {
    checkHealth()
    const timer = setInterval(checkHealth, 30000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setPopoverOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  const handleLogout = async () => {
    try {
      await authService.logout()
      logout()
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <header className="bg-slate-surface/40 backdrop-blur-md border-b border-slate-border/40 relative z-50">
      {/* Top border shine */}
      <div className="absolute inset-x-0 top-0 h-px bg-white/5 pointer-events-none" />
      
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <button onClick={onMenuClick} className="lg:hidden text-slate-400 hover:text-slate-200 p-1 hover:bg-slate-800/40 rounded-lg">
            <Menu size={22} />
          </button>
          
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/15 group-hover:scale-105 transition-transform duration-200">
              <Shield size={16} className="text-white" />
            </div>
            <span className="text-xl font-extrabold tracking-tight text-slate-100 font-display">
              Code<span className="text-indigo-400 font-medium">Viz</span>
            </span>
          </Link>
        </div>
        
        {user && (
          <div className="flex items-center gap-4">
            {/* Global API Health Monitor */}
            <div className="relative" ref={popoverRef}>
              <button
                onClick={() => setPopoverOpen(!popoverOpen)}
                className={clsx(
                  "flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold font-mono transition-all duration-250 select-none",
                  healthStatus.status === 'healthy' && "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/15 hover:border-emerald-500/40",
                  healthStatus.status === 'degraded' && "bg-amber-500/10 border-amber-500/30 text-amber-400 hover:bg-amber-500/15 hover:border-amber-500/40",
                  healthStatus.status === 'unhealthy' && "bg-rose-500/10 border-rose-500/30 text-rose-400 hover:bg-rose-500/15 hover:border-rose-500/40",
                  healthStatus.status === 'checking' && "bg-slate-900/40 border-slate-border/20 text-slate-400"
                )}
              >
                <span className={clsx(
                  "w-1.5 h-1.5 rounded-full",
                  healthStatus.status === 'healthy' && "bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]",
                  healthStatus.status === 'degraded' && "bg-amber-500 animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.5)]",
                  healthStatus.status === 'unhealthy' && "bg-rose-500 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.5)]",
                  healthStatus.status === 'checking' && "bg-slate-500 animate-pulse"
                )} />
                <span className="hidden sm:inline">
                  API: {healthStatus.status.charAt(0).toUpperCase() + healthStatus.status.slice(1)}
                </span>
                <span className="sm:hidden">
                  API
                </span>
              </button>

              {popoverOpen && (
                <div className="absolute right-0 mt-2.5 w-72 rounded-xl bg-slate-surface border border-slate-border shadow-2xl p-4 z-50 space-y-3 animate-fade-in">
                  <div className="flex justify-between items-center pb-2 border-b border-slate-border/40">
                    <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-display">System Health Status</h4>
                    <button 
                      onClick={() => {
                        setHealthStatus(prev => ({ ...prev, status: 'checking' }))
                        checkHealth()
                      }}
                      className="text-slate-500 hover:text-indigo-400 transition-colors p-1"
                      title="Run Health Diagnostics"
                    >
                      <RefreshCw size={12} className={healthStatus.status === 'checking' ? 'animate-spin text-indigo-400' : ''} />
                    </button>
                  </div>

                  <div className="space-y-2.5">
                    {/* App Server */}
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                        Core API Server
                      </span>
                      <span className={clsx(
                        "font-mono font-bold",
                        healthStatus.status !== 'unhealthy' ? "text-emerald-400" : "text-rose-450 text-rose-400"
                      )}>
                        {healthStatus.status !== 'unhealthy' ? 'Online' : 'Offline'}
                      </span>
                    </div>

                    {/* Database */}
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-violet-500" />
                        PostgreSQL Database
                      </span>
                      <span className={clsx(
                        "font-mono font-bold",
                        healthStatus.services.database?.status === 'healthy' ? "text-emerald-400" : "text-rose-450 text-rose-400"
                      )}>
                        {healthStatus.services.database?.status === 'healthy' ? 'Online' : 'Offline'}
                      </span>
                    </div>

                    {/* Cache */}
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-sky-500" />
                        Redis Cache
                      </span>
                      <span className={clsx(
                        "font-mono font-bold",
                        healthStatus.services.cache?.status === 'healthy' ? "text-emerald-400" : 
                        healthStatus.services.cache?.status === 'unavailable' ? "text-slate-500" : "text-rose-450 text-rose-400"
                      )}>
                        {healthStatus.services.cache?.status === 'healthy' ? 'Online' : 
                         healthStatus.services.cache?.status === 'unavailable' ? 'Unavailable' : 'Offline'}
                      </span>
                    </div>

                    {/* Ollama LLM */}
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        Ollama AI (LLM)
                      </span>
                      <span className={clsx(
                        "font-mono font-bold",
                        healthStatus.services.ollama?.status === 'healthy' ? "text-emerald-400" : "text-rose-450 text-rose-400"
                      )}>
                        {healthStatus.services.ollama?.status === 'healthy' ? 'Online' : 'Offline'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Theme Switcher Button */}
            <button
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              className="text-slate-450 hover:text-indigo-400 p-2 hover:bg-slate-800/30 border border-transparent rounded-lg transition-all duration-200"
              title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/40 border border-slate-border/20 text-xs text-slate-300 font-medium">
              <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
              <span>{user.name}</span>
            </div>
            
            <button 
              onClick={handleLogout} 
              className="text-slate-400 hover:text-rose-400 p-2 hover:bg-rose-500/5 hover:border-rose-500/10 border border-transparent rounded-lg transition-all duration-200"
              title="Sign Out"
            >
              <LogOut size={18} />
            </button>
          </div>
        )}
      </div>
    </header>
  )
}


