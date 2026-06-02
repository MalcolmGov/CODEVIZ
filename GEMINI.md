# CodeViz — Project Context for Antigravity

## What this is

CodeViz is a full-stack code analysis and security visualisation platform.
A developer points it at a GitHub repo (or local path), runs a scan, and gets
security findings, refactoring suggestions, performance analysis, compliance
checks, dependency graphs, code smell detection, and auto-remediation — all
in a dark-themed React dashboard backed by a Python/Flask API.

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18 + TypeScript, Vite, Tailwind CSS (dark-mode class), Lucide icons, D3 v7 |
| Backend | Python 3.9, Flask (blueprint-per-domain), SQLAlchemy + SQLite, APScheduler |
| AI | Ollama (local LLM) — accessed via `services/ollama.py` |
| Auth | GitHub OAuth (token stored in settings) |
| Notifications | Slack webhooks via `SlackNotificationManager` |

---

## Directory map

```
codeviz-proper/
├── frontend/src/
│   ├── pages/          # One file per route (see page list below)
│   ├── components/
│   │   ├── common/     # Card, Button, Badge, AskAIButton, ErrorBoundary …
│   │   ├── features/   # BugList, BugDetail, ScanForm, StagedPRModal …
│   │   └── layout/     # MainLayout, Header, Sidebar
│   ├── services/       # axios wrappers — one file per backend blueprint
│   ├── store/          # Zustand stores (auth, session, bugs, settings, theme)
│   ├── styles/         # globals.css — CSS vars, dark-mode palette, utilities
│   └── types/
├── backend/
│   ├── api/            # Flask blueprints (one file per domain)
│   ├── core/           # Business logic (scanner, security, remediation …)
│   ├── services/       # GitHub, Slack, Ollama, scheduler, email
│   └── models/         # SQLAlchemy models
├── scripts/
│   └── git-commit.sh   # MUST use this instead of bare `git commit` (see below)
├── Makefile            # dev-frontend / dev-backend / clean-locks
└── docs/               # ARCHITECTURE.md, API.md, SETUP.md
```

---

## Design system — CRITICAL for UI work

The app runs in **dark mode only** (`<html class="dark">`). All pages must use
these patterns. Do not introduce new component abstractions.

### Core tokens (Tailwind classes)

```ts
// Card container — use on every panel/section
const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

// Form labels
const LABEL = 'text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-1.5 block'

// Text inputs / selects
const INPUT = 'w-full rounded-xl border border-white/[0.08] bg-slate-elevated px-3.5 py-2.5 text-[13px] text-slate-200 placeholder-slate-700 font-mono focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all disabled:opacity-40'
```

### Colour palette (semantic)

| Use | Class | Hex (dark mode) |
|---|---|---|
| Primary action | `bg-indigo-500` | `#6366f1` |
| Primary hover | `bg-indigo-600` | `#4f46e5` |
| Success / clean | `text-emerald-400` | `#34d399` |
| Warning / medium | `text-amber-400` | `#fbbf24` |
| Danger / critical | `text-red-400` / `text-rose-400` | `#f87171` |
| High severity | `text-orange-400` | `#f97316` |
| Muted body copy | `text-slate-400` | `#94a3b8` |
| Faint labels | `text-slate-500` | `#64748b` |
| Ghost text | `text-slate-600` | `#475569` |
| Card border | `border-white/[0.08]` | rgba(255,255,255,0.08) |
| Elevated panel | `bg-slate-elevated` | `#172033` |
| Card background | `bg-slate-surface` | `#111827` |
| Page canvas | `bg-slate-canvas` | `#080b14` |

### Typography scale

| Use | Classes |
|---|---|
| Page title | `text-[22px] font-extrabold text-white font-tight tracking-tight` |
| Page subtitle | `text-slate-500 text-[13px] mt-1.5` |
| Section heading | `text-[15px] font-semibold text-slate-200 font-tight` |
| Body / description | `text-[13px] text-slate-400 leading-relaxed` |
| Small label | `text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500` |
| Mono / path | `text-[11px] font-mono text-slate-600` |
| Stat value | `text-[32px] font-black text-white font-tight leading-none tracking-tight` |

`font-tight` = Inter Tight (defined in `tailwind.config.js`).

### Button patterns (inline — do NOT use the Button component for new work)

```tsx
// Primary
'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold bg-indigo-500 hover:bg-indigo-600 text-white transition-all disabled:opacity-40'

// Secondary / ghost
'flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold border border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/[0.14] transition-all'

// Danger
'... border border-rose-500/20 bg-rose-500/[0.07] text-rose-400 hover:bg-rose-500/[0.14] ...'
```

### Stat card pattern (used on most data pages)

```tsx
function StatCard({ label, value, sub, accent, icon: Icon }) {
  return (
    <div className={`${CARD} p-6`}>
      <div className="h-[3px] w-8 rounded-full mb-5" style={{ backgroundColor: accent }} />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.13em] text-slate-500 mb-2">{label}</p>
          <p className="text-[32px] font-black text-white font-tight leading-none tracking-tight">{value}</p>
          <p className="text-[11px] text-slate-500 mt-2 leading-snug">{sub}</p>
        </div>
        <div className="p-2 rounded-xl border border-white/[0.06] bg-slate-elevated">
          <Icon size={15} style={{ color: accent }} />
        </div>
      </div>
    </div>
  )
}
```

