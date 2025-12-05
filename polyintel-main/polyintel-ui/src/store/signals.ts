import { create } from 'zustand';
import { TradeSignal } from '../services/api';

export interface SignalStore {
  signals: TradeSignal[];
  favorites: string[];
  history: TradeSignal[];
  loading: boolean;
  error: string | null;

  addSignal: (signal: TradeSignal) => void;
  removeSignal: (marketId: string) => void;
  toggleFavorite: (marketId: string) => void;
  addToHistory: (signal: TradeSignal) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearSignals: () => void;
  clearHistory: () => void;
  isFavorite: (marketId: string) => boolean;
}

export const useSignalStore = create<SignalStore>((set, get) => ({
  signals: [],
  favorites: JSON.parse(localStorage.getItem('polyintel_favorites') || '[]'),
  history: JSON.parse(localStorage.getItem('polyintel_history') || '[]'),
  loading: false,
  error: null,

  addSignal: (signal: TradeSignal) =>
    set((state) => ({
      signals: [signal, ...state.signals].slice(0, 50), // Keep last 50
    })),

  removeSignal: (marketId: string) =>
    set((state) => ({
      signals: state.signals.filter((s) => s.market_id !== marketId),
    })),

  toggleFavorite: (marketId: string) =>
    set((state) => {
      const isFav = state.favorites.includes(marketId);
      const updated = isFav
        ? state.favorites.filter((id) => id !== marketId)
        : [...state.favorites, marketId];
      localStorage.setItem('polyintel_favorites', JSON.stringify(updated));
      return { favorites: updated };
    }),

  addToHistory: (signal: TradeSignal) =>
    set((state) => {
      const updated = [
        { ...signal, timestamp: new Date().toISOString() },
        ...state.history,
      ].slice(0, 500); // Keep last 500 signals
      localStorage.setItem('polyintel_history', JSON.stringify(updated));
      return { history: updated };
    }),

  setLoading: (loading: boolean) => set({ loading }),
  setError: (error: string | null) => set({ error }),
  clearSignals: () => set({ signals: [] }),

  clearHistory: () => {
    localStorage.removeItem('polyintel_history');
    set({ history: [] });
  },

  isFavorite: (marketId: string) => {
    return get().favorites.includes(marketId);
  },
}));
