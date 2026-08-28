import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  GraduationCap, LogOut, LayoutDashboard, ShieldCheck,
  MessageSquare, CheckCircle, AlertTriangle, Zap, Sun, Moon
} from 'lucide-react';
import apiClient from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();
  const [backendHealth, setBackendHealth] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    apiClient.get('/health')
      .then(res => { setBackendHealth(res.data); setChecking(false); })
      .catch(() => { setBackendHealth(null); setChecking(false); });
  }, []);

  const handleLogout = async () => { await logout(); navigate('/login'); };

  const isActive = (path) => location.pathname === path ||
    (path !== '/' && location.pathname.startsWith(path));

  return (
    <nav style={{
      background: 'var(--bg-navbar)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderBottom: '1px solid var(--border)',
      position: 'sticky', top: 0, zIndex: 100,
    }}>
      <div style={{
        maxWidth: 1260, margin: '0 auto', padding: '0 20px',
        height: 58, display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>

        {/* ── Logo ── */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 9, textDecoration: 'none' }}>
          <div style={{
            width: 34, height: 34, borderRadius: 9,
            background: 'var(--grad-accent)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: 'var(--shadow-accent)',
          }}>
            <GraduationCap size={17} color="#fff" />
          </div>
          <span style={{
            fontFamily: 'Plus Jakarta Sans, sans-serif', fontWeight: 800,
            fontSize: 17, color: 'var(--text-primary)', letterSpacing: '-0.035em'
          }}>
            Campus<span style={{ color: 'var(--accent)' }}>AI</span>
          </span>
        </Link>

        {/* ── Right Controls ── */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>

          {/* API Status Pill */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 5,
            padding: '4px 10px', borderRadius: 99,
            background: 'var(--bg-card)', border: '1px solid var(--border)',
            fontSize: 11, fontWeight: 600, color: 'var(--text-muted)',
            letterSpacing: '0.02em'
          }}>
            <Zap size={10} color="var(--accent)" />
            <span style={{ color: 'var(--text-secondary)' }}>API</span>
            {checking ? (
              <span style={{ color: 'var(--text-muted)' }}>···</span>
            ) : backendHealth ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--green)' }}>
                <span className="status-dot online" />Online
              </span>
            ) : (
              <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--danger)' }}>
                <span className="status-dot offline" />Offline
              </span>
            )}
          </div>

          {/* Nav Links */}
          {user ? (
            <>
              <NavLink to="/chat" active={isActive('/chat')}>
                <MessageSquare size={13} /> Chat
              </NavLink>
              <NavLink to="/dashboard" active={isActive('/dashboard')}>
                <LayoutDashboard size={13} /> Dashboard
              </NavLink>
              {user.role === 'admin' && (
                <NavLink to="/admin" active={isActive('/admin')}>
                  <ShieldCheck size={13} /> Admin
                </NavLink>
              )}
              <button
                onClick={handleLogout}
                style={{
                  display: 'flex', alignItems: 'center', gap: 5,
                  padding: '6px 12px', borderRadius: 9, cursor: 'pointer',
                  background: 'transparent', border: '1px solid var(--danger-border)',
                  color: 'var(--danger-text)', fontSize: 12.5, fontWeight: 600,
                  transition: 'all 0.18s',
                  fontFamily: 'Plus Jakarta Sans, sans-serif',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'var(--danger-muted)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
              >
                <LogOut size={13} /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Log In</Link>
              <Link to="/register" className="btn-primary" style={{ padding: '7px 16px', fontSize: 13, borderRadius: 9 }}>
                Get Started
              </Link>
            </>
          )}

          {/* Theme Toggle */}
          <button className="theme-toggle" onClick={toggleTheme} title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
            {isDark
              ? <Sun size={15} color="var(--amber)" />
              : <Moon size={15} color="var(--accent)" />
            }
          </button>
        </div>
      </div>
    </nav>
  );
}

function NavLink({ to, active, children }) {
  return (
    <Link
      to={to}
      className={`nav-link ${active ? 'active' : ''}`}
    >
      {children}
    </Link>
  );
}
