import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Shield, RefreshCw, CheckCircle2, Activity, Cpu,
  Layers, ArrowRight, FileCode2, ShieldAlert,
  MessageSquare, Sparkles, ArrowUpRight, Github, ExternalLink,
  Skull, Package, Zap, Gauge, FlaskConical, Globe, Wrench,
  Network, Lock, Eye, GitPullRequest, BarChart3, Bell,
  Server, ChevronRight,
} from 'lucide-react'
import clsx from 'clsx'

const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

const GITHUB_REPO    = 'https://github.com/MalcolmGov/CODEVIZ'
const CONTACT_EMAIL  = 'mailto:malcolmgov24@gmail.com?subject=CodeViz%20Enterprise%20Enquiry'

const scrollTo = (id: string) =>
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()

  // ─── Data ────────────────────────────────────────────────────────────
  const stats = [
    { label: 'Analysis Dimensions', value: '13',      desc: 'security · perf · smells · compliance' },
    { label: 'Detection Accuracy',  value: '94%',     desc: 'with < 3% false positives'            },
    { label: 'Vulnerability Types', value: '40+',     desc: 'OWASP · CVE · MITRE ATT&CK'           },
    { label: 'Data Sent to Cloud',  value: '0 bytes', desc: 'on-premise LLM, air-gapped ready'     },
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
    },
    {
      icon: GitPullRequest,
      color: '#22c55e',
      title: 'Find → Fix → Ship in One Tool',
      desc: 'No context switching. CodeViz detects an issue, generates a patch, opens a GitHub PR, and schedules a re-scan — all from one platform.',
      badge: 'End-to-end',
    },
    {
      icon: Skull,
      color: '#ef4444',
      title: 'Threat Actor Simulation',
      desc: 'The only code analysis platform that maps your vulnerabilities to real MITRE ATT&CK kill chains — showing exactly how an attacker would exploit your code.',
      badge: 'Industry-first',
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
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/15">
              <Shield size={16} />
            </div>
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

      {/* ── HERO ─────────────────────────────────────────────────────────── */}
      <section className="relative pt-20 pb-16 px-6 max-w-7xl mx-auto text-center space-y-8">
        <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 px-3.5 py-1 rounded-full text-xs font-bold text-indigo-400">
          <Sparkles size={12} />
          <span>13-DIMENSION AI CODE ANALYSIS — ON-PREMISE, ZERO CLOUD</span>
        </div>

        <h1 className="text-4xl sm:text-6xl md:text-7xl font-black font-display tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-white via-slate-100 to-slate-400 max-w-5xl mx-auto leading-none">
          The AI Security Platform <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500">
            That Fixes What It Finds
          </span>
        </h1>

        <p className="text-slate-400 text-base sm:text-xl font-medium max-w-3xl mx-auto leading-relaxed">
          Security, performance, threats, compliance, and code quality — analysed simultaneously.
          AI-generated fixes shipped as PRs. Your code never leaves your machine.
        </p>

        <div className="flex flex-col sm:flex-row justify-center items-center gap-4 pt-4">
          <button
            onClick={() => navigate('/login')}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3 rounded-xl text-[14px] font-bold bg-indigo-500 hover:bg-indigo-600 text-white transition-all shadow-lg shadow-indigo-500/20"
          >
            Start Scanning Now <ArrowRight className="ml-2" size={18} />
          </button>
          <button onClick={() => scrollTo('loop')}
            className="w-full sm:w-auto px-6 py-3 text-sm font-bold border border-slate-border/50 hover:bg-slate-900/30 rounded-xl transition-all text-slate-300 hover:text-slate-100">
            See How It Works
          </button>
        </div>

        {/* Terminal preview */}
        <div className="pt-10 max-w-5xl mx-auto relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-2xl blur-xl opacity-20 group-hover:opacity-30 transition duration-1000" />
          <div className={clsx(CARD, "overflow-hidden relative shadow-2xl p-0.5 bg-slate-surface/30")}>
            <div className="bg-[#0b0f19] rounded-xl overflow-hidden border border-slate-border/30">
              <div className="flex items-center justify-between px-4 py-3 bg-[#070b13] border-b border-slate-border/30">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="text-[10px] font-mono text-slate-500 bg-slate-900/50 px-3 py-1 rounded border border-slate-border/20">
                  codeviz — 13-dimension analysis engine
                </div>
                <div className="w-10" />
              </div>
              <div className="p-6 text-left font-mono text-xs text-slate-300 space-y-3 max-h-[340px] overflow-y-auto bg-[#040810]/90">
                <div className="flex gap-2 text-indigo-400"><span>$</span><span>codeviz scan --repo=github.com/acme/api-service --all-dimensions</span></div>
                <div className="text-slate-500">🔍 Initialising 13-dimension analysis engine (on-premise Ollama)...</div>
                <div className="text-emerald-400">✓ Scanned 2,847 files · 94,120 LOC in 1m 43s</div>
                <div className="grid grid-cols-2 gap-x-8 gap-y-1 text-[11px] mt-2 text-slate-400">
                  <span>├── Security vulns found:      <span className="text-red-400 font-bold">12 (3 critical)</span></span>
                  <span>├── Performance regressions:   <span className="text-amber-400 font-bold">7</span></span>
                  <span>├── MITRE ATT&CK matches:      <span className="text-red-400 font-bold">4 kill chains</span></span>
                  <span>├── Dependency CVEs (OSV):     <span className="text-amber-400 font-bold">9</span></span>
                  <span>├── Code smells:               <span className="text-yellow-400 font-bold">31</span></span>
                  <span>└── Compliance gaps (SOC 2):   <span className="text-amber-400 font-bold">6</span></span>
                </div>
                <div className="text-slate-500 mt-2">🤖 Generating AI remediation patches (HITL mode)...</div>
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

      {/* ── PLATFORM FEATURES ────────────────────────────────────────────── */}
      <section id="features" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            The Complete Code Intelligence Platform
          </h2>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl mx-auto">
            13 analysis engines running simultaneously. Every scan covers security, performance, threats,
            quality, dependencies, and compliance — not just one dimension.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feat, i) => {
            const Icon = feat.icon
            return (
              <div key={i} onClick={() => navigate(feat.href)}
                className={clsx(CARD, "hover:border-indigo-500/30 p-6 flex flex-col justify-between hover:-translate-y-1 bg-slate-surface/30 cursor-pointer transition-all duration-300 group")}>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 group-hover:bg-indigo-500/20 group-hover:text-indigo-300 transition-colors">
                      <Icon size={20} />
                    </div>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border border-slate-border/60 text-slate-400 bg-slate-900/50">
                      {feat.badge}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-slate-100 font-display">{feat.title}</h3>
                  <p className="text-slate-400 text-xs leading-relaxed font-medium">{feat.desc}</p>
                </div>
                <div className="mt-4 flex items-center gap-1 text-[11px] font-semibold text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  Try it <ArrowRight size={11} />
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────────────────── */}
      <section id="loop" className="py-20 px-6 bg-slate-surface/10 border-y border-slate-border/20">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-emerald-400">
              <Zap size={10} /> THE COMPLETE LOOP
            </div>
            <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
              Find It. Fix It. Ship It. Monitor It.
            </h2>
            <p className="text-slate-400 text-sm max-w-xl mx-auto">
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
                    <p className="text-[11px] text-slate-500 leading-snug">{s.desc}</p>
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
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Three capabilities no competitor offers. Any one of them alone would be a product — together they're a moat.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {moats.map((m, i) => {
            const Icon = m.icon
            return (
              <div key={i} className="rounded-2xl border border-white/[0.07] bg-slate-surface/30 p-8 space-y-5 relative overflow-hidden group hover:border-white/[0.12] transition-all">
                <div className="absolute -top-8 -right-8 w-32 h-32 rounded-full blur-2xl opacity-10 group-hover:opacity-20 transition-opacity"
                  style={{ backgroundColor: m.color }} />
                <div className="p-3 rounded-xl border w-fit" style={{ color: m.color, borderColor: `${m.color}30`, backgroundColor: `${m.color}10` }}>
                  <Icon size={22} />
                </div>
                <div>
                  <span className="text-[9px] font-bold uppercase tracking-widest font-mono mb-2 block" style={{ color: m.color }}>{m.badge}</span>
                  <h3 className="text-lg font-extrabold text-slate-100 font-display leading-tight">{m.title}</h3>
                </div>
                <p className="text-slate-400 text-[13px] leading-relaxed">{m.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* ── MITRE ATT&CK SPOTLIGHT ───────────────────────────────────────── */}
      <section className="py-20 px-6 bg-gradient-to-b from-red-950/10 to-transparent border-y border-red-900/20">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 bg-red-500/10 border border-red-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-red-400">
              <Skull size={10} /> INDUSTRY-FIRST CAPABILITY
            </div>
            <h2 className="text-3xl md:text-4xl font-black font-display tracking-tight text-slate-100">
              Threat Actor <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">Kill Chain Simulation</span>
            </h2>
            <p className="text-slate-400 text-sm leading-relaxed">
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
                  <span className="text-[13px] text-slate-300">{pt}</span>
                </div>
              ))}
            </div>
            <button onClick={() => navigate('/threats')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm font-semibold hover:bg-red-500/20 transition-all">
              <ExternalLink size={14} /> View Threat Simulation
            </button>
          </div>

          {/* Kill chain visual */}
          <div className="rounded-2xl border border-red-900/30 bg-[#0a0505] p-6 space-y-3 font-mono text-xs">
            <div className="flex items-center gap-2 text-red-400 font-bold mb-4">
              <Skull size={14} /> MITRE ATT&CK Kill Chain — Active Threat Path
            </div>
            {[
              { phase: 'Initial Access',   tactic: 'T1190 · Exploit Public-Facing Application',  file: 'UserController.search()',    sev: 'CRITICAL' },
              { phase: 'Execution',        tactic: 'T1059 · Command & Scripting Interpreter',     file: 'shell_utils.execute()',      sev: 'HIGH'     },
              { phase: 'Persistence',      tactic: 'T1098 · Account Manipulation',               file: 'AuthService.createToken()',  sev: 'HIGH'     },
              { phase: 'Exfiltration',     tactic: 'T1041 · Exfiltration Over C2 Channel',       file: 'DataExport.send()',          sev: 'CRITICAL' },
            ].map((row, i) => (
              <div key={i} className="flex flex-col gap-1 py-2.5 border-b border-red-900/20 last:border-0">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-bold uppercase tracking-widest text-red-500/60">{row.phase}</span>
                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${row.sev === 'CRITICAL' ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'}`}>{row.sev}</span>
                </div>
                <span className="text-slate-300 text-[11px]">{row.tactic}</span>
                <span className="text-slate-600 text-[10px]">→ {row.file}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ON-PREMISE PRIVACY ───────────────────────────────────────────── */}
      <section className="py-20 px-6 max-w-7xl mx-auto">
        <div className="rounded-2xl border border-indigo-500/10 bg-gradient-to-br from-indigo-500/[0.05] to-transparent p-10 md:p-14">
          <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
            <div className="space-y-5">
              <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-indigo-400">
                <Lock size={10} /> PRIVACY BY ARCHITECTURE
              </div>
              <h2 className="text-3xl font-black font-display tracking-tight text-slate-100">
                Your Code Never Leaves Your Machine
              </h2>
              <p className="text-slate-400 text-sm leading-relaxed">
                CodeViz runs its AI engine entirely on-premise via Ollama. No API calls to OpenAI, Anthropic, or any cloud LLM. Your source code, secrets, and business logic stay local — always.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { icon: Server, label: 'On-premise LLM',       desc: 'Ollama runs locally, no cloud dependency' },
                { icon: Lock,   label: 'Air-gap compatible',   desc: 'Works in isolated enterprise environments' },
                { icon: Shield, label: 'Zero data retention',  desc: 'Nothing persisted outside your machine'   },
                { icon: Eye,    label: 'Audit-ready logs',     desc: 'Full scan provenance for compliance'      },
              ].map((item, i) => {
                const Icon = item.icon
                return (
                  <div key={i} className="flex items-start gap-3 p-4 rounded-xl border border-white/[0.06] bg-slate-surface/20">
                    <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 shrink-0">
                      <Icon size={14} />
                    </div>
                    <div>
                      <p className="text-[12px] font-bold text-slate-200">{item.label}</p>
                      <p className="text-[10px] text-slate-500 mt-0.5">{item.desc}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ── DEPENDENCY NETWORK ───────────────────────────────────────────── */}
      <section id="graph" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 px-3 py-0.5 rounded-full text-[10px] font-bold text-purple-400">
              <Activity size={10} /> VISUAL CODE MESH
            </div>
            <h2 className="text-3xl md:text-4xl font-black font-display tracking-tight leading-tight text-slate-100">
              Obsidian-Inspired <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">
                Dependency Network
              </span>
            </h2>
            <p className="text-slate-400 text-sm leading-relaxed">
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
                  <span className="text-xs text-slate-300 font-semibold">{item.title}</span>
                  <span className="text-[10px] text-slate-500 font-mono ml-auto">{item.value}</span>
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

      {/* ── COMPARISON TABLE ─────────────────────────────────────────────── */}
      <section id="compare" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            Built to Outperform
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            The only platform that combines security, performance, threat intelligence, and automated remediation — on your infrastructure.
          </p>
        </div>

        <div className={clsx(CARD, "overflow-hidden p-0 border-l-4 border-l-indigo-500 bg-slate-surface/30")}>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs md:text-sm">
              <thead>
                <tr className="border-b border-slate-border/50 bg-[#070b13]/60 text-slate-400 font-semibold font-display">
                  <th className="p-4 font-bold">Capability</th>
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
                    <td className="p-4"><span className="text-emerald-400 font-bold text-base">✓</span></td>
                    <td className="p-4 text-slate-500">{row.sonar  ? <span className="text-slate-400">✓</span> : <span className="text-slate-700">—</span>}</td>
                    <td className="p-4 text-slate-500">{row.github ? <span className="text-slate-400">✓</span> : <span className="text-slate-700">—</span>}</td>
                    <td className="p-4 text-slate-500">{row.snyk   ? <span className="text-slate-400">✓</span> : <span className="text-slate-700">—</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── USE CASES ────────────────────────────────────────────────────── */}
      <section className="py-20 bg-slate-surface/10 border-y border-slate-border/20 px-6">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <h2 className="text-3xl md:text-4xl font-black font-display tracking-tight text-slate-100">
              Built for the Entire Pipeline
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { title: 'Developer Teams',      points: ['Catch bugs before review', 'AI refactoring suggestions', 'Auto-generated PRs', 'Code smell reports'] },
              { title: 'Security Teams',        points: ['MITRE ATT&CK mapping', 'CVE dependency scanning', 'OWASP / SOC 2 compliance', 'Exportable audit trails'] },
              { title: 'Engineering Managers', points: ['Multi-dimensional posture score', 'Performance regression tracking', 'Scheduled scan reports', 'Slack alerting on drift'] },
              { title: 'Enterprise',           points: ['On-premise LLM, zero cloud', 'Air-gap compatible', 'SSO / SAML integration', 'Custom security policies'] },
            ].map((uc, i) => (
              <div key={i} className={clsx(CARD, "bg-slate-surface/30 p-5 space-y-4")}>
                <h3 className="text-sm font-bold text-indigo-400 font-display uppercase tracking-wider">{uc.title}</h3>
                <ul className="space-y-2 text-xs text-slate-400 font-medium">
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

      {/* ── PRICING ──────────────────────────────────────────────────────── */}
      <section id="pricing" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100">
            Predictable Pricing, Infinite Scale
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Every plan includes all 13 analysis dimensions. No feature gating by tier.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {pricing.map((plan, i) => (
            <div key={i} className={clsx(CARD, "p-6 flex flex-col justify-between space-y-5 relative overflow-hidden bg-slate-surface/30", plan.popular ? 'border-indigo-500/60 ring-2 ring-indigo-500/10' : '')}>
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-indigo-500 text-white font-bold text-[10px] tracking-wide uppercase px-3 py-1 rounded-bl-lg">
                  Most Popular
                </div>
              )}
              <div className="space-y-4">
                <div>
                  <h3 className="text-base font-extrabold text-slate-200 font-display">{plan.name}</h3>
                  <p className="text-[11px] text-slate-500 mt-1">{plan.desc}</p>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-black font-display text-slate-100">{plan.price}</span>
                  {plan.period && <span className="text-slate-500 text-xs">/ month</span>}
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
              {plan.btnText === 'Contact Sales' ? (
                <a href={CONTACT_EMAIL}
                  className="block w-full text-center px-4 py-2.5 rounded-xl border border-slate-border/50 text-slate-300 hover:bg-slate-800/40 text-sm font-semibold transition-all">
                  Contact Sales
                </a>
              ) : (
                <button
                  onClick={() => navigate('/login')}
                  className={clsx(
                    "flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-[12px] font-semibold w-full transition-all disabled:opacity-40",
                    plan.popular
                      ? "bg-indigo-500 hover:bg-indigo-600 text-white"
                      : "border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/[0.14]"
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
        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 rounded-2xl blur-2xl opacity-10 group-hover:opacity-20 transition duration-1000" />
        <div className={clsx(CARD, "bg-slate-surface/30 backdrop-blur-xl p-10 md:p-16 space-y-6 relative z-10 overflow-hidden")}>
          <h2 className="text-3xl md:text-5xl font-black font-display tracking-tight text-slate-100 max-w-2xl mx-auto">
            Ready to Automate Your Security & Reviews?
          </h2>
          <p className="text-slate-400 text-sm md:text-base max-w-xl mx-auto leading-relaxed">
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
      <footer className="border-t border-slate-border/20 py-12 px-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-8 mb-10">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <Shield size={12} />
              </div>
              <span className="font-extrabold tracking-tight text-slate-300">Code<span className="text-indigo-400 font-medium">Viz</span></span>
            </div>
            <p className="text-slate-600 leading-relaxed">AI-powered code analysis, security scanning, and automated remediation. On-premise. No cloud dependency.</p>
            <a href={GITHUB_REPO} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-slate-500 hover:text-slate-300 transition-colors">
              <Github size={13} /> Open source on GitHub
            </a>
          </div>

          <div className="space-y-3">
            <p className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Platform</p>
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
                className="block text-slate-600 hover:text-slate-300 transition-colors text-left">{label}</button>
            ))}
          </div>

          <div className="space-y-3">
            <p className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Links</p>
            <button onClick={() => scrollTo('features')} className="block text-slate-600 hover:text-slate-300 transition-colors text-left">Platform</button>
            <button onClick={() => scrollTo('loop')}     className="block text-slate-600 hover:text-slate-300 transition-colors text-left">How It Works</button>
            <button onClick={() => scrollTo('moats')}    className="block text-slate-600 hover:text-slate-300 transition-colors text-left">Why CodeViz</button>
            <button onClick={() => scrollTo('pricing')}  className="block text-slate-600 hover:text-slate-300 transition-colors text-left">Pricing</button>
            <button onClick={() => scrollTo('compare')}  className="block text-slate-600 hover:text-slate-300 transition-colors text-left">Comparison</button>
            <a href={CONTACT_EMAIL} className="block text-slate-600 hover:text-slate-300 transition-colors">Contact Sales</a>
            <button onClick={() => navigate('/login')} className="block text-slate-600 hover:text-slate-300 transition-colors text-left">Sign In</button>
          </div>
        </div>

        <div className="max-w-7xl mx-auto border-t border-slate-border/20 pt-6 flex flex-col sm:flex-row justify-between items-center gap-2">
          <p>© {new Date().getFullYear()} CodeViz Platform. Your code stays yours.</p>
          <p className="font-mono text-slate-700">v1.0.0 · on-premise</p>
        </div>
      </footer>
    </div>
  )
}
