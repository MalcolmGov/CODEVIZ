import { api } from './api'
import { SessionResponse, ScanResponse, ArtifactsResponse, ApiResponse } from '@/types'

export const chatService = {
  createSession: (repoPath: string) =>
    api.post<ApiResponse<SessionResponse>>('/chat/session', { repo_path: repoPath }),

  scan: (sessionId: string) =>
    api.post<ApiResponse<ScanResponse>>(`/chat/scan/${sessionId}`),

  getArtifacts: (sessionId: string) =>
    api.get<ApiResponse<ArtifactsResponse>>(`/chat/artifacts/${sessionId}`),

  ask: (sessionId: string, question: string) =>
    api.post('/chat/ask', { session_id: sessionId, question }),

  getHistory: (sessionId: string) =>
    api.get(`/chat/history/${sessionId}`),

  clearSession: (sessionId: string) =>
    api.post(`/chat/clear/${sessionId}`),
}

