import { api } from './api'

export interface ComplianceControl {
  id: string
  name: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'pass' | 'fail' | 'warn' | 'info'
  finding: string
  remediation: string
}

export interface FrameworkResult {
  id: string
  name: string
  version: string
  icon: string
  score: number
  grade: string
  controls: ComplianceControl[]
  summary: { total: number; passed: number; failed: number; warned: number }
}

export interface ComplianceReport {
  frameworks: Record<string, FrameworkResult>
  overall: { score: number; grade: string; frameworks_checked: number }
  available_frameworks: Record<string, { name: string; version: string; icon: string }>
}

export const complianceService = {
  getReport: (sessionId: string) =>
    api.get<{ data: ComplianceReport }>(`/compliance/${sessionId}`),
  listFrameworks: () =>
    api.get('/compliance/frameworks'),
}
