import React from 'react'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { useAuthStore } from '@/store/authStore'
import { User, Shield, KeyRound, Bell } from 'lucide-react'

export const SettingsPage: React.FC = () => {
  const { user } = useAuthStore()

  return (
    <div className="space-y-8 max-w-2xl select-none font-sans">
      <div>
        <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">System Settings</h1>
        <p className="text-slate-400 text-sm mt-1.5 font-medium">Manage security preferences and workspace integrations.</p>
      </div>

      <div className="space-y-6">
        <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md">
          <div className="flex items-center gap-2.5 pb-4 border-b border-slate-border/20 mb-4">
            <User size={18} className="text-indigo-400" />
            <h2 className="text-base font-bold text-slate-100 font-display">Developer Profile</h2>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm font-mono">
            <div>
              <p className="text-xs text-slate-500 mb-1">Name</p>
              <p className="text-slate-200 font-bold">{user?.name || 'Malcolm Govender'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Email</p>
              <p className="text-slate-200 font-bold">{user?.email || 'malcolm@example.com'}</p>
            </div>
          </div>
        </Card>

        <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md">
          <div className="flex items-center gap-2.5 pb-4 border-b border-slate-border/20 mb-4">
            <Shield size={18} className="text-emerald-400" />
            <h2 className="text-base font-bold text-slate-100 font-display">Integrations</h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 rounded-lg bg-slate-950/40 border border-slate-border/30">
              <div>
                <p className="text-xs font-bold text-slate-200 font-display">GitHub Connection</p>
                <p className="text-[10px] text-slate-500 mt-0.5">Authorizes automated scanning on PR events.</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono tracking-wide bg-emerald-500/10 border border-emerald-500/20 text-emerald-455 text-emerald-400">
                CONNECTED
              </span>
            </div>
          </div>
        </Card>

        <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md opacity-60">
          <div className="flex items-center gap-2.5 pb-4 border-b border-slate-border/20 mb-4">
            <KeyRound size={18} className="text-slate-500" />
            <h2 className="text-base font-bold text-slate-400 font-display">Preferences</h2>
          </div>
          <p className="text-xs text-slate-500 font-mono">Advanced workspace profiles & scanner custom settings coming soon...</p>
        </Card>
      </div>
    </div>
  )
}

