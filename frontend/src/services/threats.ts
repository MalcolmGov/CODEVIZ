import { api } from './api'

export const threatsService = {
  simulate: (sessionId: string) => api.post(`/threats/simulate/${sessionId}`, {}),
}
