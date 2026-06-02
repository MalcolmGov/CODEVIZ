import { api } from './api'

export const threatsService = {
  // Pass existing bugs so backend skips re-scanning
  simulate: (sessionId: string, bugs: any[] = []) =>
    api.post(`/threats/simulate/${sessionId}`, { bugs }),
}
