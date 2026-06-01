import React, { useState, useEffect } from 'react'
import { TextInput } from '@/components/forms/TextInput'
import { SelectInput } from '@/components/forms/SelectInput'
import { Button } from '@/components/common/Button'
import { useSessionStore } from '@/store/sessionStore'
import { chatService } from '@/services/chat'
import { repositoriesService, GitHubRepository } from '@/services/repositories'

export const ScanForm: React.FC<{ onScanComplete: (sessionId: string) => void }> = ({ onScanComplete }) => {
  const [repoPath, setRepoPath] = useState('/Users/malcolmgovender/.gemini/antigravity-ide/scratch/codeviz')
  const [repos, setRepos] = useState<GitHubRepository[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string>('')
  const [isCustomPath, setIsCustomPath] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>()
  const { createSession } = useSessionStore()

  useEffect(() => {
    const fetchRepos = async () => {
      try {
        const response = await repositoriesService.listGitHubRepos()
        const fetchedRepos = response.data.data.repositories || []
        setRepos(fetchedRepos)
        
        // Auto-select the first repo if available
        if (fetchedRepos.length > 0) {
          const first = fetchedRepos[0]
          setSelectedRepo(first.id)
          setRepoPath(first.local_path || first.clone_url)
        } else {
          setIsCustomPath(true)
        }
      } catch (err) {
        console.error('Failed to load GitHub repositories:', err)
        setIsCustomPath(true)
      }
    }

    fetchRepos()
  }, [])

  const handleRepoChange = (id: string) => {
    setSelectedRepo(id)
    if (id === 'custom') {
      setIsCustomPath(true)
      setRepoPath('')
    } else {
      setIsCustomPath(false)
      const found = repos.find(r => r.id === id)
      if (found) {
        setRepoPath(found.local_path || found.clone_url)
      }
    }
  }

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!repoPath) {
      setError('Please select or specify a repository to scan')
      return
    }

    setLoading(true)
    setError(undefined)

    try {
      const sessionId = await createSession(repoPath)
      await chatService.scan(sessionId)
      onScanComplete(sessionId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  const selectOptions = [
    ...repos.map(r => ({
      value: r.id,
      label: `${r.full_name} (${r.private ? '🔒 Private' : '🌐 Public'})`
    })),
    { value: 'custom', label: '📁 Local Directory Path / Custom URL...' }
  ]

  return (
    <form onSubmit={handleScan} className="space-y-4">
      {repos.length > 0 && (
        <SelectInput
          label="Select Authorized Repository"
          options={selectOptions}
          value={selectedRepo}
          onChange={handleRepoChange}
          required
        />
      )}

      {isCustomPath && (
        <TextInput
          label="Repository Location Path or URL"
          placeholder="/path/to/local/repo or https://github.com/user/repo"
          value={repoPath}
          onChange={setRepoPath}
          required
        />
      )}

      {error && <p className="text-rose-400 text-xs font-mono mt-1.5">{error}</p>}
      
      <Button type="submit" loading={loading} size="lg" className="w-full sm:w-auto shadow-md">
        🚀 Scan Repository
      </Button>
    </form>
  )
}
