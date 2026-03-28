/**
 * Herald Crypto Exchange - Instrument Selector (FE-08)
 */
import React from 'react';
import type { Instrument } from '@herald/shared';

interface Props {
  instruments: Instrument[];
  selected: string;
  onSelect: (id: string) => void;
}

export const InstrumentSelector: React.FC<Props> = ({ instruments, selected, onSelect }) => {
  return (
    <div style={{
      display: 'flex', gap: 4, padding: '8px 16px',
      background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)',
      overflowX: 'auto',
    }}>
      {instruments.map((inst) => {
        const isActive = inst.instrument_id === selected;
        return (
          <button
            key={inst.instrument_id}
            onClick={() => onSelect(inst.instrument_id)}
            style={{
              padding: '6px 12px', borderRadius: 4, fontSize: 12, fontWeight: 500,
              cursor: 'pointer', whiteSpace: 'nowrap', border: 'none',
              background: isActive ? 'var(--bg-tertiary)' : 'transparent',
              color: isActive ? 'var(--accent)' : 'var(--text-secondary)',
              transition: 'all 0.15s',
            }}
          >
            <span>{inst.base_asset}/{inst.quote_asset}</span>
            {inst.best_bid && (
              <span style={{ marginLeft: 8, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                {parseFloat(inst.best_bid).toLocaleString()}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
