/**
 * Herald Crypto Exchange - Order Entry Component (FE-12)
 */
import React, { useState } from 'react';
import type { PlaceOrderRequest, Side } from '@herald/shared';

interface Props {
  instrumentId: string;
  bestBid: string | null;
  bestAsk: string | null;
  onSubmit: (order: PlaceOrderRequest) => Promise<void>;
}

export const OrderEntry: React.FC<Props> = ({ instrumentId, bestBid, bestAsk, onSubmit }) => {
  const [side, setSide] = useState<Side>('BUY');
  const [orderType, setOrderType] = useState<'LIMIT' | 'MARKET'>('LIMIT');
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!quantity || parseFloat(quantity) <= 0) {
      setError('Enter a valid quantity');
      return;
    }
    if (orderType === 'LIMIT' && (!price || parseFloat(price) <= 0)) {
      setError('Enter a valid price');
      return;
    }
    setSubmitting(true);
    try {
      const req: PlaceOrderRequest = {
        instrument_id: instrumentId,
        side,
        order_type: orderType,
        quantity,
        ...(orderType === 'LIMIT' ? { price } : {}),
      };
      await onSubmit(req);
      setSuccess(`${side} order submitted`);
      setQuantity('');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Order failed');
    } finally {
      setSubmitting(false);
    }
  };

  const setPercentage = (pct: number) => {
    // Placeholder - in real app would calculate from balance
    const refPrice = side === 'BUY' ? bestAsk : bestBid;
    if (refPrice) {
      const p = parseFloat(refPrice);
      setPrice(p.toFixed(2));
    }
  };

  const parts = instrumentId.split('-');
  const base = parts[0] || '';
  const quote = parts[1] || '';

  const notional = price && quantity
    ? (parseFloat(price) * parseFloat(quantity)).toFixed(2)
    : '0.00';

  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-header">Place Order</div>
      <div style={{ padding: 16 }}>
        {/* Side selector */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 12 }}>
          <button
            className={`btn btn-full ${side === 'BUY' ? 'btn-buy' : 'btn-outline'}`}
            onClick={() => setSide('BUY')}
            style={{ flex: 1 }}
          >Buy</button>
          <button
            className={`btn btn-full ${side === 'SELL' ? 'btn-sell' : 'btn-outline'}`}
            onClick={() => setSide('SELL')}
            style={{ flex: 1 }}
          >Sell</button>
        </div>

        {/* Order type */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 12 }}>
          {(['LIMIT', 'MARKET'] as const).map((t) => (
            <button
              key={t}
              className={`tab ${orderType === t ? 'active' : ''}`}
              onClick={() => setOrderType(t)}
              style={{ flex: 1, textAlign: 'center' }}
            >{t}</button>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
          {/* Price */}
          {orderType === 'LIMIT' && (
            <div style={{ marginBottom: 8 }}>
              <label style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4, display: 'block' }}>
                Price ({quote})
              </label>
              <input
                className="input mono"
                type="number"
                step="any"
                placeholder="0.00"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
              <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
                {bestBid && (
                  <button type="button" className="btn btn-outline btn-sm" style={{ flex: 1, fontSize: 10 }}
                    onClick={() => setPrice(parseFloat(bestBid).toFixed(2))}>Bid</button>
                )}
                {bestAsk && (
                  <button type="button" className="btn btn-outline btn-sm" style={{ flex: 1, fontSize: 10 }}
                    onClick={() => setPrice(parseFloat(bestAsk).toFixed(2))}>Ask</button>
                )}
              </div>
            </div>
          )}

          {/* Quantity */}
          <div style={{ marginBottom: 8 }}>
            <label style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4, display: 'block' }}>
              Quantity ({base})
            </label>
            <input
              className="input mono"
              type="number"
              step="any"
              placeholder="0.00000"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
            <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
              {[25, 50, 75, 100].map((pct) => (
                <button key={pct} type="button" className="btn btn-outline btn-sm"
                  style={{ flex: 1, fontSize: 10 }}
                  onClick={() => setPercentage(pct)}>
                  {pct}%
                </button>
              ))}
            </div>
          </div>

          {/* Notional */}
          {orderType === 'LIMIT' && price && quantity && (
            <div style={{
              marginBottom: 12, padding: '8px 12px',
              background: 'var(--bg-secondary)', borderRadius: 4,
              display: 'flex', justifyContent: 'space-between', fontSize: 12,
            }}>
              <span className="muted">Total</span>
              <span className="mono">{notional} {quote}</span>
            </div>
          )}

          {/* Error / Success */}
          {error && (
            <div style={{
              marginBottom: 8, padding: '6px 10px', borderRadius: 4, fontSize: 12,
              background: 'rgba(246,70,93,0.1)', color: 'var(--sell)',
            }}>{error}</div>
          )}
          {success && (
            <div style={{
              marginBottom: 8, padding: '6px 10px', borderRadius: 4, fontSize: 12,
              background: 'rgba(14,203,129,0.1)', color: 'var(--buy)',
            }}>{success}</div>
          )}

          {/* Submit */}
          <button
            type="submit"
            className={`btn btn-full ${side === 'BUY' ? 'btn-buy' : 'btn-sell'}`}
            disabled={submitting}
            style={{ height: 40, fontSize: 14, fontWeight: 600 }}
          >
            {submitting ? 'Submitting...' : `${side} ${base}`}
          </button>
        </form>
      </div>
    </div>
  );
};
