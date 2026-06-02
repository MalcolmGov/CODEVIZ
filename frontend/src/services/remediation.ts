import { api } from './api'

export interface TestGenRequest {
  issue_type:    string
  file_path:     string
  description:   string
  original_code: string
  fixed_code:    string
  language?:     string
}

export interface TestGenResult {
  test_code:          string
  language:           string
  suggested_filename: string
  issue_type:         string
  llm_used:           boolean
}

export const remediationService = {
  scan:    (sessionId: string)                         => api.post(`/remediation/scan/${sessionId}`, {}),
  preview: (sessionId: string, category: string)       => api.post(`/remediation/preview/${sessionId}`, { category }),
  generateTests: (req: TestGenRequest)                 => api.post('/remediation/generate-tests', req),
}
