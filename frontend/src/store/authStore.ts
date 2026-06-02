import { create } from 'zustand'
import { AuthState, User } from '@/types'
import { useSessionStore } from '@/store/sessionStore'

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  githubToken: undefined,

  login: (user: User, token: string) => {
    localStorage.setItem('github_token', token)
    localStorage.setItem('user', JSON.stringify(user))
    set({
      user,
      isAuthenticated: true,
      githubToken: token,
    })
    // Always start with a clean slate — no stale session from a previous user/repo
    useSessionStore.getState().clearSession()
  },

  logout: () => {
    localStorage.removeItem('github_token')
    localStorage.removeItem('user')
    set({
      user: null,
      isAuthenticated: false,
      githubToken: undefined,
    })
    // Clear the active scan session so a fresh login always starts clean
    useSessionStore.getState().clearSession()
  },

  setUser: (user: User) => {
    set({ user })
  },
}))

// Initialize from localStorage
export const initializeAuth = () => {
  const token = localStorage.getItem('github_token')
  const userStr = localStorage.getItem('user')

  if (token && userStr) {
    try {
      const user = JSON.parse(userStr)
      useAuthStore.getState().login(user, token)
    } catch {
      // Invalid data, clear it
      localStorage.removeItem('github_token')
      localStorage.removeItem('user')
    }
  }
}
