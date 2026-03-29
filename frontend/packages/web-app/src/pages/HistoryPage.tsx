/**
 * Herald Crypto Exchange - Order History Page
 */
import React from 'react';
import type { OrderResponse } from '@herald/shared';

interface Props {
  orders: OrderResponse[];
}

export const HistoryPage: React.FC<Props> = ({ orders }) => {
  return (
    <div style={{ padding: 16, maxWidth: 1200, margin: '0 auto' }}>
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>Order History</h2>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Instrument</th>
              <th>Side</th>
              <th>Type</th>
              <th className="right">Qty</th>
              <th className="right">Price</th>
              <th className="right">Remaining</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', color: 'var(--text-tertiary)', padding: 24 }}>
                  No orders yet. Place your first order on the Trade page.
                </td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={o.order_id}>
                  <td className="muted" style={{ fontSize: 11 }}>
                    {new Date(o.created_at).toLocaleString()}
                  </td>
                  <td style={{ fontWeight: 500 }}>{o.instrument_id}</td>
                  <td>
                    <span className={o.side === 'BUY' ? 'badge badge-buy' : 'badge badge-sell'}>
                      {o.side}
                    </span>
                  </td>
                  <td className="muted">{o.order_type}</td>
                  <td className="right mono">{parseFloat(o.quantity).toFixed(5)}</td>
                  <td className="right mono">{o.price ? parseFloat(o.price).toFixed(2) : '—'}</td>
                  <td className="right mono">{parseFloat(o.remaining_quantity).toFixed(5)}</td>
                  <td>
                    <span className="badge badge-accent">{o.status}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
