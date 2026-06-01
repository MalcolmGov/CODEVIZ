import React from 'react'
import clsx from 'clsx'

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  onClick?: () => void
}

export const Card: React.FC<CardProps> = ({ children, className, hover = false, onClick }) => (
  <div 
    onClick={onClick}
    className={clsx(
      'bg-slate-surface rounded-xl border border-slate-border/50 p-6 shadow-2xl relative overflow-hidden transition-all duration-300',
      'bg-gradient-to-br from-slate-800/40 to-slate-900/60',
      hover && 'hover:-translate-y-1 hover:border-slate-border hover:shadow-indigo-500/10 hover:shadow-2xl cursor-pointer',
      className
    )}
  >
    <div className="absolute inset-0 border border-white/5 pointer-events-none rounded-xl" />
    {children}
  </div>
)

