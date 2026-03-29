/**
 * Herald Crypto Exchange - API Hooks
 * React hooks for data fetching and mutations.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { HeraldApiClient } from '@herald/api-client';
import type { Instrument, OrderBook, Trade, Balances, Ticker } from '@herald/shared';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const client = new HeraldApiClient(API_URL);

export function useApiClient() {
  return client;
}

export function useInstruments() {
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.getInstruments()
      .then((res) => {
        // API may return array directly or {instruments: [...]}
        const list = Array.isArray(res) ? res : (res.instruments || []);
        setInstruments(list);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return { instruments, loading };
}

export function useOrderBook(instrumentId: string) {
  const [orderBook, setOrderBook] = useState<OrderBook | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const fetch = useCallback(() => {
    if (!instrumentId) return;
    client.getOrderBook(instrumentId, 20)
      .then(setOrderBook)
      .catch(() => {});
  }, [instrumentId]);

  useEffect(() => {
    fetch();
    intervalRef.current = setInterval(fetch, 2000);
    return () => clearInterval(intervalRef.current);
  }, [fetch]);

  return orderBook;
}

export function useRecentTrades(instrumentId: string) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const fetch = useCallback(() => {
    if (!instrumentId) return;
    client.getRecentTrades(instrumentId, 50)
      .then((res) => setTrades(res.trades))
      .catch(() => {});
  }, [instrumentId]);

  useEffect(() => {
    fetch();
    intervalRef.current = setInterval(fetch, 3000);
    return () => clearInterval(intervalRef.current);
  }, [fetch]);

  return trades;
}

export function useTicker(instrumentId: string) {
  const [ticker, setTicker] = useState<Ticker | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const fetch = useCallback(() => {
    if (!instrumentId) return;
    client.getTicker(instrumentId)
      .then(setTicker)
      .catch(() => {});
  }, [instrumentId]);

  useEffect(() => {
    fetch();
    intervalRef.current = setInterval(fetch, 2000);
    return () => clearInterval(intervalRef.current);
  }, [fetch]);

  return ticker;
}

export function useBalances(token: string | null) {
  const [balances, setBalances] = useState<Balances>({});
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const fetch = useCallback(() => {
    if (!token) return;
    client.setToken(token);
    client.getBalances()
      .then((res) => setBalances(res.balances))
      .catch(() => {});
  }, [token]);

  useEffect(() => {
    fetch();
    intervalRef.current = setInterval(fetch, 5000);
    return () => clearInterval(intervalRef.current);
  }, [fetch]);

  return { balances, refresh: fetch };
}
