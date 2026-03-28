/**
 * Herald Crypto Exchange - Ticker Bar Component (FE-11)
 */
import React from 'react';
import type { Ticker } from '@herald/shared';

interface Props {
  ticker: Ticker | null;
  instrumentId: string;
}

export const TickerBar: React.FC<Props> = ({ ticker, instrumentId }) => {
  const parts = instrumentId.split('-');
  const base = parts[0] || '';
  const quote = parts[1] || '';
  const changePct = ticker?.change_24h_pct ? parseFloat(ticker.change_24h_pct) : 0;
  const isPositive = changePct >= 0;

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 24,
      padding: '8px 16px', background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border)', fontSize: 13,
    }}>
      <div>
        <span style={{ fontWeight: 700, fontSize: 16 }}>{base}/{quote}</span>
        <span className="muted" style={{ marginLeft: 8, fontSize: 11 }}>
          {parts[2] || 'SPOT'}
        </span>
      </div>
      <div>
        <span className="muted">Last </span>
        <span className="mono" style={{ fontWeight: 600, fontSize: 15 }}>
          {ticker?.last_price ? parseFloat(ticker.last_price).toLocaleString(undefined, { minimumFractionDigits: 2 }) : '—'}
        </span>
      </div>
      <div>
        <span className="muted">24h </span>
        <span className={isPositive ? 'profit-text' : 'loss-text'} style={{ fontWeight: 500 }}>
          {isPositive ? '+' : ''}{changePct.toFixed(2)}%
        </span>
      </div>
      <div>
        <span className="muted">High </span>
        <span className="mono">
          {ticker?.high_24h ? parseFloat(ticker.high_24h).toLocaleString() : '—'}
        </span>
      </div>
      <div>
        <span className="muted">Low </span>
        <span className="mono">
          {ticker?.low_24h ? parseFloat(ticker.low_24h).toLocaleString() : '—'}
        </span>
      </div>
      <div>
        <span className="muted">Vol </span>
        <span className="mono">
          {ticker?.volume_24h ? parseFloat(ticker.volume_24h).toFixed(4) : '0'}
        </span>
      </div>
      <div>
        <span className="muted">Bid </span>
        <span className="mono buy-text">
          {ticker?.best_bid ? parseFloat(ticker.best_bid).toLocaleString() : '—'}
        </span>
      </div>
      <div>
        <span className="muted">Ask </span>
        <span className="mono sell-text">
          {ticker?.best_ask ? parseFloat(ticker.best_ask).toLocaleString() : '—'}
        </span>
      </div>
    </div>
  );
};
