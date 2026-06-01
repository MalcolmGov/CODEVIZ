import React from 'react'
import clsx from 'clsx'

interface SelectInputProps {
  label?: string
  options: Array<{ value: string; label: string }>
  value: string
  onChange: (value: string) => void
  error?: string
  required?: boolean
  className?: string
}

export const SelectInput: React.FC<SelectInputProps> = ({
  label,
  options,
  value,
  onChange,
  error,
  required,
  className,
}) => (
  <div className={clsx('mb-4', className)}>
    {label && (
      <label className="block text-sm font-semibold text-slate-300 mb-1.5 font-display">
        {label} {required && <span className="text-rose-500">*</span>}
      </label>
    )}
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-4 py-2.5 bg-slate-950/40 border border-slate-border/50 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/50 transition duration-150 text-sm font-sans"
    >
      <option value="" className="bg-slate-900 text-slate-300">Select...</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value} className="bg-slate-900 text-slate-100">
          {opt.label}
        </option>
      ))}
    </select>
    {error && <p className="text-rose-400 text-xs mt-1.5 font-mono">{error}</p>}
  </div>
)

