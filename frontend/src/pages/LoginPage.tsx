import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/common/Button'
import { Card } from '@/components/common/Card'
import { useAuthStore } from '@/store/authStore'
import { Github, ShieldAlert, Terminal } from 'lucide-react'
import { authService } from '@/services/auth'
import { api } from '@/services/api'

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login } = useAuthStore()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const token = params.get('token')
    
    if (token) {
      const fetchProfileAndLogin = async () => {
        try {
          // Get user details from backend using the real/mock token
          const response = await api.get('/auth/user', {
            headers: { Authorization: `Bearer ${token}` }
          })
          const userProfile = response.data.data
          login(userProfile, token)
          navigate('/dashboard')
        } catch (err) {
          console.error('OAuth profile retrieval failed:', err)
        }
      }
      
      fetchProfileAndLogin()
    }
  }, [navigate, login])

  const handleGitHubLogin = async () => {
    try {
      const response = await authService.getGitHubLoginUrl()
      const authUrl = response.data.data?.auth_url
      if (authUrl) {
        window.location.href = authUrl
        return
      }
    } catch (err) {
      console.warn('GitHub OAuth not configured on backend, falling back to Sandbox development login...', err)
    }

    // Fallback Mock OAuth Login for Sandbox Dev environment
    const mockUser = { id: 1, email: 'malcolm@example.com', name: 'Malcolm Govender' }
    login(mockUser, 'mock_token_123')
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-[#030712] relative overflow-hidden flex items-center justify-center p-4 select-none font-sans">
      {/* Decorative Grids and Light Rings */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f29370a_1px,transparent_1px),linear-gradient(to_bottom,#1f29370a_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-violet-500/10 rounded-full blur-[90px] pointer-events-none" />

      <Card className="w-full max-w-md relative z-10 p-8 border-slate-border/60 bg-slate-surface/40 backdrop-blur-xl shadow-2xl">
        {/* Glow accent bar at top of card */}
        <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />
        
        <div className="text-center space-y-8">
          <div className="space-y-3">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-600 text-white shadow-xl shadow-indigo-500/20 mb-2">
              <ShieldAlert size={24} />
            </div>
            <h1 className="text-4xl font-black tracking-tight text-slate-100 font-display">
              Code<span className="text-indigo-400 font-medium">Viz</span>
            </h1>
            <p className="text-slate-400 text-sm font-medium">
              Enterprise AI Vulnerability Scanner & Refactoring Engine
            </p>
          </div>

          <div className="space-y-4 pt-2">
            <Button 
              onClick={handleGitHubLogin} 
              variant="primary" 
              size="lg" 
              icon={Github} 
              className="w-full flex items-center justify-center py-3 text-sm font-semibold tracking-wide"
            >
              Sign In with GitHub
            </Button>
            
            <p className="text-[11px] text-slate-500 flex items-center justify-center gap-1.5 font-mono">
              <Terminal size={12} /> secure OAuth handshake sandbox
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}

