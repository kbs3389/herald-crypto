/**
 * Herald Crypto Exchange - Global State Store
 * Lightweight state management without external dependencies.
 */

import { useState, useCallback, useMemo } from 'react';
import type { Instrument, OrderBook, Trade, Balances, OrderResponse, Ticker } from '@herald/shared';

export interface AppState {
  // Auth
  token: string | null;
  userId: string | null;
  username: string | null;
  // Market
  instruments: Instrument[];
  selectedInstrument: string;
  orderBook: OrderBook | null;
  recentTrades: Trade[];
  ticker: Ticker | null;
  // Account
  balances: Balances;
  openOrders: OrderResponse[];
  orderHistory: OrderResponse[];
  // UI
  activeTab: 'trade' | 'portfolio' | 'history';
  orderSide: 'BUY' | 'SELL';
}

const INITIAL_STATE: AppState = {
  token: localStorage.getItem('herald_auth_token'),
  userId: localStorage.getItem('herald_user_id'),
  username: localStorage.getItem('herald_username'),
  instruments: [],
  selectedInstrument: 'BTC-USDT-SPOT',
  orderBook: null,
  recentTrades: [],
  ticker: null,
  balances: {},
  openOrders: [],
  orderHistory: [],
  activeTab: 'trade',
  orderSide: 'BUY',
};

export function useAppState() {
  const [state, setState] = useState<AppState>(INITIAL_STATE);

  const update = useCallback((partial: Partial<AppState>) => {
    setState((prev) => ({ ...prev, ...partial }));
  }, []);

  const login = useCallback((token: string, userId: string, username: string) => {
    localStorage.setItem('herald_auth_token', token);
    localStorage.setItem('herald_user_id', userId);
    localStorage.setItem('herald_username', username);
    setState((prev) => ({ ...prev, token, userId, username }));
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('herald_auth_token');
    localStorage.removeItem('herald_user_id');
    localStorage.removeItem('herald_username');
    setState((prev) => ({
      ...prev, token: null, userId: null, username: null,
      balances: {}, openOrders: [], orderHistory: [],
    }));
  }, []);

  const selectInstrument = useCallback((instrumentId: string) => {
    setState((prev) => ({
      ...prev, selectedInstrument: instrumentId,
      orderBook: null, recentTrades: [], ticker: null,
    }));
  }, []);

  return useMemo(() => ({
    state, update, login, logout, selectInstrument,
  }), [state, update, login, logout, selectInstrument]);
}
