import { api } from './api'
import { ApiResponse } from '@/types'

export interface GitHubRepository {
  id: string
  name: string
  full_name: string
  url: string
  clone_url: string
  description: string | null
  private: boolean
  branch: string
  local_path?: string
}

export const repositoriesService = {
  listGitHubRepos: () =>
    api.get<ApiResponse<{ repositories: GitHubRepository[]; count: number }>>('/repositories/github'),
}
