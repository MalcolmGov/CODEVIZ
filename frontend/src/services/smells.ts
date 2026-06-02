import { api } from './api'

export const smellsService = {
  scan: (sessionId: string) => api.post(`/smells/scan/${sessionId}`, {}),
}
