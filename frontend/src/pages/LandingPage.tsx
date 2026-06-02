import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Shield, RefreshCw, CheckCircle2, Activity, Cpu,
  Layers, ArrowRight, ShieldAlert,
  Sparkles, ArrowUpRight, Github, ExternalLink,
  Skull, Package, Zap, Gauge, FlaskConical, Wrench,
  Lock, Eye, GitPullRequest, Bell,
  Server, ChevronRight, Clock,
} from 'lucide-react'
import clsx from 'clsx'

const CARD = 'rounded-3xl border border-white/[0.12] border-t-white/[0.22] bg-slate-elevated/95 shadow-card backdrop-blur-md transition-all duration-300'
const CARD_P = `${CARD} p-6`

const GITHUB_REPO    = 'https://github.com/MalcolmGov/CODEVIZ'
const CONTACT_EMAIL  = 'mailto:malcolmgov24@gmail.com?subject=CodeViz%20Enterprise%20Enquiry'

const scrollTo = (id: string) =>
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()

  // ─── Data ────────────────────────────────────────────────────────────
  const stats = [
    { 
      label: 'Analysis Dimensions', 
      value: '13',      
      desc: 'security · perf · smells · compliance',
      color: 'indigo',
      fromColor: 'from-indigo-500/10',
      toColor: 'to-indigo-500/0',
      borderColor: 'border-white/[0.08] hover:border-indigo-500/40',
      glowColor: 'group-hover:shadow-[0_0_30px_-5px_rgba(99,102,241,0.2)]',
      orbColor: 'bg-indigo-500/10 group-hover:bg-indigo-500/20',
      textColor: 'from-indigo-400 via-purple-400 to-pink-400'
    },
    { 
      label: 'Detection Accuracy',  
      value: '94%',     
      desc: 'with < 3% false positives',
      color: 'emerald',
      fromColor: 'from-emerald-500/10',
      toColor: 'to-emerald-500/0',
      borderColor: 'border-white/[0.08] hover:border-emerald-500/40',
      glowColor: 'group-hover:shadow-[0_0_30px_-5px_rgba(16,185,129,0.2)]',
      orbColor: 'bg-emerald-500/10 group-hover:bg-emerald-500/20',
      textColor: 'from-emerald-400 via-teal-400 to-emerald-300'
    },
    { 
      label: 'Vulnerability Types', 
      value: '40+',     
      desc: 'OWASP · CVE · MITRE ATT&CK',
      color: 'rose',
      fromColor: 'from-rose-500/10',
      toColor: 'to-rose-500/0',
      borderColor: 'border-white/[0.08] hover:border-rose-500/40',
      glowColor: 'group-hover:shadow-[0_0_30px_-5px_rgba(244,63,94,0.2)]',
      orbColor: 'bg-rose-500/10 group-hover:bg-rose-500/20',
      textColor: 'from-rose-400 via-pink-500 to-red-400'
    },
    { 
      label: 'Data Sent to Cloud',  
      value: '0 bytes', 
      desc: 'on-premise LLM, air-gapped ready',
      color: 'amber',
      fromColor: 'from-amber-500/10',
      toColor: 'to-amber-500/0',
      borderColor: 'border-white/[0.08] hover:border-amber-500/40',
      glowColor: 'group-hover:shadow-[0_0_30px_-5px_rgba(245,158,11,0.2)]',
      orbColor: 'bg-amber-500/10 group-hover:bg-amber-500/20',
      textColor: 'from-amber-400 via-yellow-400 to-orange-400'
    },
  ]

  const features = [
    { icon: Cpu,         title: 'Repository Scanner',          desc: 'Multi-language AST indexing across Python, JS/TS, Go, Java with real-time session logs.',                                                badge: 'Real-time',    href: '/scanner'          },
    { icon: ShieldAlert, title: 'Security Analysis',           desc: 'CVE detection, OWASP Top 10 mapping, SQLi/XSS, hardcoded secret scanning — 94% accuracy.',                                             badge: '94% Accuracy',  href: '/security'         },
    { icon: Skull,       title: 'Threat Actor Simulation',     desc: 'MITRE ATT&CK kill chain modelling. Map your code paths to real-world threat actor tactics.',                                            badge: 'MITRE ATT&CK',  href: '/threats'          },
    { icon: Gauge,       title: 'Performance Regression',      desc: 'Static detection of N+1 queries, memory leaks, blocking I/O, and inefficient loops before they hit prod.',                             badge: 'Proactive',     href: '/performance'      },
    { icon: Wrench,      title: 'Auto-Remediation',            desc: 'AI-generated fixes in HITL or Autonomous mode. Review diffs or let CodeViz push directly.',                                           badge: 'HITL + Auto',   href: '/remediation'      },
    { icon: RefreshCw,   title: 'Intelligent Refactoring',     desc: 'Complexity reduction, deduplication, type-safety upgrades, and modern syntax rewrites — all with one-click PRs.',                     badge: 'AI Engine',     href: '/refactoring'      },
    { icon: FlaskConical,title: 'Code Smell Detection',        desc: 'Dead code, deep nesting, cyclomatic complexity, and copy-paste duplication surfaced with actionable fixes.',                           badge: 'Quality',       href: '/code-smells'      },
    { icon: Package,     title: 'Dependency CVE Scanner',      desc: 'Cross-references every dependency against OSV.dev for known CVEs — with severity scores and upgrade paths.',                           badge: 'OSV.dev',       href: '/dependencies'     },
    { icon: Layers,      title: 'Compliance & Risk Scoring',   desc: 'OWASP, SOC 2, GDPR, PCI-DSS, HIPAA — posture grades, gap analysis, and audit-ready reports.',                                         badge: 'Enterprise',    href: '/compliance'       },
  ]

  const loop = [
    { step: '01', icon: Cpu,           label: 'Connect',  desc: 'Link a GitHub repo or local path in seconds'        },
    { step: '02', icon: Eye,           label: 'Scan',     desc: '13-dimension analysis runs in under 2 minutes'      },
    { step: '03', icon: ShieldAlert,   label: 'Detect',   desc: 'Security, perf, smells, threats — all ranked'       },
    { step: '04', icon: Zap,           label: 'Fix',      desc: 'AI generates a patch; you approve or auto-merge'    },
    { step: '05', icon: Bell,          label: 'Monitor',  desc: 'Schedule recurring scans, get Slack alerts on drift' },
  ]

  const moats = [
    {
      icon: Lock,
      color: '#6366f1',
      title: 'Zero Data Exfiltration',
      desc: 'CodeViz runs entirely on-premise using Ollama. Your source code never touches an external server. Air-gap compatible for regulated environments.',
      badge: 'Privacy-first',
      shadow: 'hover:shadow-[0_0_24px_-6px_rgba(99,102,241,0.16)] hover:border-indigo-500/30 border-indigo-500/10'
    },
    {
      icon: GitPullRequest,
      color: '#22c55e',
      title: 'Find → Fix → Ship in One Tool',
      desc: 'No context switching. CodeViz detects an issue, generates a patch, opens a GitHub PR, and schedules a re-scan — all from one platform.',
      badge: 'End-to-end',
      shadow: 'hover:shadow-[0_0_24px_-6px_rgba(34,197,94,0.16)] hover:border-emerald-500/30 border-emerald-500/10'
    },
    {
      icon: Skull,
      color: '#ef4444',
      title: 'Threat Actor Simulation',
      desc: 'The only code analysis platform that maps your vulnerabilities to real MITRE ATT&CK kill chains — showing exactly how an attacker would exploit your code.',
      badge: 'Industry-first',
      shadow: 'hover:shadow-[0_0_24px_-6px_rgba(239,68,68,0.16)] hover:border-red-500/30 border-red-500/10'
    },
  ]

  const comparisons = [
    { name: 'AI-Powered Reasoning',             codeviz: true,  sonar: false, github: true,  snyk: false },
    { name: 'MITRE ATT&CK Threat Simulation',   codeviz: true,  sonar: false, github: false, snyk: false },
    { name: 'Performance Regression Detection',  codeviz: true,  sonar: false, github: false, snyk: false },
    { name: 'On-Premise LLM (Zero Cloud)',       codeviz: true,  sonar: false, github: false, snyk: false },
    { name: 'Auto-Remediation + PR Generation',  codeviz: true,  sonar: false, github: false, snyk: false },
    { name: 'HITL vs Autonomous Fix Modes',      codeviz: true,  sonar: false, github: false, snyk: false },
    { name: 'Contextual AI Chat per Finding',    codeviz: true,  sonar: false, github: false, snyk: false },
    { name: 'Dependency CVE via OSV.dev',        codeviz: true,  sonar: true,  github: true,  snyk: true  },
    { name: 'Compliance Reports (SOC2/PCI)',      codeviz: true,  sonar: true,  github: true,  snyk: false },
    { name: 'Scheduled Continuous Monitoring',   codeviz: true,  sonar: true,  github: false, snyk: false },
  ]

  const pricing = [
    { name: 'Free Tier',        price: '$0',     period: true,  desc: 'For individual developers testing AI analysis.',           features: ['2 scans / month', '1 active repository', 'Security + CVE scanning', 'Standard reports'],                                              btnText: 'Start Free',    popular: false },
    { name: 'Developer Pro',    price: '$49',    period: true,  desc: 'For professionals needing the full platform.',             features: ['Unlimited scans', '5 repositories', 'All 13 analysis dimensions', 'AI auto-remediation', 'Full GitHub integration'],                  btnText: 'Go Pro',        popular: true  },
    { name: 'Engineering Team', price: '$199',   period: true,  desc: 'For collaborative teams and engineering workflows.',       features: ['20 repositories', 'Team dashboards', 'Slack alerting', 'Custom security policies', 'Priority support'],                              btnText: 'Get Team',      popular: false },
    { name: 'Enterprise',       price: 'Custom', period: false, desc: 'On-premise deployability and dedicated infrastructure.',   features: ['Unlimited repos', 'Air-gapped LLM deployment', 'SSO/SAML', 'Dedicated SLA', 'Audit trail + compliance exports'],                     btnText: 'Contact Sales', popular: false },
  ]


  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 relative overflow-hidden select-none font-sans scroll-smooth">
      {/* Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f293708_1px,transparent_1px),linear-gradient(to_bottom,#1f293708_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-600/5 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-[20%] left-[-100px] w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-[150px] pointer-events-none" />
      <div className="absolute bottom-[10%] right-[-100px] w-[500px] h-[500px] bg-emerald-600/5 rounded-full blur-[130px] pointer-events-none" />

      {/* ── NAV ──────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 bg-[#030712]/80 backdrop-blur-md border-b border-slate-border/20 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img 
              src="/images/logo.png" 
              alt="CodeViz 3D Logo" 
              className="w-8 h-8 rounded-lg object-contain"
            />
            <span className="text-xl font-extrabold tracking-tight text-slate-100 font-display">
              Code<span className="text-indigo-400 font-medium">Viz</span>
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-400">
            {[
              { label: 'Platform',    id: 'features'  },
              { label: 'How It Works', id: 'loop'     },
              { label: 'Why CodeViz', id: 'moats'     },
              { label: 'Pricing',     id: 'pricing'   },
              { label: 'vs Others',   id: 'compare'   },
            ].map(({ label, id }) => (
              <button key={id} onClick={() => scrollTo(id)}
                className="hover:text-slate-200 transition-colors cursor-pointer">{label}</button>
            ))}
            <a href={GITHUB_REPO} target="_blank" rel="noopener noreferrer"
              className="hover:text-slate-200 transition-colors flex items-center gap-1">
              <Github size={14} /> GitHub
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/login')}
              className="text-sm font-semibold text-slate-300 hover:text-slate-100 px-4 py-2">
              Sign In
            </button>
            <button
              onClick={() => navigate('/login')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold bg-indigo-500 hover:bg-indigo-600 text-white transition-all shadow-md"
            >
              Get Started Free
            </button>
          </div>
        </div>
      </header>

      {/* ── HERO (Dual Column Redesign with 3D Image) ──────────────────── */}
      <section className="relative pt-16 pb-20 px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Hero Column */}
          <div className="lg:col-span-7 text-left space-y-6">
            <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 px-3.5 py-1 rounded-full text-xs font-bold text-indigo-400">
              <Sparkles size={12} />
              <span>13-DIMENSION AI CODE ANALYSIS — ON-PREMISE, ZERO CLOUD</span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black font-display tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-white via-slate-100 to-slate-300 leading-none">
              The AI Security Platform <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500">
                That Fixes What It Finds
              </span>
            </h1>

            <p className="text-slate-300 text-base sm:text-lg font-medium leading-relaxed max-w-2xl">
              Security, performance, threats, compliance, and code quality — analysed simultaneously.
              AI-generated fixes shipped as PRs. Your code never leaves your machine.
            </p>

            <div className="flex flex-col sm:flex-row justify-start items-center gap-4 pt-2">
              <button
                onClick={() => navigate('/login')}
                className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl text-[14px] font-bold bg-indigo-500 hover:bg-indigo-600 text-white transition-all shadow-lg shadow-indigo-500/20 hover:scale-[1.02] active:scale-[0.98]"
              >
                Start Scanning Now <ArrowRight className="ml-2" size={18} />
              </button>
              <button onClick={() => scrollTo('loop')}
                className="w-full sm:w-auto px-6 py-3.5 text-sm font-bold border border-slate-border/50 hover:bg-slate-900/30 rounded-xl transition-all text-slate-300 hover:text-slate-100">
                See How It Works
              </button>
            </div>
          </div>

          {/* Right Hero Column - 3D Visual Asset */}
          <div className="lg:col-span-5 relative group">
            <div className="absolute -inset-2 bg-gradient-to-tr from-indigo-500 via-purple-500 to-emerald-500 rounded-3xl blur-2xl opacity-20 group-hover:opacity-30 transition duration-1000" />
            <div className="relative rounded-2xl border border-white/[0.12] border-t-white/[0.22] bg-[#080d19]/90 shadow-2xl p-1 overflow-hidden">
              <img 
                src="/images/hero-visual.png" 
                alt="CodeViz AI Cyber Shield active protection dashboard" 
                className="w-full h-auto rounded-xl object-cover hover:scale-[1.02] transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#080d19]/60 via-transparent to-transparent pointer-events-none" />
            </div>
          </div>
        </div>
      </section>

      {/* ── TERMINAL LIVE PREVIEW ────────────────────────────────────────── */}
      <section className="py-12 px-6 max-w-5xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-indigo-400">ANALYSIS CONSOLE</p>
          <h2 className="text-2xl font-extrabold text-white font-display">Witness Local AI Code Analysis in Real Time</h2>
        </div>
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-2xl blur-xl opacity-20 group-hover:opacity-35 transition duration-1000" />
          <div className="overflow-hidden relative shadow-2xl rounded-3xl border border-white/[0.12] border-t-white/[0.22] p-0.5 bg-[#0b0f19]/90">
            <div className="bg-[#0b0f19] rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 bg-[#070b13] border-b border-slate-border/30">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="text-[10px] font-mono text-slate-400 bg-slate-900/50 px-3 py-1 rounded border border-slate-border/20">
                  codeviz — 13-dimension analysis engine
                </div>
                <div className="w-10" />
              </div>
              <div className="p-6 text-left font-mono text-xs text-slate-300 space-y-3 max-h-[340px] overflow-y-auto bg-[#040810]/95">
                <div className="flex gap-2 text-indigo-400"><span>$</span><span>codeviz scan --repo=github.com/acme/api-service --all-dimensions</span></div>
                <div className="text-slate-400">🔍 Initialising 13-dimension analysis engine (on-premise Ollama)...</div>
                <div className="text-emerald-400">✓ Scanned 2,847 files · 94,120 LOC in 1m 43s</div>
                <div className="grid grid-cols-2 gap-x-8 gap-y-1 text-[11px] mt-2 text-slate-400">
                  <span>├── Security vulns found:      <span className="text-red-400 font-bold">12 (3 critical)</span></span>
                  <span>├── Performance regressions:   <span className="text-amber-400 font-bold">7</span></span>
                  <span>├── MITRE ATT&CK matches:      <span className="text-red-400 font-bold">4 kill chains</span></span>
                  <span>├── Dependency CVEs (OSV):     <span className="text-amber-400 font-bold">9</span></span>
                  <span>├── Code smells:               <span className="text-yellow-400 font-bold">31</span></span>
                  <span>└── Compliance gaps (SOC 2):   <span className="text-amber-400 font-bold">6</span></span>
                </div>
                <div className="text-slate-400 mt-2">🤖 Generating AI remediation patches (HITL mode)...</div>
                <div className="text-indigo-400 bg-indigo-950/30 border border-indigo-500/20 p-3 rounded-lg flex items-start gap-3 mt-2">
                  <Activity size={14} className="text-indigo-400 mt-0.5 animate-pulse" />
                  <div>
                    <span className="font-bold text-slate-200">CRITICAL — SQL Injection (OWASP A03):</span>
                    <p className="text-slate-400 text-[11px] mt-0.5">Unsanitised input in <code className="text-indigo-300">UserController.search()</code>. Patch staged. MITRE T1190 exploit path confirmed.</p>
                  </div>
                </div>
                <div className="text-emerald-400 font-bold mt-2">✓ PR #247 opened · "fix: SQL injection in UserController + 4 related issues" · Awaiting review</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── STATS BANNER ─────────────────────────────────────────────────── */}
      <section className="bg-[#070b13] border-y border-slate-border/20 py-12 px-6 shadow-lg relative overflow-hidden">
        {/* Background decorative grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff01_1px,transparent_1px),linear-gradient(to_bottom,#ffffff01_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
        
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {stats.map((stat, i) => (
            <div key={i} className={clsx(
              "relative overflow-hidden rounded-3xl p-7 border-t-2 bg-[#090d16]/90 shadow-card backdrop-blur-xl transition-all duration-500 group hover:scale-[1.04] flex flex-col justify-between min-h-[160px]",
              stat.color === 'indigo' ? 'border-t-indigo-500/40' :
              stat.color === 'emerald' ? 'border-t-emerald-500/40' :
              stat.color === 'rose' ? 'border-t-rose-500/40' : 'border-t-amber-500/40',
              stat.borderColor,
              stat.glowColor
            )}>
              {/* Dynamic top hover glow line */}
              <div className={clsx("absolute top-0 left-0 right-0 h-[2px] opacity-35 group-hover:opacity-100 transition-opacity duration-500", 
                stat.color === 'indigo' ? 'bg-indigo-400' :
                stat.color === 'emerald' ? 'bg-emerald-400' :
                stat.color === 'rose' ? 'bg-rose-400' : 'bg-amber-400'
              )} />
              
              {/* Interactive light shine overlay */}
              <div className="absolute inset-0 bg-gradient-to-tr from-white/[0.005] via-white/[0.025] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none -z-10" />
              
              {/* Background gradient flare */}
              <div className={clsx("absolute inset-0 bg-gradient-to-b opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none -z-10", stat.fromColor, stat.toColor)} />
              
              {/* Larger colored radial blur orb */}
              <div className={clsx("absolute -bottom-16 -right-16 w-32 h-32 rounded-full blur-2xl transition-all duration-500 -z-10 pointer-events-none opacity-20 group-hover:opacity-50", stat.orbColor)} />
              
              <div className="space-y-1.5 z-10 relative flex flex-col justify-between h-full">
                <div>
                  <p className={clsx(
                    "text-4xl md:text-5xl font-black font-display tracking-tight text-transparent bg-clip-text bg-gradient-to-r drop-shadow-[0_2px_10px_rgba(0,0,0,0.3)] transition-all",
                    stat.textColor
                  )}>
                    {stat.value}
                  </p>
                  <p className="text-[11px] font-bold text-slate-200 font-display uppercase tracking-widest mt-2">{stat.label}</p>
                </div>
                <p className="text-[11px] text-slate-400 font-mono mt-2 leading-normal">{stat.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── PLATFORM FEATURES (Redesigned visual cards & glows) ──────────── */}
      <section id="features" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            The Complete Code Intelligence Platform
          </h2>
          <p className="text-slate-300 text-sm md:text-base max-w-2xl mx-auto font-medium">
            13 analysis engines running simultaneously. Every scan covers security, performance, threats,
            quality, dependencies, and compliance — not just one dimension.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, i) => {
            const Icon = feat.icon
            
            // Get category-based theme color for icon and vertical bar highlight
            const isSec = feat.title.toLowerCase().includes('security') || feat.title.toLowerCase().includes('threat')
            const isPerf = feat.title.toLowerCase().includes('performance')
            const isRef = feat.title.toLowerCase().includes('refactoring') || feat.title.toLowerCase().includes('smell')
            
            const theme = isSec ? 'security' : isPerf ? 'performance' : isRef ? 'refactoring' : 'general'

            const colors = {
              security: {
                accentColor: 'text-rose-400',
                accentBg: 'bg-rose-500/[0.02] group-hover:bg-rose-500/[0.08]',
                accentBorder: 'border-rose-500/20 group-hover:border-rose-500/40',
                cardBorder: 'hover:border-rose-500/30',
                cardShadow: 'hover:shadow-[0_0_30px_-5px_rgba(244,63,94,0.2)]',
                leftPill: 'bg-rose-500 group-hover:shadow-[0_0_12px_#f43f5e]',
                badgeCls: 'text-rose-400 bg-rose-950/40 border-rose-500/20 group-hover:border-rose-500/40',
                glowOrb: 'from-rose-500/20 to-transparent'
              },
              performance: {
                accentColor: 'text-orange-400',
                accentBg: 'bg-orange-500/[0.02] group-hover:bg-orange-500/[0.08]',
                accentBorder: 'border-orange-500/20 group-hover:border-orange-500/40',
                cardBorder: 'hover:border-orange-500/30',
                cardShadow: 'hover:shadow-[0_0_30px_-5px_rgba(249,115,22,0.2)]',
                leftPill: 'bg-orange-500 group-hover:shadow-[0_0_12px_#f97316]',
                badgeCls: 'text-orange-400 bg-orange-950/40 border-orange-500/20 group-hover:border-orange-500/40',
                glowOrb: 'from-orange-500/20 to-transparent'
              },
              refactoring: {
                accentColor: 'text-purple-400',
                accentBg: 'bg-purple-500/[0.02] group-hover:bg-purple-500/[0.08]',
                accentBorder: 'border-purple-500/20 group-hover:border-purple-500/40',
                cardBorder: 'hover:border-purple-500/30',
                cardShadow: 'hover:shadow-[0_0_30px_-5px_rgba(168,85,247,0.2)]',
                leftPill: 'bg-purple-500 group-hover:shadow-[0_0_12px_#a855f7]',
                badgeCls: 'text-purple-400 bg-purple-950/40 border-purple-500/20 group-hover:border-purple-500/40',
                glowOrb: 'from-purple-500/20 to-transparent'
              },
              general: {
                accentColor: 'text-indigo-400',
                accentBg: 'bg-indigo-500/[0.02] group-hover:bg-indigo-500/[0.08]',
                accentBorder: 'border-indigo-500/20 group-hover:border-indigo-500/40',
                cardBorder: 'hover:border-indigo-500/30',
                cardShadow: 'hover:shadow-[0_0_30px_-5px_rgba(99,102,241,0.2)]',
                leftPill: 'bg-indigo-500 group-hover:shadow-[0_0_12px_#6366f1]',
                badgeCls: 'text-indigo-400 bg-indigo-950/40 border-indigo-500/20 group-hover:border-indigo-500/40',
                glowOrb: 'from-indigo-500/20 to-transparent'
              }
            }[theme]

            return (
              <div key={i} onClick={() => navigate(feat.href)}
                className={clsx(
                  "rounded-3xl border border-white/[0.06] border-t-white/[0.18] bg-gradient-to-b from-[#0d1326] to-[#040812] p-7 flex flex-col justify-between hover:-translate-y-2 cursor-pointer transition-all duration-500 group relative overflow-hidden",
                  colors.cardBorder,
                  colors.cardShadow
                )}>
                
                {/* Floating vertical pill indicator */}
                <div className={clsx(
                  "absolute left-0 top-1/2 -translate-y-1/2 w-[3px] rounded-r-full transition-all duration-500 opacity-60 group-hover:opacity-100 h-8 group-hover:h-16",
                  colors.leftPill
                )} />

                {/* Internal gradient flare orb */}
                <div className={clsx("absolute -top-16 -right-16 w-32 h-32 rounded-full bg-gradient-to-br blur-3xl opacity-0 group-hover:opacity-40 transition-opacity duration-500 pointer-events-none -z-10", colors.glowOrb)} />

                {/* Interactive light shine overlay */}
                <div className="absolute inset-0 bg-gradient-to-tr from-white/[0.005] via-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none -z-10" />

                <div className="space-y-5 pl-1.5">
                  <div className="flex justify-between items-center">
                    {/* Icon Wrapper */}
                    <div className={clsx(
                      "p-3 rounded-2xl border transition-all duration-500 shadow-inner group-hover:scale-105 group-hover:rotate-3",
                      colors.accentBg,
                      colors.accentBorder,
                      colors.accentColor
                    )}>
                      <Icon size={22} className="transition-transform duration-500" />
                    </div>
                    {/* Badge */}
                    <span className={clsx(
                      "text-[10px] font-mono font-bold px-3 py-1 rounded-full border transition-all duration-300 shadow-sm",
                      colors.badgeCls
                    )}>
                      {feat.badge}
                    </span>
                  </div>
                  <h3 className="text-base font-extrabold text-white font-display leading-tight">{feat.title}</h3>
                  <p className="text-slate-400 group-hover:text-slate-200 text-xs leading-relaxed font-medium transition-colors duration-300">{feat.desc}</p>
                </div>
                
                <div className={clsx(
                  "mt-5 flex items-center gap-1 text-[11px] font-bold opacity-0 group-hover:opacity-100 transition-all duration-300 pl-1.5",
                  colors.accentColor
                )}>
                  <span>Try it</span>
                  <ArrowRight size={11} className="transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────────────────── */}
      <section id="loop" className="py-20 px-6 bg-[#060a12]/60 border-y border-slate-border/20">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-emerald-400">
              <Zap size={10} /> THE COMPLETE LOOP
            </div>
            <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
              Find It. Fix It. Ship It. Monitor It.
            </h2>
            <p className="text-slate-300 text-sm max-w-xl mx-auto font-medium">
              No other platform closes the full loop — from first scan to merged PR to ongoing monitoring — in a single tool.
            </p>
          </div>

          <div className="relative">
            {/* Connector line */}
            <div className="hidden lg:block absolute top-12 left-[10%] right-[10%] h-px bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent" />

            <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-6">
              {loop.map((s, i) => {
                const Icon = s.icon
                return (
                  <div key={i} className="flex flex-col items-center text-center space-y-3 relative">
                    <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 relative z-10">
                      <Icon size={22} />
                    </div>
                    <div className="text-[9px] font-bold text-indigo-400/60 font-mono tracking-widest">{s.step}</div>
                    <p className="text-sm font-bold text-slate-200 font-display">{s.label}</p>
                    <p className="text-[11px] text-slate-400 leading-snug font-medium">{s.desc}</p>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="flex justify-center">
            <button onClick={() => navigate('/login')}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold tracking-wide transition-all shadow-lg shadow-indigo-500/20">
              <Zap size={15} /> Start your first scan free
            </button>
          </div>
        </div>
      </section>

      {/* ── WHY CODEVIZ — CORE MOATS ─────────────────────────────────────── */}
      <section id="moats" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            Why CodeViz Wins
          </h2>
          <p className="text-slate-300 text-sm max-w-xl mx-auto font-medium">
            Three capabilities no competitor offers. Any one of them alone would be a product — together they're a moat.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {moats.map((m, i) => {
            const Icon = m.icon
            return (
              <div key={i} className={clsx(
                "rounded-2xl border p-8 space-y-5 relative overflow-hidden group transition-all duration-300",
                m.shadow
              )}>
                <div className="absolute -top-8 -right-8 w-32 h-32 rounded-full blur-2xl opacity-10 group-hover:opacity-20 transition-opacity"
                  style={{ backgroundColor: m.color }} />
                <div className="p-3 rounded-xl border w-fit" style={{ color: m.color, borderColor: `${m.color}30`, backgroundColor: `${m.color}10` }}>
                  <Icon size={22} />
                </div>
                <div>
                  <span className="text-[9px] font-bold uppercase tracking-widest font-mono mb-2 block" style={{ color: m.color }}>{m.badge}</span>
                  <h3 className="text-lg font-extrabold text-slate-100 font-display leading-tight">{m.title}</h3>
                </div>
                <p className="text-slate-300 text-[13px] leading-relaxed font-medium">{m.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* ── MITRE ATT&CK SPOTLIGHT (Redesigned with 3D Image) ─────────────── */}
      <section className="py-20 px-6 bg-gradient-to-b from-red-950/10 to-transparent border-y border-red-900/20">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6 text-left">
            <div className="inline-flex items-center gap-2 bg-red-500/10 border border-red-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-red-400">
              <Skull size={10} /> INDUSTRY-FIRST CAPABILITY
            </div>
            <h2 className="text-3xl md:text-4xl font-black font-display tracking-tight text-slate-100">
              Threat Actor <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">Kill Chain Simulation</span>
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed font-medium">
              CodeViz maps your detected vulnerabilities to the MITRE ATT&CK framework — showing you exactly which
              tactics, techniques, and procedures (TTPs) a real threat actor would use to exploit your codebase.
            </p>
            <div className="space-y-3">
              {[
                'Maps code vulns to MITRE ATT&CK TTPs',
                'Visualises complete kill chains from initial access to exfiltration',
                'Prioritises fixes by real-world exploit likelihood',
                'Aligns with SOC and red team reporting standards',
              ].map((pt, i) => (
                <div key={i} className="flex items-start gap-2.5">
                  <CheckCircle2 size={14} className="text-red-400 mt-0.5 shrink-0" />
                  <span className="text-[13px] text-slate-300 font-medium">{pt}</span>
                </div>
              ))}
            </div>
            <button onClick={() => navigate('/threats')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm font-semibold hover:bg-red-500/20 transition-all">
              <ExternalLink size={14} /> View Threat Simulation
            </button>
          </div>

          {/* Kill chain visual column */}
          <div className="flex flex-col gap-5 text-left">
            {/* 3D Threat simulation visual */}
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-tr from-red-500 to-orange-500 rounded-2xl blur-lg opacity-25 group-hover:opacity-35 transition duration-1000" />
              <div className="relative rounded-2xl border border-red-900/40 bg-[#0c0606] overflow-hidden shadow-2xl">
                <img 
                  src="/images/threat-simulation.png" 
                  alt="3D cybersecurity threat simulation kill chain graphic" 
                  className="w-full h-[220px] object-cover hover:scale-[1.02] transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0a0505] via-transparent to-transparent pointer-events-none" />
              </div>
            </div>

            {/* Kill chain list */}
            <div className="rounded-2xl border border-red-900/30 bg-[#0a0505]/90 p-6 space-y-3 font-mono text-xs shadow-xl">
              <div className="flex items-center gap-2 text-red-400 font-bold mb-2">
                <Skull size={14} /> MITRE ATT&CK Kill Chain — Active Threat Path
              </div>
              {[
                { phase: 'Initial Access',   tactic: 'T1190 · Exploit Public-Facing Application',  file: 'UserController.search()',    sev: 'CRITICAL' },
                { phase: 'Execution',        tactic: 'T1059 · Command & Scripting Interpreter',     file: 'shell_utils.execute()',      sev: 'HIGH'     },
                { phase: 'Persistence',      tactic: 'T1098 · Account Manipulation',               file: 'AuthService.createToken()',  sev: 'HIGH'     },
                { phase: 'Exfiltration',     tactic: 'T1041 · Exfiltration Over C2 Channel',       file: 'DataExport.send()',          sev: 'CRITICAL' },
              ].map((row, i) => (
                <div key={i} className="flex flex-col gap-1 py-2 border-b border-red-900/20 last:border-0">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-bold uppercase tracking-widest text-red-500/60">{row.phase}</span>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${row.sev === 'CRITICAL' ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'}`}>{row.sev}</span>
                  </div>
                  <span className="text-slate-200 text-[11px] font-medium">{row.tactic}</span>
                  <span className="text-slate-400 text-[10px]">→ {row.file}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── ON-PREMISE PRIVACY (Redesigned with 3D Server graphic) ───────── */}
      <section className="py-20 px-6 max-w-7xl mx-auto">
        <div className="rounded-3xl border border-indigo-500/10 bg-gradient-to-br from-[#0c0f1c] via-[#080b14] to-transparent p-8 md:p-12 shadow-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-indigo-500/5 rounded-full blur-[100px] pointer-events-none" />
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center text-left">
            {/* Column 1: Copy (5/12 width) */}
            <div className="lg:col-span-5 space-y-5">
              <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-indigo-400">
                <Lock size={10} /> PRIVACY BY ARCHITECTURE
              </div>
              <h2 className="text-3xl font-black font-display tracking-tight text-slate-100 leading-tight">
                Your Code Never Leaves Your Machine
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed font-medium">
                CodeViz runs its AI engine entirely on-premise via Ollama. No API calls to OpenAI, Anthropic, or any cloud LLM. Your source code, secrets, and business logic stay local — always.
              </p>
            </div>

            {/* Column 2: 3D Image (3/12 width) */}
            <div className="lg:col-span-3 relative group">
              <div className="absolute -inset-1 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-2xl blur-lg opacity-20 group-hover:opacity-30 transition duration-1000" />
              <div className="relative rounded-2xl border border-white/[0.12] border-t-white/[0.22] bg-[#0c0f1c] overflow-hidden shadow-xl">
                <img 
                  src="/images/privacy-server.png" 
                  alt="CodeViz 3D local secure on-premise hardware server lock" 
                  className="w-full h-auto object-cover hover:scale-[1.03] transition-transform duration-500"
                />
              </div>
            </div>

            {/* Column 3: Features (4/12 width) */}
            <div className="lg:col-span-4 grid grid-cols-1 gap-3">
              {[
                { icon: Server, label: 'On-premise LLM',       desc: 'Ollama runs locally, no cloud dependency' },
                { icon: Lock,   label: 'Air-gap compatible',   desc: 'Works in isolated enterprise environments' },
                { icon: Shield, label: 'Zero data retention',  desc: 'Nothing persisted outside your machine'   },
                { icon: Eye,    label: 'Audit-ready logs',     desc: 'Full scan provenance for compliance'      },
              ].map((item, i) => {
                const Icon = item.icon
                return (
                  <div key={i} className="flex items-start gap-3 p-4 rounded-xl border border-white/[0.08] bg-slate-elevated/95 shadow-md hover:border-white/[0.14] transition-all">
                    <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 shrink-0">
                      <Icon size={14} />
                    </div>
                    <div>
                      <p className="text-[12px] font-bold text-slate-200">{item.label}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5 font-medium">{item.desc}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ── DEPENDENCY NETWORK (Interactive SVG) ─────────────────────────── */}
      <section id="graph" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6 text-left">
            <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-purple-400">
              <Activity size={10} /> VISUAL CODE MESH
            </div>
            <h2 className="text-3xl md:text-4xl font-black font-display tracking-tight leading-tight text-slate-100">
              Obsidian-Inspired <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">
                Dependency Network
              </span>
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed font-medium">
              See exactly how your codebase is wired. Force-directed graph shows every import relationship — drag nodes, zoom in, click to inspect. Spot circular dependencies and high-coupling hotspots at a glance.
            </p>
            <div className="space-y-3">
              {[
                { title: 'Interactive drag & zoom physics',     value: 'D3 force simulation'         },
                { title: 'Language-grouped node colouring',     value: 'Python · TS · JS'            },
                { title: 'Click-to-inspect file details',       value: 'Path, type, import count'    },
              ].map((item, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />
                  <span className="text-xs text-slate-200 font-semibold">{item.title}</span>
                  <span className="text-[10px] text-slate-400 font-mono ml-auto">{item.value}</span>
                </div>
              ))}
            </div>
            <button onClick={() => navigate('/dependency-graph')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-purple-500/30 bg-purple-500/10 text-purple-300 text-sm font-semibold hover:bg-purple-500/20 transition-all">
              <ExternalLink size={14} /> Try it live in your repo
            </button>
          </div>

          <div className="relative p-0.5 bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-transparent rounded-2xl border border-slate-border/40 overflow-hidden shadow-2xl">
            <svg viewBox="0 0 400 350" className="w-full h-[350px] relative z-10 select-none pointer-events-none">
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.015)" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              <g stroke="rgba(255,255,255,0.08)" strokeWidth="1">
                <line x1="80" y1="120" x2="200" y2="80" /><line x1="200" y1="80" x2="320" y2="120" />
                <line x1="200" y1="80" x2="200" y2="200" /><line x1="80" y1="120" x2="110" y2="240" />
                <line x1="320" y1="120" x2="290" y2="240" /><line x1="200" y1="200" x2="110" y2="240" />
                <line x1="200" y1="200" x2="290" y2="240" /><line x1="110" y1="240" x2="200" y2="290" />
                <line x1="290" y1="240" x2="200" y2="290" />
              </g>
              <g transform="translate(200,80)"><circle r="22" fill="rgba(99,102,241,0.15)" stroke="rgba(99,102,241,0.8)" strokeWidth="1.5" /><text y="4" textAnchor="middle" fill="#e2e8f0" fontSize="9" fontWeight="bold" fontFamily="monospace">API</text></g>
              <g transform="translate(80,120)"><circle r="18" fill="rgba(124,58,237,0.15)" stroke="rgba(124,58,237,0.8)" strokeWidth="1.5" /><text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="8" fontFamily="monospace">Auth</text></g>
              <g transform="translate(320,120)"><circle r="18" fill="rgba(124,58,237,0.15)" stroke="rgba(124,58,237,0.8)" strokeWidth="1.5" /><text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="8" fontFamily="monospace">Users</text></g>
              <g transform="translate(200,200)"><circle r="20" fill="rgba(124,58,237,0.15)" stroke="rgba(124,58,237,0.8)" strokeWidth="1.5" /><text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="8" fontFamily="monospace">Model</text></g>
              <g transform="translate(110,240)"><circle r="15" fill="rgba(16,185,129,0.15)" stroke="rgba(16,185,129,0.8)" strokeWidth="1.5" /><text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="7" fontFamily="monospace">DB</text></g>
              <g transform="translate(290,240)"><circle r="15" fill="rgba(16,185,129,0.15)" stroke="rgba(16,185,129,0.8)" strokeWidth="1.5" /><text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="7" fontFamily="monospace">Cache</text></g>
              <g transform="translate(200,290)"><circle r="16" fill="rgba(16,185,129,0.15)" stroke="rgba(16,185,129,0.8)" strokeWidth="1.5" /><text y="3" textAnchor="middle" fill="#e2e8f0" fontSize="7" fontFamily="monospace">Utils</text></g>
            </svg>
          </div>
        </div>
      </section>

      {/* ── COMPARISON TABLE (High fidelity & solid background) ──────────── */}
      <section id="compare" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            Built to Outperform
          </h2>
          <p className="text-slate-300 text-sm max-w-xl mx-auto font-medium">
            The only platform that combines security, performance, threat intelligence, and automated remediation — on your infrastructure.
          </p>
        </div>

        <div className="rounded-3xl border border-white/[0.12] border-t-white/[0.22] overflow-hidden p-0 border-l-4 border-l-indigo-500 bg-slate-elevated/95 shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs md:text-sm">
              <thead>
                <tr className="border-b border-white/[0.08] bg-[#070b13]/80 text-slate-200 font-semibold font-display">
                  <th className="p-4 font-bold">Capability</th>
                  <th className="p-4 text-indigo-400 font-black">CodeViz</th>
                  <th className="p-4">SonarQube</th>
                  <th className="p-4">GitHub Sec</th>
                  <th className="p-4">Snyk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.06] font-medium text-slate-300">
                {comparisons.map((row, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.015] transition-colors">
                    <td className="p-4 font-display font-bold text-slate-100">{row.name}</td>
                    <td className="p-4"><span className="text-emerald-400 font-bold text-base">✓</span></td>
                    <td className="p-4 text-slate-500">{row.sonar  ? <span className="text-slate-300">✓</span> : <span className="text-white/10">—</span>}</td>
                    <td className="p-4 text-slate-500">{row.github ? <span className="text-slate-300">✓</span> : <span className="text-white/10">—</span>}</td>
                    <td className="p-4 text-slate-500">{row.snyk   ? <span className="text-slate-300">✓</span> : <span className="text-white/10">—</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── USE CASES ────────────────────────────────────────────────────── */}
      <section className="py-20 bg-[#060a12]/60 border-y border-slate-border/20 px-6">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <h2 className="text-3xl md:text-4xl font-black font-display tracking-tight text-slate-100">
              Built for the Entire Pipeline
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 text-left">
            {[
              { title: 'Developer Teams',      points: ['Catch bugs before review', 'AI refactoring suggestions', 'Auto-generated PRs', 'Code smell reports'] },
              { title: 'Security Teams',        points: ['MITRE ATT&CK mapping', 'CVE dependency scanning', 'OWASP / SOC 2 compliance', 'Exportable audit trails'] },
              { title: 'Engineering Managers', points: ['Multi-dimensional posture score', 'Performance regression tracking', 'Scheduled scan reports', 'Slack alerting on drift'] },
              { title: 'Enterprise',           points: ['On-premise LLM, zero cloud', 'Air-gap compatible', 'SSO / SAML integration', 'Custom security policies'] },
            ].map((uc, i) => (
              <div key={i} className="rounded-2xl border border-white/[0.08] border-t-white/[0.14] bg-slate-elevated/95 p-5 space-y-4 shadow-md">
                <h3 className="text-sm font-bold text-indigo-400 font-display uppercase tracking-wider">{uc.title}</h3>
                <ul className="space-y-2 text-xs text-slate-300 font-medium">
                  {uc.points.map((p, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <ChevronRight size={12} className="text-indigo-400 mt-0.5 shrink-0" />
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── PRICING (Sleek cards & glows) ────────────────────────────────── */}
      <section id="pricing" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            Predictable Pricing, Infinite Scale
          </h2>
          <p className="text-slate-300 text-sm max-w-xl mx-auto font-medium">
            Every plan includes all 13 analysis dimensions. No feature gating by tier.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 text-left">
          {pricing.map((plan, i) => (
            <div key={i} className={clsx(
              "rounded-3xl border p-6 flex flex-col justify-between space-y-5 relative overflow-hidden bg-slate-elevated/95 transition-all duration-300 shadow-xl",
              plan.popular 
                ? 'border-indigo-500/50 shadow-[0_0_30px_-5px_rgba(99,102,241,0.2)] hover:border-indigo-500/70' 
                : 'border-white/[0.12] border-t-white/[0.22] hover:border-white/[0.18]'
            )}>
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-indigo-500 text-white font-bold text-[10px] tracking-wide uppercase px-3 py-1 rounded-bl-lg">
                  Most Popular
                </div>
              )}
              <div className="space-y-4">
                <div>
                  <h3 className="text-base font-extrabold text-slate-200 font-display">{plan.name}</h3>
                  <p className="text-[11px] text-slate-400 mt-1 font-medium">{plan.desc}</p>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-black font-display text-slate-100">{plan.price}</span>
                  {plan.period && <span className="text-slate-400 text-xs">/ month</span>}
                </div>
                <ul className="space-y-2 border-t border-white/[0.08] pt-4 text-xs text-slate-300 font-medium">
                  {plan.features.map((feat, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <CheckCircle2 size={12} className="text-indigo-400 flex-shrink-0" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>
              {plan.btnText === 'Contact Sales' ? (
                <a href={CONTACT_EMAIL}
                  className="block w-full text-center px-4 py-2.5 rounded-xl border border-white/[0.12] text-slate-300 hover:bg-[#070b13]/40 text-sm font-semibold transition-all">
                  Contact Sales
                </a>
              ) : (
                <button
                  onClick={() => navigate('/login')}
                  className={clsx(
                    "flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-[12px] font-semibold w-full transition-all disabled:opacity-40",
                    plan.popular
                      ? "bg-indigo-500 hover:bg-indigo-600 text-white"
                      : "border border-white/[0.08] text-slate-300 hover:text-slate-100 hover:border-white/[0.14]"
                  )}
                >
                  {plan.btnText}
                </button>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA BANNER ───────────────────────────────────────────────────── */}
      <section className="py-20 px-6 max-w-5xl mx-auto text-center relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-3xl blur-2xl opacity-10 group-hover:opacity-20 transition duration-1000" />
        <div className="rounded-3xl border border-white/[0.12] border-t-white/[0.22] bg-[#0c0f1c]/90 backdrop-blur-xl p-10 md:p-16 space-y-6 relative z-10 overflow-hidden shadow-2xl">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100 max-w-2xl mx-auto leading-none">
            Ready to Automate Your Security & Reviews?
          </h2>
          <p className="text-slate-300 text-sm md:text-base max-w-xl mx-auto leading-relaxed font-medium">
            13 analysis dimensions. On-premise AI. Automated PRs. Threat actor simulation. All in one platform.
          </p>
          <div className="pt-4 flex flex-col sm:flex-row justify-center items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3 rounded-xl text-[14px] font-bold bg-indigo-500 hover:bg-indigo-600 text-white transition-all shadow-xl shadow-indigo-500/20"
            >
              Get Started with GitHub <ArrowUpRight className="ml-1" size={16} />
            </button>
            <a href={GITHUB_REPO} target="_blank" rel="noopener noreferrer"
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 text-xs font-bold border border-slate-border/50 hover:bg-slate-900/30 rounded-xl transition-all text-slate-300 hover:text-slate-100 font-mono">
              <Github size={13} /> View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────────────────── */}
      <footer className="border-t border-slate-border/20 py-12 px-6 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-8 mb-10 text-left">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <img 
                src="/images/logo.png" 
                alt="CodeViz 3D Logo" 
                className="w-6 h-6 rounded-md object-contain"
              />
              <span className="font-extrabold tracking-tight text-slate-300">Code<span className="text-indigo-400 font-medium">Viz</span></span>
            </div>
            <p className="text-slate-400 leading-relaxed font-medium">AI-powered code analysis, security scanning, and automated remediation. On-premise. No cloud dependency.</p>
            <a href={GITHUB_REPO} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-slate-400 hover:text-slate-200 transition-colors">
              <Github size={13} /> Open source on GitHub
            </a>
          </div>

          <div className="space-y-3">
            <p className="text-slate-300 font-semibold uppercase tracking-wider text-[10px]">Platform</p>
            {[
              { label: 'Scanner',          path: '/scanner'          },
              { label: 'Security',         path: '/security'         },
              { label: 'Threat Simulation', path: '/threats'         },
              { label: 'Refactoring',      path: '/refactoring'      },
              { label: 'Compliance',       path: '/compliance'       },
              { label: 'Dependency Graph', path: '/dependency-graph' },
              { label: 'API Analyzer',     path: '/api-analyzer'     },
            ].map(({ label, path }) => (
              <button key={path} onClick={() => navigate(path)}
                className="block text-slate-400 hover:text-slate-200 transition-colors text-left font-medium">{label}</button>
            ))}
          </div>

          <div className="space-y-3">
            <p className="text-slate-300 font-semibold uppercase tracking-wider text-[10px]">Links</p>
            <button onClick={() => scrollTo('features')} className="block text-slate-400 hover:text-slate-200 transition-colors text-left font-medium">Platform</button>
            <button onClick={() => scrollTo('loop')}     className="block text-slate-400 hover:text-slate-200 transition-colors text-left font-medium">How It Works</button>
            <button onClick={() => scrollTo('moats')}    className="block text-slate-400 hover:text-slate-200 transition-colors text-left font-medium">Why CodeViz</button>
            <button onClick={() => scrollTo('pricing')}  className="block text-slate-400 hover:text-slate-200 transition-colors text-left font-medium">Pricing</button>
            <button onClick={() => scrollTo('compare')}  className="block text-slate-400 hover:text-slate-200 transition-colors text-left font-medium">Comparison</button>
            <a href={CONTACT_EMAIL} className="block text-slate-400 hover:text-slate-200 transition-colors font-medium">Contact Sales</a>
            <button onClick={() => navigate('/login')} className="block text-slate-400 hover:text-slate-200 transition-colors text-left font-medium">Sign In</button>
          </div>
        </div>

        <div className="max-w-7xl mx-auto border-t border-white/[0.08] pt-6 flex flex-col sm:flex-row justify-between items-center gap-2">
          <p>© {new Date().getFullYear()} CodeViz Platform. Your code stays yours.</p>
          <p className="font-mono text-slate-600">v1.0.0 · on-premise</p>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
