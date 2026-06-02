import { api } from './api'

export const dashboardService = {
  getSummary: (sessionId: string) => api.get(`/dashboard/summary/${sessionId}`),
  getSessions: ()                  => api.get('/dashboard/sessions'),
}
