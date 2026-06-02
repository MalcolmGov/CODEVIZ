import { api } from './api'

export const performanceService = {
  scan:      (sessionId: string) => api.post(`/performance/scan/${sessionId}`, {}),
  getIssue:  (sessionId: string, issueId: string) => api.get(`/performance/issue/${sessionId}/${issueId}`),
}
