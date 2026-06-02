import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Github, ShieldAlert, AlertCircle, Loader2 } from 'lucide-react'
import { authService } from '@/services/auth'
import { api } from '@/services/api'
import clsx from 'clsx'

const CARD = 'rounded-2xl border border-white/[0.08] bg-slate-surface shadow-card backdrop-blur-md'

export const LoginPage: React.FC = () => {
  const navigate   = useNavigate()
  const { login }  = useAuthStore()

  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState<string | null>(null)
  const [resolving,  setResolving]  = useState(false)

  // Handle OAuth callback — ?token=... lands here after GitHub redirects back
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const token  = params.get('token')
    const err    = params.get('error')

    if (err) {
      setError(err === 'access_denied'
        ? 'GitHub access was denied. Please try again.'
        : `OAuth error: ${err}`)
      // Clean up the URL
      window.history.replaceState({}, '', '/login')
      return
    }

    if (token) {
      setResolving(true)
      api.get('/auth/user', { headers: { Authorization: `Bearer ${token}` } })
        .then(res => {
          login(res.data.data, token)
          navigate('/dashboard')
        })
        .catch(() => {
          setError('Could not retrieve your profile. Please try signing in again.')
          setResolving(false)
          window.history.replaceState({}, '', '/login')
        })
    }
  }, [navigate, login])

  const handleGitHubLogin = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await authService.getGitHubLoginUrl()
      const authUrl  = response.data.data?.auth_url
      if (authUrl) {
        window.location.href = authUrl
        return  // keep spinner going while browser navigates away
      }
      // Backend returned 200 but no auth_url — misconfigured
      setError('GitHub OAuth is not configured on the backend. Check your GITHUB_CLIENT_ID in .env.')
    } catch {
      setError('Cannot reach the backend. Make sure the backend server is running on port 8000.')
    }
    setLoading(false)
  }

  // Show a minimal "resolving profile…" screen while the callback processes
  if (resolving) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center">
        <div className="text-center space-y-3">
          <Loader2 size={28} className="text-indigo-400 animate-spin mx-auto" />
          <p className="text-slate-400 text-sm font-medium">Signing you in…</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#030712] relative overflow-hidden flex items-center justify-center p-4 select-none font-sans">
      {/* Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f29370a_1px,transparent_1px),linear-gradient(to_bottom,#1f29370a_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-violet-500/10 rounded-full blur-[90px] pointer-events-none" />

      <div className={clsx(CARD, "w-full max-w-md relative z-10 p-8 bg-slate-surface/40 backdrop-blur-xl")}>
        <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-t-2xl" />

        <div className="text-center space-y-8">
          <div className="space-y-3">
            <img 
              src="/images/logo.png" 
              alt="CodeViz 3D Logo" 
              className="inline-flex w-12 h-12 rounded-xl object-contain shadow-xl shadow-indigo-500/20 mb-2"
            />
            <h1 className="text-4xl font-black tracking-tight text-slate-100 font-display">
              Code<span className="text-indigo-400 font-medium">Viz</span>
            </h1>
            <p className="text-slate-400 text-sm font-medium">
              AI-Powered Code Analysis & Security Platform
            </p>
          </div>

          <div className="space-y-3 pt-2">
            {/* Error banner */}
            {error && (
              <div className="flex items-start gap-2.5 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-left">
                <AlertCircle size={15} className="text-red-400 mt-0.5 shrink-0" />
                <p className="text-red-300 text-[12px] leading-snug">{error}</p>
              </div>
            )}

            <button
              onClick={handleGitHubLogin}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2.5 py-3 px-5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed text-white text-sm font-semibold tracking-wide transition-all shadow-lg shadow-indigo-500/20"
            >
              {loading
                ? <Loader2 size={16} className="animate-spin" />
                : <Github size={16} />}
              {loading ? 'Redirecting to GitHub…' : 'Sign in with GitHub'}
            </button>

            <p className="text-[11px] text-slate-600 font-mono">
              Secure OAuth · your code never leaves your machine
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
