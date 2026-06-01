import { api } from './api'

export const securityService = {
  scan: (sessionId: string) =>
    api.post(`/security/scan/${sessionId}`),

  getBugs: (sessionId: string) =>
    api.get(`/security/bugs/${sessionId}`),

  getBugFix: (bugId: string) =>
    api.get(`/security/fix/${bugId}`),

  getReport: (sessionId: string) =>
    api.get(`/security/report/${sessionId}`),
}
