import { api } from './api'

export const authService = {
  getGitHubLoginUrl: () =>
    api.get('/auth/github/login'),

  getAuthStatus: () =>
    api.get('/auth/status'),

  logout: () =>
    api.post('/auth/logout'),
}
