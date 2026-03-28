/**
 * Herald Crypto Exchange - API Client (FE-02)
 *
 * Typed REST client for all exchange endpoints.
 * Handles authentication, error handling, and request/response typing.
 */

import type {
  AuthResponse, Balances, HealthStatus, Instrument, LoginRequest,
  OrderBook, OrderResponse, PlaceOrderRequest, RegisterRequest,
  SystemStats, Ticker, Trade, Transaction,
} from '@herald/shared';

const DEFAULT_BASE = 'http://localhost:8000';

export class HeraldApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || DEFAULT_BASE;
  }

  setToken(token: string | null): void {
    this.token = token;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const init: RequestInit = { method, headers: this.headers() };
    if (body) init.body = JSON.stringify(body);
    const res = await fetch(url, init);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(res.status, err.detail || 'Request failed');
    }
    return res.json();
  }

  // ── Auth ───────────────────────────────────────────────────────────
  async login(req: LoginRequest): Promise<AuthResponse> {
    return this.request('POST', '/api/v1/auth/login', req);
  }

  async register(req: RegisterRequest): Promise<AuthResponse> {
    return this.request('POST', '/api/v1/auth/register', req);
  }

  // ── Market Data ────────────────────────────────────────────────────
  async getInstruments(): Promise<{ instruments: Instrument[] }> {
    return this.request('GET', '/api/v1/instruments');
  }

  async getOrderBook(instrumentId: string, depth = 20): Promise<OrderBook> {
    return this.request('GET', `/api/v1/market/${instrumentId}/orderbook?depth=${depth}`);
  }

  async getRecentTrades(instrumentId: string, limit = 50): Promise<{ instrument_id: string; trades: Trade[] }> {
    return this.request('GET', `/api/v1/market/${instrumentId}/trades?limit=${limit}`);
  }

  async getTicker(instrumentId: string): Promise<Ticker> {
    return this.request('GET', `/api/v1/market/${instrumentId}/ticker`);
  }

  // ── Trading ────────────────────────────────────────────────────────
  async placeOrder(req: PlaceOrderRequest): Promise<OrderResponse> {
    return this.request('POST', '/api/v1/orders', req);
  }

  async cancelOrder(orderId: string, instrumentId: string): Promise<{ order_id: string; status: string }> {
    return this.request('DELETE', `/api/v1/orders/${orderId}?instrument_id=${instrumentId}`);
  }

  // ── Account ────────────────────────────────────────────────────────
  async getBalances(): Promise<{ balances: Balances }> {
    return this.request('GET', '/api/v1/account/balances');
  }

  async deposit(asset: string, amount: string): Promise<{ status: string; asset: string; amount: string; new_balance: string }> {
    return this.request('POST', '/api/v1/account/deposit', { asset, amount });
  }

  async withdraw(asset: string, amount: string): Promise<{ status: string; asset: string; amount: string; new_balance: string }> {
    return this.request('POST', '/api/v1/account/withdraw', { asset, amount });
  }

  async getTransactions(limit = 50): Promise<{ transactions: Transaction[] }> {
    return this.request('GET', `/api/v1/account/transactions?limit=${limit}`);
  }

  // ── Risk ───────────────────────────────────────────────────────────
  async getRiskParams(instrumentId: string): Promise<Record<string, string>> {
    return this.request('GET', `/api/v1/risk/parameters/${instrumentId}`);
  }

  // ── System ─────────────────────────────────────────────────────────
  async getHealth(): Promise<HealthStatus> {
    return this.request('GET', '/api/v1/health');
  }

  async getStats(): Promise<SystemStats> {
    return this.request('GET', '/api/v1/system/stats');
  }
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const apiClient = new HeraldApiClient();
