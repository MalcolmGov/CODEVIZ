import React, { useState } from 'react'
import { TextInput } from '@/components/forms/TextInput'
import { Button } from '@/components/common/Button'
import { useSessionStore } from '@/store/sessionStore'
import { chatService } from '@/services/chat'

export const ScanForm: React.FC<{ onScanComplete: (sessionId: string) => void }> = ({ onScanComplete }) => {
  const [repoPath, setRepoPath] = useState('/Users/malcolmgovender/.gemini/antigravity-ide/scratch/codeviz/backend')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>()
  const { createSession } = useSessionStore()


  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
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

  return (
    <form onSubmit={handleScan} className="space-y-4">
      <TextInput
        label="Repository Path"
        placeholder="/app/src"
        value={repoPath}
        onChange={setRepoPath}
        required
      />
      {error && <p className="text-red-600">{error}</p>}
      <Button type="submit" loading={loading} size="lg">
        🚀 Scan Repository
      </Button>
    </form>
  )
}
