/**
 * Herald Crypto Exchange - Shared Type Definitions
 * Used across all frontend surfaces (web, mobile, desktop)
 */

// ── Enums ────────────────────────────────────────────────────────────

export type Side = 'BUY' | 'SELL';
export type OrderType = 'LIMIT' | 'MARKET' | 'STOP_LIMIT' | 'STOP_MARKET';
export type TimeInForce = 'GTC' | 'IOC' | 'FOK' | 'GTD' | 'DAY';
export type OrderStatus = 'PENDING' | 'ACCEPTED' | 'PARTIALLY_FILLED' | 'FILLED' | 'CANCELLED' | 'REJECTED' | 'EXPIRED';
export type InstrumentType = 'SPOT' | 'PERPETUAL' | 'FUTURE' | 'OPTION';
export type KycLevel = 'NONE' | 'BASIC' | 'INTERMEDIATE' | 'ADVANCED' | 'INSTITUTIONAL';

// ── Market Data ──────────────────────────────────────────────────────

export interface Instrument {
  instrument_id: string;
  base_asset: string;
  quote_asset: string;
  instrument_type: InstrumentType;
  tick_size: string;
  lot_size: string;
  best_bid: string | null;
  best_ask: string | null;
  spread: string | null;
  // Option-specific fields
  strike?: string;
  expiry?: string;
  option_type?: 'CALL' | 'PUT';
}

export interface OrderBookLevel {
  price: string;
  quantity: string;
  orders: number;
}

export interface OrderBook {
  instrument_id: string;
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  best_bid: string | null;
  best_ask: string | null;
  spread: string | null;
  timestamp: string;
}

export interface Trade {
  fill_id: string;
  price: string;
  quantity: string;
  maker_side: Side;
  timestamp: string;
}

export interface Ticker {
  instrument_id: string;
  best_bid: string | null;
  best_ask: string | null;
  last_price: string | null;
  volume_24h: string;
  high_24h: string | null;
  low_24h: string | null;
  change_24h_pct: string;
  timestamp: string;
}

export interface Kline {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ── Trading ──────────────────────────────────────────────────────────

export interface PlaceOrderRequest {
  instrument_id: string;
  side: Side;
  order_type: OrderType;
  quantity: string;
  price?: string;
  time_in_force?: TimeInForce;
  client_order_id?: string;
}

export interface OrderFill {
  fill_id: string;
  price: string;
  quantity: string;
  maker_side: Side;
  timestamp: string;
}

export interface OrderResponse {
  order_id: string;
  instrument_id: string;
  side: Side;
  order_type: OrderType;
  quantity: string;
  price: string | null;
  status: string;
  fills: OrderFill[];
  remaining_quantity: string;
  created_at: string;
}

// ── Account ──────────────────────────────────────────────────────────

export interface Balance {
  available: string;
  reserved: string;
  total: string;
}

export interface Balances {
  [asset: string]: Balance;
}

export interface Transaction {
  entry_id: string;
  asset: string;
  amount: string;
  direction: 'DEBIT' | 'CREDIT';
  type: string;
  timestamp: string;
}

// ── Auth ─────────────────────────────────────────────────────────────

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email: string;
}

export interface AuthResponse {
  token: string;
  user_id: string;
  username: string;
}

export interface User {
  user_id: string;
  username: string;
  email?: string;
  kyc_level: KycLevel;
  is_active: boolean;
}

// ── Notifications ────────────────────────────────────────────────────

export interface Notification {
  notification_id: string;
  notification_type: string;
  channel: string;
  priority: string;
  title: string;
  body: string;
  data: Record<string, unknown>;
  read: boolean;
  created_at: string;
}

export interface PriceAlert {
  alert_id: string;
  instrument_id: string;
  condition: 'ABOVE' | 'BELOW';
  target_price: string;
  is_active: boolean;
  triggered: boolean;
  created_at: string;
}

// ── WebSocket Messages ───────────────────────────────────────────────

export interface WsTradeMessage {
  type: 'trade';
  instrument_id: string;
  trades: Trade[];
  timestamp: string;
}

export interface WsOrderBookMessage {
  type: 'orderbook';
  instrument_id: string;
  data: OrderBook;
  timestamp: string;
}

export type WsMessage = WsTradeMessage | WsOrderBookMessage;

// ── System ───────────────────────────────────────────────────────────

export interface HealthStatus {
  status: string;
  timestamp: string;
  instruments: number;
  ledger_entries: number;
  journal_entries: number;
}

export interface SystemStats {
  instruments: number;
  ledger_entries: number;
  ledger_transactions: number;
  journal_entries: number;
  journal_sequence: number;
  registered_users: number;
  timestamp: string;
}
