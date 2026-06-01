import React, { useState } from 'react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex flex-col h-screen bg-transparent text-slate-100 relative overflow-hidden select-none font-sans">
      {/* Background radial glow */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-violet-600/5 rounded-full blur-[120px] pointer-events-none" />

      <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-1 overflow-hidden relative z-10">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 overflow-auto p-6 lg:p-8 relative z-10 fade-in">
          {children}
        </main>
      </div>
    </div>
  )
}

