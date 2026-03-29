/**
 * Herald Crypto Exchange - Instrument Selector (FE-08)
 * Groups instruments by type: Spot, Perpetual, Options
 */
import React, { useState } from 'react';
import type { Instrument } from '@herald/shared';

interface Props {
  instruments: Instrument[];
  selected: string;
  onSelect: (id: string) => void;
}

type MarketTab = 'SPOT' | 'PERPETUAL' | 'OPTION';

const TAB_LABELS: Record<MarketTab, string> = {
  SPOT: 'Spot',
  PERPETUAL: 'Perpetuals',
  OPTION: 'Options',
};

export const InstrumentSelector: React.FC<Props> = ({ instruments, selected, onSelect }) => {
  const selectedInst = instruments.find((i) => i.instrument_id === selected);
  const initialTab = (selectedInst?.instrument_type as MarketTab) || 'SPOT';
  const [activeTab, setActiveTab] = useState<MarketTab>(initialTab);

  const grouped: Record<MarketTab, Instrument[]> = { SPOT: [], PERPETUAL: [], OPTION: [] };
  for (const inst of instruments) {
    const t = inst.instrument_type as MarketTab;
    if (grouped[t]) grouped[t].push(inst);
  }

  const tabs: MarketTab[] = (['SPOT', 'PERPETUAL', 'OPTION'] as MarketTab[]).filter(
    (t) => grouped[t].length > 0,
  );

  const filtered = grouped[activeTab] || [];

  const formatLabel = (inst: Instrument) => {
    if (inst.instrument_type === 'OPTION') {
      return `${inst.base_asset} ${inst.strike} ${inst.option_type} ${inst.expiry}`;
    }
    return `${inst.base_asset}/${inst.quote_asset}`;
  };

  return (
    <div style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)' }}>
      {/* Market type tabs */}
      <div style={{ display: 'flex', gap: 0, borderBottom: '1px solid var(--border)' }}>
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 20px', fontSize: 12, fontWeight: 600, cursor: 'pointer',
              border: 'none', borderBottom: activeTab === tab ? '2px solid var(--accent)' : '2px solid transparent',
              background: 'transparent',
              color: activeTab === tab ? 'var(--accent)' : 'var(--text-secondary)',
              transition: 'all 0.15s', textTransform: 'uppercase', letterSpacing: '0.5px',
            }}
          >
            {TAB_LABELS[tab]}
            <span style={{ marginLeft: 6, fontSize: 10, opacity: 0.6 }}>
              {grouped[tab].length}
            </span>
          </button>
        ))}
      </div>
      {/* Instrument buttons */}
      <div style={{ display: 'flex', gap: 4, padding: '8px 16px', overflowX: 'auto' }}>
        {filtered.map((inst) => {
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
              <span>{formatLabel(inst)}</span>
              {inst.best_bid && (
                <span style={{ marginLeft: 8, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                  {parseFloat(inst.best_bid).toLocaleString()}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
