/**
 * Herald Crypto Exchange - Login/Register Form (FE-15)
 */
import React, { useState } from 'react';

interface Props {
  onLogin: (username: string, password: string) => Promise<void>;
  onRegister: (username: string, password: string, email: string) => Promise<void>;
}

export const LoginForm: React.FC<Props> = ({ onLogin, onRegister }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!username || !password) {
      setError('Username and password required');
      return;
    }
    if (mode === 'register' && !email) {
      setError('Email required');
      return;
    }
    setLoading(true);
    try {
      if (mode === 'login') {
        await onLogin(username, password);
      } else {
        await onRegister(username, password, email);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      height: '100vh', background: 'var(--bg-primary)',
    }}>
      <div style={{
        width: 380, padding: 32, background: 'var(--bg-card)',
        border: '1px solid var(--border)', borderRadius: 12,
      }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent)', marginBottom: 4 }}>
            Herald
          </div>
          <div className="muted" style={{ fontSize: 13 }}>
            Institutional-Grade Crypto Exchange
          </div>
        </div>

        <div style={{ display: 'flex', gap: 4, marginBottom: 20 }}>
          <button
            className={`tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => setMode('login')}
            style={{ flex: 1, textAlign: 'center' }}
          >Login</button>
          <button
            className={`tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => setMode('register')}
            style={{ flex: 1, textAlign: 'center' }}
          >Register</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4, display: 'block' }}>
              Username
            </label>
            <input
              className="input"
              type="text"
              placeholder="Enter username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>

          {mode === 'register' && (
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4, display: 'block' }}>
                Email
              </label>
              <input
                className="input"
                type="email"
                placeholder="Enter email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>
          )}

          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4, display: 'block' }}>
              Password
            </label>
            <input
              className="input"
              type="password"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </div>

          {error && (
            <div style={{
              marginBottom: 12, padding: '8px 12px', borderRadius: 4,
              background: 'rgba(246,70,93,0.1)', color: 'var(--sell)', fontSize: 13,
            }}>{error}</div>
          )}

          <button
            type="submit"
            className="btn btn-accent btn-full"
            disabled={loading}
            style={{ height: 42, fontSize: 15, fontWeight: 600 }}
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Create Account'}
          </button>
        </form>

        <div style={{ marginTop: 16, textAlign: 'center', fontSize: 12, color: 'var(--text-tertiary)' }}>
          Demo: username <strong>demo</strong> / password <strong>herald2026</strong>
        </div>
      </div>
    </div>
  );
};
