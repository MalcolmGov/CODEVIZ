import React from 'react'

export const Loader: React.FC<{ text?: string }> = ({ text = 'Analyzing code viz...' }) => (
  <div className="flex flex-col items-center justify-center p-12">
    <div className="relative flex items-center justify-center">
      {/* Outer Glow Ring */}
      <div className="absolute w-14 h-14 rounded-full border border-indigo-500/30 animate-ping opacity-25" />
      {/* Spinner */}
      <div className="w-12 h-12 rounded-full border-2 border-slate-800 border-t-indigo-500 animate-spin" />
    </div>
    {text && <p className="mt-5 text-sm font-medium tracking-wide text-slate-400 font-display animate-pulse">{text}</p>}
  </div>
)

