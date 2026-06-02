import { api } from './api'

export const authService = {
  getGitHubLoginUrl: () =>
    api.get('/auth/github/login', { params: { frontend_url: window.location.origin } }),

  getAuthStatus: () =>
    api.get('/auth/status'),

  logout: () =>
    api.post('/auth/logout'),
}
