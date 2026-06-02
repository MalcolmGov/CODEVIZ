import { api } from './api'

export const remediationService = {
  scan:    (sessionId: string)                         => api.post(`/remediation/scan/${sessionId}`, {}),
  preview: (sessionId: string, category: string)       => api.post(`/remediation/preview/${sessionId}`, { category }),
}
