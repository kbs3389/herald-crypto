/**
 * Herald Crypto Exchange - Mobile Trade Screen (FE-05/06/07)
 */
import React, { useState } from 'react';

export const TradeScreen: React.FC = () => {
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [price, setPrice] = useState('');
  const [qty, setQty] = useState('');

  return (
    <div style={{ padding: 16, color: '#eaecef' }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>BTC/USDT</h2>
      <div style={{ display: 'flex', gap: 4, marginBottom: 16 }}>
        <button onClick={() => setSide('BUY')} style={{
          flex: 1, padding: 10, border: 'none', borderRadius: 6, fontWeight: 600,
          background: side === 'BUY' ? '#0ecb81' : '#2b3139', color: '#fff', cursor: 'pointer',
        }}>Buy</button>
        <button onClick={() => setSide('SELL')} style={{
          flex: 1, padding: 10, border: 'none', borderRadius: 6, fontWeight: 600,
          background: side === 'SELL' ? '#f6465d' : '#2b3139', color: '#fff', cursor: 'pointer',
        }}>Sell</button>
      </div>
      <div style={{ marginBottom: 12 }}>
        <label style={{ fontSize: 12, color: '#848e9c', display: 'block', marginBottom: 4 }}>Price (USDT)</label>
        <input type="number" step="any" placeholder="0.00" value={price}
          onChange={(e) => setPrice(e.target.value)}
          style={{ width: '100%', padding: 10, background: '#1e2329', border: '1px solid #2b3139',
            borderRadius: 6, color: '#eaecef', fontSize: 16 }} />
      </div>
      <div style={{ marginBottom: 16 }}>
        <label style={{ fontSize: 12, color: '#848e9c', display: 'block', marginBottom: 4 }}>Amount (BTC)</label>
        <input type="number" step="any" placeholder="0.00000" value={qty}
          onChange={(e) => setQty(e.target.value)}
          style={{ width: '100%', padding: 10, background: '#1e2329', border: '1px solid #2b3139',
            borderRadius: 6, color: '#eaecef', fontSize: 16 }} />
      </div>
      <button style={{
        width: '100%', padding: 14, border: 'none', borderRadius: 8, fontSize: 16,
        fontWeight: 700, cursor: 'pointer',
        background: side === 'BUY' ? '#0ecb81' : '#f6465d', color: '#fff',
      }}>{side} BTC</button>
    </div>
  );
};
