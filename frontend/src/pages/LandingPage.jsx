import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Sparkles, Search, FileText, BookOpen, Zap, GraduationCap, Users, Star } from 'lucide-react';

const FEATURES = [
  { icon: <Search size={20} />, title: "Natural Language Queries", desc: "Ask in plain English — get sourced, precise answers in under 2 seconds.", accentVar: '--accent' },
  { icon: <FileText size={20} />, title: "Source-Verified Answers", desc: "Every answer cites the exact document and page number — zero guesswork.", accentVar: '--green' },
  { icon: <ShieldCheck size={20} />, title: "Zero Hallucinations", desc: "If the answer isn't in official docs, CampusAI says so clearly — no fabricated policies.", accentVar: '--amber' },
  { icon: <Zap size={20} />, title: "Sub-Second Responses", desc: "Embedding cache delivers answers in milliseconds for common queries.", accentVar: '--accent' },
  { icon: <BookOpen size={20} />, title: "Comprehensive Knowledge", desc: "Covers admissions, fees, exams, hostel, library, placements, NSS, NCC and more.", accentVar: '--green' },
  { icon: <Users size={20} />, title: "Student-First Design", desc: "Built specifically for students — understands campus context perfectly.", accentVar: '--amber' },
];

const STATS = [
  { label: "Campus Documents", value: "50+", var: '--accent' },
  { label: "Knowledge Chunks", value: "500+", var: '--green' },
  { label: "Avg Response", value: "<2s", var: '--accent' },
  { label: "Answer Accuracy", value: "99%", var: '--green' },
];

const STEPS = [
  { num: "01", title: "Upload Documents", desc: "Admins upload official PDFs — rule books, circulars, handbooks, fee schedules.", var: '--accent' },
  { num: "02", title: "Vector Indexing", desc: "Text is chunked and embedded into high-dimensional vectors using Gemini Embeddings.", var: '--green' },
  { num: "03", title: "Semantic Search", desc: "Student questions are vectorized and matched against the index in real-time.", var: '--accent' },
  { num: "04", title: "Grounded Answer", desc: "Gemini synthesizes a precise response strictly bounded by retrieved campus documents.", var: '--green' },
];

