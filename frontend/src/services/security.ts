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

  applyFix: (sessionId: string, bugId: string, file: string, line: number, code: string, fix: string, type: string) =>
    api.post('/security/apply-fix', {
      session_id: sessionId,
      bug_id: bugId,
      file,
      line,
      code,
      fix,
      type
    }),

  autoStage: (sessionId: string, bugs: any[]) =>
    api.post('/security/auto-stage', { session_id: sessionId, bugs }),
}
