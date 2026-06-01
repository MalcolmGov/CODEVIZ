import { create } from 'zustand'
import { RefactoringState, Refactoring } from '@/types'

export const useRefactoringStore = create<RefactoringState>((set) => ({
  opportunities: [],
  selectedOpportunity: null,
  suggestions: {},

  setOpportunities: (opportunities: Refactoring[]) => {
    set({ opportunities })
  },

  selectOpportunity: (opportunity: Refactoring) => {
    set({ selectedOpportunity: opportunity })
  },

  setSuggestion: (index: number, suggestion: any) => {
    set((state) => ({
      suggestions: {
        ...state.suggestions,
        [index]: suggestion,
      },
    }))
  },
}))
