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
      'bg-slate-surface rounded-xl border border-slate-border/50 p-6 shadow-xl relative overflow-hidden transition-all duration-300',
      hover && 'hover:-translate-y-0.5 hover:border-slate-border hover:shadow-indigo-500/5 hover:shadow-2xl',
      className
    )}
  >
    <div className="absolute inset-0 border border-white/5 pointer-events-none rounded-xl" />
    {children}
  </div>
)

