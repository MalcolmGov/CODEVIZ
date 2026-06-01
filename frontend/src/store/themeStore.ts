import { create } from 'zustand'

interface ThemeStore {
  isDark: boolean
}

// Clear any light mode preference from localStorage
if (typeof window !== 'undefined') {
  localStorage.removeItem('codeviz-theme')
  document.documentElement.classList.remove('light')
  document.documentElement.classList.add('dark')
}

export const useThemeStore = create<ThemeStore>(() => ({
  isDark: true
}))
