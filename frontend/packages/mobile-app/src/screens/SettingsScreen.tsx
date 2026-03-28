/**
 * Herald Crypto Exchange - Mobile Settings Screen (FE-05)
 */
import React from 'react';

export const SettingsScreen: React.FC = () => {
  return (
    <div style={{ padding: 16, color: '#eaecef' }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Settings</h2>
      {[
        { label: 'Account', desc: 'Profile, KYC verification' },
        { label: 'Security', desc: '2FA, password, sessions' },
        { label: 'Notifications', desc: 'Push, email, price alerts' },
        { label: 'Appearance', desc: 'Theme, language' },
        { label: 'About', desc: 'Version 0.1.0' },
      ].map((item) => (
        <div key={item.label} style={{
          padding: '14px 0', borderBottom: '1px solid #2b3139',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <div>
            <div style={{ fontWeight: 500 }}>{item.label}</div>
            <div style={{ fontSize: 12, color: '#848e9c' }}>{item.desc}</div>
          </div>
          <span style={{ color: '#848e9c' }}>›</span>
        </div>
      ))}
    </div>
  );
};
