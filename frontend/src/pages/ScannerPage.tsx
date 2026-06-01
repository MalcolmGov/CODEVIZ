import React, { useState, useEffect, useRef } from 'react'
import { ScanForm } from '@/components/features/ScanForm'
import { Card } from '@/components/common/Card'
import { Tabs } from '@/components/common/Tabs'
import { Table } from '@/components/common/Table'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { useSessionStore } from '@/store/sessionStore'
import { chatService } from '@/services/chat'
import { 
  Terminal, ShieldCheck, Cpu, Code2, Server, Globe, 
  Layers, Package, Settings, Activity, FolderGit2, Search, ArrowRight,
  FileCode2, ShieldAlert, Split, Database, ListPlus, Link, Hash, Key, Palette,
  RefreshCw, ChevronRight, ArrowUpRight, BarChart3
} from 'lucide-react'
import { Network, DataSet } from 'vis-network/standalone'
import 'vis-network/styles/vis-network.css'
import { api } from '@/services/api'
import clsx from 'clsx'

export const ScannerPage: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [artifacts, setArtifacts] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [activeStep, setActiveStep] = useState(0)
  const [selectedKeyFile, setSelectedKeyFile] = useState<any>(null)
  const networkRef = useRef<HTMLDivElement>(null)
  const [searchQueries, setSearchQueries] = useState<Record<string, string>>({})
  const [currentPages, setCurrentPages] = useState<Record<string, number>>({})
  const [apiHealth, setApiHealth] = useState<Record<string, { loading: boolean; status: string; code?: number; message?: string }>>({})
  
  const [currentTab, setCurrentTab] = useState<string>('overview')
  const [pingProgress, setPingProgress] = useState(0)
  const [isPingingAll, setIsPingingAll] = useState(false)

  const handleTestEndpoint = async (path: string, method: string, baseUrl?: string) => {
    setApiHealth(prev => ({
      ...prev,
      [path]: { loading: true, status: 'Testing...' }
    }))
    try {
      const response = await api.post('/health/ping-endpoint', { path, method, base_url: baseUrl })
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
        const response = await api.post('/health/ping-endpoint', { path, method, base_url: baseUrl })
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
      <Card className="bg-slate-surface/30 border-slate-border/40 space-y-4">
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
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setCurrentPages(prev => ({ ...prev, [tabId]: Math.max(0, page - 1) }))}
                disabled={page === 0}
                className="py-1 px-2.5"
              >
                Previous
              </Button>
              <span>{page + 1} / {totalPages}</span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setCurrentPages(prev => ({ ...prev, [tabId]: Math.min(totalPages - 1, page + 1) }))}
                disabled={page >= totalPages - 1}
                className="py-1 px-2.5"
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </Card>
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
    try {
      const response = await chatService.getArtifacts(id)
      const data = response.data.data.artifacts
      setArtifacts(data)
      if (data?.key_files?.length > 0) {
        setSelectedKeyFile(data.key_files[0])
      }
    } catch (error) {
      console.error('Failed to get artifacts:', error)
    } finally {
      // Allow the loading animation to reach final steps for premium aesthetic
      setTimeout(() => {
        setLoading(false)
      }, 1000)
    }
  }

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
        
        <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md">
          <ScanForm onScanComplete={handleScanComplete} />
        </Card>
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

  const metricCards = [
    { id: 'files', label: 'Files', count: artifacts?.files?.length || 0, icon: FileCode2, color: 'text-indigo-400 border-indigo-500/20 bg-indigo-500/5' },
    { id: 'apis', label: 'APIs', count: apis.length, icon: Server, color: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5' },
    { id: 'classes', label: 'Classes', count: classes.length, icon: Cpu, color: 'text-purple-400 border-purple-500/20 bg-purple-500/5' },
    { id: 'functions', label: 'Functions', count: functions.length, icon: Code2, color: 'text-pink-400 border-pink-500/20 bg-pink-500/5' },
    { id: 'middleware', label: 'Middleware', count: middleware.length, icon: Split, color: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/5' },
    { id: 'models', label: 'Models', count: models.length, icon: Database, color: 'text-amber-400 border-amber-500/20 bg-amber-500/5' },
    { id: 'enums', label: 'Enums', count: enums.length, icon: ListPlus, color: 'text-orange-400 border-orange-500/20 bg-orange-500/5' },
    { id: 'error_handlers', label: 'Errors', count: error_handlers.length, icon: ShieldAlert, color: 'text-rose-400 border-rose-500/20 bg-rose-500/5' },
    { id: 'interfaces', label: 'Interfaces', count: interfaces.length, icon: Link, color: 'text-blue-400 border-blue-500/20 bg-blue-500/5' },
    { id: 'dependencies', label: 'Dependencies', count: dependencies.length, icon: Package, color: 'text-violet-400 border-violet-500/20 bg-violet-500/5' },
  ]

  const dashboardTabs = [
    {
      id: 'overview',
      label: '📊 Overview',
      content: (
        <div className="space-y-6">
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            {metricCards.map((card) => (
              <div 
                key={card.id}
                onClick={() => setCurrentTab(card.id)}
                className="bg-slate-950/40 border border-slate-border/50 hover:border-indigo-500/40 rounded-xl p-4 transition-all duration-205 cursor-pointer hover:-translate-y-0.5 group flex flex-col justify-between h-[110px]"
              >
                <div className="flex justify-between items-start">
                  <span className="text-slate-400 text-[10px] font-bold uppercase tracking-wider font-display truncate">
                    {card.label}
                  </span>
                  <div className={clsx("p-1.5 rounded-lg border", card.color.split(' ')[1], card.color.split(' ')[2])}>
                    <card.icon size={12} className={card.color.split(' ')[0]} />
                  </div>
                </div>
                <div className="mt-2 flex justify-between items-baseline">
                  <span className="text-xl font-black text-slate-100 font-display tracking-tight group-hover:text-indigo-400 transition-colors">
                    {card.count}
                  </span>
                  <span className="text-[10px] text-slate-500 group-hover:text-indigo-400/80 transition-colors font-mono">
                    View →
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Diagnostics and Highlights */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* API Diagnostics */}
            <Card className="lg:col-span-2 space-y-4 bg-slate-surface/30 border-slate-border/40 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                  <div>
                    <h3 className="text-base font-bold text-slate-100 font-display flex items-center gap-2">
                      <Server size={16} className="text-indigo-400" />
                      API Diagnostics Check
                    </h3>
                    <p className="text-slate-400 text-xs mt-0.5">Test reachability and status of discovered endpoints.</p>
                  </div>
                  
                  <button
                    onClick={handlePingAll}
                    disabled={isPingingAll || apis.length === 0}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold font-mono bg-indigo-500 hover:bg-indigo-600 disabled:bg-indigo-800/40 text-white disabled:text-slate-400 border border-indigo-500/20 disabled:border-transparent transition-all shrink-0"
                  >
                    <RefreshCw size={12} className={clsx(isPingingAll && 'animate-spin')} />
                    {isPingingAll ? 'Pinging...' : 'Ping All Routes'}
                  </button>
                </div>

                {isPingingAll && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] font-mono text-slate-400">
                      <span>Running diagnostics check...</span>
                      <span>{pingProgress}%</span>
                    </div>
                    <div className="w-full bg-slate-950/50 rounded-full h-1 border border-slate-border/40 overflow-hidden">
                      <div 
                        className="bg-indigo-500 h-full rounded-full transition-all duration-200" 
                        style={{ width: `${pingProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                {apis.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-[220px] overflow-y-auto pr-1">
                    {apis.map((apiItem: any, idx: number) => {
                      const health = apiHealth[apiItem.path]
                      const method = apiItem.methods?.[0] || 'GET'
                      return (
                        <div 
                          key={idx}
                          className="flex items-center justify-between p-2 rounded-lg bg-slate-950/30 border border-slate-border/30 hover:border-slate-border/60 transition-all text-xs"
                        >
                          <div className="flex items-center gap-2 font-mono overflow-hidden mr-2">
                            <span className="px-1.5 py-0.5 rounded text-[8px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase">
                              {method}
                            </span>
                            <span className="text-slate-300 font-semibold truncate text-[11px]" title={apiItem.path}>
                              {apiItem.path}
                            </span>
                          </div>
                          
                          <div className="flex items-center gap-2 shrink-0">
                            <span className={clsx(
                              "w-1.5 h-1.5 rounded-full",
                              health?.loading ? "bg-amber-500 animate-pulse" :
                              health?.status === 'Online' ? "bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.4)]" :
                              health?.status === 'Offline' ? "bg-rose-500 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.4)]" : "bg-slate-500"
                            )} />
                            <span className={clsx(
                              "text-[9px] font-bold font-mono",
                              health?.loading ? "text-amber-400" :
                              health?.status === 'Online' ? "text-emerald-400" :
                              health?.status === 'Offline' ? "text-rose-400" : "text-slate-500"
                            )}>
                              {health?.loading ? 'Ping...' : health?.status === 'Online' ? `200` : health?.status === 'Offline' ? 'ERR' : 'Untested'}
                            </span>
                            
                            <button
                              onClick={() => handleTestEndpoint(apiItem.path, method)}
                              disabled={isPingingAll}
                              className="text-[9px] bg-slate-900 border border-slate-border/60 text-slate-400 hover:text-indigo-400 px-1.5 py-0.5 rounded transition-all font-mono"
                            >
                              Test
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-slate-500 text-xs italic py-4 text-center">
                    No REST endpoints found in this repository.
                  </div>
                )}
              </div>
            </Card>

            {/* Code Highlights */}
            <Card className="bg-slate-surface/30 border-slate-border/40 flex flex-col justify-between">
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-100 font-display flex items-center gap-2">
                  <FileCode2 size={16} className="text-indigo-400" />
                  Key Code Highlights
                </h3>
                {keyFiles.length > 0 ? (
                  <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                    {keyFiles.slice(0, 4).map((file: any, idx: number) => {
                      const maxLines = Math.max(...keyFiles.map((f: any) => f.lines || 1))
                      const percentage = Math.min(100, Math.round((file.lines / maxLines) * 100))
                      return (
                        <div 
                          key={idx} 
                          onClick={() => {
                            setSelectedKeyFile(file)
                            setCurrentTab('key_files')
                          }}
                          className="bg-slate-950/40 border border-slate-border/50 hover:border-indigo-500/30 p-2.5 rounded-xl transition-all duration-200 cursor-pointer group space-y-1.5"
                        >
                          <div className="flex justify-between items-center text-xs">
                            <span className="font-mono text-slate-300 font-bold group-hover:text-indigo-400 transition-colors truncate max-w-[170px]" title={file.name}>
                              {file.name}
                            </span>
                            <span className="text-[10px] text-slate-500 font-mono">
                              {file.lines} lines
                            </span>
                          </div>
                          <div className="w-full bg-slate-900/60 h-1 rounded-full overflow-hidden">
                            <div 
                              className="bg-gradient-to-r from-indigo-500 to-indigo-400 h-full rounded-full transition-all"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-slate-500 text-xs italic py-4 text-center">
                    No key files identified.
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Network Graph */}
          <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md p-6 space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-base font-bold text-slate-100 font-display">🌐 Interconnected Network Mesh</h3>
                <p className="text-slate-400 text-xs mt-0.5">Obsidian-inspired interconnected view of APIs, classes, and functions.</p>
              </div>
              <Badge severity="medium">vis.js Network</Badge>
            </div>
            
            <div 
              ref={networkRef}
              className="w-full h-[320px] bg-slate-950/60 rounded-xl border border-slate-border/30 overflow-hidden relative"
            />
          </Card>
        </div>
      )
    },
    {
      id: 'structure',
      label: '🌳 Structure',
      content: (
        <Card className="space-y-4 bg-slate-surface/30 border-slate-border/40">
          <div>
            <h3 className="text-base font-bold text-slate-100 font-display">Directory Structure</h3>
            <p className="text-slate-400 text-xs mt-0.5">Static representation of repository directories.</p>
          </div>
          <pre className="bg-slate-950/60 p-5 border border-slate-border/30 rounded-xl overflow-x-auto text-xs font-mono text-slate-300 leading-relaxed max-h-[500px]">
            {artifacts?.structure || 'No structure parsed.'}
          </pre>
        </Card>
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
      content: renderExplorer('apis', 'Discovered REST Endpoints', 'Routes parsed from router annotations and HTTP middleware.', apis, apisColumns, ['path', 'file', 'methods'])
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
          <Card className="bg-slate-surface/30 border-slate-border/40 max-h-[500px] overflow-y-auto">
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
          </Card>

          <Card className="lg:col-span-2 bg-slate-surface/30 border-slate-border/40 flex flex-col">
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
          </Card>
        </div>
      )
    },
    {
      id: 'dependencies',
      label: `📚 Deps (${dependencies.length})`,
      content: renderExplorer('dependencies', 'Manifest Dependencies', 'Project modules parsed from lockfiles and requirements.', dependencies, dependenciesColumns, ['package', 'type'])
    },
    {
      id: 'tech_stack',
      label: '🛠️ Tech Stack',
      content: (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Languages</h3>
            <div className="flex flex-wrap gap-1.5">
              {techStack.languages?.length > 0 ? (
                techStack.languages.map((l: string, i: number) => (
                  <span key={i} className="text-xs bg-slate-900 border border-slate-border/40 text-slate-300 px-2 py-0.5 rounded-lg font-mono">{l}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </Card>
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Frameworks</h3>
            <div className="flex flex-wrap gap-1.5">
              {techStack.frameworks?.length > 0 ? (
                techStack.frameworks.map((f: string, i: number) => (
                  <span key={i} className="text-xs bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded-lg font-mono">{f}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </Card>
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Databases</h3>
            <div className="flex flex-wrap gap-1.5">
              {techStack.databases?.length > 0 ? (
                techStack.databases.map((db: string, i: number) => (
                  <span key={i} className="text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-lg font-mono">{db}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </Card>
        </div>
      )
    },
    {
      id: 'architecture',
      label: '🏗️ Architecture',
      content: (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Backend Architecture Layers</h3>
            <div className="space-y-2">
              {architecture.layers?.length > 0 ? (
                architecture.layers.map((l: string, i: number) => (
                  <div key={i} className="bg-slate-900 border border-slate-border/40 p-2 rounded text-xs text-slate-300 font-mono">{l}</div>
                ))
              ) : <div className="text-slate-500 italic text-xs">None detected</div>}
            </div>
          </Card>
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">Structural Patterns</h3>
            <div className="space-y-2">
              {architecture.patterns?.length > 0 ? (
                architecture.patterns.map((p: string, i: number) => (
                  <div key={i} className="bg-slate-900 border border-slate-border/40 p-2 rounded text-xs text-slate-300 font-mono">{p}</div>
                ))
              ) : <div className="text-slate-500 italic text-xs">None detected</div>}
            </div>
          </Card>
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h3 className="text-sm font-bold text-slate-100 font-display mb-3">External Integrations</h3>
            <div className="space-y-2">
              {architecture.external_services?.length > 0 ? (
                architecture.external_services.map((s: string, i: number) => (
                  <div key={i} className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 p-2 rounded text-xs font-mono">{s}</div>
                ))
              ) : <div className="text-slate-500 italic text-xs">None detected</div>}
            </div>
          </Card>
        </div>
      )
    },
    {
      id: 'ux_architecture',
      label: '🎨 UX & Build',
      content: (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">Frontend Framework</h4>
            <div className="text-slate-200 font-bold font-mono text-sm">{uxArchitecture.frontend_framework || 'Not detected'}</div>
          </Card>
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">Styling Libraries</h4>
            <div className="flex flex-wrap gap-1.5">
              {uxArchitecture.styling?.length > 0 ? (
                uxArchitecture.styling.map((s: string, i: number) => (
                  <span key={i} className="bg-slate-900 border border-slate-border/40 px-2 py-0.5 rounded text-xs font-mono text-slate-300">{s}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </Card>
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">State Management</h4>
            <div className="flex flex-wrap gap-1.5">
              {uxArchitecture.state_management?.length > 0 ? (
                uxArchitecture.state_management.map((m: string, i: number) => (
                  <span key={i} className="bg-slate-900 border border-slate-border/40 px-2 py-0.5 rounded text-xs font-mono text-slate-300">{m}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </Card>
          <Card className="bg-slate-surface/30 border-slate-border/40">
            <h4 className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-2">Build Tools</h4>
            <div className="flex flex-wrap gap-1.5">
              {uxArchitecture.build_tools?.length > 0 ? (
                uxArchitecture.build_tools.map((b: string, i: number) => (
                  <span key={i} className="bg-slate-900 border border-slate-border/40 px-2 py-0.5 rounded text-xs font-mono text-slate-300">{b}</span>
                ))
              ) : <span className="text-slate-500 italic text-xs">None detected</span>}
            </div>
          </Card>
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6 select-none animate-fade-in">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-100 font-display tracking-tight">Scan Results</h1>
          <p className="text-slate-400 text-sm mt-1.5 font-medium">Session ID: <span className="text-indigo-400 font-mono">{sessionId}</span></p>
        </div>
        <Button 
          onClick={() => {
            setSessionId(null)
            setArtifacts(null)
            setSelectedKeyFile(null)
            setCurrentTab('overview')
          }}
          variant="secondary"
          size="sm"
          className="border-slate-border/80 hover:bg-slate-800"
        >
          New Sandbox Scan
        </Button>
      </div>
      
      {dashboardTabs.length > 0 && (
        <Tabs 
          tabs={dashboardTabs} 
          activeTab={currentTab} 
          onChange={(tabId) => setCurrentTab(tabId)} 
        />
      )}
    </div>
  )
}


