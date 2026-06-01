import React from 'react'
import { Menu, LogOut, Shield } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/auth'
import { Link, useNavigate } from 'react-router-dom'

export const Header: React.FC<{ onMenuClick: () => void }> = ({ onMenuClick }) => {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

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

