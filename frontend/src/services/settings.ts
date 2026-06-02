import { api } from './api'

export const settingsService = {
  get: () => api.get('/settings'),
  save: (data: Record<string, unknown>) => api.post('/settings', data),
  testGitHub: (token: string) => api.post('/settings/test/github', { token }),
  testOllama: (url: string)   => api.post('/settings/test/ollama', { url }),
  testSlack:  (webhook: string) => api.post('/settings/test/slack', { webhook }),
}
