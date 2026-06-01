import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/common/Button'
import { Card } from '@/components/common/Card'
import { 
  Shield, BarChart3, RefreshCw, Terminal, CheckCircle2, 
  ChevronRight, Activity, Cpu, Code2, Server, Globe, 
  Layers, Package, ArrowRight, FileCode2, ShieldAlert, 
  MessageSquare, Sparkles, AlertCircle, ArrowUpRight, HelpCircle
} from 'lucide-react'

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()

  const stats = [
    { label: 'Scan Performance', value: '10k+ LOC', desc: 'in < 2 minutes' },
    { label: 'Detection Accuracy', value: '94%', desc: 'with < 3% false positives' },
    { label: 'Functional Endpoints', value: '28 API', desc: 'endpoints active' },
    { label: 'State Management', value: '4 Stores', desc: 'powered by Zustand' },
  ]

  const features = [
    {
      icon: Cpu,
      title: 'Repository Scanner',
      desc: 'Static AST indexing and multi-language support (Python, JS/TS, Go, Java) with real-time session progress logs.',
      badge: 'Real-time'
    },
    {
      icon: ShieldAlert,
      title: 'Security Analysis',
      desc: 'CVE detection, OWASP mapping, SQLi/XSS prevention, and hardcoded secret scanning with high confidence scoring.',
      badge: '94% Accuracy'
    },
    {
      icon: RefreshCw,
      title: 'Intelligent Refactoring',
      desc: 'AI-driven suggestions for complexity reduction, duplication removal, type-safety additions, and modern code syntax.',
      badge: 'AI Engine'
    },
    {
      icon: FileCode2,
      title: 'Automated PR Generation',
      desc: 'One-click GitHub pull request creation with detailed summaries explaining the changes, risks, and testing guidelines.',
      badge: 'Automated'
    },
    {
      icon: MessageSquare,
      title: 'AI Code Chat Companion',
      desc: 'Context-aware interactive conversational interface. Ask questions like "What does this do?" or "How can I improve this?".',
      badge: 'Context-Aware'
    },
    {
      icon: Layers,
      title: 'Compliance & Risk Scoring',
      desc: 'PCI-DSS validation, SOC2 readiness, HIPAA validation, and business impact score maps compiled dynamically.',
      badge: 'Enterprise'
    }
  ]

  const comparisons = [
    { name: 'AI-Powered Reasoning', codeviz: true, sonar: false, github: true, snyk: true },
    { name: 'Refactoring Code Suggestions', codeviz: true, sonar: false, github: false, snyk: false },
    { name: 'On-Click PR Generation', codeviz: true, sonar: false, github: false, snyk: true },
    { name: 'Contextual Chat Companion', codeviz: true, sonar: false, github: false, snyk: false },
    { name: 'On-Premise LLM Support', codeviz: true, sonar: false, github: false, snyk: false },
    { name: 'Compliance Reports (SOC2/PCI)', codeviz: true, sonar: true, github: true, snyk: false },
    { name: 'Custom Security Policies', codeviz: true, sonar: true, github: false, snyk: true },
  ]

  const pricing = [
    {
      name: 'Free Tier',
      price: '$0',
      desc: 'For individual developers testing AI analysis.',
      features: ['2 scans / month', '1 active repository', 'Basic security scanning', 'Standard reports'],
      btnText: 'Start Free',
      popular: false
    },
    {
      name: 'Developer Pro',
      price: '$49',
      desc: 'For professional developers needing full capabilities.',
      features: ['Unlimited repository scans', '5 active repositories', 'Advanced refactoring engine', 'Email support', 'Full GitHub integration'],
      btnText: 'Go Pro',
      popular: true
    },
    {
      name: 'Engineering Team',
      price: '$199',
      desc: 'For collaborative teams and development workflows.',
      features: ['20 active repositories', 'Team collaboration sandbox', 'Custom security policies', 'Slack integration', 'Priority support'],
      btnText: 'Get Team',
      popular: false
    },
    {
      name: 'Enterprise Custom',
      price: 'Custom',
      desc: 'On-premise deployability and dedicated infrastructure.',
      features: ['Unlimited repositories', 'On-premise LLM deployment', 'SSO/SAML integration', 'Dedicated support SLA', 'Audit trail logging'],
      btnText: 'Contact Sales',
      popular: false
    }
  ]

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 relative overflow-hidden select-none font-sans scroll-smooth">
      {/* Background decoration elements */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f293708_1px,transparent_1px),linear-gradient(to_bottom,#1f293708_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-600/5 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-[20%] left-[-100px] w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-[150px] pointer-events-none" />
      <div className="absolute bottom-[10%] right-[-100px] w-[500px] h-[500px] bg-emerald-600/5 rounded-full blur-[130px] pointer-events-none" />

      {/* Navigation Header */}
      <header className="sticky top-0 bg-[#030712]/75 backdrop-blur-md border-b border-slate-border/20 z-50 px-6 py-4 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/15">
              <Shield size={16} />
            </div>
            <span className="text-xl font-extrabold tracking-tight text-slate-100 font-display">
              Code<span className="text-indigo-400 font-medium">Viz</span>
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-400">
            <a href="#features" className="hover:text-slate-200 transition-colors">Features</a>
            <a href="#graph" className="hover:text-slate-200 transition-colors">Dependency Visualizer</a>
            <a href="#pricing" className="hover:text-slate-200 transition-colors">Pricing</a>
            <a href="#compare" className="hover:text-slate-200 transition-colors">Comparison</a>
          </nav>

          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate('/login')} 
              className="text-sm font-semibold text-slate-300 hover:text-slate-100 px-4 py-2"
            >
              Sign In
            </button>
            <Button 
              onClick={() => navigate('/login')} 
              variant="primary" 
              size="sm"
            >
              Get Started Free
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-16 px-6 max-w-7xl mx-auto text-center space-y-8">
        <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 px-3.5 py-1 rounded-full text-xs font-bold text-indigo-400 animate-pulse">
          <Sparkles size={12} />
          <span>POWERED BY ON-PREMISE AI LLM REASONING</span>
        </div>

        <h1 className="text-4xl sm:text-6xl md:text-7xl font-black font-display tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-white via-slate-100 to-slate-400 max-w-4xl mx-auto leading-none">
          The AI Code Reviewer <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500">
            That Never Sleeps
          </span>
        </h1>

        <p className="text-slate-400 text-base sm:text-xl font-medium max-w-2xl mx-auto leading-relaxed">
          Scan entire codebases, detect security vulnerabilities with 94% accuracy, suggest refactoring diffs, and generate pull requests automatically.
        </p>

        <div className="flex flex-col sm:flex-row justify-center items-center gap-4 pt-4">
          <Button 
            onClick={() => navigate('/login')} 
            variant="primary" 
            size="lg"
            className="w-full sm:w-auto px-8 py-3 text-base shadow-lg shadow-indigo-500/20"
          >
            Start Scanning Now <ArrowRight className="ml-2" size={18} />
          </Button>
          <button
            onClick={() => {
              const el = document.getElementById('features')
              el?.scrollIntoView({ behavior: 'smooth' })
            }}
            className="w-full sm:w-auto px-6 py-3 text-sm font-bold border border-slate-border/50 hover:bg-slate-900/30 rounded-xl transition-all text-slate-300 hover:text-slate-100"
          >
            Explore Platform Features
          </button>
        </div>

        {/* Hero Interactive Screen Preview */}
        <div className="pt-10 max-w-5xl mx-auto relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-2xl blur-xl opacity-20 group-hover:opacity-30 transition duration-1000" />
          <Card className="bg-slate-surface/30 border-slate-border/40 backdrop-blur-md overflow-hidden relative shadow-2xl p-0.5">
            <div className="bg-[#0b0f19] rounded-xl overflow-hidden border border-slate-border/30">
              {/* Window Controls */}
              <div className="flex items-center justify-between px-4 py-3 bg-[#070b13] border-b border-slate-border/30">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="text-[10px] font-mono text-slate-500 bg-slate-900/50 px-3 py-1 rounded border border-slate-border/20">
                  sandbox://codeviz-terminal-preview
                </div>
                <div className="w-10" />
              </div>
              {/* Terminal Screen Mock */}
              <div className="p-6 text-left font-mono text-xs text-slate-300 space-y-4 max-h-[360px] overflow-y-auto bg-[#040810]/90">
                <div className="flex gap-2 text-indigo-400">
                  <span>$</span>
                  <span>codeviz scan --path=/app/src</span>
                </div>
                <div className="text-slate-500">🔍 Initializing static codebase analysis engine...</div>
                <div className="text-emerald-400">✓ Parsed 82 codebase source files (3.2M LOC total)</div>
                <div className="text-slate-400">├── Discovered 17 REST endpoints</div>
                <div className="text-slate-400">├── Discovered 408 structure classes</div>
                <div className="text-slate-400">└── Discovered 1,761 modular function declarations</div>
                <div className="text-amber-400">⚠️  Vulnerability Score: 8 security vulnerabilities detected</div>
                <div className="text-indigo-400 bg-indigo-950/20 border border-indigo-500/20 p-3 rounded-lg mt-3 flex items-start gap-3">
                  <Activity size={16} className="text-indigo-400 mt-0.5 animate-pulse" />
                  <div>
                    <span className="font-bold text-slate-200">Refactoring Opportunity Found:</span>
                    <p className="text-slate-400 text-[11px] mt-0.5">Complexity exceeds 15 inside `backend/core/scanner_legacy.py`. Suggested Extract Method patch created.</p>
                  </div>
                </div>
                <div className="text-emerald-400 font-bold">$ codeviz pr-generate --issue=SEC-08</div>
                <div className="text-slate-300">🚀 Generating automated security patch pull request... done. (PR #42 opened on GitHub)</div>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Stats Banner */}
      <section className="bg-slate-surface/10 border-y border-slate-border/20 py-10 px-6">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {stats.map((stat, i) => (
            <div key={i} className="space-y-1">
              <p className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-400 font-display">
                {stat.value}
              </p>
              <p className="text-xs font-semibold text-slate-300 font-display uppercase tracking-wider">{stat.label}</p>
              <p className="text-[10px] text-slate-500 font-mono">{stat.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            Multi-Dimensional Analysis
          </h2>
          <p className="text-slate-400 text-sm md:text-base max-w-xl mx-auto">
            Unlike traditional scanning utilities that isolate features, CodeViz analyzes structure, quality, security, and refactoring pathways simultaneously.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, i) => {
            const Icon = feat.icon
            return (
              <Card key={i} className="bg-slate-surface/30 border-slate-border/40 hover:border-indigo-500/30 p-6 flex flex-col justify-between hover:-translate-y-0.5 transition-all duration-300 group">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 group-hover:bg-indigo-500/20 group-hover:text-indigo-300 transition-colors">
                      <Icon size={20} />
                    </div>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border border-slate-border/60 text-slate-400 bg-slate-900/50">
                      {feat.badge}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-100 font-display">{feat.title}</h3>
                  <p className="text-slate-400 text-xs leading-relaxed font-medium">{feat.desc}</p>
                </div>
              </Card>
            )
          })}
        </div>
      </section>

      {/* Animated Obsidian Graph Showcase */}
      <section id="graph" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-purple-400">
              <Activity size={10} />
              <span>VISUAL CODE MESH</span>
            </div>
            <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight leading-tight text-slate-100">
              Obsidian-Inspired <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">
                Dependency Network
              </span>
            </h2>
            <p className="text-slate-400 text-sm md:text-base leading-relaxed">
              Explore structural coupling, classes, functions, and API linkages in a fully interactive, force-directed graph. View how modifications in one class propagate changes across downstream functions instantly.
            </p>
            <div className="space-y-3">
              {[
                { title: 'Interactive drag & zoom physics controls', value: 'forceAtlas2Based solver' },
                { title: 'Type-grouped Node accent colors', value: 'APIs, Classes, & Functions' },
                { title: 'Seamless ES Module bundling', value: 'Zero external CDN dependancy errors' },
              ].map((item, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />
                  <span className="text-xs text-slate-300 font-semibold">{item.title}</span>
                  <span className="text-[10px] text-slate-500 font-mono ml-auto">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Mock Graph */}
          <div className="relative p-0.5 bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-transparent rounded-2xl border border-slate-border/40 overflow-hidden shadow-2xl">
            <div className="absolute inset-0 bg-[#030712]/40 backdrop-blur-sm pointer-events-none" />
            
            {/* Animated SVG Graph */}
            <svg viewBox="0 0 400 350" className="w-full h-[350px] relative z-10 select-none pointer-events-none">
              {/* Grid backdrop */}
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.015)" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              {/* Connections (Edges) */}
              <g stroke="rgba(255,255,255,0.08)" strokeWidth="1">
                <line x1="80" y1="120" x2="200" y2="80" className="animate-pulse" />
                <line x1="200" y1="80" x2="320" y2="120" />
                <line x1="200" y1="80" x2="200" y2="200" />
                <line x1="80" y1="120" x2="110" y2="240" />
                <line x1="320" y1="120" x2="290" y2="240" />
                <line x1="200" y1="200" x2="110" y2="240" />
                <line x1="200" y1="200" x2="290" y2="240" />
                <line x1="110" y1="240" x2="200" y2="290" />
                <line x1="290" y1="240" x2="200" y2="290" />
              </g>

              {/* API Node (Indigo) */}
              <g transform="translate(200, 80)">
                <circle r="22" fill="rgba(99, 102, 241, 0.15)" stroke="rgba(99, 102, 241, 0.8)" strokeWidth="1.5" />
                <text y="4" textAnchor="middle" fill="#e2e8f0" fontSize="9" fontWeight="bold" fontFamily="monospace">API</text>
              </g>

              {/* Class Nodes (Purple) */}
              <g transform="translate(80, 120)">
                <circle r="18" fill="rgba(124, 58, 237, 0.15)" stroke="rgba(124, 58, 237, 0.8)" strokeWidth="1.5" />
                <text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="8" fontFamily="monospace">Class A</text>
              </g>
              <g transform="translate(320, 120)">
                <circle r="18" fill="rgba(124, 58, 237, 0.15)" stroke="rgba(124, 58, 237, 0.8)" strokeWidth="1.5" />
                <text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="8" fontFamily="monospace">Class B</text>
              </g>
              <g transform="translate(200, 200)">
                <circle r="20" fill="rgba(124, 58, 237, 0.15)" stroke="rgba(124, 58, 237, 0.8)" strokeWidth="1.5" />
                <text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="8" fontFamily="monospace">Model</text>
              </g>

              {/* Function Nodes (Emerald) */}
              <g transform="translate(110, 240)">
                <circle r="15" fill="rgba(16, 185, 129, 0.15)" stroke="rgba(16, 185, 129, 0.8)" strokeWidth="1.5" />
                <text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="7" fontFamily="monospace">Func 1</text>
              </g>
              <g transform="translate(290, 240)">
                <circle r="15" fill="rgba(16, 185, 129, 0.15)" stroke="rgba(16, 185, 129, 0.8)" strokeWidth="1.5" />
                <text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="7" fontFamily="monospace">Func 2</text>
              </g>
              <g transform="translate(200, 290)">
                <circle r="16" fill="rgba(16, 185, 129, 0.15)" stroke="rgba(16, 185, 129, 0.8)" strokeWidth="1.5" />
                <text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="7" fontFamily="monospace">Helper</text>
              </g>
            </svg>
          </div>
        </div>
      </section>

      {/* Comparison Matrix */}
      <section id="compare" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            Outperforming the Rest
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Traditional vulnerability scanning is prescriptive. CodeViz offers reasoning, automated refactoring patches, and on-premise execution out-of-the-box.
          </p>
        </div>

        <Card className="bg-slate-surface/30 border-slate-border/40 backdrop-blur-md overflow-hidden p-0 border-l-4 border-l-indigo-500">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs md:text-sm">
              <thead>
                <tr className="border-b border-slate-border/50 bg-[#070b13]/60 text-slate-400 font-semibold font-display">
                  <th className="p-4 font-bold">Platform Capability</th>
                  <th className="p-4 text-indigo-400 font-black">CodeViz</th>
                  <th className="p-4">SonarQube</th>
                  <th className="p-4">GitHub Sec</th>
                  <th className="p-4">Snyk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-border/30 font-medium text-slate-300">
                {comparisons.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/20 transition-colors">
                    <td className="p-4 font-display font-bold text-slate-200">{row.name}</td>
                    <td className="p-4 text-indigo-400 font-bold">{row.codeviz ? '✓' : '—'}</td>
                    <td className="p-4 text-slate-500">{row.sonar ? '✓' : '—'}</td>
                    <td className="p-4 text-slate-500">{row.github ? '✓' : '—'}</td>
                    <td className="p-4 text-slate-500">{row.snyk ? '✓' : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </section>

      {/* Use Cases Section */}
      <section className="py-20 bg-slate-surface/10 border-y border-slate-border/20 px-6">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
              Built for the Entire Pipeline
            </h2>
            <p className="text-slate-400 text-sm max-w-xl mx-auto">
              Empower developers, security teams, managers, and enterprise directors with specialized analytical insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: 'Developer Teams',
                points: ['Automate code review (70% faster)', 'Contextual junior onboarding', 'Build quality gate filters on PRs', 'Prioritize technical debt items']
              },
              {
                title: 'Security Teams',
                points: ['Vulnerability discovery scanning', 'PCI-DSS & SOC2 compliance logs', 'Prioritize incident responses', 'Exportable audit-ready trails']
              },
              {
                title: 'Engineering Managers',
                points: ['Quantitative code quality metrics', 'Track developer task efficiency', 'Monitor refactoring progress ROI', 'Clear visibility on threat exposure']
              },
              {
                title: 'Enterprise Directors',
                points: ['Cross-repository dashboard oversight', 'Deploy custom safety policies', 'On-premise LLM data privacy', 'Integrate enterprise SSO/SAML']
              }
            ].map((uc, i) => (
              <Card key={i} className="bg-slate-surface/30 border-slate-border/40 p-5 flex flex-col justify-between space-y-4">
                <h3 className="text-base font-bold text-indigo-400 font-display uppercase tracking-wider">{uc.title}</h3>
                <ul className="space-y-2.5 text-xs text-slate-400 font-medium">
                  {uc.points.map((p, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-indigo-400 font-mono mt-0.5">•</span>
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            Predictable Pricing, Infinite Scale
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Choose the subscription tier that best matches your codebase scale and developer workforce demands.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {pricing.map((plan, i) => (
            <Card 
              key={i} 
              className={`p-6 flex flex-col justify-between space-y-6 relative overflow-hidden bg-slate-surface/30 border-slate-border/40 ${
                plan.popular ? 'border-indigo-500/60 ring-2 ring-indigo-500/10' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-indigo-500 text-white font-bold text-[10px] tracking-wide uppercase px-3 py-1 rounded-bl-lg">
                  Most Popular
                </div>
              )}
              <div className="space-y-4">
                <div>
                  <h3 className="text-base font-extrabold text-slate-200 font-display">{plan.name}</h3>
                  <p className="text-[11px] text-slate-500 mt-1 font-mono">{plan.desc}</p>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-black font-display text-slate-100">{plan.price}</span>
                  {plan.price !== 'Custom' && <span className="text-slate-500 text-xs">/ month</span>}
                </div>
                <ul className="space-y-2 border-t border-slate-border/20 pt-4 text-xs text-slate-400 font-medium">
                  {plan.features.map((feat, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <CheckCircle2 size={12} className="text-indigo-400 flex-shrink-0" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <Button 
                onClick={() => navigate('/login')} 
                variant={plan.popular ? 'primary' : 'secondary'} 
                size="md"
                className="w-full justify-center"
              >
                {plan.btnText}
              </Button>
            </Card>
          ))}
        </div>
      </section>

      {/* CTA Footer Banner */}
      <section className="py-20 px-6 max-w-5xl mx-auto text-center relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-2xl blur-2xl opacity-10 group-hover:opacity-20 transition duration-1000" />
        <Card className="bg-slate-surface/30 border-slate-border/40 backdrop-blur-xl p-10 md:p-16 space-y-6 text-center shadow-2xl relative z-10 overflow-hidden">
          <div className="absolute -top-10 -left-10 w-40 h-40 rounded-full bg-indigo-500/10 blur-2xl pointer-events-none" />
          <div className="absolute -bottom-10 -right-10 w-40 h-40 rounded-full bg-purple-500/10 blur-2xl pointer-events-none" />
          
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100 max-w-2xl mx-auto">
            Ready to Automate Your Security & Reviews?
          </h2>
          <p className="text-slate-400 text-sm md:text-base max-w-xl mx-auto leading-relaxed">
            Connect your repository sandbox, analyze code structures, discover issues, and generate fixes instantly.
          </p>
          <div className="pt-4 flex flex-col sm:flex-row justify-center items-center gap-3">
            <Button 
              onClick={() => navigate('/login')} 
              variant="primary" 
              size="lg"
              className="w-full sm:w-auto px-8 shadow-xl shadow-indigo-500/20"
            >
              Get Started with GitHub <ArrowUpRight className="ml-1" size={16} />
            </Button>
            <button
              onClick={() => navigate('/login')}
              className="w-full sm:w-auto px-6 py-3 text-xs font-bold border border-slate-border/50 hover:bg-slate-900/30 rounded-xl transition-all text-slate-300 hover:text-slate-100 font-mono"
            >
              sandbox_v1.0.0_release
            </button>
          </div>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-border/20 py-10 px-6 text-center text-xs text-slate-500 space-y-4">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shadow-sm">
              <Shield size={12} />
            </div>
            <span className="font-extrabold tracking-tight text-slate-300">
              Code<span className="text-indigo-400 font-medium">Viz</span>
            </span>
          </div>
          <p className="font-medium">
            © {new Date().getFullYear()} CodeViz Platform. Monitor securely.
          </p>
        </div>
      </footer>
    </div>
  )
}
