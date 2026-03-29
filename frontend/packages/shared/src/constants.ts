/**
 * Herald Crypto Exchange - Shared Constants
 */

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

export const SUPPORTED_ASSETS = ['BTC', 'ETH', 'SOL', 'XRP', 'USDT', 'USDC'] as const;

export const INSTRUMENT_ICONS: Record<string, string> = {
  BTC: '₿', ETH: 'Ξ', SOL: '◎', XRP: '✕', USDT: '₮', USDC: '$',
};

export const ORDER_SIDE_COLORS = {
  BUY: { bg: '#0ecb81', text: '#ffffff', light: '#e6f9f0' },
  SELL: { bg: '#f6465d', text: '#ffffff', light: '#fde8eb' },
} as const;

export const PRICE_PRECISION: Record<string, number> = {
  'BTC-USDT-SPOT': 2, 'ETH-USDT-SPOT': 2, 'SOL-USDT-SPOT': 3,
  'XRP-USDT-SPOT': 4, 'BTC-USDT-PERP': 1, 'ETH-USDT-PERP': 2,
};

export const QTY_PRECISION: Record<string, number> = {
  'BTC-USDT-SPOT': 5, 'ETH-USDT-SPOT': 4, 'SOL-USDT-SPOT': 2,
  'XRP-USDT-SPOT': 0, 'BTC-USDT-PERP': 3, 'ETH-USDT-PERP': 2,
};

export const TOKEN_STORAGE_KEY = 'herald_auth_token';
export const USER_STORAGE_KEY = 'herald_user';
export const THEME_STORAGE_KEY = 'herald_theme';

export const WS_RECONNECT_DELAY_MS = 2000;
export const WS_MAX_RECONNECT_ATTEMPTS = 10;
export const ORDERBOOK_DEPTH = 20;
export const RECENT_TRADES_LIMIT = 50;
