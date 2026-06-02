import { api } from './api'

export interface ScanRecord {
  id: number
  repo_full_name: string
  repo_name: string
  session_id: string
  scanned_at: string
  posture_score: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  total_issues: number
  refactor_count: number
  smell_count: number
  perf_count: number
  compliance_score: number
}

export const historyService = {
  record: (sessionId: string, overrides?: { posture_score?: number; repo_full_name?: string }) =>
    api.post(`/history/record/${sessionId}`, overrides || {}),

  recent: (limit = 20) =>
    api.get(`/history/recent?limit=${limit}`),

  repoHistory: (repoName: string, limit = 30) =>
    api.get(`/history/repo/${encodeURIComponent(repoName)}?limit=${limit}`),

  stats: () =>
    api.get('/history/stats'),

  deleteRecord: (id: number) =>
    api.delete(`/history/${id}`),
}
