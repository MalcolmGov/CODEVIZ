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
  FileCode2, ShieldAlert, Split, Database, ListPlus, Link, Hash, Key, Palette
} from 'lucide-react'
import { Network, DataSet } from 'vis-network/standalone'
import 'vis-network/styles/vis-network.css'

export const ScannerPage: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [artifacts, setArtifacts] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [activeStep, setActiveStep] = useState(0)
  const [selectedKeyFile, setSelectedKeyFile] = useState<any>(null)
  const networkRef = useRef<HTMLDivElement>(null)

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
    if (!artifacts) return

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
  }, [artifacts])

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

  const dashboardTabs = [
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
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Scanned Files</h3>
            <p className="text-slate-400 text-xs mt-0.5">Files index compiled during AST scanning.</p>
          </div>
          <Table 
            columns={[
              { key: 'path', label: 'File Path', render: (row) => <span className="font-mono text-xs text-slate-300">{row.path}</span> },
              { 
                key: 'ext', 
                label: 'File Type', 
                render: (row) => {
                  const ext = row.path.split('.').pop() || 'file';
                  return <Badge severity="low">{ext.toUpperCase()}</Badge>
                }
              }
            ]}
            data={(artifacts?.files || []).map((f: string) => ({ path: f }))}
          />
        </Card>
      )
    },
    {
      id: 'apis',
      label: `🔌 APIs (${apis.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Discovered REST Endpoints</h3>
            <p className="text-slate-400 text-xs mt-0.5">Routes parsed from router annotations and HTTP middleware.</p>
          </div>
          <Table 
            columns={[
              { 
                key: 'methods', 
                label: 'Method',
                render: (row) => (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border border-indigo-500/20 bg-indigo-500/10 text-indigo-400">
                    {row.methods?.join(', ') || 'GET'}
                  </span>
                )
              },
              { key: 'path', label: 'Route Path', render: (row) => <code className="text-xs text-indigo-300 bg-indigo-950/20 px-1.5 py-0.5 rounded font-mono">{row.path}</code> },
              { key: 'file', label: 'Source Location', render: (row) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> },
              {
                key: 'type',
                label: 'Framework',
                render: (row) => (
                  <span className="text-xs text-slate-500 font-mono">
                    {row.type || 'Route'}
                  </span>
                )
              }
            ]}
            data={apis}
          />
        </Card>
      )
    },
    {
      id: 'classes',
      label: `📦 Classes (${classes.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">AST Class Models</h3>
            <p className="text-slate-400 text-xs mt-0.5">Classes, structural hierarchies, and inheritance contexts.</p>
          </div>
          <Table 
            columns={[
              { key: 'name', label: 'Class Name', render: (row) => <span className="font-bold text-slate-200">{row.name}</span> },
              { key: 'bases', label: 'Extends / Base Class', render: (row) => row.bases ? <code className="text-xs font-mono text-indigo-400">{row.bases}</code> : <span className="text-slate-600">-</span> },
              { key: 'file', label: 'Source Location', render: (row) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> },
              {
                key: 'type',
                label: 'Archetype',
                render: (row) => (
                  <Badge severity="medium">
                    {row.type || 'Class'}
                  </Badge>
                )
              }
            ]}
            data={classes}
          />
        </Card>
      )
    },
    {
      id: 'functions',
      label: `⚙️ Functions (${functions.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Functions & Methods</h3>
            <p className="text-slate-400 text-xs mt-0.5">Extracted functions, parameters, and callback actions.</p>
          </div>
          <Table 
            columns={[
              { key: 'name', label: 'Function Name', render: (row) => <span className="font-mono text-indigo-300 font-semibold">{row.name}</span> },
              { 
                key: 'params', 
                label: 'Parameters',
                render: (row) => (
                  <span className="font-mono text-xs text-slate-400">
                    {row.params ? `(${row.params})` : '()'}
                  </span>
                )
              },
              { key: 'file', label: 'Source Location', render: (row) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
            ]}
            data={functions}
          />
        </Card>
      )
    },
    {
      id: 'error_handlers',
      label: `❌ Errors (${error_handlers.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Error Handlers</h3>
            <p className="text-slate-400 text-xs mt-0.5">Global REST exception handlers.</p>
          </div>
          <Table 
            columns={[
              { 
                key: 'error_code', 
                label: 'HTTP Code', 
                render: (row) => <Badge severity={parseInt(row.error_code) >= 500 ? 'critical' : 'medium'}>{row.error_code || 'Catch-all'}</Badge> 
              },
              { key: 'file', label: 'File Location', render: (row) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
            ]}
            data={error_handlers}
          />
        </Card>
      )
    },
    {
      id: 'middleware',
      label: `🛣️ Middleware (${middleware.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Middleware Interceptors</h3>
            <p className="text-slate-400 text-xs mt-0.5">Custom middleware blocks executing on routes.</p>
          </div>
          <Table 
            columns={[
              { key: 'name', label: 'Middleware Name', render: (row) => <span className="font-bold text-indigo-300 font-mono">{row.name}</span> },
              { key: 'file', label: 'File Location', render: (row) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
            ]}
            data={middleware}
          />
        </Card>
      )
    },
    {
      id: 'models',
      label: `🗂️ Models (${models.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Database Models</h3>
            <p className="text-slate-400 text-xs mt-0.5">Database entities mapped to backend tables.</p>
          </div>
          <Table 
            columns={[
              { key: 'name', label: 'Model Name', render: (row) => <span className="font-bold text-slate-200">{row.name}</span> },
              { key: 'file', label: 'Source Location', render: (row) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> },
              {
                key: 'type',
                label: 'Archetype',
                render: (row) => (
                  <Badge severity="low">
                    {row.type || 'Model'}
                  </Badge>
                )
              }
            ]}
            data={models}
          />
        </Card>
      )
    },
    {
      id: 'enums',
      label: `📋 Enums (${enums.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Enums</h3>
            <p className="text-slate-400 text-xs mt-0.5">Standardized developer enum categories.</p>
          </div>
          <Table 
            columns={[
              { key: 'name', label: 'Enum Name', render: (row) => <span className="font-bold text-indigo-300 font-mono">{row.name}</span> },
              { key: 'file', label: 'Source Location', render: (row) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
            ]}
            data={enums}
          />
        </Card>
      )
    },
    {
      id: 'interfaces',
      label: `🔗 Interfaces (${interfaces.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Interfaces & Contracts</h3>
            <p className="text-slate-400 text-xs mt-0.5">Type contracts, configurations, and API structures.</p>
          </div>
          <Table 
            columns={[
              { key: 'name', label: 'Interface Name', render: (row) => <span className="font-bold text-slate-200">{row.name}</span> },
              { key: 'extends', label: 'Extends', render: (row) => row.extends ? <code className="text-xs text-indigo-400 font-mono">{row.extends}</code> : <span className="text-slate-600">-</span> },
              { key: 'file', label: 'Source Location', render: (row) => <span className="text-xs text-slate-400 font-mono">{row.file}</span> }
            ]}
            data={interfaces}
          />
        </Card>
      )
    },
    {
      id: 'constants',
      label: `📌 Constants (${constants.length})`,
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Global Constants</h3>
            <p className="text-slate-400 text-xs mt-0.5">Constant parameters and config settings.</p>
          </div>
          <Table 
            columns={[
              { key: 'name', label: 'Constant Name', render: (row) => <span className="font-bold font-mono text-indigo-300">{row.name}</span> },
              { 
                key: 'value', 
                label: 'Assigned Value',
                render: (row) => (
                  <span className="font-mono text-xs text-indigo-400 bg-indigo-500/5 px-2 py-0.5 rounded border border-indigo-500/10">
                    {row.value || '-'}
                  </span>
                )
              },
              { key: 'file', label: 'Source Location' }
            ]}
            data={constants}
          />
        </Card>
      )
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
      content: (
        <Card className="bg-slate-surface/30 border-slate-border/40">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-100 font-display">Manifest Dependencies</h3>
            <p className="text-slate-400 text-xs mt-0.5">Project modules parsed from lockfiles and requirements.</p>
          </div>
          <Table 
            columns={[
              { key: 'package', label: 'Package Name & Constraints', render: (row) => <span className="font-mono text-xs text-slate-300">{row.package}</span> },
              { 
                key: 'type', 
                label: 'Module Manager',
                render: (row) => (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-slate-900 border border-slate-border/40 text-slate-400">
                    {row.type || 'Dependency'}
                  </span>
                )
              }
            ]}
            data={dependencies}
          />
        </Card>
      )
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
          }}
          variant="secondary"
          size="sm"
          className="border-slate-border/80 hover:bg-slate-800"
        >
          New Sandbox Scan
        </Button>
      </div>
      
      {dashboardTabs.length > 0 && <Tabs tabs={dashboardTabs} defaultTab="structure" />}

      {dashboardTabs.length > 0 && (
        <Card className="border-slate-border/40 bg-slate-surface/30 backdrop-blur-md p-6 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-slate-100 font-display">🌐 Interactive Dependency Graph</h2>
              <p className="text-slate-400 text-xs mt-0.5">Obsidian-inspired interconnected view of APIs, classes, and functions.</p>
            </div>
            <Badge severity="medium">vis.js Network</Badge>
          </div>
          
          <div 
            ref={networkRef}
            className="w-full h-[450px] bg-slate-950/60 rounded-xl border border-slate-border/30 overflow-hidden relative"
          />
        </Card>
      )}
    </div>
  )
}


