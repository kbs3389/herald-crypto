/**
 * Herald Crypto Exchange - Balances View Component (FE-13)
 */
import React from 'react';
import type { Balances } from '@herald/shared';

interface Props {
  balances: Balances;
}

const ASSET_ICONS: Record<string, string> = {
  BTC: '₿', ETH: 'Ξ', SOL: '◎', XRP: '✕', USDT: '₮', USDC: '$',
};

export const BalancesView: React.FC<Props> = ({ balances }) => {
  const assets = Object.entries(balances);

  return (
    <div className="card">
      <div className="card-header">
        <span>Balances</span>
        <span className="muted" style={{ fontSize: 11 }}>{assets.length} assets</span>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Asset</th>
            <th className="right">Available</th>
            <th className="right">Reserved</th>
            <th className="right">Total</th>
          </tr>
        </thead>
        <tbody>
          {assets.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-tertiary)', padding: 24 }}>
                No balances
              </td>
            </tr>
          ) : (
            assets.map(([asset, bal]) => (
              <tr key={asset}>
                <td>
                  <span style={{ marginRight: 6 }}>{ASSET_ICONS[asset] || ''}</span>
                  <span style={{ fontWeight: 500 }}>{asset}</span>
                </td>
                <td className="right mono">{parseFloat(bal.available).toLocaleString()}</td>
                <td className="right mono muted">{parseFloat(bal.reserved).toLocaleString()}</td>
                <td className="right mono" style={{ fontWeight: 500 }}>
                  {parseFloat(bal.total).toLocaleString()}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};
