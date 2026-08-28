import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  sendChatMessage, getUserConversations, getConversationMessages,
  deleteConversation, submitFeedback
} from '../services/chat';
import {
  Send, Bot, User, BookOpen, Sparkles, AlertCircle, FileText,
  ChevronDown, ChevronUp, Plus, MessageSquare, Trash2,
  ThumbsUp, ThumbsDown, CheckCircle2, GraduationCap
} from 'lucide-react';

const SUGGESTED = [
  { q: "What is the admission process for 2026?", icon: "🎓", cat: "Admissions" },
  { q: "What are the hostel rules and curfew times?", icon: "🏠", cat: "Hostel" },
  { q: "When do end semester examinations start?", icon: "📝", cat: "Exams" },
  { q: "What is the library borrowing policy?", icon: "📚", cat: "Library" },
  { q: "What is the fee structure and scholarships?", icon: "💰", cat: "Fees" },
  { q: "What are the campus placement statistics?", icon: "💼", cat: "Placements" },
];

/* ── Simple Markdown Renderer ── */
function Markdown({ text }) {
  if (!text) return null;
  const lines = text.split('\n');
  let k = 0;
  return (
    <div className="md-answer">
      {lines.map(line => {
        if (/^###\s/.test(line))
          return <div key={k++} style={{ fontWeight: 700, fontSize: 12.5, color: 'var(--accent-text)', marginTop: 14, marginBottom: 4 }}>{line.slice(4)}</div>;
        if (/^[-•*]\s/.test(line)) {
          const html = line.slice(2).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
          return (
            <div key={k++} style={{ display: 'flex', gap: 8, marginBottom: 3 }}>
              <span style={{ color: 'var(--accent)', marginTop: 2, flexShrink: 0, fontSize: 8 }}>◆</span>
              <span dangerouslySetInnerHTML={{ __html: html }} />
            </div>
          );
        }
        if (/^\d+\.\s/.test(line)) {
          const num = line.match(/^(\d+)\./)[1];
          const html = line.replace(/^\d+\.\s/, '').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
          return (
            <div key={k++} style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
              <span style={{ color: 'var(--green)', fontWeight: 700, fontSize: 11, minWidth: 16, marginTop: 1 }}>{num}.</span>
              <span dangerouslySetInnerHTML={{ __html: html }} />
            </div>
          );
        }
        if (line.trim() === '') return <div key={k++} style={{ height: 5 }} />;
        const html = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\*(.+?)\*/g, '<em>$1</em>');
        return <p key={k++} style={{ margin: '0 0 4px' }} dangerouslySetInnerHTML={{ __html: html }} />;
      })}
    </div>
  );
}

