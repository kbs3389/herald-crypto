/**
 * Herald Crypto Exchange - Status Bar Component
 */
import React, { useEffect, useState } from 'react';
import type { HealthStatus } from '@herald/shared';

interface Props {
  apiUrl: string;
}

export const StatusBar: React.FC<Props> = ({ apiUrl }) => {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    const fetchHealth = () => {
      fetch(`${apiUrl}/api/v1/health`)
        .then((r) => r.json())
        .then(setHealth)
        .catch(() => setHealth(null));
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '4px 16px', background: 'var(--bg-secondary)',
      borderTop: '1px solid var(--border)', fontSize: 11,
      color: 'var(--text-tertiary)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{
          width: 6, height: 6, borderRadius: '50%',
          background: health ? 'var(--buy)' : 'var(--sell)',
        }} />
        <span>{health ? 'Connected' : 'Disconnected'}</span>
      </div>
      {health && (
        <div style={{ display: 'flex', gap: 16 }}>
          <span>Instruments: {health.instruments}</span>
          <span>Ledger: {health.ledger_entries}</span>
          <span>Journal: {health.journal_entries}</span>
        </div>
      )}
      <span>Herald Exchange v0.1.0</span>
    </div>
  );
};
