import { create } from 'zustand'
import { AuthState, User } from '@/types'

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
  },

  logout: () => {
    localStorage.removeItem('github_token')
    localStorage.removeItem('user')
    set({
      user: null,
      isAuthenticated: false,
      githubToken: undefined,
    })
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
