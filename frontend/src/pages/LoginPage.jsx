import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LogIn, Lock, Mail, AlertCircle, Eye, EyeOff, Loader2, GraduationCap, ArrowRight, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true);
    try {
      const res = await login(email, password);
      navigate(res.user.role === 'admin' ? '/admin' : from);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to log in. Please check your credentials.');
    } finally { setLoading(false); }
  };

  return (
    <div style={{
      minHeight: 'calc(100vh - 58px)', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      padding: 24, background: 'var(--bg)', position: 'relative', overflow: 'hidden'
    }}>
      {/* Soft glow */}
      <div style={{ position: 'absolute', top: -120, left: '-5%', width: 480, height: 480, borderRadius: '50%', background: 'radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', bottom: -80, right: '0%', width: 360, height: 360, borderRadius: '50%', background: 'radial-gradient(circle, var(--green-muted) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div className="fade-in" style={{ width: '100%', maxWidth: 420, position: 'relative', zIndex: 1 }}>
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--border)',
          borderRadius: 22, padding: '38px 34px',
          boxShadow: 'var(--shadow-lg)'
        }}>
          {/* Logo & Title */}
          <div style={{ textAlign: 'center', marginBottom: 30 }}>
            <div style={{
              width: 54, height: 54, borderRadius: 15, margin: '0 auto 15px',
              background: 'var(--grad-accent)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: 'var(--shadow-accent)'
            }}>
              <GraduationCap size={24} color="#fff" />
            </div>
            <h1 style={{ margin: '0 0 5px', fontSize: 23, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>Welcome back</h1>
            <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary)' }}>Sign in to your CampusAI account</p>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              padding: '10px 13px', borderRadius: 11, marginBottom: 18,
              background: 'var(--danger-muted)', border: '1px solid var(--danger-border)',
              display: 'flex', alignItems: 'center', gap: 8,
              color: 'var(--danger-text)', fontSize: 12.5
            }}>
              <AlertCircle size={14} style={{ flexShrink: 0 }} />{error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
            {/* Email */}
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 7 }}>Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="student@college.edu"
                  className="premium-input" style={{ paddingLeft: 38 }}
                />
              </div>
            </div>
            {/* Password */}
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 7 }}>Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                <input type={showPwd ? 'text' : 'password'} required value={password} onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="premium-input" style={{ paddingLeft: 38, paddingRight: 38 }}
                />
                <button type="button" onClick={() => setShowPwd(!showPwd)}
                  style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 2 }}>
                  {showPwd ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>
            {/* Submit */}
            <button type="submit" disabled={loading}
              className="btn-primary"
              style={{ width: '100%', marginTop: 4, padding: '13px', borderRadius: 13, fontSize: 14, opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}>
              {loading
                ? <><Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> Authenticating...</>
                : <>Sign In <ArrowRight size={14} /></>
              }
            </button>
          </form>

          {/* Demo info */}
          <div style={{
            marginTop: 18, padding: '11px 13px', borderRadius: 11,
            background: 'var(--accent-muted)', border: '1px solid var(--accent-border)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <Sparkles size={12} color="var(--accent)" />
                <span style={{ fontSize: 10.5, fontWeight: 700, color: 'var(--accent-text)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>Demo Credentials</span>
              </div>
              <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Click to fill</span>
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.8, display: 'flex', flexDirection: 'column', gap: 4 }}>
              <button type="button" onClick={() => { setEmail('student_test@college.edu'); setPassword('studentpass123'); setError(''); }}
                style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', cursor: 'pointer', color: 'inherit', fontFamily: 'inherit' }}>
                Student: <code style={{ background: 'var(--bg-input)', color: 'var(--accent-text)', padding: '2px 6px', borderRadius: 4, fontSize: 10.5, border: '1px solid var(--border)' }}>student_test@college.edu</code> / <code style={{ background: 'var(--bg-input)', color: 'var(--accent-text)', padding: '2px 6px', borderRadius: 4, fontSize: 10.5, border: '1px solid var(--border)' }}>studentpass123</code>
              </button>
              <button type="button" onClick={() => { setEmail('admin_test@college.edu'); setPassword('adminpass123'); setError(''); }}
                style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', cursor: 'pointer', color: 'inherit', fontFamily: 'inherit' }}>
                Admin: <code style={{ background: 'var(--bg-input)', color: 'var(--amber-text)', padding: '2px 6px', borderRadius: 4, fontSize: 10.5, border: '1px solid var(--border)' }}>admin_test@college.edu</code> / <code style={{ background: 'var(--bg-input)', color: 'var(--amber-text)', padding: '2px 6px', borderRadius: 4, fontSize: 10.5, border: '1px solid var(--border)' }}>adminpass123</code>
              </button>
            </div>
          </div>

          <div style={{ textAlign: 'center', marginTop: 18, fontSize: 12.5, color: 'var(--text-muted)' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: 'var(--accent)', fontWeight: 700, textDecoration: 'none' }}>Register here →</Link>
          </div>
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
