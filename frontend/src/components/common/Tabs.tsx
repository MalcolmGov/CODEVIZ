import React, { useState } from 'react'
import clsx from 'clsx'

interface TabsProps {
  tabs: Array<{ id: string; label: string; content: React.ReactNode }>
  defaultTab?: string
  activeTab?: string
  onChange?: (id: string) => void
}

export const Tabs: React.FC<TabsProps> = ({ tabs, defaultTab, activeTab: controlledActiveTab, onChange }) => {
  const [localActiveTab, setLocalActiveTab] = useState(defaultTab || tabs[0]?.id)
  
  const isControlled = controlledActiveTab !== undefined
  const activeTab = isControlled ? controlledActiveTab : localActiveTab

  const handleTabClick = (id: string) => {
    if (onChange) {
      onChange(id)
    }
    if (!isControlled) {
      setLocalActiveTab(id)
    }
  }

  return (
    <div>
      <div className="border-b border-slate-border/50 flex gap-4 overflow-x-auto pb-1 scrollbar-none whitespace-nowrap">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={clsx(
              'px-4 py-2 font-medium border-b-2 -mb-px transition-colors',
              activeTab === tab.id ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="mt-4">
        {tabs.find((tab) => tab.id === activeTab)?.content}
      </div>
    </div>
  )
}

