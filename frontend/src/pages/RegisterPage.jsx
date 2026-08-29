import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Mail, Lock, ShieldCheck, AlertCircle, Eye, EyeOff, Loader2, GraduationCap, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [role, setRole] = useState('student');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true);
    try {
      const res = await register(name, email, password, role);
      navigate(res.user.role === 'admin' ? '/admin' : '/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to register. Please check your details.');
    } finally { setLoading(false); }
  };

  return (
    <div style={{
      minHeight: 'calc(100vh - 58px)', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      padding: 24, background: 'var(--bg)', position: 'relative', overflow: 'hidden'
    }}>
      {/* Glow blobs */}
      <div style={{ position: 'absolute', top: -120, left: '-5%', width: 480, height: 480, borderRadius: '50%', background: 'radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', bottom: -80, right: '0%', width: 360, height: 360, borderRadius: '50%', background: 'radial-gradient(circle, var(--green-muted) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div className="fade-in" style={{ width: '100%', maxWidth: 420, position: 'relative', zIndex: 1 }}>
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--border)',
          borderRadius: 22, padding: '38px 34px', boxShadow: 'var(--shadow-lg)'
        }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: 26 }}>
            <div style={{
              width: 54, height: 54, borderRadius: 15, margin: '0 auto 15px',
              background: 'var(--grad-accent)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: 'var(--shadow-accent)'
            }}>
              <GraduationCap size={24} color="#fff" />
            </div>
            <h1 style={{ margin: '0 0 5px', fontSize: 23, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>Create Account</h1>
            <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary)' }}>Join CampusAI and get instant campus answers</p>
          </div>

          {error && (
            <div style={{
              padding: '10px 13px', borderRadius: 11, marginBottom: 16,
              background: 'var(--danger-muted)', border: '1px solid var(--danger-border)',
              display: 'flex', alignItems: 'center', gap: 8, color: 'var(--danger-text)', fontSize: 12.5
            }}>
              <AlertCircle size={14} style={{ flexShrink: 0 }} />{error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 13 }}>
            {/* Name */}
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Full Name</label>
              <div style={{ position: 'relative' }}>
                <User size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                <input type="text" required value={name} onChange={e => setName(e.target.value)} placeholder="Your full name" className="premium-input" style={{ paddingLeft: 38 }} />
              </div>
            </div>
            {/* Email */}
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@college.edu" className="premium-input" style={{ paddingLeft: 38 }} />
              </div>
            </div>
            {/* Password */}
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                <input type={showPwd ? 'text' : 'password'} required minLength={6} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 6 characters" className="premium-input" style={{ paddingLeft: 38, paddingRight: 38 }} />
                <button type="button" onClick={() => setShowPwd(!showPwd)}
                  style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 2 }}>
                  {showPwd ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>
            {/* Role */}
            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
                <ShieldCheck size={12} color="var(--accent)" /> Account Role
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                {[
                  { val: 'student', label: 'Student', emoji: '🎓' },
                  { val: 'admin', label: 'Administrator', emoji: '⚙️' },
                ].map(opt => (
                  <button key={opt.val} type="button" onClick={() => setRole(opt.val)}
                    style={{
                      padding: '11px 8px', borderRadius: 11, cursor: 'pointer',
                      fontFamily: 'Plus Jakarta Sans, sans-serif',
                      background: role === opt.val ? 'var(--accent-muted)' : 'var(--bg)',
                      border: `1px solid ${role === opt.val ? 'var(--accent-border)' : 'var(--border)'}`,
                      color: role === opt.val ? 'var(--accent-text)' : 'var(--text-secondary)',
                      fontSize: 12.5, fontWeight: role === opt.val ? 700 : 500,
                      transition: 'all 0.18s', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5
                    }}>
                    <span style={{ fontSize: 20 }}>{opt.emoji}</span>{opt.label}
                  </button>
                ))}
              </div>
            </div>
            {/* Submit */}
            <button type="submit" disabled={loading}
              className="btn-primary"
              style={{
                width: '100%', marginTop: 4, padding: '13px', borderRadius: 13, fontSize: 14,
                opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer'
              }}>
              {loading
                ? <><Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> Creating Account...</>
                : <>Create Account <ArrowRight size={14} /></>
              }
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 18, fontSize: 12.5, color: 'var(--text-muted)' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--accent)', fontWeight: 700, textDecoration: 'none' }}>Sign in →</Link>
          </div>
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
