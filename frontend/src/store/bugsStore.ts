import { create } from 'zustand'
import { BugsState, Issue } from '@/types'

export const useBugsStore = create<BugsState>((set) => ({
  bugs: [],
  selectedBug: null,
  filters: {
    severity: undefined,
    type: undefined,
    fixed: false,
  },

  setBugs: (bugs: Issue[]) => {
    set({ bugs })
  },

  setFilter: (filter) => {
    set((state) => ({
      filters: { ...state.filters, ...filter },
    }))
  },

  selectBug: (bug: Issue) => {
    set({ selectedBug: bug })
  },
}))

export const getFilteredBugs = () => {
  const { bugs, filters } = useBugsStore.getState()

  return bugs.filter((bug) => {
    if (filters.severity && bug.severity !== filters.severity) return false
    if (filters.type && bug.type !== filters.type) return false
    if (filters.fixed !== undefined && bug.fixed !== filters.fixed) return false
    return true
  })
}