export default function LandingPage() {
  return (
    <div style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>

      {/* ── HERO ── */}
      <section style={{ position: 'relative', padding: '88px 24px 80px', textAlign: 'center', overflow: 'hidden' }}>
        <div className="hero-grid" style={{ position: 'absolute', inset: 0, opacity: 0.6, zIndex: 0 }} />
        {/* Soft glow blobs */}
        <div style={{ position: 'absolute', top: -120, left: '10%', width: 500, height: 500, borderRadius: '50%', background: 'radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)', pointerEvents: 'none', zIndex: 0 }} />
        <div style={{ position: 'absolute', bottom: -80, right: '5%', width: 360, height: 360, borderRadius: '50%', background: 'radial-gradient(circle, var(--green-muted) 0%, transparent 70%)', pointerEvents: 'none', zIndex: 0 }} />

        <div className="fade-in" style={{ position: 'relative', zIndex: 1, maxWidth: 760, margin: '0 auto' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 7,
            padding: '5px 14px', borderRadius: 99, marginBottom: 26,
            background: 'var(--accent-muted)', border: '1px solid var(--accent-border)',
            color: 'var(--accent-text)', fontSize: 11.5, fontWeight: 700, letterSpacing: '0.04em'
          }}>
            <Sparkles size={11} />
            AI-POWERED CAMPUS KNOWLEDGE BASE
            <span className="status-dot online" style={{ width: 5, height: 5 }} />
          </div>

          <h1 style={{ fontSize: 'clamp(36px, 7vw, 68px)', fontWeight: 900, letterSpacing: '-0.04em', lineHeight: 1.05, margin: '0 0 22px', color: 'var(--text-primary)' }}>
            Your College,{' '}
            <span className="gradient-text">Fully Answered.</span>
          </h1>

          <p style={{ fontSize: 'clamp(14px, 2.5vw, 17px)', color: 'var(--text-secondary)', maxWidth: 520, margin: '0 auto 38px', lineHeight: 1.72 }}>
            CampusAI retrieves verified facts from official college documents and delivers structured, grounded answers in under 2 seconds.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 10 }}>
            <Link to="/register" className="btn-primary" style={{ fontSize: 15, padding: '13px 30px' }}>
              Get Started Free <ArrowRight size={15} />
            </Link>
            <Link to="/login" className="btn-ghost" style={{ fontSize: 15, padding: '13px 30px' }}>
              Log In to Account
            </Link>
          </div>

          <div style={{ marginTop: 30, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
            {[...Array(5)].map((_, i) => <Star key={i} size={13} color="var(--amber)" fill="var(--amber)" />)}
            <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 5 }}>Trusted by students across Kerala campuses</span>
          </div>
        </div>
      </section>

      {/* ── STATS ── */}
      <section style={{ padding: '0 24px 72px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 14 }}>
          {STATS.map((s, i) => (
            <div key={i} className="glass-card" style={{ padding: '22px', textAlign: 'center' }}>
              <div style={{ fontSize: 'clamp(30px, 5vw, 44px)', fontWeight: 900, letterSpacing: '-0.04em', color: `var(${s.var})`, lineHeight: 1 }}>{s.value}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6, fontWeight: 500 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section style={{ padding: '0 24px 88px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 44 }}>
          <div style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--accent)', marginBottom: 10 }}>Under the Hood</div>
          <h2 style={{ margin: 0, fontSize: 'clamp(24px, 4vw, 38px)', fontWeight: 900, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>How RAG Works</h2>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginTop: 10, maxWidth: 440, margin: '10px auto 0', lineHeight: 1.65 }}>A four-step pipeline that guarantees every answer is grounded in verified campus documents.</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
          {STEPS.map((s, i) => (
            <div key={i} className="glass-card" style={{ padding: '26px 22px', borderTop: `2px solid var(${s.var})`, position: 'relative', overflow: 'hidden' }}>
              <div style={{ fontSize: 44, fontWeight: 900, color: `var(${s.var})`, opacity: 0.08, position: 'absolute', top: 10, right: 14, lineHeight: 1, letterSpacing: '-0.05em', pointerEvents: 'none' }}>{s.num}</div>
              <div style={{ width: 34, height: 34, borderRadius: 9, background: `var(${s.var}-muted, var(--accent-muted))`, border: `1px solid var(${s.var}-border, var(--accent-border))`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
                <span style={{ fontSize: 12, fontWeight: 800, color: `var(${s.var})` }}>{s.num}</span>
              </div>
              <h3 style={{ margin: '0 0 7px', fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>{s.title}</h3>
              <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.65 }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section style={{ padding: '0 24px 88px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 44 }}>
          <div style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--green)', marginBottom: 10 }}>Why CampusAI</div>
          <h2 style={{ margin: 0, fontSize: 'clamp(24px, 4vw, 38px)', fontWeight: 900, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>Built Different</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: 14 }}>
          {FEATURES.map((f, i) => (
            <div key={i} className="feature-card">
              <div style={{ width: 42, height: 42, borderRadius: 12, background: 'var(--accent-muted)', border: '1px solid var(--accent-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14, color: `var(${f.accentVar})` }}>
                {f.icon}
              </div>
              <h3 style={{ margin: '0 0 7px', fontSize: 14.5, fontWeight: 700, color: 'var(--text-primary)' }}>{f.title}</h3>
              <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.65 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{ padding: '0 24px 88px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{
          borderRadius: 24, padding: 'clamp(44px, 7vw, 72px) clamp(28px, 6vw, 72px)',
          background: 'var(--bg-card)', border: '1px solid var(--accent-border)',
          textAlign: 'center', position: 'relative', overflow: 'hidden',
          boxShadow: 'var(--shadow-lg)'
        }}>
          <div style={{ position: 'absolute', top: -100, left: '50%', transform: 'translateX(-50%)', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)', pointerEvents: 'none' }} />
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ width: 56, height: 56, borderRadius: 16, background: 'var(--grad-accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', boxShadow: 'var(--shadow-accent)' }}>
              <GraduationCap size={26} color="#fff" />
            </div>
            <h2 style={{ margin: '0 0 12px', fontSize: 'clamp(24px, 4vw, 40px)', fontWeight: 900, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
              Ready to Get <span className="gradient-text">Instant Answers?</span>
            </h2>
            <p style={{ fontSize: 15, color: 'var(--text-secondary)', margin: '0 auto 32px', maxWidth: 440, lineHeight: 1.65 }}>
              Join students getting accurate, grounded answers from official campus documents — for free.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 10 }}>
              <Link to="/register" className="btn-primary" style={{ fontSize: 15, padding: '13px 32px' }}>
                Create Free Account <ArrowRight size={15} />
              </Link>
              <Link to="/login" className="btn-ghost" style={{ fontSize: 15, padding: '13px 32px' }}>Sign In</Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '28px 24px', textAlign: 'center', fontSize: 12, color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7, marginBottom: 7 }}>
          <div style={{ width: 22, height: 22, borderRadius: 6, background: 'var(--grad-accent)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <GraduationCap size={11} color="#fff" />
          </div>
          <span style={{ fontWeight: 700, color: 'var(--text-secondary)' }}>CampusAI</span>
        </div>
        <p style={{ margin: 0 }}>© 2026 CampusAI — RAG-Based College Information Assistant. Powered by Gemini & FastAPI.</p>
      </footer>
    </div>
  );
}
