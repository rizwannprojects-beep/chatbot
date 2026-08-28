import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, BookOpen, Sparkles, Loader2, GraduationCap, TrendingUp, Zap, ArrowRight, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getUserConversations } from '../services/chat';

const CATEGORIES = [
  { title: 'Admissions', emoji: '🎓', desc: 'Certificates, deadlines & requirements' },
  { title: 'Examinations', emoji: '📝', desc: 'Semester schedules & grading rules' },
  { title: 'Hostel & Housing', emoji: '🏠', desc: 'Curfew times & check-in guidelines' },
  { title: 'Library Services', emoji: '📚', desc: 'Textbook borrowing & quiet hours' },
  { title: 'Fee Structure', emoji: '💰', desc: 'Tuition, hostel fees & scholarships' },
  { title: 'Placements', emoji: '💼', desc: 'Campus recruitment & career guidance' },
];

const QUICK_ASKS = [
  { label: 'Admission process 2026', emoji: '🎓' },
  { label: 'Hostel rules & curfew', emoji: '🏠' },
  { label: 'Exam schedule', emoji: '📝' },
  { label: 'Fee structure', emoji: '💰' },
  { label: 'Placement stats', emoji: '📈' },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUserConversations()
      .then(d => { setConversations(d || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const greet = () => {
    const h = new Date().getHours();
    return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
  };

  const METRICS = [
    { icon: <MessageSquare size={17} color="var(--accent)" />, label: 'Chat Threads', value: loading ? null : conversations.length },
    { icon: <BookOpen size={17} color="var(--green)" />, label: 'Knowledge Docs', value: '50+' },
    { icon: <Zap size={17} color="var(--amber)" />, label: 'Avg Response', value: '<2s' },
    { icon: <TrendingUp size={17} color="var(--accent)" />, label: 'Role', value: user?.role === 'admin' ? 'Admin' : 'Student' },
  ];

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '28px 22px', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>

      {/* ── WELCOME ── */}
      <div className="fade-in" style={{
        display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between',
        gap: 18, marginBottom: 24,
        padding: '24px 28px',
        background: 'var(--bg-card)',
        border: '1px solid var(--accent-border)',
        borderRadius: 18,
        boxShadow: 'var(--shadow-sm)',
        position: 'relative', overflow: 'hidden'
      }}>
        <div style={{ position: 'absolute', top: -80, right: -40, width: 280, height: 280, borderRadius: '50%', background: 'radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)', pointerEvents: 'none' }} />
        <div style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ width: 46, height: 46, borderRadius: 13, background: 'var(--grad-accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'var(--shadow-accent)', flexShrink: 0 }}>
            <User size={20} color="#fff" />
          </div>
          <div>
            <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>{greet()},</p>
            <h1 style={{ margin: 0, fontSize: 20, fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
              {user?.name || 'Student'} 👋
            </h1>
            <p style={{ margin: 0, fontSize: 12.5, color: 'var(--text-secondary)', marginTop: 2 }}>Your campus knowledge assistant is ready.</p>
          </div>
        </div>
        <Link to="/chat" className="btn-primary" style={{ fontSize: 13, padding: '10px 20px', position: 'relative', zIndex: 1 }}>
          <MessageSquare size={13} /> Open Campus Chat <ArrowRight size={13} />
        </Link>
      </div>

      {/* ── METRICS ── */}
      <div className="fade-in" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 12, marginBottom: 20 }}>
        {METRICS.map((m, i) => (
          <div key={i} className="glass-card" style={{ padding: '18px 20px' }}>
            <div style={{ marginBottom: 10 }}>{m.icon}</div>
            <div style={{ fontSize: 28, fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.04em', lineHeight: 1 }}>
              {m.value === null ? <div className="shimmer" style={{ width: 36, height: 28, borderRadius: 7 }} /> : m.value}
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 5, fontWeight: 500 }}>{m.label}</div>
          </div>
        ))}
      </div>

      {/* ── GRID ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.5fr)', gap: 14, marginBottom: 16 }}>

        {/* Recent Conversations */}
        <div className="fade-in glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <h2 style={{ margin: 0, fontSize: 13.5, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <MessageSquare size={13} color="var(--accent)" /> Recent Chats
            </h2>
            <Link to="/chat" style={{ fontSize: 11, color: 'var(--accent)', textDecoration: 'none', fontWeight: 700 }}>View all →</Link>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
            {loading
              ? [1, 2, 3].map(i => <div key={i} className="shimmer" style={{ height: 42, borderRadius: 9 }} />)
              : conversations.length === 0
                ? (
                  <div style={{ padding: '28px 0', textAlign: 'center' }}>
                    <div style={{ fontSize: 30, marginBottom: 8 }}>💬</div>
                    <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0 }}>No chats yet.</p>
                    <Link to="/chat" style={{ fontSize: 12, color: 'var(--accent)', fontWeight: 700, textDecoration: 'none', display: 'block', marginTop: 7 }}>Start your first chat →</Link>
                  </div>
                )
                : conversations.slice(0, 5).map(conv => (
                  <Link key={conv.id} to="/chat" style={{ textDecoration: 'none' }}>
                    <div style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: '9px 11px', borderRadius: 9,
                      background: 'var(--bg)', border: '1px solid var(--border)', transition: 'all 0.15s'
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-border)'; e.currentTarget.style.background = 'var(--accent-muted)'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--bg)'; }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 7, minWidth: 0, flex: 1 }}>
                        <MessageSquare size={11} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                        <span style={{ fontSize: 12, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{conv.title || 'Untitled Chat'}</span>
                      </div>
                      <span style={{ fontSize: 10.5, color: 'var(--text-muted)', flexShrink: 0, marginLeft: 8 }}>
                        {new Date(conv.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </Link>
                ))
            }
          </div>
        </div>

        {/* Knowledge Categories */}
        <div className="fade-in glass-card" style={{ padding: '20px' }}>
          <h2 style={{ margin: '0 0 13px', fontSize: 13.5, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Sparkles size={13} color="var(--green)" /> Knowledge Base
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {CATEGORIES.map((cat, i) => (
              <Link key={i} to="/chat" className="cat-card">
                <span style={{ fontSize: 20, display: 'block', marginBottom: 5 }}>{cat.emoji}</span>
                <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 3 }}>{cat.title}</div>
                <div style={{ fontSize: 10.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{cat.desc}</div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* ── QUICK ASKS ── */}
      <div className="fade-in glass-card" style={{ padding: '18px 20px' }}>
        <h2 style={{ margin: '0 0 12px', fontSize: 13.5, fontWeight: 700, color: 'var(--text-primary)' }}>Quick Questions</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {QUICK_ASKS.map((a, i) => (
            <Link key={i} to="/chat" style={{ textDecoration: 'none' }}>
              <button style={{
                padding: '7px 13px', borderRadius: 9, cursor: 'pointer',
                background: 'var(--bg)', border: '1px solid var(--border)',
                color: 'var(--text-secondary)', fontSize: 12, fontWeight: 500,
                display: 'flex', alignItems: 'center', gap: 6,
                fontFamily: 'Plus Jakarta Sans, sans-serif', transition: 'all 0.18s'
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-border)'; e.currentTarget.style.color = 'var(--accent-text)'; e.currentTarget.style.background = 'var(--accent-muted)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.background = 'var(--bg)'; }}
              >
                <span>{a.emoji}</span> {a.label}
              </button>
            </Link>
          ))}
        </div>
      </div>

    </div>
  );
}
