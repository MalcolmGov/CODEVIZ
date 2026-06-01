import React, { useState, useRef } from 'react'
import clsx from 'clsx'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface TabsProps {
  tabs: Array<{ id: string; label: string; content: React.ReactNode }>
  defaultTab?: string
  activeTab?: string
  onChange?: (id: string) => void
}

export const Tabs: React.FC<TabsProps> = ({ tabs, defaultTab, activeTab: controlledActiveTab, onChange }) => {
  const [localActiveTab, setLocalActiveTab] = useState(defaultTab || tabs[0]?.id)
  const scrollRef = useRef<HTMLDivElement>(null)

  const isControlled = controlledActiveTab !== undefined
  const activeTab = isControlled ? controlledActiveTab : localActiveTab

  const handleTabClick = (id: string) => {
    if (onChange) onChange(id)
    if (!isControlled) setLocalActiveTab(id)
  }

  const scroll = (dir: 'left' | 'right') => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: dir === 'right' ? 240 : -240, behavior: 'smooth' })
    }
  }

  return (
    <div>
      <div className="relative flex items-center border-b border-slate-border/50">
        {/* Left arrow */}
        <button
          onClick={() => scroll('left')}
          className="shrink-0 p-1 text-slate-500 hover:text-indigo-400 transition-colors"
        >
          <ChevronLeft size={16} />
        </button>

        {/* Scrollable tab row */}
        <div
          ref={scrollRef}
          className="flex gap-1 overflow-x-auto pb-1 scrollbar-none whitespace-nowrap flex-1"
        >
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={clsx(
                'px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors shrink-0',
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Right arrow */}
        <button
          onClick={() => scroll('right')}
          className="shrink-0 p-1 text-slate-500 hover:text-indigo-400 transition-colors"
        >
          <ChevronRight size={16} />
        </button>
      </div>

      <div className="mt-4">
        {tabs.find((tab) => tab.id === activeTab)?.content}
      </div>
    </div>
  )
}

