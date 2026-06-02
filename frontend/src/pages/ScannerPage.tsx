import React, { useState, useEffect, useRef } from 'react'
import { ScanForm } from '@/components/features/ScanForm'
import { Tabs } from '@/components/common/Tabs'
import { Table } from '@/components/common/Table'
import { Badge } from '@/components/common/Badge'
import { useSessionStore } from '@/store/sessionStore'
import { useBugsStore } from '@/store/bugsStore'
import { useRefactoringStore } from '@/store/refactoringStore'
import { chatService } from '@/services/chat'
import { scoringService, RiskProfile } from '@/services/scoring'
import { securityService, cveService } from '@/services/security'
import { refactoringService } from '@/services/refactoring'
import {
  Terminal, ShieldCheck, Cpu, Code2, Server, Globe, Shield,
  Layers, Package, Settings, Activity, FolderGit2, Search, ArrowRight,
  FileCode2, ShieldAlert, Split, Database, ListPlus, Link, Hash, Key, Palette,
  RefreshCw, ChevronRight, ArrowUpRight, BarChart3, Trophy, AlertTriangle, CheckCircle2, Info,
  MessageSquare, Send, Zap, GitBranch,
} from 'lucide-react'
import { Network, DataSet } from 'vis-network/standalone'
import 'vis-network/styles/vis-network.css'
import { api } from '@/services/api'
import clsx from 'clsx'

const CARD = 'rounded-2xl border border-white/[0.08] border-t-white/[0.15] bg-slate-surface shadow-card backdrop-blur-md transition-all duration-300 hover:border-white/[0.14] hover:shadow-[0_0_24px_-6px_rgba(99,102,241,0.06)]'

// Inline parser for bold (**), inline code (`), and links ([text](url))
const parseInlineMarkdown = (text: string) => {
  const regex = /(\*\*.*?\*\*|`.*?`|\[.*?\]\(.*?\))/g
  const parts = text.split(regex)
  
  if (parts.length === 1) return text
  
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-bold text-slate-100">{part.slice(2, -2)}</strong>
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="bg-indigo-950/40 text-indigo-300 px-1.5 py-0.5 rounded font-mono text-[10.5px] border border-indigo-500/10">
          {part.slice(1, -1)}
        </code>
      )
    }
    const linkMatch = part.match(/^\[(.*?)\]\((.*?)\)$/)
    if (linkMatch) {
      return (
        <a 
          key={i} 
          href={linkMatch[2]} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="text-indigo-400 hover:text-indigo-300 underline font-semibold transition-colors font-mono"
        >
          {linkMatch[1]}
        </a>
      )
    }
    return part
  })
}

interface MarkdownRendererProps {
  content: string
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  if (!content) return null
  
  // Split content by code blocks
  const parts = content.split(/(```[\s\S]*?```)/g)
  
