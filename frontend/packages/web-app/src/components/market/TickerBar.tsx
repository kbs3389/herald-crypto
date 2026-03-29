/**
 * Herald Crypto Exchange - Ticker Bar Component (FE-11)
 */
import React from 'react';
import type { Ticker } from '@herald/shared';

interface Props {
  ticker: Ticker | null;
  instrumentId: string;
}

function formatVolume(vol: string | undefined): string {
  if (!vol) return '0';
  const n = parseFloat(vol);
  if (n >= 1_000_000_000) return (n / 1_000_000_000).toFixed(2) + 'B';
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(2) + 'K';
  return n.toFixed(2);
}

function formatPrice(val: string | null | undefined, digits = 2): string {
  if (!val) return '--';
  const n = parseFloat(val);
  if (isNaN(n)) return '--';
  return n.toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export const TickerBar: React.FC<Props> = ({ ticker, instrumentId }) => {
  const parts = instrumentId.split('-');
  const base = parts[0] || '';
  const quote = parts[1] || '';
  const type = parts[2] || 'SPOT';
  const changePct = ticker?.change_24h_pct ? parseFloat(ticker.change_24h_pct) : 0;
  const isPositive = changePct >= 0;
  const lastPrice = ticker?.last_price || ticker?.best_bid;

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 20,
      padding: '8px 16px', background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border)', fontSize: 12,
      flexWrap: 'wrap',
    }}>
      {/* Pair name */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>
          {base}/{quote}
        </span>
        <span style={{
          fontSize: 10, padding: '1px 5px', borderRadius: 3,
          background: type === 'SPOT' ? 'rgba(14,203,129,0.12)' : type === 'PERP' ? 'rgba(240,185,11,0.12)' : 'rgba(139,92,246,0.12)',
          color: type === 'SPOT' ? 'var(--buy)' : type === 'PERP' ? 'var(--accent)' : '#8b5cf6',
          fontWeight: 600,
        }}>
          {type === 'PERPETUAL' ? 'PERP' : type}
        </span>
      </div>

      {/* Divider */}
      <div style={{ width: 1, height: 24, background: 'var(--border)' }} />

      {/* Last price */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <span className="mono" style={{
          fontWeight: 700, fontSize: 18,
          color: isPositive ? 'var(--buy)' : 'var(--sell)',
        }}>
          {formatPrice(lastPrice)}
        </span>
      </div>

      {/* 24h change */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <span style={{ fontSize: 10, color: 'var(--text-tertiary)', fontWeight: 500 }}>24h Change</span>
        <span className="mono" style={{
          fontWeight: 600, fontSize: 13,
          color: isPositive ? 'var(--buy)' : 'var(--sell)',
        }}>
          {isPositive ? '+' : ''}{changePct.toFixed(2)}%
        </span>
      </div>

      {/* 24h High */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <span style={{ fontSize: 10, color: 'var(--text-tertiary)', fontWeight: 500 }}>24h High</span>
        <span className="mono" style={{ fontSize: 13 }}>
          {formatPrice(ticker?.high_24h)}
        </span>
      </div>

      {/* 24h Low */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <span style={{ fontSize: 10, color: 'var(--text-tertiary)', fontWeight: 500 }}>24h Low</span>
        <span className="mono" style={{ fontSize: 13 }}>
          {formatPrice(ticker?.low_24h)}
        </span>
      </div>

      {/* 24h Volume */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <span style={{ fontSize: 10, color: 'var(--text-tertiary)', fontWeight: 500 }}>24h Vol({base})</span>
        <span className="mono" style={{ fontSize: 13 }}>
          {formatVolume(ticker?.volume_24h)}
        </span>
      </div>

      {/* Bid / Ask */}
      <div style={{ marginLeft: 'auto', display: 'flex', gap: 16 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <span style={{ fontSize: 10, color: 'var(--text-tertiary)', fontWeight: 500 }}>Bid</span>
          <span className="mono buy-text" style={{ fontSize: 13, fontWeight: 600 }}>
            {formatPrice(ticker?.best_bid)}
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <span style={{ fontSize: 10, color: 'var(--text-tertiary)', fontWeight: 500 }}>Ask</span>
          <span className="mono sell-text" style={{ fontSize: 13, fontWeight: 600 }}>
            {formatPrice(ticker?.best_ask)}
          </span>
        </div>
      </div>
    </div>
  );
};
