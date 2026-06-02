import { api } from './api'

export const apisService = {
  endpoints:   (sessionId: string)                    => api.get(`/apis/endpoints/${sessionId}`),
  probe:       (sessionId: string, baseUrl: string)   => api.post(`/apis/probe/${sessionId}`, { base_url: baseUrl }),
  graph:       (sessionId: string)                    => api.get(`/apis/graph/${sessionId}`),
}

export const notificationsService = {
  slackStatus: ()                                      => api.get('/notifications/slack/status'),
  slackTest:   (webhookUrl: string)                   => api.post('/notifications/slack/test', { webhook_url: webhookUrl }),
  slackAlert:  (sessionId: string, webhookUrl?: string) => api.post(`/notifications/slack/alert/${sessionId}`, { webhook_url: webhookUrl }),
}