  return (
    <div className="space-y-3 text-slate-300 text-xs font-sans leading-relaxed">
      {parts.map((part, idx) => {
        if (part.startsWith('```')) {
          const lines = part.split('\n')
          const lang = lines[0].replace('```', '').trim()
          const code = lines.slice(1, -1).join('\n')
          return (
            <div key={idx} className="relative group/code my-2 font-mono text-[11px] bg-slate-950/80 rounded-lg border border-slate-border/30 overflow-hidden">
              {lang && (
                <div className="flex justify-between items-center px-3 py-1.5 bg-slate-900 border-b border-slate-border/20 text-[10px] text-slate-500 font-bold uppercase">
                  <span>{lang}</span>
                  <button 
                    type="button"
                    onClick={() => navigator.clipboard.writeText(code)}
                    className="hover:text-indigo-400 transition-colors"
                  >
                    Copy
                  </button>
                </div>
              )}
              <pre className="p-3 overflow-x-auto text-slate-300 leading-relaxed max-h-[300px]">
                <code>{code}</code>
              </pre>
            </div>
          )
        } else {
          const lines = part.split('\n')
          return (
            <div key={idx} className="space-y-1">
              {lines.map((line, lIdx) => {
                const trimmed = line.trim()
                
                if (trimmed.startsWith('###')) {
                  return (
                    <h5 key={lIdx} className="text-xs font-bold text-slate-100 font-display mt-3 mb-1.5 flex items-center gap-1.5">
                      {parseInlineMarkdown(trimmed.replace(/^###\s*/, ''))}
                    </h5>
                  )
                }
                if (trimmed.startsWith('##')) {
                  return (
                    <h4 key={lIdx} className="text-sm font-bold text-indigo-400 font-display mt-4 mb-2">
                      {parseInlineMarkdown(trimmed.replace(/^##\s*/, ''))}
                    </h4>
                  )
                }
                if (trimmed.startsWith('#')) {
                  return (
                    <h3 key={lIdx} className="text-base font-extrabold text-indigo-300 font-display mt-4 mb-2">
                      {parseInlineMarkdown(trimmed.replace(/^#\s*/, ''))}
                    </h3>
                  )
                }
                
                if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
                  return (
                    <div key={lIdx} className="flex items-start gap-2 pl-2 my-1">
                      <span className="text-indigo-400 mt-1.5 shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-500/80" />
                      <span className="flex-1">{parseInlineMarkdown(trimmed.replace(/^[-*]\s*/, ''))}</span>
                    </div>
                  )
                }
                
                if (!trimmed) {
                  return <div key={lIdx} className="h-2" />
                }
                
                return (
                  <p key={lIdx} className="leading-relaxed">
                    {parseInlineMarkdown(line)}
                  </p>
                )
              })}
            </div>
          )
        }
      })}
    </div>
  )
}

export const ScannerPage: React.FC = () => {
  const { currentSessionId, setSessionId: setGlobalSessionId, remediationMode, setRemediationMode } = useSessionStore()
  const [sessionId, setSessionId] = useState<string | null>(currentSessionId)
  const [artifacts, setArtifacts] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [activeStep, setActiveStep] = useState(0)
  const [selectedKeyFile, setSelectedKeyFile] = useState<any>(null)
  const networkRef = useRef<HTMLDivElement>(null)
  const [searchQueries, setSearchQueries] = useState<Record<string, string>>({})
  const [currentPages, setCurrentPages] = useState<Record<string, number>>({})
  const [apiHealth, setApiHealth] = useState<Record<string, { loading: boolean; status: string; code?: number; message?: string }>>({})
  const [customBaseUrl, setCustomBaseUrl] = useState<string>('')
  const [riskProfile, setRiskProfile] = useState<RiskProfile | null>(null)
  const [riskLoading, setRiskLoading] = useState(false)

  const [currentTab, setCurrentTab] = useState<string>('overview')
  const [pingProgress, setPingProgress] = useState(0)
  const [isPingingAll, setIsPingingAll] = useState(false)

  const [chatMessages, setChatMessages] = useState<any[]>([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Security + refactoring data for security-first overview
  const { bugs, setBugs } = useBugsStore()
  const { opportunities, setOpportunities } = useRefactoringStore()
  const [securityLoading, setSecurityLoading] = useState(false)
  const [refactorLoading, setRefactorLoading] = useState(false)

  // CVE scan state
  const [cveResults, setCveResults]   = useState<any[]>([])
  const [cveSummary, setCveSummary]   = useState<any>(null)
  const [cveScanned, setCveScanned]   = useState(0)
  const [cveAffected, setCveAffected] = useState(0)
  const [cveLoading, setCveLoading]   = useState(false)
  const [cveRan, setCveRan]           = useState(false)

  // Scroll to bottom of chat when messages change or tab changes to chat
  useEffect(() => {
    if (currentTab === 'chat') {
      setTimeout(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 50)
    }
  }, [chatMessages, currentTab])

  const handleSendQuestion = async (text: string) => {
    if (!text.trim() || chatLoading || !sessionId) return
    
    const userMsg = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    }
    setChatMessages(prev => [...prev, userMsg])
    setChatInput('')
    setChatLoading(true)
    
    try {
      const response = await chatService.ask(sessionId, text)
      const data = response.data.data
      
      const assistantMsg = {
        role: 'assistant',
        content: data.answer,
        timestamp: new Date().toISOString()
      }
      setChatMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      console.error('Failed to ask chatbot:', err)
      const errorMsg = {
        role: 'assistant',
        content: '❌ Sorry, there was an issue querying the AST session context. Please make sure the backend server is running and healthy.',
        timestamp: new Date().toISOString()
      }
      setChatMessages(prev => [...prev, errorMsg])
    } finally {
      setChatLoading(false)
    }
  }

  const handleTestEndpoint = async (path: string, method: string, baseUrl?: string) => {
    setApiHealth(prev => ({
      ...prev,
      [path]: { loading: true, status: 'Testing...' }
    }))
    try {
      const response = await api.post('/health/ping-endpoint', { path, method, base_url: customBaseUrl || baseUrl })
      const resData = response.data.data || response.data
      setApiHealth(prev => ({
        ...prev,
        [path]: {
          loading: false,
          status: resData.is_active ? 'Online' : 'Offline',
          code: resData.status_code,
          message: resData.message
        }
      }))
    } catch (err) {
      setApiHealth(prev => ({
        ...prev,
        [path]: {
          loading: false,
          status: 'Offline',
          message: 'Connection failed'
        }
      }))
    }
  }

  const handlePingAll = async () => {
    const apisList = artifacts?.apis || []
    if (isPingingAll || apisList.length === 0) return
    setIsPingingAll(true)
    setPingProgress(0)
    
    let completedCount = 0
    
    const pingPromises = apisList.map(async (apiItem: any) => {
      const path = apiItem.path
      const method = apiItem.methods?.[0] || 'GET'
      const baseUrl = apiItem.base_url
      
      setApiHealth(prev => ({
        ...prev,
        [path]: { loading: true, status: 'Testing...' }
      }))
      
      try {
        const response = await api.post('/health/ping-endpoint', { path, method, base_url: customBaseUrl || baseUrl })
        const resData = response.data.data || response.data
        setApiHealth(prev => ({
          ...prev,
          [path]: {
            loading: false,
            status: resData.is_active ? 'Online' : 'Offline',
            code: resData.status_code,
            message: resData.message
          }
        }))
      } catch (err) {
        setApiHealth(prev => ({
          ...prev,
          [path]: {
            loading: false,
            status: 'Offline',
            message: 'Connection failed'
          }
        }))
      } finally {
        completedCount++
        setPingProgress(Math.round((completedCount / apisList.length) * 100))
      }
    })

    await Promise.all(pingPromises)
    setIsPingingAll(false)
  }

  const itemsPerPage = 10

  const renderExplorer = (
    tabId: string,
    title: string,
    description: string,
    rawData: any[],
    columns: any[],
    searchKeys: string[]
  ) => {
    const query = (searchQueries[tabId] || '').toLowerCase()
    const page = currentPages[tabId] || 0

    // Filter
    const filteredData = rawData.filter(row => 
      searchKeys.some(key => String(row[key] || '').toLowerCase().includes(query))
    )

    // Paginate
    const totalPages = Math.ceil(filteredData.length / itemsPerPage)
    const paginatedData = filteredData.slice(page * itemsPerPage, (page + 1) * itemsPerPage)

    return (
      <div className={clsx(CARD, 'p-6 bg-slate-surface/30 space-y-4')}>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-2">
          <div>
            <h3 className="text-base font-bold text-slate-100 font-display">{title}</h3>
            <p className="text-slate-400 text-xs mt-0.5">{description}</p>
          </div>
          
          <div className="relative w-full sm:w-64">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500 pointer-events-none">
              <Search size={14} />
            </span>
            <input
              type="text"
              placeholder="Search..."
              value={searchQueries[tabId] || ''}
              onChange={(e) => {
                setSearchQueries(prev => ({ ...prev, [tabId]: e.target.value }))
                setCurrentPages(prev => ({ ...prev, [tabId]: 0 }))
              }}
              className="w-full pl-9 pr-4 py-1.5 bg-slate-950/40 border border-slate-border/50 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/30 focus:border-indigo-500/50 text-xs font-sans transition-all"
            />
          </div>
        </div>

        <Table columns={columns} data={paginatedData} />

        {totalPages > 1 && (
          <div className="flex justify-between items-center text-xs font-mono text-slate-500 pt-2">
            <span>
              Showing {page * itemsPerPage + 1}-{Math.min((page + 1) * itemsPerPage, filteredData.length)} of {filteredData.length} entries
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPages(prev => ({ ...prev, [tabId]: Math.max(0, page - 1) }))}
                disabled={page === 0}
                className="flex items-center gap-2 px-2.5 py-1 rounded-xl text-[12px] font-semibold border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/[0.14] transition-all disabled:opacity-40"
              >
                Previous
              </button>
              <span>{page + 1} / {totalPages}</span>
              <button
                onClick={() => setCurrentPages(prev => ({ ...prev, [tabId]: Math.min(totalPages - 1, page + 1) }))}
                disabled={page >= totalPages - 1}
                className="flex items-center gap-2 px-2.5 py-1 rounded-xl text-[12px] font-semibold border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/[0.14] transition-all disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    )
  }

  const scanSteps = [
    { title: 'Initializing workspace sandbox', icon: Terminal },
    { title: 'Indexing code directory structures', icon: FolderGit2 },
    { title: 'Parsing Abstract Syntax Trees (AST)', icon: Cpu },
    { title: 'Resolving third-party dependencies', icon: Package },
    { title: 'Generating security model context', icon: ShieldCheck },
  ]

  // Sequential loading simulation to give a high-fidelity feel
  useEffect(() => {
    let timer: any

    if (loading) {
      setActiveStep(0)
      const runStep = (step: number) => {
        if (step < scanSteps.length) {
          timer = setTimeout(() => {
            setActiveStep(step)
            runStep(step + 1)
          }, 1500)
        }
      }
      runStep(1)
    }
    return () => clearTimeout(timer)
  }, [loading])

  const handleScanComplete = async (id: string) => {
    setLoading(true)
    setSessionId(id)
    setGlobalSessionId(id)
    try {
      const response = await chatService.getArtifacts(id)
      const data = response.data.data.artifacts
      setArtifacts(data)
      if (data?.key_files?.length > 0) {
        setSelectedKeyFile(data.key_files[0])
      }
      if (data?.production_base_url) {
        setCustomBaseUrl(data.production_base_url)
      } else if (data?.apis?.length > 0 && data.apis[0].base_url) {
        setCustomBaseUrl(data.apis[0].base_url)
      } else {
        setCustomBaseUrl('http://localhost:8000')
      }

      // Load previous conversation history if available
      try {
        const historyRes = await chatService.getHistory(id)
        if (historyRes.data?.data?.history) {
          setChatMessages(historyRes.data.data.history)
        }
      } catch (err) {
        console.error('Failed to load chat history:', err)
      }
    } catch (error) {
      console.error('Failed to get artifacts:', error)
      // Stale/expired session (e.g. the backend restarted and in-memory sessions
      // were lost). Reset so the scan form + repo selector is shown instead of an
      // empty results page.
      setSessionId(null)
      setArtifacts(null)
      setGlobalSessionId(null)
    } finally {
      // Allow the loading animation to reach final steps for premium aesthetic
      setTimeout(() => setLoading(false), 1000)
    }
  }

  // Fetch risk score after scan completes
  useEffect(() => {
    if (!sessionId || loading) return
    setRiskLoading(true)
    scoringService.getScore(sessionId)
      .then(res => setRiskProfile((res.data as any).data))
      .catch(err => console.error('Risk score fetch failed:', err))
      .finally(() => setRiskLoading(false))
  }, [sessionId, loading])

  // Auto-fetch security bugs + refactoring opportunities for security-first overview
  useEffect(() => {
    if (!sessionId || loading) return
    if (bugs.length === 0) {
      setSecurityLoading(true)
      securityService.scan(sessionId)
        .then(res => setBugs((res.data as any).data?.bugs || []))
        .catch(() => {})
        .finally(() => setSecurityLoading(false))
    }
    if (opportunities.length === 0) {
      setRefactorLoading(true)
      refactoringService.getOpportunities(sessionId)
        .then(res => setOpportunities((res.data as any)?.data?.opportunities || []))
        .catch(() => {})
        .finally(() => setRefactorLoading(false))
    }
  }, [sessionId, loading])

  // Restore session artifacts and history automatically on mount if session already exists
  useEffect(() => {
    if (currentSessionId) {
      setSessionId(currentSessionId)
      if (!artifacts && !loading) {
        handleScanComplete(currentSessionId)
      }
    } else {
      setSessionId(null)
      setArtifacts(null)
    }
  }, [currentSessionId])

  // vis.js Network Graph Integration
  useEffect(() => {
    if (currentTab !== 'overview' || !artifacts) return

    const apisList = artifacts.apis || []
    const classesList = artifacts.classes || []
    const functionsList = artifacts.functions || []

    const nodes: any[] = []
    const edges: any[] = []

    // 1. API Nodes (Indigo)
    apisList.slice(0, 15).forEach((api: any, idx: number) => {
      nodes.push({
        id: `api-${idx}`,
        label: `${(api.methods || ['GET']).join('/')}\n${(api.path || '').substring(0, 20)}`,
        color: {
          background: 'rgba(99, 102, 241, 0.15)',
          border: 'rgba(99, 102, 241, 0.6)',
          highlight: {
            background: 'rgba(99, 102, 241, 0.3)',
            border: 'rgba(99, 102, 241, 0.9)'
          }
        },
        font: { color: '#e2e8f0', size: 10, face: 'Inter' },
        shape: 'box',
        borderWidth: 1
      })
    })

    // 2. Class Nodes (Purple)
    classesList.slice(0, 15).forEach((cls: any, idx: number) => {
      nodes.push({
        id: `class-${idx}`,
        label: cls.name,
        color: {
          background: 'rgba(124, 58, 237, 0.15)',
          border: 'rgba(124, 58, 237, 0.6)',
          highlight: {
            background: 'rgba(124, 58, 237, 0.3)',
            border: 'rgba(124, 58, 237, 0.9)'
          }
        },
        font: { color: '#e2e8f0', size: 10, face: 'Inter' },
        shape: 'ellipse',
        borderWidth: 1
      })
    })

    // 3. Function Nodes (Emerald)
    functionsList.slice(0, 15).forEach((func: any, idx: number) => {
      nodes.push({
        id: `func-${idx}`,
        label: `${func.name}()`,
        color: {
          background: 'rgba(16, 185, 129, 0.15)',
          border: 'rgba(16, 185, 129, 0.6)',
          highlight: {
            background: 'rgba(16, 185, 129, 0.3)',
            border: 'rgba(16, 185, 129, 0.9)'
          }
        },
        font: { color: '#e2e8f0', size: 10, face: 'Inter' },
        shape: 'dot',
        size: 10,
        borderWidth: 1
      })
    })

    // Add some links between them to make it look Obsidian-like
    if (apisList.length > 0 && classesList.length > 0) {
      edges.push({ from: 'api-0', to: 'class-0', color: { color: 'rgba(255, 255, 255, 0.1)' } })
    }
    if (classesList.length > 1) {
      edges.push({ from: 'class-0', to: 'class-1', color: { color: 'rgba(255, 255, 255, 0.1)' } })
    }
    if (functionsList.length > 0 && classesList.length > 0) {
      edges.push({ from: 'class-0', to: 'func-0', color: { color: 'rgba(255, 255, 255, 0.1)' } })
    }
    if (apisList.length > 1 && functionsList.length > 0) {
      edges.push({ from: 'api-1', to: 'func-0', color: { color: 'rgba(255, 255, 255, 0.1)' } })
    }

    // Dynamic connectors to fill up the network mesh
    for (let i = 1; i < Math.min(apisList.length, 10); i++) {
      if (classesList.length > 0 && classesList.length > i % classesList.length) {
        edges.push({ from: `api-${i}`, to: `class-${i % classesList.length}`, color: { color: 'rgba(255, 255, 255, 0.08)' } })
      }
    }
    for (let i = 1; i < Math.min(functionsList.length, 15); i++) {
      if (classesList.length > 0 && classesList.length > i % classesList.length) {
        edges.push({ from: `func-${i}`, to: `class-${i % classesList.length}`, color: { color: 'rgba(255, 255, 255, 0.08)' } })
      }
    }

    const container = networkRef.current

    if (container) {
      const data = {
        nodes: new DataSet(nodes),
        edges: new DataSet(edges)
      }

      const options = {
        physics: {
          enabled: true,
          solver: 'forceAtlas2Based',
          forceAtlas2Based: {
            gravitationalConstant: -100,
            centralGravity: 0.02,
            springLength: 120,
            springConstant: 0.05
          },
          stabilization: { iterations: 100 }
        },
        interaction: {
          hover: true,
          navigationButtons: true,
          zoomView: true,
          dragView: true
        }
      }

      const network = new Network(container, data, options)

      return () => {
        network.destroy()
      }
    }
  }, [artifacts, currentTab])

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center max-w-xl mx-auto space-y-8 select-none">
        <div className="relative flex items-center justify-center">
          <div className="absolute w-24 h-24 rounded-full border border-indigo-500/20 animate-ping opacity-25" />
          <div className="w-16 h-16 rounded-full border-4 border-slate-800 border-t-indigo-500 animate-spin" />
        </div>
        
        <div className="w-full space-y-4">
          <div className="text-center">
            <h3 className="text-lg font-bold text-slate-100 font-display">Analyzing Codebase</h3>
            <p className="text-slate-400 text-xs mt-1">Generating static analysis metadata context...</p>
          </div>
          
          <div className="space-y-2 bg-slate-900/40 border border-slate-border/30 rounded-xl p-5 font-mono">
            {scanSteps.map((step, idx) => {
              const Icon = step.icon
              const isCompleted = idx < activeStep
              const isActive = idx === activeStep
              return (
                <div 
                  key={idx}
                  className={`flex items-center gap-3 text-xs transition-all duration-300 ${
                    isCompleted ? 'text-indigo-400 opacity-60' : isActive ? 'text-slate-200' : 'text-slate-600'
                  }`}
                >
                  <Icon size={14} className={isActive ? 'animate-pulse text-indigo-400' : ''} />
                  <span>{step.title}</span>
                  {isCompleted && <span className="ml-auto text-indigo-500">✓</span>}
                  {isActive && <span className="ml-auto text-indigo-400 animate-pulse">scanning...</span>}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    )
  }

  if (!sessionId) {
    return (
      <div className="max-w-3xl space-y-6">
        <div>
          <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">Repository Scanner</h1>
          <p className="text-slate-400 text-sm mt-1.5 font-medium">
            Scan your project's codebase to discover APIs, classes, and analyze overall architecture.
          </p>
        </div>
        
        <div className={clsx(CARD, "p-6 bg-slate-surface/30 space-y-6")}>
          <ScanForm onScanComplete={handleScanComplete} />
          
          <div className="border-t border-slate-border/20 pt-4 space-y-3">
            <h3 className="text-sm font-bold text-slate-200 font-display">Default Remediation Mode</h3>
            <p className="text-slate-400 text-xs leading-relaxed max-w-xl">
              Configure how CodeViz handles automatically suggested security and architectural fixes:
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              <div className="flex items-center gap-1.5 p-1 bg-slate-950/60 border border-slate-border/30 rounded-xl font-mono text-[11px]">
                <button
                  type="button"
                  onClick={() => setRemediationMode('hitl')}
                  className={clsx(
                    "px-3 py-1.5 rounded-lg transition-all font-semibold flex items-center gap-1.5",
                    remediationMode === 'hitl'
                      ? "bg-indigo-500/10 border border-indigo-500/20 text-indigo-400"
                      : "border border-transparent text-slate-400 hover:text-slate-200"
                  )}
                >
                  👥 HITL Mode
                </button>
                <button
                  type="button"
                  onClick={() => setRemediationMode('autonomous')}
                  className={clsx(
                    "px-3 py-1.5 rounded-lg transition-all font-semibold flex items-center gap-1.5",
                    remediationMode === 'autonomous'
                      ? "bg-indigo-500/10 border border-indigo-500/20 text-indigo-400"
                      : "border border-transparent text-slate-400 hover:text-slate-200"
                  )}
                >
                  🤖 Autonomous
                </button>
              </div>
              
              <div className="text-[11px] text-slate-500">
                {remediationMode === 'hitl' ? (
                  <span><strong>Human-in-the-Loop:</strong> Stages fixes in individual task branches, letting you inspect and merge each one manually.</span>
                ) : (
                  <span><strong>Fully Autonomous:</strong> Automates full remediation by compiling all high-confidence fixes into a single PR branch.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Render components once artifacts are loaded
  const stats = artifacts?.statistics || {}
  const apis = artifacts?.apis || []
  const classes = artifacts?.classes || []
  const functions = artifacts?.functions || []
  const dependencies = artifacts?.dependencies || []
  const techStack = artifacts?.tech_stack || {}

  const models = artifacts?.models || []
  const enums = artifacts?.enums || []
  const interfaces = artifacts?.interfaces || []
  const constants = artifacts?.constants || []
  const error_handlers = artifacts?.error_handlers || []
  const middleware = artifacts?.middleware || []
  const keyFiles = artifacts?.key_files || []
  const architecture = artifacts?.architecture || {}
  const uxArchitecture = artifacts?.ux_architecture || {}

  const filesColumns = [
    { key: 'path', label: 'File Path', render: (row: any) => <span className="font-mono text-xs text-slate-300">{row.path}</span> },
    { 
      key: 'ext', 
      label: 'File Type', 
      render: (row: any) => {
        const ext = row.path.split('.').pop() || 'file';
        return <Badge severity="low">{ext.toUpperCase()}</Badge>
      }
    }
  ]

  const apisColumns = [
    { 
      key: 'methods', 
      label: 'Method',
      render: (row: any) => (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border border-indigo-500/20 bg-indigo-500/10 text-indigo-400">
          {row.methods?.join(', ') || 'GET'}
        </span>
      )
    },
    { key: 'path', label: 'Route Path', render: (row: any) => <code className="text-xs text-indigo-300 bg-indigo-950/20 px-1.5 py-0.5 rounded font-mono">{row.path}</code> },
    { key: 'file', label: 'Source Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> },
    {
      key: 'health',
      label: 'Health Check',
      render: (row: any) => {
        const health = apiHealth[row.path]
        return (
          <div className="flex items-center gap-2">
            {health ? (
              <>
                <span className={clsx(
                  "w-2 h-2 rounded-full",
                  health.loading ? "bg-amber-505 bg-amber-500 animate-pulse" :
                  health.status === 'Online' ? "bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-rose-500 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.5)]"
                )} />
                <span className={clsx(
                  "text-xs font-semibold font-mono",
                  health.loading ? "text-amber-400" :
                  health.status === 'Online' ? "text-emerald-450 text-emerald-400" : "text-rose-455 text-rose-450 text-rose-400"
                )}>
                  {health.status} {health.code ? `(${health.code})` : ''}
                </span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-slate-500" />
                <span className="text-slate-500 text-xs font-semibold font-mono">Not tested</span>
              </>
            )}
            <button
              onClick={(e) => {
                e.stopPropagation()
                handleTestEndpoint(row.path, row.methods?.[0] || 'GET', row.base_url)
              }}
              className="ml-auto text-[10px] bg-slate-950/50 border border-slate-border/50 hover:bg-indigo-500/10 hover:border-indigo-500/20 text-slate-450 hover:text-indigo-400 px-2 py-0.5 rounded-md transition-all font-mono"
            >
              {health?.loading ? 'Testing...' : 'Test'}
            </button>
          </div>
        )
      }
    }
  ]

  const classesColumns = [
    { key: 'name', label: 'Class Name', render: (row: any) => <span className="font-bold text-slate-200">{row.name}</span> },
    { key: 'bases', label: 'Extends / Base Class', render: (row: any) => row.bases ? <code className="text-xs font-mono text-indigo-400">{row.bases}</code> : <span className="text-slate-600">-</span> },
    { key: 'file', label: 'Source Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> },
    {
      key: 'type',
      label: 'Archetype',
      render: (row: any) => (
        <Badge severity="medium">
          {row.type || 'Class'}
        </Badge>
      )
    }
  ]

  const functionsColumns = [
    { key: 'name', label: 'Function Name', render: (row: any) => <span className="font-mono text-indigo-300 font-semibold">{row.name}</span> },
    { 
      key: 'params', 
      label: 'Parameters',
      render: (row: any) => (
        <span className="font-mono text-xs text-slate-500">
          {row.params ? `(${row.params})` : '()'}
        </span>
      )
    },
    { key: 'file', label: 'Source Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
  ]

  const errorHandlersColumns = [
    { 
      key: 'error_code', 
      label: 'HTTP Code', 
      render: (row: any) => <Badge severity={parseInt(row.error_code) >= 500 ? 'critical' : 'medium'}>{row.error_code || 'Catch-all'}</Badge> 
    },
    { key: 'file', label: 'File Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
  ]

  const middlewareColumns = [
    { key: 'name', label: 'Middleware Name', render: (row: any) => <span className="font-bold text-indigo-300 font-mono">{row.name}</span> },
    { key: 'file', label: 'File Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
  ]

  const modelsColumns = [
    { key: 'name', label: 'Model Name', render: (row: any) => <span className="font-bold text-slate-200">{row.name}</span> },
    { key: 'file', label: 'Source Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> },
    {
      key: 'type',
      label: 'Archetype',
      render: (row: any) => (
        <Badge severity="low">
          {row.type || 'Model'}
        </Badge>
      )
    }
  ]

  const enumsColumns = [
    { key: 'name', label: 'Enum Name', render: (row: any) => <span className="font-bold text-indigo-300 font-mono">{row.name}</span> },
    { key: 'file', label: 'Source Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
  ]

  const interfacesColumns = [
    { key: 'name', label: 'Interface Name', render: (row: any) => <span className="font-bold text-slate-200">{row.name}</span> },
    { key: 'extends', label: 'Extends', render: (row: any) => row.extends ? <code className="text-xs text-indigo-400 font-mono">{row.extends}</code> : <span className="text-slate-600">-</span> },
    { key: 'file', label: 'Source Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
  ]

  const constantsColumns = [
    { key: 'name', label: 'Constant Name', render: (row: any) => <span className="font-bold font-mono text-indigo-300">{row.name}</span> },
    { 
      key: 'value', 
      label: 'Assigned Value',
      render: (row: any) => (
        <span className="font-mono text-xs text-indigo-400 bg-indigo-500/5 px-2 py-0.5 rounded border border-indigo-500/10">
          {row.value || '-'}
        </span>
      )
    },
    { key: 'file', label: 'Source Location', render: (row: any) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
  ]

  const dependenciesColumns = [
    { key: 'package', label: 'Package Name & Constraints', render: (row: any) => <span className="font-mono text-xs text-slate-300">{row.package}</span> },
    { 
      key: 'type', 
      label: 'Module Manager',
      render: (row: any) => (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-slate-900 border border-slate-border/40 text-slate-400">
          {row.type || 'Dependency'}
        </span>
      )
    }
  ]

  // ── Security-first derived data ──────────────────────────────────────────
  const SEV_HEX: Record<string, string> = {
    critical: '#ef4444', high: '#f97316', medium: '#eab308',
    low: '#3b82f6', info: '#64748b', clean: '#22c55e',
  }
  const critCount  = bugs.filter((b: any) => b.severity === 'critical').length
  const highCount  = bugs.filter((b: any) => b.severity === 'high').length
  const medCount   = bugs.filter((b: any) => b.severity === 'medium').length
  const lowCount   = bugs.filter((b: any) => !b.severity || b.severity === 'low').length
  const totalBugs  = bugs.length
  const postureScore  = riskProfile?.composite.score ?? null
  const scoreColor = !postureScore ? SEV_HEX.info
    : postureScore >= 80 ? SEV_HEX.clean
    : postureScore >= 60 ? SEV_HEX.medium
    : postureScore >= 40 ? SEV_HEX.high : SEV_HEX.critical

  const aiRecs = (() => {
    const fromOpps = opportunities.slice(0, 3).map((opp: any) => ({
      sev: 'medium' as string,
      title: opp.type || 'Code Quality Issue',
      desc: opp.description || 'Refactoring opportunity detected.',
      file: opp.file || '',
      effort: '~30 min', confidence: 82,
    }))
    if (fromOpps.length > 0) return fromOpps
    return [
      { sev: bugs[0]?.severity || 'critical', title: bugs[0]?.type || 'Security Scan Initialising',
        desc: bugs[0]?.description || 'Vulnerabilities will appear as the scan completes.',
        file: bugs[0]?.file || '', effort: '~20 min', confidence: 92 },
      { sev: bugs[1]?.severity || 'high', title: bugs[1]?.type || 'Dependency Audit Recommended',
        desc: bugs[1]?.description || 'Review third-party packages for known CVEs.',
        file: bugs[1]?.file || '', effort: '~15 min', confidence: 87 },
      { sev: 'medium', title: 'API Authentication Review',
        desc: 'Verify all endpoints enforce authentication and rate limiting.',
        file: apis[0]?.file || '', effort: '~45 min', confidence: 78 },
    ]
  })()

  // Compact metric cards (used in Technical Stats section)
  const metricCards = [
    { id: 'files',        label: 'Files',        count: artifacts?.files?.length || 0, icon: FileCode2 },
    { id: 'apis',         label: 'APIs',         count: apis.length,              icon: Server },
    { id: 'classes',      label: 'Classes',      count: classes.length,           icon: Cpu },
    { id: 'functions',    label: 'Functions',    count: functions.length,         icon: Code2 },
    { id: 'middleware',   label: 'Middleware',   count: middleware.length,        icon: Split },
    { id: 'models',       label: 'Models',       count: models.length,            icon: Database },
    { id: 'enums',        label: 'Enums',        count: enums.length,             icon: ListPlus },
    { id: 'error_handlers', label: 'Errors',     count: error_handlers.length,   icon: ShieldAlert },
    { id: 'interfaces',   label: 'Interfaces',   count: interfaces.length,        icon: Link },
    { id: 'dependencies', label: 'Dependencies', count: dependencies.length,     icon: Package },
  ]

  const dashboardTabs = [
    {
      id: 'overview',
      label: 'Security Overview',
      content: (
        <div className="space-y-5 pb-4">

          {/* ── 1. Scan Summary Bar ─────────────────────────────────────────── */}
          <div className={`${CARD} p-4`}>
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-emerald-500/[0.08] border border-emerald-500/20">
                  <CheckCircle2 size={15} className="text-emerald-400" />
                </div>
                <div>
                  <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">Scan Complete</p>
                  <p className="text-slate-200 font-semibold text-[13px] font-tight mt-0.5">
                    {artifacts?.repo_name || sessionId?.slice(0, 8) || 'Repository'}
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                {[
                  { label: `${(artifacts?.files?.length || 0).toLocaleString()} files`, icon: FileCode2 },
                  { label: `${apis.length} APIs`, icon: Server },
                  { label: `${classes.length} classes`, icon: Cpu },
                  { label: `${dependencies.length} deps`, icon: Package },
                ].map((s, i) => (
                  <div key={i} className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-elevated border border-white/[0.06] text-[11px] text-slate-500 font-mono">
                    <s.icon size={10} className="text-slate-400" />
                    {s.label}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ── 2. Security Posture + Threat Distribution ───────────────────── */}
          <div className="grid grid-cols-12 gap-5">

            {/* Posture Score */}
            <div className="col-span-12 lg:col-span-4 rounded-2xl border border-white/[0.08] border-t-white/[0.15] bg-gradient-to-br from-indigo-500/[0.02] to-slate-surface/30 shadow-card backdrop-blur-md p-6 flex flex-col hover:border-indigo-500/20 hover:shadow-[0_0_24px_-6px_rgba(99,102,241,0.12)] transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">Security Posture</p>
                  <p className="text-slate-300 text-[13px] font-medium mt-0.5">Overall risk score</p>
                </div>
                <div className="p-2 rounded-xl bg-slate-elevated border border-white/[0.06]">
                  <Shield size={15} className="text-slate-400" />
                </div>
              </div>
              <div className="flex justify-center py-2">
                {postureScore != null ? (() => {
                  const size = 156, r = size / 2 - 14
                  const circ = 2 * Math.PI * r
                  const fill = (Math.max(0, Math.min(100, postureScore)) / 100) * circ
                  const grade = postureScore >= 90 ? 'A' : postureScore >= 80 ? 'B' : postureScore >= 70 ? 'C' : postureScore >= 60 ? 'D' : 'F'
                  const posLabel = postureScore >= 80 ? 'Strong' : postureScore >= 60 ? 'Moderate' : postureScore >= 40 ? 'Elevated' : 'Critical Risk'
                  return (
                    <div className="flex flex-col items-center gap-2">
                      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={12} />
                        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={scoreColor} strokeWidth={12}
                          strokeLinecap="round" strokeDasharray={`${fill} ${circ}`}
                          transform={`rotate(-90 ${size/2} ${size/2})`}
                          style={{ transition: 'stroke-dasharray 1.2s cubic-bezier(.4,0,.2,1)', filter: `drop-shadow(0 0 6px ${scoreColor}45)` }} />
                        <text x={size/2} y={size/2 - 10} textAnchor="middle" dominantBaseline="middle"
                          fontSize={40} fontWeight="800" fontFamily="'Inter Tight',Inter,sans-serif" fill="#f9fafb">
                          {postureScore.toFixed(0)}
                        </text>
                        <text x={size/2} y={size/2 + 19} textAnchor="middle" dominantBaseline="middle"
                          fontSize={12} fontWeight="600" fontFamily="Inter,sans-serif" fill={scoreColor} letterSpacing="0.06em">
                          GRADE {grade}
                        </text>
                      </svg>
                      <span className="text-[11px] font-semibold uppercase tracking-[0.1em]" style={{ color: scoreColor }}>
                        {posLabel} Posture
                      </span>
                    </div>
                  )
                })() : (
                  <div className="w-[156px] h-[156px] rounded-full border-[12px] border-white/[0.04] flex items-center justify-center">
                    <p className="text-slate-400 text-[10px] font-mono text-center">{riskLoading ? 'Computing…' : 'No data'}</p>
                  </div>
                )}
              </div>
              {riskProfile && (
                <div className="mt-auto pt-4 border-t border-white/[0.05] grid grid-cols-3 gap-0 text-center">
                  {[
                    { val: riskProfile.summary.positives,      label: 'Passing',  col: '#22c55e' },
                    { val: riskProfile.summary.warnings,       label: 'Warnings', col: '#eab308' },
                    { val: riskProfile.summary.critical_flags, label: 'Critical', col: '#ef4444' },
                  ].map((s, i) => (
                    <div key={i} className={i === 1 ? 'border-x border-white/[0.05]' : ''}>
                      <p className="text-[22px] font-black font-tight" style={{ color: s.col }}>{s.val}</p>
                      <p className="text-[9px] uppercase tracking-[0.1em] text-slate-400 mt-0.5">{s.label}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Threat Distribution */}
            <div className="col-span-12 lg:col-span-8 grid grid-cols-2 gap-4">
              {[
                { key: 'critical', label: 'Critical',  count: critCount, icon: ShieldAlert,   desc: 'Immediate action required', bg: 'from-rose-500/[0.02] to-slate-surface/30 hover:from-rose-500/[0.06]', border: 'border-rose-500/10 hover:border-rose-500/30', shadow: 'hover:shadow-[0_0_24px_-6px_rgba(239,68,68,0.12)]' },
                { key: 'high',     label: 'High',      count: highCount, icon: AlertTriangle,  desc: 'Address within 24 hours', bg: 'from-amber-500/[0.02] to-slate-surface/30 hover:from-amber-500/[0.06]', border: 'border-amber-500/10 hover:border-amber-500/30', shadow: 'hover:shadow-[0_0_24px_-6px_rgba(249,115,22,0.12)]' },
                { key: 'medium',   label: 'Medium',    count: medCount,  icon: Info,           desc: 'Schedule for remediation', bg: 'from-yellow-500/[0.015] to-slate-surface/30 hover:from-yellow-500/[0.05]', border: 'border-yellow-500/10 hover:border-yellow-500/30', shadow: 'hover:shadow-[0_0_24px_-6px_rgba(234,179,8,0.08)]' },
                { key: 'low',      label: 'Low',       count: lowCount,  icon: CheckCircle2,   desc: 'Monitor and track', bg: 'from-blue-500/[0.02] to-slate-surface/30 hover:from-blue-500/[0.06]', border: 'border-blue-500/10 hover:border-blue-500/30', shadow: 'hover:shadow-[0_0_24px_-6px_rgba(59,130,246,0.12)]' },
              ].map(s => (
                <div key={s.key}
                  className={`relative overflow-hidden rounded-2xl border ${s.border} bg-gradient-to-br ${s.bg} ${s.shadow} backdrop-blur-md p-5 cursor-pointer transition-all duration-300`}>
                  <div className="absolute left-0 top-3 bottom-3 w-[4px] rounded-r-lg"
                    style={{ backgroundColor: SEV_HEX[s.key], opacity: s.count > 0 ? 1 : 0.2 }} />
                  <div className="pl-3">
                    <div className="flex items-center justify-between mb-4">
                      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">{s.label}</p>
                      <div className="p-1.5 rounded-lg border"
                        style={{ backgroundColor: `${SEV_HEX[s.key]}14`, borderColor: `${SEV_HEX[s.key]}28` }}>
                        <s.icon size={13} style={{ color: SEV_HEX[s.key], opacity: s.count > 0 ? 1 : 0.3 }} />
                      </div>
                    </div>
                    <p className="text-[50px] font-black font-tight leading-none tracking-tight text-white">
                      {securityLoading ? '—' : s.count}
                    </p>
                    <p className="text-[11px] text-slate-300 mt-2">{s.desc}</p>
                    {totalBugs > 0 && (
                      <div className="mt-3 w-full h-[2px] rounded-full bg-white/[0.05] overflow-hidden">
                        <div className="h-full rounded-full"
                          style={{ width: `${(s.count / totalBugs) * 100}%`, backgroundColor: SEV_HEX[s.key], opacity: 0.6 }} />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── 2b. CVE Supply Chain Summary (shown after scan) ───────────────── */}
          {cveRan && cveSummary && (cveResults.length > 0) && (
            <div className="rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card p-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-amber-500/[0.08] border border-amber-500/20">
                    <Package size={15} className="text-amber-400" />
                  </div>
                  <div>
                    <p className="text-[9px] font-bold uppercase tracking-[0.13em] text-slate-400">Supply Chain</p>
                    <p className="text-slate-300 text-[13px] font-semibold font-tight">
                      {cveResults.length} CVEs in {cveAffected} packages
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  {(['critical','high','medium','low'] as const).map(sev => {
                    const SEV_HEX_OV: Record<string, string> = { critical:'#ef4444', high:'#f97316', medium:'#eab308', low:'#3b82f6' }
                    const count = cveSummary[sev] || 0
                    if (!count) return null
                    return (
                      <div key={sev} className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border"
                        style={{ borderColor: `${SEV_HEX_OV[sev]}25`, backgroundColor: `${SEV_HEX_OV[sev]}10` }}>
                        <span className="text-[16px] font-black font-tight" style={{ color: SEV_HEX_OV[sev] }}>{count}</span>
                        <span className="text-[9px] uppercase tracking-wider" style={{ color: SEV_HEX_OV[sev], opacity: 0.7 }}>{sev}</span>
                      </div>
                    )
                  })}
                  <button onClick={() => setCurrentTab('dependencies')}
                    className="text-[11px] text-indigo-400/60 hover:text-indigo-400 font-medium transition-colors flex items-center gap-1">
                    View details <ChevronRight size={11} />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ── 3. Top Findings + AI Recommendations ─────────────────────────── */}
          <div className="grid grid-cols-12 gap-5">

            {/* Top Findings */}
            <div className={`col-span-12 lg:col-span-7 ${CARD} p-6`}>
              <div className="flex items-start justify-between mb-5">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400 mb-1">Findings</p>
                  <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Top Security Issues</h2>
                </div>
                {totalBugs > 0 && <span className="text-[10px] text-slate-400 font-mono mt-1">{totalBugs} total</span>}
              </div>
              {securityLoading ? (
                <div className="flex items-center gap-2.5 py-6 text-slate-400 text-[12px] font-mono">
                  <RefreshCw size={13} className="animate-spin text-indigo-400/60" />
                  Scanning for vulnerabilities…
                </div>
              ) : bugs.length === 0 ? (
                <div className="py-8 text-center border border-dashed border-white/[0.06] rounded-xl">
                  <ShieldCheck size={20} className="text-slate-500 mx-auto mb-2" />
                  <p className="text-slate-400 text-[12px]">No findings detected</p>
                  <p className="text-slate-400 text-[11px] mt-1">Your codebase appears clean or scan is still running.</p>
                </div>
              ) : (
                <div>
                  {bugs.slice(0, 7).map((bug: any, i: number) => (
                    <div key={i}
                      className="flex items-start gap-3 py-3 border-b border-white/[0.05] last:border-0 -mx-2 px-2 rounded-lg hover:bg-white/[0.02] transition-colors cursor-pointer group">
                      <div className="w-1.5 h-1.5 rounded-full shrink-0 mt-1.5"
                        style={{ backgroundColor: SEV_HEX[bug.severity] || SEV_HEX.info }} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border"
                            style={{ color: SEV_HEX[bug.severity] || SEV_HEX.info, backgroundColor: `${SEV_HEX[bug.severity] || SEV_HEX.info}12`, borderColor: `${SEV_HEX[bug.severity] || SEV_HEX.info}25` }}>
                            {bug.severity || 'info'}
                          </span>
                          <span className="text-[12px] font-semibold text-slate-300 font-tight truncate">{bug.type || 'Security Issue'}</span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-snug truncate">{bug.description || 'Vulnerability detected'}</p>
                        {bug.file && <p className="text-[10px] text-slate-400 font-mono mt-0.5 truncate">{bug.file}{bug.line ? `:${bug.line}` : ''}</p>}
                      </div>
                      <ChevronRight size={11} className="text-slate-500 group-hover:text-slate-300 shrink-0 mt-1 transition-colors" />
                    </div>
                  ))}
                  {bugs.length > 7 && (
                    <p className="text-center text-[11px] text-indigo-400/60 font-medium pt-3">
                      +{bugs.length - 7} more in Security →
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* AI Remediation Recommendations */}
            <div className="col-span-12 lg:col-span-5 flex flex-col gap-3">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400 mb-1">AI-Powered</p>
                <h2 className="text-[15px] font-semibold text-slate-200 font-tight mb-3">Remediation Recommendations</h2>
              </div>
              {aiRecs.map((rec: any, i: number) => (
                <div key={i}
                  className={`relative overflow-hidden ${CARD} p-4 cursor-pointer group hover:border-white/[0.14] hover:bg-slate-elevated transition-all duration-200`}>
                  <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-2xl"
                    style={{ backgroundColor: SEV_HEX[rec.sev] || SEV_HEX.medium }} />
                  <div className="pl-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border"
                        style={{ color: SEV_HEX[rec.sev] || SEV_HEX.medium, backgroundColor: `${SEV_HEX[rec.sev] || SEV_HEX.medium}12`, borderColor: `${SEV_HEX[rec.sev] || SEV_HEX.medium}25` }}>
                        {rec.sev}
                      </span>
                      <div className="flex items-center gap-1">
                        <Zap size={9} className="text-indigo-400/50" />
                        <span className="text-[9px] text-indigo-400/50 font-mono">{rec.confidence}%</span>
                      </div>
                    </div>
                    <h3 className="text-[13px] font-semibold text-slate-300 font-tight group-hover:text-slate-100 transition-colors leading-snug">
                      {rec.title}
                    </h3>
                    <p className="text-[11px] text-slate-300 leading-relaxed line-clamp-2">{rec.desc}</p>
                    <div className="flex items-center justify-between pt-2 border-t border-white/[0.04]">
                      <span className="text-[9px] text-slate-400 font-mono truncate max-w-[55%]">{rec.file || '—'}</span>
                      <span className="text-[9px] text-slate-400 font-mono">{rec.effort}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── 4. API Security + Files Requiring Attention ──────────────────── */}
          <div className="grid grid-cols-12 gap-5">

            {/* API Overview */}
            <div className={`col-span-12 lg:col-span-6 ${CARD} p-6`}>
              <div className="flex items-start justify-between mb-5">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400 mb-1">Endpoints</p>
                  <h2 className="text-[15px] font-semibold text-slate-200 font-tight">API Security Overview</h2>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-slate-400 font-mono">{apis.length} routes</span>
                  {customBaseUrl && (
                    <span className="text-[9px] font-mono text-indigo-400/50 bg-indigo-500/[0.07] px-2 py-0.5 rounded border border-indigo-500/15 truncate max-w-[110px]">
                      {customBaseUrl.replace(/https?:\/\//, '')}
                    </span>
                  )}
                </div>
              </div>
              {apis.length === 0 ? (
                <div className="py-6 text-center"><Server size={18} className="text-slate-500 mx-auto mb-2" /><p className="text-slate-400 text-[11px]">No endpoints detected</p></div>
              ) : (
                <div className="space-y-0.5 max-h-[260px] overflow-y-auto scrollbar-none">
                  {apis.slice(0, 14).map((apiItem: any, idx: number) => {
                    const health = apiHealth[apiItem.path]
                    const method = apiItem.methods?.[0] || 'GET'
                    const mc: Record<string, string> = { GET: '#3b82f6', POST: '#22c55e', PUT: '#f97316', DELETE: '#ef4444', PATCH: '#8b5cf6' }
                    return (
                      <div key={idx} className="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-white/[0.025] group transition-colors">
                        <span className="text-[9px] font-bold w-9 text-center py-0.5 rounded border shrink-0"
                          style={{ color: mc[method] || '#64748b', backgroundColor: `${mc[method] || '#64748b'}14`, borderColor: `${mc[method] || '#64748b'}28` }}>
                          {method}
                        </span>
                        <code className="text-[11px] text-slate-500 font-mono flex-1 truncate group-hover:text-slate-300 transition-colors">{apiItem.path}</code>
                        <div className="flex items-center gap-1.5 shrink-0">
                          <div className={clsx('w-1.5 h-1.5 rounded-full',
                            health?.loading ? 'bg-amber-400 animate-pulse' :
                            health?.status === 'Online' ? 'bg-emerald-400' :
                            health ? 'bg-rose-400' : 'bg-slate-800'
                          )} />
                          <button onClick={(e) => { e.stopPropagation(); handleTestEndpoint(apiItem.path, method, apiItem.base_url) }}
                            className="text-[9px] text-slate-400 hover:text-indigo-300 font-mono transition-colors">
                            {health?.loading ? '…' : 'test'}
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
              {apis.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/[0.05]">
                  <button onClick={handlePingAll} disabled={isPingingAll}
                    className="flex items-center gap-1.5 text-[11px] font-medium text-indigo-400/60 hover:text-indigo-400 transition-colors disabled:opacity-40">
                    <RefreshCw size={11} className={clsx(isPingingAll && 'animate-spin')} />
                    {isPingingAll ? `Pinging… ${pingProgress}%` : 'Ping all routes'}
                  </button>
                </div>
              )}
            </div>

            {/* Files Requiring Attention */}
            <div className={`col-span-12 lg:col-span-6 ${CARD} p-6`}>
              <div className="flex items-start justify-between mb-5">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400 mb-1">Key Files</p>
                  <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Files Requiring Attention</h2>
                </div>
                <span className="text-[11px] text-slate-400 font-mono mt-1">{keyFiles.length} flagged</span>
              </div>
              {keyFiles.length === 0 ? (
                <div className="py-6 text-center"><FileCode2 size={18} className="text-slate-500 mx-auto mb-2" /><p className="text-slate-400 text-[11px]">No key files flagged</p></div>
              ) : (
                <div className="space-y-0.5 max-h-[260px] overflow-y-auto scrollbar-none">
                  {keyFiles.slice(0, 14).map((file: any, i: number) => {
                    const ext = (file.path || '').split('.').pop() || 'file'
                    const ec: Record<string, string> = { py: '#3b82f6', ts: '#6366f1', tsx: '#8b5cf6', js: '#eab308', jsx: '#f97316', json: '#22c55e' }
                    const fileBugs = bugs.filter((b: any) => b.file && file.path && b.file.includes(file.path.split('/').pop() || ''))
                    return (
                      <div key={i} onClick={() => setCurrentTab('key_files')}
                        className="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-white/[0.025] group transition-colors cursor-pointer">
                        <span className="text-[9px] font-bold w-6 text-center shrink-0" style={{ color: ec[ext] || '#64748b' }}>{ext}</span>
                        <span className="text-[11px] text-slate-500 font-mono flex-1 truncate group-hover:text-slate-300 transition-colors">{file.path}</span>
                        <div className="flex items-center gap-2 shrink-0">
                          {fileBugs.length > 0 && (
                            <span className="text-[9px] font-bold text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20">
                              {fileBugs.length} issue{fileBugs.length > 1 ? 's' : ''}
                            </span>
                          )}
                          <span className="text-[9px] text-slate-400 font-mono">{file.lines || '—'}L</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

          {/* ── 5. Technical Stats (secondary) ───────────────────────────────── */}
          <div className={`${CARD} p-6`}>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400 mb-1">Code Statistics</p>
                <h2 className="text-[15px] font-semibold text-slate-200 font-tight">Technical Scan Summary</h2>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Click to explore</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              {metricCards.map(card => (
                <div key={card.id} onClick={() => setCurrentTab(card.id)}
                  className="flex items-center justify-between p-3 rounded-xl border border-white/[0.05] bg-slate-elevated hover:border-white/[0.1] hover:bg-white/[0.03] transition-all cursor-pointer group">
                  <div>
                    <p className="text-[9px] font-bold uppercase tracking-[0.1em] text-slate-400 mb-1">{card.label}</p>
                    <p className="text-[22px] font-black text-slate-400 font-tight leading-none group-hover:text-slate-200 transition-colors">
                      {card.count.toLocaleString()}
                    </p>
                  </div>
                  <card.icon size={14} className="text-slate-500 group-hover:text-slate-300 transition-colors shrink-0" />
                </div>
              ))}
            </div>
          </div>

        </div>
      )
    },
    {
      id: 'chat',
      label: '💬 AI Chat',
      content: (
        <div className={clsx(CARD, "flex flex-col h-[550px] bg-slate-surface/30 p-0 overflow-hidden")}>
          {/* Header */}
          <div className="flex justify-between items-center px-6 py-4 bg-slate-900/60 border-b border-slate-border/30">
            <div>
              <h3 className="text-sm font-bold text-slate-100 font-display flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_8px_rgba(99,102,241,0.6)]" />
                AI Codebase Navigator
              </h3>
              <p className="text-slate-400 text-[10px] mt-0.5 font-mono uppercase tracking-wider">
                AST Sandbox Context Loaded
              </p>
            </div>
            {chatMessages.length > 0 && (
              <button
                type="button"
                onClick={() => {
                  if (confirm('Clear chat history?')) {
                    setChatMessages([])
                  }
                }}
                className="text-[10px] font-mono text-slate-500 hover:text-rose-400 hover:underline transition-all"
              >
                Clear Conversation
              </button>
            )}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 flex flex-col scrollbar-thin">
            {chatMessages.length === 0 ? (
              <div className="flex-1 flex flex-col justify-center items-center max-w-lg mx-auto text-center space-y-6 my-auto">
                <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-indigo-400 animate-bounce">
                  <Terminal size={24} />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-200 font-display">Codebase Natural Language Assistant</h4>
                  <p className="text-slate-400 text-xs mt-1.5 leading-relaxed">
                    Chat directly about your project. The assistant runs a localized Abstract Syntax Tree (AST) scanning pipeline to find security hotspots, trace API route architectures, catalog database models, and map patterns.
                  </p>
                </div>
                
                <div className="w-full space-y-2.5">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider text-left">Suggested Queries</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                    {[
                      { text: "Show me all SQL injection risks", desc: "Scan raw DB query concatenations" },
                      { text: "List the API endpoints", desc: "Catalog active backend route signatures" },
                      { text: "Show scanned database models", desc: "Identify classes mapped to tables" },
                      { text: "Explain files related to auth", desc: "Explore matching codebase concepts" }
                    ].map((chip, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleSendQuestion(chip.text)}
                        className="p-3 bg-slate-950/40 border border-slate-border/50 hover:border-indigo-500/40 rounded-xl transition-all duration-150 text-left group hover:-translate-y-0.5"
                      >
                        <p className="text-xs font-bold text-slate-300 group-hover:text-indigo-400 transition-colors">{chip.text}</p>
                        <p className="text-[10px] text-slate-500 mt-0.5">{chip.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              chatMessages.map((msg, idx) => {
                const isAI = msg.role === 'assistant'
                return (
                  <div 
                    key={idx}
                    className={clsx(
                      "flex gap-3 max-w-[85%] items-start animate-fade-in",
                      isAI ? "self-start" : "self-end flex-row-reverse"
                    )}
                  >
                    <div className={clsx(
                      "w-7 h-7 rounded-full shrink-0 flex items-center justify-center border font-mono text-[10px] font-bold shadow-sm",
                      isAI 
                        ? "bg-indigo-500/10 border-indigo-500/30 text-indigo-400" 
                        : "bg-slate-900 border-slate-border/50 text-slate-300"
                    )}>
                      {isAI ? 'AI' : 'U'}
                    </div>

                    <div className={clsx(
                      "rounded-2xl px-4 py-3 relative border text-xs",
                      isAI 
                        ? "bg-slate-950/20 border-slate-border/30 text-slate-200 rounded-tl-none" 
                        : "bg-indigo-600/10 border-indigo-500/30 text-slate-100 rounded-tr-none"
                    )}>
                      {isAI ? (
                        <MarkdownRenderer content={msg.content} />
                      ) : (
                        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                      )}
                      
                      {msg.timestamp && (
                        <span className="block text-[8px] text-slate-500 font-mono mt-1.5 text-right uppercase">
                          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>
                  </div>
                )
              })
            )}

            {chatLoading && (
              <div className="flex gap-3 max-w-[80%] items-start self-start">
                <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center border bg-indigo-500/10 border-indigo-500/30 text-indigo-400 font-mono text-[10px] font-bold">
                  AI
                </div>
                <div className="bg-slate-950/20 border border-slate-border/30 rounded-2xl rounded-tl-none px-4 py-3 text-xs space-y-1">
                  <div className="flex items-center gap-1.5 py-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse [animation-delay:0.2s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse [animation-delay:0.4s]" />
                  </div>
                  <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wider block">Scanning AST Context...</span>
                </div>
              </div>
            )}
            
            <div ref={chatEndRef} />
          </div>

          {/* Prompt quick suggestions */}
          {chatMessages.length > 0 && (
            <div className="px-6 py-2 border-t border-slate-border/25 flex gap-2 overflow-x-auto scrollbar-none bg-slate-950/25">
              {[
                "Show me all SQL injection risks",
                "List the API endpoints",
                "Show database models",
                "Explain auth files"
              ].map((text, i) => (
                <button
                  key={i}
                  type="button"
                  disabled={chatLoading}
                  onClick={() => handleSendQuestion(text)}
                  className="px-2.5 py-1 text-[10px] font-semibold bg-slate-900 border border-slate-border/40 hover:border-indigo-500/40 text-slate-400 hover:text-indigo-400 rounded-lg transition-all"
                >
                  {text}
                </button>
              ))}
            </div>
          )}

          {/* Form */}
          <form 
            onSubmit={(e) => {
              e.preventDefault()
              handleSendQuestion(chatInput)
            }}
            className="p-4 bg-slate-900/60 border-t border-slate-border/30 flex gap-3 items-center"
          >
            <input
              type="text"
              placeholder="Ask about security vulnerabilities, routes, models..."
              value={chatInput}
              disabled={chatLoading}
              onChange={(e) => setChatInput(e.target.value)}
              className="flex-1 px-4 py-2.5 bg-slate-950/60 border border-slate-border/50 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/30 focus:border-indigo-500/50"
            />
            <button
              type="submit"
              disabled={chatLoading || !chatInput.trim()}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold bg-indigo-500 hover:bg-indigo-600 text-white transition-all disabled:opacity-40"
            >
              Send
            </button>
          </form>
        </div>
      )
    },
    {
      id: 'structure',
      label: '🌳 Structure',
      content: (
        <div className={clsx(CARD, "p-6 space-y-4 bg-slate-surface/30")}>
          <div>
            <h3 className="text-base font-bold text-slate-100 font-display">Directory Structure</h3>
            <p className="text-slate-400 text-xs mt-0.5">Static representation of repository directories.</p>
          </div>
          <pre className="bg-slate-950/60 p-5 border border-slate-border/30 rounded-xl overflow-x-auto text-xs font-mono text-slate-300 leading-relaxed max-h-[500px]">
            {artifacts?.structure || 'No structure parsed.'}
          </pre>
        </div>
      )
    },
    {
      id: 'files',
      label: `📄 Files (${artifacts?.files?.length || 0})`,
      content: renderExplorer('files', 'Scanned Files', 'Files index compiled during AST scanning.', (artifacts?.files || []).map((f: string) => ({ path: f })), filesColumns, ['path'])
    },
    {
      id: 'apis',
      label: `🔌 APIs (${apis.length})`,
      content: (
        <div className="space-y-4">
          <div className={clsx(CARD, "bg-slate-surface/30 p-4")}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-indigo-400" />
                  API Testing Host Target
                </h4>
                <p className="text-xs text-slate-400">
                  Target host for pings. Set to localhost for dev, or a public host for production testing.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full md:w-auto">
                <input
                  type="text"
                  placeholder="e.g., https://www.gaslite.co.za"
                  value={customBaseUrl}
                  onChange={(e) => setCustomBaseUrl(e.target.value)}
                  className="px-3 py-1.5 bg-slate-950/60 border border-slate-border/50 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500/30 focus:border-indigo-500/50 w-full sm:w-64"
                />
                
                {artifacts?.production_base_url && artifacts.production_base_url !== customBaseUrl && (
                  <button
                    onClick={() => setCustomBaseUrl(artifacts.production_base_url)}
                    className="text-[10px] whitespace-nowrap bg-indigo-500/10 border border-indigo-500/20 hover:bg-indigo-500/20 text-indigo-300 px-3 py-1.5 rounded-lg transition-all font-mono"
                  >
                    🌍 Use Prod: {artifacts.production_base_url.replace(/^https?:\/\//, '')}
                  </button>
                )}
              </div>
            </div>
          </div>
          
          {renderExplorer('apis', 'Discovered REST Endpoints', 'Routes parsed from router annotations and HTTP middleware.', apis, apisColumns, ['path', 'file', 'methods'])}
        </div>
      )
    },
    {
      id: 'classes',
      label: `📦 Classes (${classes.length})`,
      content: renderExplorer('classes', 'AST Class Models', 'Classes, structural hierarchies, and inheritance contexts.', classes, classesColumns, ['name', 'file', 'bases'])
    },
    {
      id: 'functions',
      label: `⚙️ Functions (${functions.length})`,
      content: renderExplorer('functions', 'Functions & Methods', 'Extracted functions, parameters, and callback actions.', functions, functionsColumns, ['name', 'file'])
    },
    {
      id: 'error_handlers',
      label: `❌ Errors (${error_handlers.length})`,
      content: renderExplorer('error_handlers', 'Error Handlers', 'Global REST exception handlers.', error_handlers, errorHandlersColumns, ['error_code', 'file'])
    },
    {
      id: 'middleware',
      label: `🛣️ Middleware (${middleware.length})`,
      content: renderExplorer('middleware', 'Middleware Interceptors', 'Custom middleware blocks executing on routes.', middleware, middlewareColumns, ['name', 'file'])
    },
    {
      id: 'models',
      label: `🗂️ Models (${models.length})`,
      content: renderExplorer('models', 'Database Models', 'Database entities mapped to backend tables.', models, modelsColumns, ['name', 'file'])
    },
    {
      id: 'enums',
      label: `📋 Enums (${enums.length})`,
      content: renderExplorer('enums', 'Enums', 'Standardized developer enum categories.', enums, enumsColumns, ['name', 'file'])
    },
    {
      id: 'interfaces',
      label: `🔗 Interfaces (${interfaces.length})`,
      content: renderExplorer('interfaces', 'Interfaces & Contracts', 'Type contracts, configurations, and API structures.', interfaces, interfacesColumns, ['name', 'file', 'extends'])
    },
    {
      id: 'constants',
      label: `📌 Constants (${constants.length})`,
      content: renderExplorer('constants', 'Global Constants', 'Constant parameters and config settings.', constants, constantsColumns, ['name', 'file'])
    },
    {
      id: 'key_files',
      label: `🔑 Key Files (${keyFiles.length})`,
      content: (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className={clsx(CARD, "p-6 bg-slate-surface/30 max-h-[500px] overflow-y-auto")}>
            <h3 className="text-base font-bold text-slate-100 font-display mb-4">Code Highlights</h3>
            <div className="space-y-2">
              {keyFiles.map((file: any, idx: number) => (
                <button
                  key={idx}
                  onClick={() => setSelectedKeyFile(file)}
                  className={`w-full text-left p-3 rounded-lg border text-xs font-mono transition-all duration-150 ${
                    selectedKeyFile?.name === file.name
                      ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300'
                      : 'bg-slate-900/30 border-slate-border/40 text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
                  }`}
                >
                  <p className="font-bold truncate">{file.name}</p>
                  <div className="flex gap-3 text-[10px] text-slate-500 mt-1">
                    <span>Lines: {file.lines}</span>
                    <span>Size: {(file.size / 1024).toFixed(1)} KB</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className={clsx(CARD, "p-6 lg:col-span-2 bg-slate-surface/30 flex flex-col")}>
            <div className="flex justify-between items-center mb-4 pb-3 border-b border-slate-border/30">
              <div>
                <h3 className="text-base font-bold text-slate-100 font-display">Code Viewer</h3>
                <p className="text-slate-400 text-xs mt-0.5">{selectedKeyFile?.name || 'Select a file'}</p>
              </div>
              {selectedKeyFile && (
                <span className="text-[10px] font-mono text-slate-500">
                  Size: {(selectedKeyFile.size / 1024).toFixed(1)} KB
                </span>
              )}
            </div>
            
            {selectedKeyFile ? (
              <pre className="bg-slate-950 p-4 border border-slate-border/30 rounded-xl overflow-x-auto text-xs font-mono text-slate-300 leading-relaxed max-h-[380px] border-l-4 border-l-indigo-500/80">
                <code>{selectedKeyFile.content}</code>
              </pre>
            ) : (
              <div className="text-center py-20 text-slate-500 italic text-xs">
                Select a key file from the list to view its code snippet.
              </div>
            )}
          </div>
        </div>
      )
    },
    {
      id: 'dependencies',
      label: `📚 Deps (${dependencies.length})`,
      content: (() => {
        const SEV_HEX_CVE: Record<string, string> = {
          critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#3b82f6',
        }
        const runCveScan = async () => {
          if (!sessionId || cveLoading) return
          setCveLoading(true)
          try {
            const res = await cveService.scan(sessionId)
            const d = (res.data as any).data
            setCveResults(d.vulnerabilities || [])
            setCveSummary(d.summary || {})
            setCveScanned(d.scanned || 0)
            setCveAffected(d.affected || 0)
            setCveRan(true)
          } catch {
            setCveRan(true)
          } finally {
            setCveLoading(false)
          }
        }

        return (
          <div className="space-y-5">
            {/* Header + scan button */}
            <div className="rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card p-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-600 mb-1">
                    Supply Chain Security
                  </p>
                  <h2 className="text-[15px] font-semibold text-slate-200 font-tight">
                    Dependency CVE Scan
                  </h2>
                  <p className="text-[12px] text-slate-500 mt-0.5">
                    {dependencies.length} packages detected · powered by{' '}
                    <span className="text-indigo-400/70 font-mono">osv.dev</span>
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  {cveRan && cveSummary && (
                    <div className="flex items-center gap-2">
                      {[
                        { key: 'critical', label: 'Critical' },
                        { key: 'high',     label: 'High'     },
                        { key: 'medium',   label: 'Medium'   },
                        { key: 'low',      label: 'Low'      },
                      ].map(s => (
                        cveSummary[s.key] > 0 && (
                          <div key={s.key}
                            className="text-center px-3 py-1.5 rounded-lg border"
                            style={{ borderColor: `${SEV_HEX_CVE[s.key]}28`, backgroundColor: `${SEV_HEX_CVE[s.key]}10` }}>
                            <p className="text-[18px] font-black font-tight leading-none" style={{ color: SEV_HEX_CVE[s.key] }}>
                              {cveSummary[s.key]}
                            </p>
                            <p className="text-[9px] uppercase tracking-wider mt-0.5" style={{ color: SEV_HEX_CVE[s.key], opacity: 0.7 }}>
                              {s.label}
                            </p>
                          </div>
                        )
                      ))}
                    </div>
                  )}
                  <button
                    onClick={runCveScan}
                    disabled={cveLoading || !sessionId}
                    className={clsx(
                      'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all duration-200',
                      cveRan
                        ? 'border border-white/[0.08] bg-slate-elevated text-slate-400 hover:text-slate-200 hover:border-white/[0.14]'
                        : 'bg-indigo-500 hover:bg-indigo-600 text-white shadow-sm shadow-indigo-500/30',
                      'disabled:opacity-40'
                    )}>
                    {cveLoading
                      ? <><RefreshCw size={13} className="animate-spin" /> Scanning OSV…</>
                      : cveRan
                      ? <><RefreshCw size={13} /> Rescan</>
                      : <><ShieldAlert size={13} /> Scan for CVEs</>}
                  </button>
                </div>
              </div>

              {/* Scan meta */}
              {cveRan && (
                <div className="flex items-center gap-4 mt-4 pt-4 border-t border-white/[0.05] text-[11px] text-slate-600 font-mono">
                  <span>{cveScanned} packages scanned</span>
                  <span>·</span>
                  <span>{cveResults.length} CVEs found</span>
                  <span>·</span>
                  <span>{cveAffected} packages affected</span>
                </div>
              )}
            </div>

            {/* CVE results table */}
            {cveRan && cveResults.length > 0 && (
              <div className="rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card overflow-hidden">
                {/* Table header */}
                <div className="grid grid-cols-12 gap-3 px-5 py-3 bg-slate-elevated border-b border-white/[0.06]">
                  {[
                    ['Package',   'col-span-2'],
                    ['Version',   'col-span-1'],
                    ['CVE ID',    'col-span-3'],
                    ['Severity',  'col-span-2'],
                    ['CVSS',      'col-span-1'],
                    ['Fix',       'col-span-2'],
                    ['',          'col-span-1'],
                  ].map(([h, c]) => (
                    <div key={h} className={`${c} text-[9px] font-bold uppercase tracking-[0.13em] text-slate-600`}>{h}</div>
                  ))}
                </div>

                {/* Rows */}
                <div className="divide-y divide-white/[0.04] max-h-[540px] overflow-y-auto scrollbar-none">
                  {cveResults.map((v: any, i: number) => (
                    <div key={i}
                      className="grid grid-cols-12 gap-3 px-5 py-3.5 hover:bg-white/[0.025] transition-colors group">

                      {/* Package */}
                      <div className="col-span-2 flex items-center">
                        <div className="flex items-center gap-2 min-w-0">
                          <div className="w-1.5 h-1.5 rounded-full shrink-0"
                            style={{ backgroundColor: SEV_HEX_CVE[v.severity] || '#64748b' }} />
                          <span className="text-[12px] font-semibold text-slate-300 font-mono truncate">
                            {v.package}
                          </span>
                        </div>
                      </div>

                      {/* Version */}
                      <div className="col-span-1 flex items-center">
                        <span className="text-[11px] text-slate-600 font-mono truncate">
                          {v.version || '—'}
                        </span>
                      </div>

                      {/* CVE ID */}
                      <div className="col-span-3 flex items-center">
                        <span className="text-[11px] font-mono text-slate-400 truncate" title={v.title}>
                          {v.cve_id || v.osv_id || '—'}
                        </span>
                      </div>

                      {/* Severity badge */}
                      <div className="col-span-2 flex items-center">
                        <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border"
                          style={{
                            color: SEV_HEX_CVE[v.severity] || '#64748b',
                            backgroundColor: `${SEV_HEX_CVE[v.severity] || '#64748b'}12`,
                            borderColor: `${SEV_HEX_CVE[v.severity] || '#64748b'}28`,
                          }}>
                          {v.severity}
                        </span>
                      </div>

                      {/* CVSS Score */}
                      <div className="col-span-1 flex items-center">
                        <span className="text-[12px] font-bold font-mono"
                          style={{ color: v.cvss_score ? SEV_HEX_CVE[v.severity] : '#475569' }}>
                          {v.cvss_score ?? '—'}
                        </span>
                      </div>

                      {/* Fix available */}
                      <div className="col-span-2 flex items-center">
                        {v.fixed_in ? (
                          <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/[0.08] px-2 py-0.5 rounded border border-emerald-500/20 truncate">
                            → {v.fixed_in}
                          </span>
                        ) : (
                          <span className="text-[10px] text-slate-700 font-mono">No fix</span>
                        )}
                      </div>

                      {/* Details link */}
                      <div className="col-span-1 flex items-center justify-end">
                        <a href={v.details_url} target="_blank" rel="noopener noreferrer"
                          className="text-[10px] text-indigo-400/50 hover:text-indigo-400 font-mono transition-colors"
                          onClick={e => e.stopPropagation()}>
                          OSV ↗
                        </a>
                      </div>

                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Empty state after scan */}
            {cveRan && cveResults.length === 0 && (
              <div className="rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card p-10 text-center">
                <CheckCircle2 size={24} className="text-emerald-400 mx-auto mb-3" />
                <p className="text-slate-300 text-[14px] font-semibold font-tight">No CVEs found</p>
                <p className="text-slate-600 text-[12px] mt-1">
                  All {cveScanned} scanned packages appear clean in the OSV database.
                </p>
              </div>
            )}

            {/* Pre-scan state */}
            {!cveRan && (
              <div className="rounded-2xl border border-dashed border-white/[0.07] p-10 text-center">
                <ShieldAlert size={22} className="text-slate-700 mx-auto mb-3" />
                <p className="text-slate-600 text-[13px] font-medium">Click "Scan for CVEs" to check all {dependencies.length} packages</p>
                <p className="text-slate-700 text-[11px] mt-1 font-mono">
                  Queries osv.dev · free · no API key required · covers PyPI, npm, and more
                </p>
              </div>
            )}

            {/* Raw dependency list below (always visible) */}
            <div className="rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card p-5">
              <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-600 mb-3">
                All dependencies ({dependencies.length})
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 max-h-[320px] overflow-y-auto scrollbar-none">
                {dependencies.map((d: any, i: number) => {
                  const isAffected = cveRan && cveResults.some((v: any) => d.package?.includes(v.package))
                  return (
                    <div key={i} className={clsx(
                      'flex items-center gap-2.5 px-3 py-2 rounded-xl transition-colors',
                      isAffected ? 'bg-rose-500/[0.06] border border-rose-500/20' : 'hover:bg-white/[0.025]'
                    )}>
                      <span className={clsx(
                        'text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border font-mono shrink-0',
                        d.type === 'python'
                          ? 'text-blue-400 bg-blue-500/10 border-blue-500/20'
                          : d.type === 'npm_dev'
                          ? 'text-slate-500 bg-slate-800/30 border-slate-700/30'
                          : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                      )}>
                        {d.type === 'python' ? 'py' : d.type === 'npm_dev' ? 'dev' : 'npm'}
                      </span>
                      <span className="text-[11px] text-slate-400 font-mono truncate flex-1">{d.package}</span>
                      {isAffected && (
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400 shrink-0" title="CVE found" />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )
      })()
    },
    {
      id: 'tech_stack',
      label: '🛠️ Tech Stack',
      content: (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Languages</h3>
            <div className="flex flex-wrap gap-1.5">
              {techStack.languages?.length > 0 ? (
                techStack.languages.map((l: string, i: number) => (
                  <span key={i} className="text-xs bg-slate-900 border border-slate-border/40 text-slate-300 px-2 py-0.5 rounded-lg font-mono">{l}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </div>
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Frameworks</h3>
            <div className="flex flex-wrap gap-1.5">
              {techStack.frameworks?.length > 0 ? (
                techStack.frameworks.map((f: string, i: number) => (
                  <span key={i} className="text-xs bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded-lg font-mono">{f}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </div>
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Databases</h3>
            <div className="flex flex-wrap gap-1.5">
              {techStack.databases?.length > 0 ? (
                techStack.databases.map((db: string, i: number) => (
                  <span key={i} className="text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-lg font-mono">{db}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'architecture',
      label: '🏗️ Architecture',
      content: (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Backend Architecture Layers</h3>
            <div className="space-y-2">
              {architecture.layers?.length > 0 ? (
                architecture.layers.map((l: string, i: number) => (
                  <div key={i} className="bg-slate-900 border border-slate-border/40 p-2 rounded text-xs text-slate-300 font-mono">{l}</div>
                ))
              ) : <div className="text-slate-500 italic text-xs">None detected</div>}
            </div>
          </div>
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Structural Patterns</h3>
            <div className="space-y-2">
              {architecture.patterns?.length > 0 ? (
                architecture.patterns.map((p: string, i: number) => (
                  <div key={i} className="bg-slate-900 border border-slate-border/40 p-2 rounded text-xs text-slate-300 font-mono">{p}</div>
                ))
              ) : <div className="text-slate-500 italic text-xs">None detected</div>}
            </div>
          </div>
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">External Integrations</h3>
            <div className="space-y-2">
              {architecture.external_services?.length > 0 ? (
                architecture.external_services.map((s: string, i: number) => (
                  <div key={i} className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 p-2 rounded text-xs font-mono">{s}</div>
                ))
              ) : <div className="text-slate-500 italic text-xs">None detected</div>}
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'ux_architecture',
      label: '🎨 UX & Build',
      content: (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">Frontend Framework</h4>
            <div className="text-slate-200 font-bold font-mono text-sm">{uxArchitecture.frontend_framework || 'Not detected'}</div>
          </div>
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">Styling Libraries</h4>
            <div className="flex flex-wrap gap-1.5">
              {uxArchitecture.styling?.length > 0 ? (
                uxArchitecture.styling.map((s: string, i: number) => (
                  <span key={i} className="bg-slate-900 border border-slate-border/40 px-2 py-0.5 rounded text-xs font-mono text-slate-300">{s}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </div>
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">State Management</h4>
            <div className="flex flex-wrap gap-1.5">
              {uxArchitecture.state_management?.length > 0 ? (
                uxArchitecture.state_management.map((m: string, i: number) => (
                  <span key={i} className="bg-slate-900 border border-slate-border/40 px-2 py-0.5 rounded text-xs font-mono text-slate-300">{m}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </div>
          <div className={clsx(CARD, "p-6 bg-slate-surface/30")}>
            <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">Build Tools</h4>
            <div className="flex flex-wrap gap-1.5">
              {uxArchitecture.build_tools?.length > 0 ? (
                uxArchitecture.build_tools.map((b: string, i: number) => (
                  <span key={i} className="bg-slate-900 border border-slate-border/40 px-2 py-0.5 rounded text-xs font-mono text-slate-300">{b}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </div>
        </div>
      )
    },
    // ── Tier 2: Multi-Dimensional Risk Score ──────────────────────────────────
    {
      id: 'risk_score',
      label: '🏆 Risk Score',
      content: (
        <div className="space-y-6">
          {riskLoading ? (
            <div className="flex items-center justify-center py-24 text-slate-400 text-sm font-mono gap-3">
              <RefreshCw size={16} className="animate-spin text-indigo-400" />
              Computing multi-dimensional risk profile...
            </div>
          ) : !riskProfile ? (
            <div className="flex items-center justify-center py-24 text-slate-500 text-sm italic">
              Risk score unavailable — rescan to compute.
            </div>
          ) : (() => {
            const colorMap: Record<string, string> = {
              emerald: 'text-emerald-400', green: 'text-emerald-400',
              amber: 'text-amber-400', orange: 'text-orange-400', rose: 'text-rose-400'
            }
            const bgMap: Record<string, string> = {
              emerald: 'bg-emerald-500/10 border-emerald-500/20', green: 'bg-emerald-500/10 border-emerald-500/20',
              amber: 'bg-amber-500/10 border-amber-500/20', orange: 'bg-orange-500/10 border-orange-500/20',
              rose: 'bg-rose-500/10 border-rose-500/20'
            }
            const barMap: Record<string, string> = {
              emerald: 'from-emerald-500 to-emerald-400', green: 'from-emerald-500 to-emerald-400',
              amber: 'from-amber-500 to-amber-400', orange: 'from-orange-500 to-orange-400',
              rose: 'from-rose-500 to-rose-400'
            }

            // Radar chart (pure SVG)
            const cx = 140, cy = 140, r = 105
            const dims = riskProfile.dimensions
            const angles = dims.map((_, i) => (i / dims.length) * 2 * Math.PI - Math.PI / 2)
            const toXY = (angle: number, val: number) => ({
              x: cx + (val / 100) * r * Math.cos(angle),
              y: cy + (val / 100) * r * Math.sin(angle)
            })
            const gridPts = (frac: number) =>
              angles.map(a => `${cx + frac * r * Math.cos(a)},${cy + frac * r * Math.sin(a)}`).join(' ')
            const scorePts = dims.map((d, i) => {
              const p = toXY(angles[i], d.score)
              return `${p.x},${p.y}`
            }).join(' ')
            const labelPts = dims.map((d, i) => {
              const dist = r + 22
              return { x: cx + dist * Math.cos(angles[i]), y: cy + dist * Math.sin(angles[i]), name: d.name }
            })

            return (
              <>
                {/* Composite Score Hero */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className={clsx(CARD, 'lg:col-span-1 flex flex-col items-center justify-center py-10 border', bgMap[riskProfile.composite.color] || 'bg-slate-surface/30 border-white/[0.08]')}>
                    <div className="text-7xl font-black font-display tracking-tight">
                      <span className={colorMap[riskProfile.composite.color] || 'text-slate-100'}>
                        {riskProfile.composite.score.toFixed(0)}
                      </span>
                    </div>
                    <div className={clsx('text-4xl font-black mt-1', colorMap[riskProfile.composite.color])}>
                      {riskProfile.composite.grade}
                    </div>
                    <div className="text-slate-300 font-bold mt-2 text-lg">{riskProfile.composite.label}</div>
                    <div className="text-slate-500 text-xs mt-1 font-mono">Composite Risk Score</div>

                    {/* Summary pills */}
                    <div className="flex gap-3 mt-6 flex-wrap justify-center">
                      <span className="flex items-center gap-1.5 text-xs bg-rose-500/10 border border-rose-500/20 text-rose-400 px-2.5 py-1 rounded-full font-mono">
                        <AlertTriangle size={10} /> {riskProfile.summary.critical_flags} critical
                      </span>
                      <span className="flex items-center gap-1.5 text-xs bg-amber-500/10 border border-amber-500/20 text-amber-400 px-2.5 py-1 rounded-full font-mono">
                        <Info size={10} /> {riskProfile.summary.warnings} warnings
                      </span>
                      <span className="flex items-center gap-1.5 text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2.5 py-1 rounded-full font-mono">
                        <CheckCircle2 size={10} /> {riskProfile.summary.positives} passing
                      </span>
                    </div>
                  </div>

                  {/* Radar Chart */}
                  <div className={clsx(CARD, "p-6 lg:col-span-2 bg-slate-surface/30 flex items-center justify-center")}>
                    <svg viewBox="0 0 280 280" width="280" height="280">
                      {/* Grid rings */}
                      {[0.25, 0.5, 0.75, 1].map(frac => (
                        <polygon key={frac} points={gridPts(frac)}
                          fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
                      ))}
                      {/* Axis lines */}
                      {angles.map((angle, i) => (
                        <line key={i}
                          x1={cx} y1={cy}
                          x2={cx + r * Math.cos(angle)} y2={cy + r * Math.sin(angle)}
                          stroke="rgba(255,255,255,0.08)" strokeWidth="1" />
                      ))}
                      {/* Score polygon */}
                      <polygon points={scorePts}
                        fill="rgba(99,102,241,0.15)" stroke="rgba(99,102,241,0.7)"
                        strokeWidth="2" strokeLinejoin="round" />
                      {/* Score dots */}
                      {dims.map((d, i) => {
                        const p = toXY(angles[i], d.score)
                        return <circle key={i} cx={p.x} cy={p.y} r="4"
                          fill="#6366f1" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" />
                      })}
                      {/* Labels */}
                      {labelPts.map((lp, i) => (
                        <text key={i} x={lp.x} y={lp.y} textAnchor="middle" dominantBaseline="middle"
                          fontSize="9" fontFamily="Inter,sans-serif" fill="#94a3b8" fontWeight="600">
                          {lp.name}
                        </text>
                      ))}
                    </svg>
                  </div>
                </div>

                {/* Dimension Breakdown */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {riskProfile.dimensions.map(dim => (
                    <div key={dim.name} className={clsx(CARD, "p-6 bg-slate-surface/30 space-y-4")}>
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-bold text-slate-100 font-display text-sm">{dim.name}</h4>
                          <p className="text-slate-500 text-[10px] font-mono mt-0.5">Weight: {dim.weight}%</p>
                        </div>
                        <div className="text-right">
                          <span className={clsx('text-2xl font-black font-display', colorMap[dim.color] || 'text-slate-100')}>
                            {dim.score.toFixed(0)}
                          </span>
                          <span className={clsx('ml-1.5 text-sm font-bold', colorMap[dim.color])}>
                            {dim.grade}
                          </span>
                        </div>
                      </div>

                      {/* Score bar */}
                      <div className="w-full bg-slate-950/60 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={clsx('h-full rounded-full bg-gradient-to-r transition-all duration-500', barMap[dim.color] || 'from-indigo-500 to-indigo-400')}
                          style={{ width: `${dim.score}%` }}
                        />
                      </div>

                      {/* Findings */}
                      <ul className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                        {dim.findings.map((f, i) => (
                          <li key={i} className="text-[11px] text-slate-400 leading-snug">{f}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </>
            )
          })()}
        </div>
      )
    }
  ]

  // ── Navigation ────────────────────────────────────────────────────────────
  const tabGroups = [
    { id: 'security',  label: 'Security',   tabIds: ['overview', 'risk_score'] },
    { id: 'ask_ai',    label: 'ask_ai',      tabIds: ['chat'] },
    { id: 'apis',      label: 'APIs',        tabIds: ['apis'] },
    { id: 'technical', label: 'Technical',   tabIds: ['structure', 'files', 'classes', 'functions', 'error_handlers', 'middleware', 'models', 'enums', 'interfaces', 'constants', 'key_files', 'dependencies', 'tech_stack', 'architecture', 'ux_architecture'] },
  ]

  const activeGroup = tabGroups.find(g => g.tabIds.includes(currentTab))?.id ?? 'security'

  const handleGroupChange = (groupId: string) => {
    const group = tabGroups.find(g => g.id === groupId)
    if (group) setCurrentTab(group.tabIds[0])
  }

  const subTabs = dashboardTabs.filter(t =>
    tabGroups.find(g => g.id === activeGroup)?.tabIds.includes(t.id)
  )

  const activeContent = dashboardTabs.find(t => t.id === currentTab)?.content

  return (
    <div className="space-y-5 select-none animate-fade-in pb-8">

      {/* ── Page Header ───────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pt-1">
        <div>
          <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight leading-none">
            Scan Results
          </h1>
          <p className="text-slate-500 text-[13px] mt-1.5">
            Session&nbsp;<span className="text-indigo-400/80 font-mono text-[11px]">{sessionId}</span>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Remediation mode selector */}
          <div className="flex items-center gap-1 p-1 rounded-xl border border-white/[0.07] bg-slate-elevated font-mono text-[10.5px]">
            {([
              { id: 'hitl',       label: '👥 HITL',      title: 'Human-in-the-Loop: stage individual task branches' },
              { id: 'autonomous', label: '🤖 Autonomous', title: 'Autonomous: compile all fixes into one PR' },
            ] as const).map(m => (
              <button key={m.id} type="button" title={m.title}
                onClick={() => setRemediationMode(m.id)}
                className={clsx(
                  'px-3 py-1.5 rounded-lg transition-all font-semibold',
                  remediationMode === m.id
                    ? 'bg-indigo-500/15 border border-indigo-500/25 text-indigo-400'
                    : 'border border-transparent text-slate-500 hover:text-slate-300'
                )}>
                {m.label}
              </button>
            ))}
          </div>

          <button
            onClick={() => { setSessionId(null); setGlobalSessionId(null); setArtifacts(null); setSelectedKeyFile(null); setCurrentTab('overview') }}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-[11px] font-semibold border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/[0.14] transition-all bg-slate-surface hover:bg-slate-elevated"
          >
            New Scan
          </button>
        </div>
      </div>

      {/* ── Navigation ────────────────────────────────────────────────────── */}
      {dashboardTabs.length > 0 && (
        <div>
          {/* Primary group pills */}
          <div className="flex gap-2 flex-wrap items-center">
            {tabGroups.map(group => {
              const isActive = activeGroup === group.id
              const isAskAI  = group.id === 'ask_ai'

              if (isAskAI) return (
                <button key={group.id} onClick={() => handleGroupChange(group.id)}
                  className={clsx(
                    'relative overflow-hidden px-4 py-1.5 rounded-full text-[11px] font-bold font-mono transition-all duration-200 animate-glow-pulse',
                    isActive
                      ? 'bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500 text-white scale-105'
                      : 'bg-gradient-to-r from-indigo-500/20 via-violet-500/20 to-purple-500/20 border border-violet-500/35 text-violet-300 hover:border-violet-400/60 hover:scale-105'
                  )}>
                  <span className="absolute inset-0 w-1/3 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer pointer-events-none" />
                  <span className="relative flex items-center gap-1.5">
                    <span className={clsx('w-1.5 h-1.5 rounded-full shrink-0 animate-pulse', isActive ? 'bg-white/80' : 'bg-violet-400')} />
                    ✨ Ask AI
                  </span>
                </button>
              )

              return (
                <button key={group.id} onClick={() => handleGroupChange(group.id)}
                  className={clsx(
                    'px-4 py-1.5 rounded-full text-[11px] font-semibold transition-all duration-200',
                    isActive
                      ? 'bg-indigo-500 text-white shadow-sm shadow-indigo-500/30'
                      : 'border border-white/[0.08] bg-slate-surface text-slate-400 hover:text-slate-200 hover:border-white/[0.14]'
                  )}>
                  {group.label}
                </button>
              )
            })}
          </div>

          {/* Sub-tabs — underline style for small groups, wrapping pills for large */}
          {subTabs.length > 1 && (
            subTabs.length <= 4 ? (
              /* Underline tabs — Security group (2 tabs) */
              <div className="flex gap-0 border-b border-white/[0.06] mt-4">
                {subTabs.map(tab => (
                  <button key={tab.id} onClick={() => setCurrentTab(tab.id)}
                    className={clsx(
                      'px-4 py-2 text-[12px] font-medium border-b-2 -mb-px transition-colors whitespace-nowrap shrink-0',
                      currentTab === tab.id
                        ? 'border-indigo-500 text-indigo-400'
                        : 'border-transparent text-slate-500 hover:text-slate-300'
                    )}>
                    {tab.label}
                  </button>
                ))}
              </div>
            ) : (
              /* Wrapping pills — Technical group (many tabs) */
              <div className="flex flex-wrap gap-1.5 mt-4 p-3 rounded-2xl border border-white/[0.06] bg-slate-elevated">
                {subTabs.map(tab => (
                  <button key={tab.id} onClick={() => setCurrentTab(tab.id)}
                    className={clsx(
                      'px-3 py-1.5 rounded-lg text-[11px] font-medium transition-all duration-150',
                      currentTab === tab.id
                        ? 'bg-indigo-500/20 border border-indigo-500/30 text-indigo-400'
                        : 'border border-white/[0.06] text-slate-500 hover:text-slate-300 hover:border-white/[0.12] hover:bg-white/[0.03]'
                    )}>
                    {tab.label}
                  </button>
                ))}
              </div>
            )
          )}

          {/* Active tab content */}
          <div className="mt-5">{activeContent}</div>
        </div>
      )}
    </div>
  )
}


