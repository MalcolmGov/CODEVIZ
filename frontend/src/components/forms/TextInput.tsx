import React from 'react'
import clsx from 'clsx'

interface TextInputProps {
  label?: string
  placeholder?: string
  value: string
  onChange: (value: string) => void
  error?: string
  type?: string
  required?: boolean
  className?: string
}

export const TextInput: React.FC<TextInputProps> = ({
  label,
  placeholder,
  value,
  onChange,
  error,
  type = 'text',
  required,
  className,
}) => (
  <div className={clsx('mb-4', className)}>
    {label && (
      <label className="block text-sm font-semibold text-slate-300 mb-1.5 font-display">
        {label} {required && <span className="text-rose-500">*</span>}
      </label>
    )}
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-4 py-2.5 bg-slate-950/40 border border-slate-border/50 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/50 transition duration-150 text-sm font-sans"
    />
    {error && <p className="text-rose-400 text-xs mt-1.5 font-mono">{error}</p>}
  </div>
)

