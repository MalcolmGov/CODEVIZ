import { api } from './api'

export interface Schedule {
  id: string
  repo_path: string
  email: string
  cron: string
  label: string
  timezone: string
  created_at: string
  last_run: string | null
  last_status: string | null
  scheduler_status: string
}

export const reportsService = {
  downloadPdf: (sessionId: string) =>
    api.get(`/reports/generate/${sessionId}`, { responseType: 'blob' }),

  emailReport: (sessionId: string, email: string) =>
    api.post(`/reports/email/${sessionId}`, { email }),

  previewUrl: (sessionId: string) =>
    `${(import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api'}/reports/preview/${sessionId}`,

  listSchedules: () =>
    api.get<{ data: { schedules: Schedule[] } }>('/reports/schedules'),

  createSchedule: (payload: {
    repo_paths?: string[]
    recipients?: string[]
    frequency?: string
    hour?: number
    label?: string
    timezone?: string
    cron?: string
    // legacy
    repo_path?: string
    email?: string
  }) => api.post('/reports/schedules', payload),

  deleteSchedule: (id: string) =>
    api.delete(`/reports/schedules/${id}`),

  runNow: (id: string) =>
    api.post(`/reports/schedules/${id}/run`),
}
