import { api } from './api'

export const dependenciesService = {
  scan: (sessionId: string) => api.post(`/security/cve-scan/${sessionId}`, {}),
}
