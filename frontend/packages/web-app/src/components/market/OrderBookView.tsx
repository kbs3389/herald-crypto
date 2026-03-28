/**
 * Herald Crypto Exchange - Order Book Component (FE-11)
 */
import React from 'react';
import type { OrderBook } from '@herald/shared';

interface Props {
  orderBook: OrderBook | null;
  onPriceClick?: (price: string) => void;
}

export const OrderBookView: React.FC<Props> = ({ orderBook, onPriceClick }) => {
  if (!orderBook) {
    return (
      <div className="card" style={{ height: '100%' }}>
        <div className="card-header">Order Book</div>
        <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-tertiary)' }}>
          Loading...
        </div>
      </div>
    );
  }

  const maxQty = Math.max(
    ...orderBook.asks.map((l) => parseFloat(l.quantity)),
    ...orderBook.bids.map((l) => parseFloat(l.quantity)),
    0.001,
  );

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="card-header">
        <span>Order Book</span>
        {orderBook.spread && (
          <span className="muted" style={{ fontSize: 11 }}>
            Spread: {parseFloat(orderBook.spread).toFixed(2)}
          </span>
        )}
      </div>
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {/* Column headers */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', padding: '4px 12px',
          fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase',
        }}>
          <span>Price</span>
          <span style={{ textAlign: 'right' }}>Size</span>
          <span style={{ textAlign: 'right' }}>Total</span>
        </div>

        {/* Asks (reversed so lowest ask is at bottom) */}
        <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
          {[...orderBook.asks].reverse().slice(0, 15).map((level, i) => {
            const pct = (parseFloat(level.quantity) / maxQty) * 100;
            return (
              <div
                key={`ask-${i}`}
                onClick={() => onPriceClick?.(level.price)}
                style={{
                  display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
                  padding: '2px 12px', fontSize: 12, cursor: 'pointer',
                  position: 'relative', fontFamily: 'monospace',
                }}
              >
                <div style={{
                  position: 'absolute', right: 0, top: 0, bottom: 0,
                  width: `${pct}%`, background: 'rgba(246,70,93,0.08)',
                }} />
                <span className="sell-text">{parseFloat(level.price).toFixed(2)}</span>
                <span style={{ textAlign: 'right' }}>{parseFloat(level.quantity).toFixed(5)}</span>
                <span style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>
                  {level.orders}
                </span>
              </div>
            );
          })}
        </div>

        {/* Spread / mid price */}
        <div style={{
          padding: '6px 12px', borderTop: '1px solid var(--border)',
          borderBottom: '1px solid var(--border)', textAlign: 'center',
          fontSize: 16, fontWeight: 600, fontFamily: 'monospace',
        }}>
          {orderBook.best_bid && orderBook.best_ask
            ? ((parseFloat(orderBook.best_bid) + parseFloat(orderBook.best_ask)) / 2).toFixed(2)
            : '—'}
        </div>

        {/* Bids */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          {orderBook.bids.slice(0, 15).map((level, i) => {
            const pct = (parseFloat(level.quantity) / maxQty) * 100;
            return (
              <div
                key={`bid-${i}`}
                onClick={() => onPriceClick?.(level.price)}
                style={{
                  display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
                  padding: '2px 12px', fontSize: 12, cursor: 'pointer',
                  position: 'relative', fontFamily: 'monospace',
                }}
              >
                <div style={{
                  position: 'absolute', right: 0, top: 0, bottom: 0,
                  width: `${pct}%`, background: 'rgba(14,203,129,0.08)',
                }} />
                <span className="buy-text">{parseFloat(level.price).toFixed(2)}</span>
                <span style={{ textAlign: 'right' }}>{parseFloat(level.quantity).toFixed(5)}</span>
                <span style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>
                  {level.orders}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
