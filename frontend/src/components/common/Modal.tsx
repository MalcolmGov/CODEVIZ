import React from 'react'
import { X } from 'lucide-react'
import clsx from 'clsx'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-2xl',
  }

  return (
    <div className="fixed inset-0 bg-slate-canvas/70 backdrop-blur-md flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className={clsx(
        'bg-slate-surface rounded-xl border border-slate-border/60 shadow-2xl relative overflow-hidden w-full transition-all duration-300 transform scale-100',
        sizes[size]
      )}>
        {/* Border shine */}
        <div className="absolute inset-0 border border-white/5 pointer-events-none rounded-xl" />
        
        <div className="flex justify-between items-center p-5 border-b border-slate-border/40 bg-slate-950/30">
          <h2 className="text-lg font-semibold text-slate-100 font-display">{title}</h2>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-slate-200 transition-colors p-1 hover:bg-slate-800/40 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-6 text-slate-300 font-sans">{children}</div>
      </div>
    </div>
  )
}

