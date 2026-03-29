/**
 * Herald Crypto Exchange - Shared Utilities
 */

/** Format a decimal string to fixed precision */
export function formatPrice(value: string | null | undefined, precision = 2): string {
  if (!value) return '—';
  return parseFloat(value).toFixed(precision);
}

/** Format quantity with appropriate precision */
export function formatQuantity(value: string | null | undefined, precision = 4): string {
  if (!value) return '—';
  return parseFloat(value).toFixed(precision);
}

/** Format percentage */
export function formatPercent(value: string | null | undefined): string {
  if (!value) return '0.00%';
  const num = parseFloat(value);
  const sign = num >= 0 ? '+' : '';
  return `${sign}${num.toFixed(2)}%`;
}

/** Format currency with symbol */
export function formatCurrency(value: string | number, currency = 'USD'): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('en-US', {
    style: 'currency', currency, minimumFractionDigits: 2,
  }).format(num);
}

/** Format large numbers with K/M/B suffix */
export function formatCompact(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
  if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
  if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
  return num.toFixed(2);
}

/** Format timestamp to locale string */
export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  });
}

/** Format date + time */
export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    second: '2-digit', hour12: false,
  });
}

/** Calculate mid price from bid/ask */
export function midPrice(bid: string | null, ask: string | null): string | null {
  if (!bid || !ask) return null;
  return ((parseFloat(bid) + parseFloat(ask)) / 2).toString();
}

/** Generate a short client order ID */
export function generateClientOrderId(): string {
  return `cli-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
}

/** Debounce function */
export function debounce<T extends (...args: unknown[]) => void>(fn: T, ms: number): T {
  let timer: ReturnType<typeof setTimeout>;
  return ((...args: unknown[]) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  }) as T;
}

/** Clamp a number between min and max */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}