### Page wrapper pattern

```tsx
<div className="space-y-5 animate-fade-in pb-10 select-none">
  {/* header */}
  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
    <div>
      <h1 className="text-[22px] font-extrabold text-white font-tight tracking-tight">Page Title</h1>
      <p className="text-slate-500 text-[13px] mt-1.5">Subtitle.</p>
    </div>
    {/* primary action button */}
  </div>
  {/* content cards */}
</div>
```

### Misc utilities

- `scrollbar-none` — hides scrollbars on overflow containers
- `animate-fade-in` — 0.3s ease-in-out fade on page mount
- `shadow-card` — `0 1px 3px rgba(0,0,0,0.45), 0 2px 8px rgba(0,0,0,0.3)`
- `backdrop-blur-md` — always applied to cards

---

## Page status — which need UI polish

### ✅ Fully polished (use as reference)
These pages use the canonical design system end-to-end:

| Page | File |
|---|---|
| Dashboard | `pages/DashboardPage.tsx` |
| Code Smells | `pages/CodeSmellsPage.tsx` |
| Remediation | `pages/RemediationPage.tsx` |
| Performance | `pages/PerformancePage.tsx` |
| Threats | `pages/ThreatPage.tsx` |
| Dependencies | `pages/DependenciesPage.tsx` |
| Dependency Graph | `pages/DependencyGraphPage.tsx` |
| API Analyzer | `pages/ApiAnalyzerPage.tsx` |
| Reports | `pages/ReportsPage.tsx` |
| Settings | `pages/SettingsPage.tsx` |

### ⚠️ Still use legacy Card / Button components — need polishing
These import from `@/components/common/Card` and `@/components/common/Button`.
Replace with inline `CARD` constant + inline button patterns described above.

| Page | File | Notes |
|---|---|---|
| Scanner | `pages/ScannerPage.tsx` | Core entry point — high priority |
| Security | `pages/SecurityPage.tsx` | Most-used results page — high priority |
| Compliance | `pages/CompliancePage.tsx` | |
| Refactoring | `pages/RefactoringPage.tsx` | |
| Login | `pages/LoginPage.tsx` | |
| Landing | `pages/LandingPage.tsx` | Marketing page, lower priority |

> **Reference file:** `pages/DashboardPage.tsx` is the gold standard for how a fully
> polished page looks. Read it first before touching any page.

---

## Backend blueprint → frontend service mapping

| Blueprint | URL prefix | Frontend service |
|---|---|---|
| `chat_bp` | `/api/chat` | `services/chat.ts` |
| `security_bp` | `/api/security` | `services/security.ts` |
| `remediation_bp` | `/api/remediation` | `services/remediation.ts` |
| `notifications_bp` | `/api/notifications` | `services/apis.ts` → `notificationsService` |
| `apis_bp` | `/api/apis` | `services/apis.ts` → `apisService` |
| `smells_bp` | `/api/smells` | `services/smells.ts` |
| `reports_bp` | `/api/reports` | `services/reports.ts` |
| `settings_bp` | `/api/settings` | `services/settings.ts` |
| `history_bp` | `/api/history` | `services/history.ts` |
| `scoring_bp` | `/api/scoring` | `services/scoring.ts` |

---

## Dev servers

```bash
# Backend — http://localhost:8000
make dev-backend
# or: cd backend && source venv/bin/activate && python main.py

# Frontend — http://localhost:5173 (or 5174 if port taken)
make dev-frontend
# or: cd frontend && npm run dev
```

Python version: **3.9** — do not use `X | Y` union type syntax (use `Optional[X]`).

---

## Git commit workflow — IMPORTANT

The repo lives on a FUSE/virtiofs mount that blocks `unlink()` on lock files.
**Never run `git commit` directly** — it will fail with a lock error.

Always use the wrapper:

```bash
bash scripts/git-commit.sh -- -m "your message"
```

To stage specific files first:

```bash
git add <files>
bash scripts/git-commit.sh -- -m "your message"
```

The script moves stale `.lock` files aside before running git.

---

## Key Zustand stores

| Store | File | Key state |
|---|---|---|
| `useSessionStore` | `store/sessionStore.ts` | `currentSessionId`, `sessionData` |
| `useAuthStore` | `store/authStore.ts` | `isAuthenticated`, `user` |
| `useSettingsStore` | `store/settingsStore.ts` | `githubToken`, `slackWebhook`, `ollamaUrl`, `ollamaModel` |
| `useBugsStore` | `store/bugsStore.ts` | `bugs` (security findings) |

---

## AskAIButton component

Available at `@/components/common/AskAIButton`. Drop it into any findings detail
panel to let users query the local Ollama LLM about a specific issue:

```tsx
<AskAIButton
  label="SQL Injection"
  context="Full finding description here — file, line, description, suggested fix"
/>
```

Requires an active session (`currentSessionId`). Shows inline collapsible panel with Regenerate.
