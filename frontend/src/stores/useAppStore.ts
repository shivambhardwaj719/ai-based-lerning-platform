import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'student' | 'admin';
  rating: number;
  xp?: number;
  streak?: number;
  level?: number;
}

interface AppState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  theme: 'light' | 'dark' | 'system';
  isSidebarOpen: boolean;
  commandPaletteOpen: boolean;

  setUser: (user: UserProfile | null) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  logout: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      theme: 'dark',
      isSidebarOpen: true,
      commandPaletteOpen: false,

      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      setSidebarOpen: (open) => set({ isSidebarOpen: open }),
      setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
      logout: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'nexuslearn-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        theme: state.theme,
        isSidebarOpen: state.isSidebarOpen,
      }),
    }
  )
);
