/**
 * Herald Crypto Exchange - Header Component (FE-08)
 */
import React from 'react';

interface HeaderProps {
  username: string | null;
  onLogout: () => void;
  activeTab: string;
  onTabChange: (tab: 'trade' | 'portfolio' | 'history') => void;
}

export const Header: React.FC<HeaderProps> = ({ username, onLogout, activeTab, onTabChange }) => {
  return (
    <header style={{
      background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border)',
      padding: '0 16px',
      height: 48,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: 'var(--accent)', fontSize: 20, fontWeight: 700 }}>H</span>
          <span style={{ fontWeight: 600, fontSize: 16 }}>Herald</span>
        </div>
        <nav style={{ display: 'flex', gap: 4 }}>
          {(['trade', 'portfolio', 'history'] as const).map((tab) => (
            <button
              key={tab}
              className={`tab ${activeTab === tab ? 'active' : ''}`}
              onClick={() => onTabChange(tab)}
              style={{ textTransform: 'capitalize' }}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {username && (
          <>
            <span className="muted" style={{ fontSize: 13 }}>{username}</span>
            <button className="btn btn-outline btn-sm" onClick={onLogout}>Logout</button>
          </>
        )}
      </div>
    </header>
  );
};
