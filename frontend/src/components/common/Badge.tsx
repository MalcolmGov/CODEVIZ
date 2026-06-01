import React from 'react'
import clsx from 'clsx'

interface BadgeProps {
  children: React.ReactNode
  severity?: 'critical' | 'high' | 'medium' | 'low'
  className?: string
}

export const Badge: React.FC<BadgeProps> = ({ children, severity, className }) => {
  const colors = {
    critical: 'bg-rose-500/10 text-rose-400 border border-rose-500/20 shadow-sm shadow-rose-500/5',
    high: 'bg-amber-500/10 text-amber-450 text-amber-400 border border-amber-500/20 shadow-sm shadow-amber-500/5',
    medium: 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 shadow-sm shadow-yellow-500/5',
    low: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-sm shadow-emerald-500/5',
  }

  return (
    <span className={clsx(
      'px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide border font-sans inline-flex items-center gap-1.5',
      colors[severity || 'medium'],
      className
    )}>
      <span className={clsx(
        'w-1.5 h-1.5 rounded-full animate-pulse',
        severity === 'critical' && 'bg-rose-400',
        severity === 'high' && 'bg-amber-400',
        severity === 'medium' && 'bg-yellow-400',
        (severity === 'low' || !severity) && 'bg-emerald-400'
      )} />
      {children}
    </span>
  )
}

