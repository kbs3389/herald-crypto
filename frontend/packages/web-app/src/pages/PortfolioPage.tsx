/**
 * Herald Crypto Exchange - Portfolio Page (FE-13)
 */
import React, { useEffect, useState } from 'react';
import type { Balances, Transaction } from '@herald/shared';
import { BalancesView } from '../components/portfolio/BalancesView';
import { useApiClient } from '../hooks/useApi';

interface Props {
  token: string | null;
  balances: Balances;
}

export const PortfolioPage: React.FC<Props> = ({ token, balances }) => {
  const client = useApiClient();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [depositAsset, setDepositAsset] = useState('USDT');
  const [depositAmount, setDepositAmount] = useState('');
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!token) return;
    client.setToken(token);
    client.getTransactions(20)
      .then((res) => setTransactions(res.transactions))
      .catch(() => {});
  }, [token, client]);

  const handleDeposit = async () => {
    if (!depositAmount || parseFloat(depositAmount) <= 0) return;
    client.setToken(token);
    try {
      const res = await client.deposit(depositAsset, depositAmount);
      setMsg(`Deposited ${res.amount} ${res.asset}. New balance: ${res.new_balance}`);
      setDepositAmount('');
      client.getTransactions(20).then((r) => setTransactions(r.transactions)).catch(() => {});
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : 'Deposit failed');
    }
  };

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 1200, margin: '0 auto' }}>
      <h2 style={{ fontSize: 20, fontWeight: 600 }}>Portfolio</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <BalancesView balances={balances} />

        {/* Deposit */}
        <div className="card">
          <div className="card-header">Quick Deposit</div>
          <div style={{ padding: 16 }}>
            <div style={{ marginBottom: 8 }}>
              <label style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4, display: 'block' }}>Asset</label>
              <select className="input" value={depositAsset} onChange={(e) => setDepositAsset(e.target.value)}>
                {['USDT', 'BTC', 'ETH', 'SOL', 'XRP'].map((a) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4, display: 'block' }}>Amount</label>
              <input className="input mono" type="number" step="any" placeholder="0.00"
                value={depositAmount} onChange={(e) => setDepositAmount(e.target.value)} />
            </div>
            {msg && (
              <div style={{ marginBottom: 8, padding: '6px 10px', borderRadius: 4, fontSize: 12,
                background: 'rgba(14,203,129,0.1)', color: 'var(--buy)' }}>{msg}</div>
            )}
            <button className="btn btn-accent btn-full" onClick={handleDeposit}>Deposit</button>
          </div>
        </div>
      </div>

      {/* Transaction History */}
      <div className="card">
        <div className="card-header">Recent Transactions</div>
        <table className="table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Asset</th>
              <th className="right">Amount</th>
              <th className="right">Direction</th>
              <th className="right">Time</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 ? (
              <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-tertiary)', padding: 24 }}>No transactions</td></tr>
            ) : (
              transactions.slice(0, 20).map((tx) => (
                <tr key={tx.entry_id}>
                  <td><span className="badge badge-accent">{tx.type}</span></td>
                  <td style={{ fontWeight: 500 }}>{tx.asset}</td>
                  <td className="right mono">{parseFloat(tx.amount).toLocaleString()}</td>
                  <td className="right">
                    <span className={tx.direction === 'DEBIT' ? 'buy-text' : 'sell-text'}>{tx.direction}</span>
                  </td>
                  <td className="right muted" style={{ fontSize: 11 }}>
                    {new Date(tx.timestamp).toLocaleString()}
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
