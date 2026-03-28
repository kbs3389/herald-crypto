/**
 * Herald Crypto Exchange - Recent Trades Component (FE-11)
 */
import React from 'react';
import type { Trade } from '@herald/shared';

interface Props {
  trades: Trade[];
  instrumentId: string;
}

export const RecentTrades: React.FC<Props> = ({ trades, instrumentId }) => {
  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="card-header">
        <span>Recent Trades</span>
        <span className="muted" style={{ fontSize: 11 }}>{instrumentId}</span>
      </div>
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', padding: '4px 12px',
        fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase',
      }}>
        <span>Price</span>
        <span style={{ textAlign: 'right' }}>Size</span>
        <span style={{ textAlign: 'right' }}>Time</span>
      </div>
      <div style={{ flex: 1, overflow: 'auto' }}>
        {trades.length === 0 ? (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-tertiary)' }}>
            No trades yet
          </div>
        ) : (
          trades.map((trade, i) => (
            <div
              key={trade.fill_id || i}
              style={{
                display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
                padding: '2px 12px', fontSize: 12, fontFamily: 'monospace',
              }}
            >
              <span className={trade.maker_side === 'BUY' ? 'sell-text' : 'buy-text'}>
                {parseFloat(trade.price).toFixed(2)}
              </span>
              <span style={{ textAlign: 'right' }}>
                {parseFloat(trade.quantity).toFixed(5)}
              </span>
              <span style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>
                {new Date(trade.timestamp).toLocaleTimeString('en-US', {
                  hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
                })}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
