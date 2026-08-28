import React from 'react';
import Navbar from '../components/Navbar';

export default function MainLayout({ children }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)', color: 'var(--text-primary)', transition: 'background 0.25s, color 0.25s' }}>
      <Navbar />
      <main style={{ flex: 1 }}>
        {children}
      </main>
    </div>
  );
}