export default function ChatPage() {
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputQ, setInputQ] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [convLoading, setConvLoading] = useState(true);
  const [msgLoading, setMsgLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sources, setSources] = useState({});   // expanded sources per msg
  const [feedback, setFeedback] = useState({});
  const endRef = useRef(null);
  const inputRef = useRef(null);

  const scrollBottom = () => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); };
  useEffect(() => { scrollBottom(); }, [messages, isLoading]);

  const fetchConvs = useCallback(async () => {
    setConvLoading(true);
    try { const d = await getUserConversations(); setConversations(d || []); }
    catch { }
    finally { setConvLoading(false); }
  }, []);

  useEffect(() => { fetchConvs(); }, [fetchConvs]);

  const selectConv = async (id) => {
    setActiveConvId(id); setError(null); setMsgLoading(true);
    try {
      const hist = await getConversationMessages(id);
      setMessages(hist.map(m => ({
        id: m.id, sender: m.role === 'user' ? 'user' : 'ai',
        text: m.content, sources: m.sources || [],
        ts: new Date(m.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      })));
    } catch { setError('Could not load conversation.'); }
    finally { setMsgLoading(false); }
  };

  const newChat = () => {
    setActiveConvId(null); setMessages([]); setError(null); setInputQ('');
    setTimeout(() => inputRef.current?.focus(), 80);
  };

  const deleteConv = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation?')) return;
    try {
      await deleteConversation(id);
      setConversations(p => p.filter(c => c.id !== id));
      if (activeConvId === id) newChat();
    } catch { setError('Failed to delete.'); }
  };

  const doFeedback = async (msgId, rating) => {
    try { await submitFeedback(msgId, rating); setFeedback(p => ({ ...p, [msgId]: { rating, done: true } })); }
    catch { }
  };

  const send = async (q) => {
    const text = (q || inputQ).trim();
    if (!text || isLoading) return;
    setError(null); setInputQ('');
    const userMsg = { id: Date.now().toString(), sender: 'user', text, ts: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    setMessages(p => [...p, userMsg]);
    setIsLoading(true);
    try {
      const data = await sendChatMessage(text, activeConvId);
      if (data.conversation_id && data.conversation_id !== activeConvId) setActiveConvId(data.conversation_id);
      setMessages(p => [...p, {
        id: data.message_id || String(Date.now() + 1), sender: 'ai',
        text: data.answer, sources: data.sources || [],
        ts: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
      fetchConvs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get a response. Please try again.');
    } finally { setIsLoading(false); }
  };

  const toggleSrc = (id) => setSources(p => ({ ...p, [id]: !p[id] }));

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 58px)', background: 'var(--bg)', overflow: 'hidden' }}>

      {/* ════ SIDEBAR ════ */}
      <aside style={{
        width: 256, flexShrink: 0,
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column', padding: '14px 10px',
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 4px', marginBottom: 12 }}>
          <span style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text-secondary)' }}>Conversations</span>
          <button onClick={newChat} style={{
            width: 28, height: 28, borderRadius: 8, border: 'none', cursor: 'pointer',
            background: 'var(--grad-accent)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: 'var(--shadow-accent)', transition: 'opacity 0.15s'
          }}
            onMouseEnter={e => e.currentTarget.style.opacity = '0.85'}
            onMouseLeave={e => e.currentTarget.style.opacity = '1'}
            title="New Chat"
          >
            <Plus size={14} color="#fff" />
          </button>
        </div>

        {/* List */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}>
          {convLoading ? (
            [1, 2, 3].map(i => <div key={i} className="shimmer" style={{ height: 40, borderRadius: 10, margin: '2px 0' }} />)
          ) : conversations.length === 0 ? (
            <div style={{ padding: '36px 16px', textAlign: 'center' }}>
              <Sparkles size={22} color="var(--text-muted)" style={{ margin: '0 auto 10px', display: 'block' }} />
              <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0, lineHeight: 1.65 }}>No chats yet.<br />Ask your first question!</p>
            </div>
          ) : conversations.map(conv => {
            const active = conv.id === activeConvId;
            return (
              <div key={conv.id} className={`conv-item ${active ? 'active' : ''}`} onClick={() => selectConv(conv.id)}>
                {active && <div style={{ position: 'absolute', left: 0, top: '18%', bottom: '18%', width: 2, borderRadius: 99, background: 'var(--accent)' }} />}
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, minWidth: 0, flex: 1, paddingLeft: active ? 6 : 2 }}>
                  <MessageSquare size={11} color={active ? 'var(--accent)' : 'var(--text-muted)'} style={{ flexShrink: 0 }} />
                  <span style={{ fontSize: 12, fontWeight: active ? 600 : 400, color: active ? 'var(--accent-text)' : 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {conv.title || 'Untitled Chat'}
                  </span>
                </div>
                <button
                  className="conv-delete"
                  onClick={e => deleteConv(e, conv.id)}
                  style={{ opacity: 0, padding: 4, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--danger)', borderRadius: 6, flexShrink: 0 }}
                >
                  <Trash2 size={11} />
                </button>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border)', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
          <span className="status-dot online" style={{ width: 5, height: 5 }} />
          <span style={{ fontSize: 10.5, color: 'var(--text-muted)' }}>RAG Knowledge Base</span>
        </div>
      </aside>

      {/* ════ MAIN ════ */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg)', minWidth: 0 }}>

        {/* Chat Header */}
        <div style={{
          display: 'flex', alignItems: 'center', padding: '13px 22px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-card)', gap: 12, flexShrink: 0
        }}>
          <div style={{
            width: 38, height: 38, borderRadius: 11, background: 'var(--grad-accent)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: 'var(--shadow-accent)', flexShrink: 0
          }}>
            <Bot size={18} color="#fff" />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
              <h1 style={{ margin: 0, fontSize: 14.5, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                CampusAI Assistant
              </h1>
              <span style={{
                padding: '2px 9px', borderRadius: 99, fontSize: 9.5, fontWeight: 700,
                background: 'var(--green-muted)', border: '1px solid var(--green-border)',
                color: 'var(--green-text)', letterSpacing: '0.05em'
              }}>
                RAG-GROUNDED
              </span>
            </div>
            <p style={{ margin: 0, fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>
              Answers powered by official campus documents
            </p>
          </div>
          <button onClick={newChat} style={{
            display: 'flex', alignItems: 'center', gap: 5, padding: '6px 13px',
            borderRadius: 9, cursor: 'pointer', border: '1px solid var(--border)',
            background: 'var(--bg)', color: 'var(--text-secondary)', fontSize: 12,
            fontWeight: 600, fontFamily: 'Plus Jakarta Sans, sans-serif', transition: 'all 0.18s'
          }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-border)'; e.currentTarget.style.color = 'var(--accent-text)'; e.currentTarget.style.background = 'var(--accent-muted)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.background = 'var(--bg)'; }}
          >
            <Plus size={13} /> New Chat
          </button>
        </div>

        {/* Error */}
        {error && (
          <div style={{
            margin: '10px 20px 0', padding: '10px 14px', borderRadius: 11,
            background: 'var(--danger-muted)', border: '1px solid var(--danger-border)',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            color: 'var(--danger-text)', fontSize: 12.5
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
              <AlertCircle size={14} />{error}
            </div>
            <button onClick={() => setError(null)} style={{ background: 'none', border: 'none', color: 'var(--danger-text)', cursor: 'pointer', fontWeight: 700, fontSize: 11, paddingLeft: 12 }}>Dismiss</button>
          </div>
        )}

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: 18 }}>
          {msgLoading ? (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ display: 'flex', gap: 6, justifyContent: 'center', marginBottom: 10 }}>
                  <span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" />
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0 }}>Loading messages...</p>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <WelcomeScreen onSend={send} />
          ) : (
            messages.map(msg => (
              <ChatBubble key={msg.id} msg={msg} fb={feedback[msg.id]} expanded={sources[msg.id]} toggleSrc={toggleSrc} doFeedback={doFeedback} />
            ))
          )}

          {/* Typing indicator */}
          {isLoading && (
            <div className="msg-in" style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
              <AiAvatar />
              <div style={{
                padding: '12px 16px', borderRadius: '4px 16px 16px 16px',
                background: 'var(--bubble-ai-bg)', border: '1px solid var(--bubble-ai-border)',
                display: 'flex', alignItems: 'center', gap: 10,
                boxShadow: 'var(--shadow-sm)'
              }}>
                <div style={{ display: 'flex', gap: 5 }}>
                  <span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" />
                </div>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Searching knowledge base...</span>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Input */}
        <div style={{
          padding: '14px 22px', borderTop: '1px solid var(--border)',
          background: 'var(--bg-card)'
        }}>
          <form onSubmit={e => { e.preventDefault(); send(); }} style={{ display: 'flex', gap: 9 }}>
            <div style={{ flex: 1, position: 'relative' }}>
              <input
                ref={inputRef}
                type="text"
                value={inputQ}
                onChange={e => setInputQ(e.target.value)}
                placeholder="Ask about admissions, exams, hostel, fees..."
                disabled={isLoading}
                className="premium-input"
                style={{ paddingLeft: 42, opacity: isLoading ? 0.6 : 1 }}
              />
              <Sparkles size={15} color="var(--accent)" style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', opacity: 0.65 }} />
            </div>
            <button type="submit" disabled={!inputQ.trim() || isLoading}
              style={{
                width: 44, height: 44, borderRadius: 12, border: 'none', cursor: inputQ.trim() && !isLoading ? 'pointer' : 'not-allowed',
                background: inputQ.trim() && !isLoading ? 'var(--grad-accent)' : 'var(--bg-card-hover)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0, transition: 'all 0.2s',
                boxShadow: inputQ.trim() && !isLoading ? 'var(--shadow-accent)' : 'none',
              }}>
              <Send size={16} color={inputQ.trim() && !isLoading ? '#fff' : 'var(--text-muted)'} />
            </button>
          </form>
          <p style={{ margin: '7px 0 0', textAlign: 'center', fontSize: 10.5, color: 'var(--text-muted)' }}>
            Grounded exclusively in official campus documents
          </p>
        </div>
      </main>
    </div>
  );
}

function AiAvatar() {
  return (
    <div style={{
      width: 32, height: 32, borderRadius: 9, background: 'var(--grad-accent)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexShrink: 0, boxShadow: 'var(--shadow-accent)'
    }}>
      <Bot size={15} color="#fff" />
    </div>
  );
}

function WelcomeScreen({ onSend }) {
  return (
    <div className="fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '32px 16px', textAlign: 'center', gap: 28 }}>
      <div>
        <div style={{
          width: 66, height: 66, borderRadius: 20, margin: '0 auto 18px',
          background: 'var(--accent-muted)', border: '1px solid var(--accent-border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: 'var(--shadow-md)'
        }}>
          <GraduationCap size={30} color="var(--accent)" />
        </div>
        <h2 style={{ margin: '0 0 8px', fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
          Ask CampusAI Anything
        </h2>
        <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary)', maxWidth: 360, lineHeight: 1.65 }}>
          Get instant, grounded answers from official college documents — admissions, exams, hostel, fees, and more.
        </p>
      </div>
      <div style={{ width: '100%', maxWidth: 560 }}>
        <p style={{ fontSize: 10.5, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.09em', textTransform: 'uppercase', marginBottom: 10 }}>
          Suggested Questions
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 8 }}>
          {SUGGESTED.map((item, i) => (
            <button key={i} className="suggest-btn" onClick={() => onSend(item.q)}>
              <span style={{ fontSize: 18, lineHeight: 1, flexShrink: 0 }}>{item.icon}</span>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontSize: 9.5, fontWeight: 700, color: 'var(--accent)', letterSpacing: '0.06em', marginBottom: 3, textTransform: 'uppercase' }}>{item.cat}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45 }}>{item.q}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function ChatBubble({ msg, fb, expanded, toggleSrc, doFeedback }) {
  const isUser = msg.sender === 'user';
  return (
    <div className="msg-in" style={{ display: 'flex', gap: 10, justifyContent: isUser ? 'flex-end' : 'flex-start', alignItems: 'flex-start' }}>
      {!isUser && <AiAvatar />}
      <div style={{ maxWidth: '78%', display: 'flex', flexDirection: 'column', gap: 5 }}>
        {/* Bubble */}
        <div style={{
          padding: '12px 15px',
          borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
          background: isUser ? 'var(--bubble-user-bg)' : 'var(--bubble-ai-bg)',
          border: isUser ? 'none' : '1px solid var(--bubble-ai-border)',
          boxShadow: isUser ? 'var(--shadow-accent)' : 'var(--shadow-sm)',
          color: isUser ? 'var(--bubble-user-text)' : 'var(--bubble-ai-text)',
        }}>
          {isUser
            ? <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, fontFamily: 'Plus Jakarta Sans, sans-serif' }}>{msg.text}</p>
            : <Markdown text={msg.text} />
          }
          <span style={{ display: 'block', fontSize: 10, marginTop: 7, opacity: 0.5, textAlign: isUser ? 'right' : 'left' }}>{msg.ts}</span>
        </div>

        {/* Sources */}
        {!isUser && msg.sources && msg.sources.length > 0 && (
          <div style={{ borderRadius: 11, overflow: 'hidden', background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
            <button onClick={() => toggleSrc(msg.id)} style={{
              width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '7px 11px', background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--accent)', fontFamily: 'Plus Jakarta Sans, sans-serif'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, fontWeight: 600 }}>
                <FileText size={11} /><span>Sources ({msg.sources.length})</span>
              </div>
              {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            {expanded && (
              <div style={{ padding: '0 9px 9px', display: 'flex', flexDirection: 'column', gap: 5 }}>
                {msg.sources.map((src, i) => (
                  <div key={i} style={{ padding: '8px 10px', borderRadius: 9, background: 'var(--bg)', border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 180 }}>{src.document_title}</span>
                      <span className="source-badge">p.{src.page_number} · {(src.similarity * 100).toFixed(0)}%</span>
                    </div>
                    <p style={{ margin: 0, fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5, fontStyle: 'italic' }}>
                      "{src.snippet?.slice(0, 100)}{src.snippet?.length > 100 ? '...' : ''}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Feedback */}
        {!isUser && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, paddingLeft: 2 }}>
            {fb?.done ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10.5, color: 'var(--green)', fontWeight: 600 }}>
                <CheckCircle2 size={12} /> Feedback recorded
              </span>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <span style={{ fontSize: 10.5, color: 'var(--text-muted)' }}>Helpful?</span>
                {[
                  { icon: <ThumbsUp size={11} />, rating: 'helpful', col: 'var(--green)', bg: 'var(--green-muted)', border: 'var(--green-border)' },
                  { icon: <ThumbsDown size={11} />, rating: 'unhelpful', col: 'var(--danger)', bg: 'var(--danger-muted)', border: 'var(--danger-border)' },
                ].map(btn => (
                  <button key={btn.rating} onClick={() => doFeedback(msg.id, btn.rating)}
                    style={{
                      padding: '4px 6px', background: 'none', border: '1px solid var(--border)',
                      borderRadius: 7, cursor: 'pointer', color: 'var(--text-muted)', transition: 'all 0.15s'
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = btn.bg; e.currentTarget.style.borderColor = btn.border; e.currentTarget.style.color = btn.col; }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'none'; e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
                  >
                    {btn.icon}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div style={{
          width: 32, height: 32, borderRadius: 9, background: 'var(--bg-card)', border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
        }}>
          <User size={14} color="var(--text-muted)" />
        </div>
      )}
    </div>
  );
}
