import { api } from './api'
import { OpportunitiesResponse, ApiResponse } from '@/types'

export const refactoringService = {
  getOpportunities: (sessionId: string) =>
    api.get<ApiResponse<OpportunitiesResponse>>(`/refactoring/opportunities/${sessionId}`),

  getSuggestion: (sessionId: string, index: number) =>
    api.get(`/refactoring/suggest/${sessionId}/${index}`),

  getPRContent: (sessionId: string, index: number) =>
    api.get(`/refactoring/pr/${sessionId}/${index}`),

  createPR: (repoName: string, prContent: any, githubToken: string) =>
    api.post('/refactoring/create-pr', {
      repo_name: repoName,
      pr_content: prContent,
      github_token: githubToken,
    }),
}

