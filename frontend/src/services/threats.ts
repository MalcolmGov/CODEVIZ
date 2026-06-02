import { api } from './api'

export interface ThreatActor {
  id: string
  name: string
  icon: string
  description: string
  skill_level: number
  motivation: string
  exploitability_multiplier: number
}

export interface KillChainStage {
  stage: string
  active_vectors: number
  total_vectors: number
  exploitability: number
  impact: number
  risk: number
  compromised: boolean
  vectors: AttackVector[]
}

export interface AttackVector {
  id: string
  name: string
  stage: string
  tactic: string
  technique: string
  description: string
  exploitability: number
  impact: number
  risk_score: number
  present: boolean
  evidence: string
  mitigations: string[]
  affected_assets: string[]
}

export interface HeatMapPoint {
  id: string
  name: string
  stage: string
  exploitability: number
  impact: number
  present: boolean
}

export interface ThreatSimulation {
  actor: ThreatActor
  kill_chain: KillChainStage[]
  vectors: AttackVector[]
  heat_map: HeatMapPoint[]
  business_impact: {
    data_breach_risk: string
    service_disruption: string
    reputational_damage: string
    regulatory_exposure: string
    critical_attack_paths: number
    estimated_breach_cost: string
  }
  summary: {
    total_vectors: number
    active_vectors: number
    critical_vectors: number
    overall_risk: number
    risk_label: string
    stages_compromised: number
  }
  available_actors: Record<string, ThreatActor>
}

export const threatsService = {
  simulate: (sessionId: string, actorId: string = 'apt') =>
    api.get<{ data: ThreatSimulation }>(`/threats/${sessionId}?actor=${actorId}`),
}
