// API Types
export interface User {
  id: number
  email: string
  name: string
  github_id?: number
  avatar_url?: string
}

export interface Repository {
  id: number
  name: string
  github_url: string
  default_branch: string
  last_scanned?: string
  status: 'active' | 'archived' | 'scanning'
}

export interface Scan {
  id: number
  repository_id: number
  branch: string
  commit_hash?: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  total_issues: number
  created_at: string
}

export interface Issue {
  id?: number
  bug_id?: string
  scan_id?: number
  type?: string
  severity?: string
  file?: string
  line?: number
  message: string
  cve?: string
  confidence?: number
  fixed?: boolean
  code?: string
  description?: string
  impact?: string
  fix?: string
  cwe?: string
  cvss?: number
}


export interface Refactoring {
  id: number
  scan_id: number
  type: string
  priority: number
  file?: string
  line?: number
  current_code?: string
  suggested_code?: string
  tests?: string
  explanation?: string
  confidence: number
  applied: boolean
}

export interface PullRequest {
  id: number
  title: string
  status: 'draft' | 'open' | 'merged' | 'closed'
  github_pr_number?: number
  github_pr_url?: string
}

// API Response Types
export interface ApiResponse<T> {
  status: 'success' | 'error'
  data: T
  message?: string
  timestamp?: string
}

export interface SessionResponse {
  session_id: string
  repo_path: string
}

export interface ScanResponse {
  session_id: string
  scan_status: {
    files: number
    loc: number
    apis: number
    functions: number
    classes: number
    security_issues: number
  }
}

export interface ArtifactsResponse {
  artifacts: Record<string, any>
}

export interface OpportunitiesResponse {
  opportunities: Refactoring[]
  summary: {
    total: number
    [key: string]: number
  }
}

// Store Types
export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  githubToken?: string
  login: (user: User, token: string) => void
  logout: () => void
  setUser: (user: User) => void
}

export interface SessionState {
  currentSessionId: string | null
  sessionData: {
    repo_path?: string
    scan_status?: Record<string, any>
  } | null
  remediationMode: 'hitl' | 'autonomous'
  createSession: (path: string) => Promise<string>
  setSessionId: (id: string | null) => void
  setRemediationMode: (mode: 'hitl' | 'autonomous') => void
  clearSession: () => void
}

export interface BugsState {
  bugs: Issue[]
  selectedBug: Issue | null
  filters: {
    severity?: string
    type?: string
    fixed?: boolean
  }
  setBugs: (bugs: Issue[]) => void
  setFilter: (filter: Partial<BugsState['filters']>) => void
  selectBug: (bug: Issue) => void
}

export interface RefactoringState {
  opportunities: Refactoring[]
  selectedOpportunity: Refactoring | null
  suggestions: Record<number, any>
  setOpportunities: (opps: Refactoring[]) => void
  selectOpportunity: (opp: Refactoring) => void
  setSuggestion: (index: number, suggestion: any) => void
}
