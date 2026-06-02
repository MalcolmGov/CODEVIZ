import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface SettingsState {
  // GitHub
  githubToken: string
  // AI engine
  ollamaUrl: string
  ollamaModel: string
  // Notifications
  slackWebhook: string
  gmailAddress: string
  enableSlackNotifications: boolean
  enableEmailReports: boolean
  // Scan preferences
  defaultRemediationMode: 'hitl' | 'autonomous'
  scanDepth: 'shallow' | 'standard' | 'deep'
  excludePaths: string
  maxFilesPerScan: number
  // Actions
  set: (patch: Partial<Omit<SettingsState, 'set' | 'reset'>>) => void
  reset: () => void
}

const defaults = {
  githubToken: '',
  ollamaUrl: 'http://localhost:11434',
  ollamaModel: 'mistral',
  slackWebhook: '',
  gmailAddress: '',
  enableSlackNotifications: false,
  enableEmailReports: false,
  defaultRemediationMode: 'hitl' as const,
  scanDepth: 'standard' as const,
  excludePaths: 'node_modules, .git, dist, build, venv, __pycache__',
  maxFilesPerScan: 100,
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      ...defaults,
      set: (patch) => set((s) => ({ ...s, ...patch })),
      reset: () => set(defaults),
    }),
    { name: 'codeviz-settings' }
  )
)
