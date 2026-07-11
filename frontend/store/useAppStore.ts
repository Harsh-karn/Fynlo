import { create } from 'zustand'

export interface UserProfile {
  id?: string
  name?: string
  email?: string
  phone_number?: string
  currency?: string
  monthly_budget?: number | null
}

interface AppState {
  user: UserProfile | null
  setUser: (user: UserProfile | null) => void
  logout: () => void
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null })
}))
