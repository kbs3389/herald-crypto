/**
 * Herald Crypto Exchange - Mobile App Shell (FE-05)
 *
 * React Native application shell with tab navigation.
 * Surfaces: iOS (FE-06) and Android (FE-07)
 */
import React, { useState } from 'react';
import { TradeScreen } from './screens/TradeScreen';
import { PortfolioScreen } from './screens/PortfolioScreen';
import { SettingsScreen } from './screens/SettingsScreen';

type Tab = 'trade' | 'portfolio' | 'settings';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('trade');

  const renderScreen = () => {
    switch (activeTab) {
      case 'trade': return <TradeScreen />;
      case 'portfolio': return <PortfolioScreen />;
      case 'settings': return <SettingsScreen />;
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#0b0e11' }}>
      <div style={{ flex: 1, overflow: 'auto' }}>
        {renderScreen()}
      </div>
      <nav style={{
        display: 'flex', borderTop: '1px solid #2b3139', background: '#1e2329',
        padding: '8px 0', paddingBottom: 'env(safe-area-inset-bottom, 8px)',
      }}>
        {([
          { id: 'trade' as Tab, label: 'Trade', icon: '📊' },
          { id: 'portfolio' as Tab, label: 'Portfolio', icon: '💼' },
          { id: 'settings' as Tab, label: 'Settings', icon: '⚙️' },
        ]).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center',
              gap: 2, background: 'none', border: 'none', cursor: 'pointer',
              color: activeTab === tab.id ? '#f0b90b' : '#848e9c',
              fontSize: 10, fontWeight: activeTab === tab.id ? 600 : 400,
            }}
          >
            <span style={{ fontSize: 20 }}>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
};

export default App;
