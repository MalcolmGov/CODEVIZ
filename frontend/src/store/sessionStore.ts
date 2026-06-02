import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { SessionState } from '@/types'
import { api } from '@/services/api'

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      currentSessionId: null,
      sessionData: null,
      remediationMode: 'hitl',

      createSession: async (path: string) => {
        try {
          const response = await api.post('/chat/session', { repo_path: path })
          const sessionId = response.data.data.session_id
          set({
            currentSessionId: sessionId,
            sessionData: {
              repo_path: path,
            },
          })
          return sessionId
        } catch (error) {
          console.error('Failed to create session:', error)
          throw error
        }
      },

      setSessionId: (id: string | null) => {
        set({ currentSessionId: id })
      },

      setRemediationMode: (mode) => {
        set({ remediationMode: mode })
      },

      clearSession: () => {
        set({
          currentSessionId: null,
          sessionData: null,
          remediationMode: 'hitl',
        })
      },
    }),
    {
      name: 'codeviz-session-store',
    }
  )
)
