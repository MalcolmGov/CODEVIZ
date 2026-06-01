import { api } from './api'

export interface DimensionScore {
  name: string
  score: number
  grade: string
  label: string
  color: string
  weight: number
  findings: string[]
}

export interface CompositeScore {
  score: number
  grade: string
  label: string
  color: string
}

export interface ScoreSummary {
  total_findings: number
  critical_flags: number
  warnings: number
  positives: number
}

export interface RiskProfile {
  composite: CompositeScore
  dimensions: DimensionScore[]
  summary: ScoreSummary
}

export const scoringService = {
  getScore: (sessionId: string) =>
    api.get<{ data: RiskProfile }>(`/scoring/${sessionId}`),
}
