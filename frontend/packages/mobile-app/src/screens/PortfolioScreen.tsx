/**
 * Herald Crypto Exchange - Mobile Portfolio Screen (FE-05)
 */
import React from 'react';

export const PortfolioScreen: React.FC = () => {
  return (
    <div style={{ padding: 16, color: '#eaecef' }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Portfolio</h2>
      <div style={{ background: '#1e2329', borderRadius: 8, padding: 16, marginBottom: 12 }}>
        <div style={{ fontSize: 12, color: '#848e9c', marginBottom: 4 }}>Total Balance</div>
        <div style={{ fontSize: 28, fontWeight: 700, color: '#f0b90b' }}>$0.00</div>
      </div>
      {['BTC', 'ETH', 'SOL', 'USDT'].map((asset) => (
        <div key={asset} style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '12px 0', borderBottom: '1px solid #2b3139',
        }}>
          <div>
            <div style={{ fontWeight: 500 }}>{asset}</div>
            <div style={{ fontSize: 12, color: '#848e9c' }}>0.00</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div>$0.00</div>
          </div>
        </div>
      ))}
    </div>
  );
};
