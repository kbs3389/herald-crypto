/**
 * Herald Crypto Exchange - Web Trader App (FE-08)
 * Main application shell with routing and state management.
 */
import React, { useEffect, useState, useCallback } from 'react';
import { Header } from './components/layout/Header';
import { InstrumentSelector } from './components/layout/InstrumentSelector';
import { StatusBar } from './components/common/StatusBar';
import { LoginForm } from './components/auth/LoginForm';
import { TradePage } from './pages/TradePage';
import { PortfolioPage } from './pages/PortfolioPage';
import { HistoryPage } from './pages/HistoryPage';
import { useInstruments, useBalances, useApiClient } from './hooks/useApi';
import { useAppState } from './store/useStore';
import type { OrderResponse } from '@herald/shared';
import './styles/globals.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const App: React.FC = () => {
  const { state, update, login, logout, selectInstrument } = useAppState();
  const { instruments, loading } = useInstruments();
  const { balances, refresh: refreshBalances } = useBalances(state.token);
  const client = useApiClient();
  const [orders, setOrders] = useState<OrderResponse[]>([]);

  useEffect(() => {
    if (instruments.length > 0) {
      update({ instruments });
    }
  }, [instruments, update]);

  // Track orders placed this session
  const addOrder = useCallback((order: OrderResponse) => {
    setOrders((prev) => [order, ...prev]);
    refreshBalances();
  }, [refreshBalances]);

  const handleLogin = useCallback(async (username: string, password: string) => {
    client.setToken(null);
    const res = await client.login({ username, password });
    client.setToken(res.token);
    login(res.token, res.user_id, res.username);
  }, [client, login]);

  const handleRegister = useCallback(async (username: string, password: string, email: string) => {
    client.setToken(null);
    const res = await client.register({ username, password, email });
    client.setToken(res.token);
    login(res.token, res.user_id, res.username);
  }, [client, login]);

  const handleLogout = useCallback(() => {
    client.setToken(null);
    logout();
  }, [client, logout]);

  // Show login if not authenticated
  if (!state.token) {
    return <LoginForm onLogin={handleLogin} onRegister={handleRegister} />;
  }

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        username={state.username}
        onLogout={handleLogout}
        activeTab={state.activeTab}
        onTabChange={(tab) => update({ activeTab: tab })}
      />
      <InstrumentSelector
        instruments={instruments}
        selected={state.selectedInstrument}
        onSelect={selectInstrument}
      />
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {state.activeTab === 'trade' && (
          <TradePage
            instruments={instruments}
            selectedInstrument={state.selectedInstrument}
            token={state.token}
            onSelectInstrument={selectInstrument}
          />
        )}
        {state.activeTab === 'portfolio' && (
          <PortfolioPage token={state.token} balances={balances} />
        )}
        {state.activeTab === 'history' && (
          <HistoryPage orders={orders} />
        )}
      </div>
      <StatusBar apiUrl={API_URL} />
    </div>
  );
};

export default App;
