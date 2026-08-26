import React, { useState, useRef, useEffect } from 'react';
import {
  sendChatMessage,
  getUserConversations,
  getConversationMessages,
  deleteConversation,
  submitFeedback
} from '../services/chat';
import {
  Send,
  Bot,
  User,
  BookOpen,
  Sparkles,
  AlertCircle,
  FileText,
  Loader2,
  ChevronDown,
  ChevronUp,
  Plus,
  MessageSquare,
  Trash2,
  Menu,
  X,
  ThumbsUp,
  ThumbsDown,
  CheckCircle2
} from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  "What are the hostel check-in rules and curfew times?",
  "When do end semester examinations start?",
  "What documents are required for campus admissions?",
  "What is the library textbook return policy?"
];

export default function ChatPage() {
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputQuestion, setInputQuestion] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);
  const [isConvLoading, setIsConvLoading] = useState(true);
  const [isMessagesLoading, setIsMessagesLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedSources, setExpandedSources] = useState({});
  const [feedbackState, setFeedbackState] = useState({}); // { [msgId]: { rating: 'helpful'|'unhelpful', submitted: bool, comment: string } }
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Load User Conversations on mount
  const fetchConversations = async () => {
    setIsConvLoading(true);
    try {
      const data = await getUserConversations();
      setConversations(data || []);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    } finally {
      setIsConvLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  // Load Messages when active conversation changes
  const handleSelectConversation = async (convId) => {
    setActiveConvId(convId);
    setError(null);
    setIsMessagesLoading(true);
    setIsSidebarOpen(false);

    try {
      const historyMessages = await getConversationMessages(convId);
      const formatted = historyMessages.map((msg) => ({
        id: msg.id,
        sender: msg.role === 'user' ? 'user' : 'assistant',
        text: msg.content,
        sources: msg.sources || [],
        timestamp: new Date(msg.created_at || Date.now()).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit'
        })
      }));
      setMessages(formatted);
    } catch (err) {
      console.error('Failed to load conversation messages:', err);
      setError('Could not load conversation history.');
    } finally {
      setIsMessagesLoading(false);
    }
  };

  const handleNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    setError(null);
    setInputQuestion('');
    setIsSidebarOpen(false);
  };

  const handleDeleteConversation = async (e, convId) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this conversation?')) return;

    try {
      await deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (activeConvId === convId) {
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError('Failed to delete conversation.');
    }
  };

  const handleFeedback = async (msgId, rating) => {
    try {
      await submitFeedback(msgId, rating);
      setFeedbackState((prev) => ({
        ...prev,
        [msgId]: { rating, submitted: true }
      }));
    } catch (err) {
      console.error('Feedback submit error:', err);
      setError('Could not submit feedback.');
    }
  };

  const handleSend = async (questionToSend) => {
    const queryText = questionToSend || inputQuestion;
    if (!queryText.trim() || isLoading) return;

    setError(null);
    setInputQuestion('');

    const userMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const data = await sendChatMessage(queryText, activeConvId);
      
      if (data.conversation_id && data.conversation_id !== activeConvId) {
        setActiveConvId(data.conversation_id);
      }

      const assistantMessage = {
        id: data.message_id || (Date.now() + 1).toString(),
        sender: 'assistant',
        text: data.answer,
        sources: data.sources || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Refresh sidebar list to reflect updated order/title
      fetchConversations();
    } catch (err) {
      console.error('Chat API Error:', err);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || 'Failed to generate response. Please try again.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSourceExpand = (msgId) => {
    setExpandedSources((prev) => ({
      ...prev,
      [msgId]: !prev[msgId]
    }));
  };

  return (
    <div className="max-w-7xl mx-auto px-2 sm:px-4 py-4 flex h-[calc(100vh-4.5rem)] gap-4">
      {/* Mobile Drawer Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar: Conversation History */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-72 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 flex flex-col transition-transform duration-300 ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 font-bold text-slate-800 dark:text-white text-sm">
            <MessageSquare className="w-4 h-4 text-indigo-500" />
            <span>Chat History</span>
          </div>
          <button
            onClick={handleNewChat}
            className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto space-y-1 pr-1">
          {isConvLoading ? (
            <div className="flex items-center justify-center p-8 text-slate-400 text-xs gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
              <span>Loading threads...</span>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center p-6 text-slate-400 dark:text-slate-500 text-xs">
              No previous conversations found. Click <strong>New Chat</strong> to start!
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeConvId;
              return (
                <div
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`group relative flex items-center justify-between p-2.5 rounded-xl cursor-pointer text-xs transition ${
                    isActive
                      ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-semibold border border-indigo-200 dark:border-indigo-800'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/80'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate pr-6">
                    <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400'}`} />
                    <span className="truncate">{conv.title || 'Untitled Chat'}</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(e, conv.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-500 transition"
                    title="Delete Conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 flex flex-col min-w-0">
        {/* Top Header Controls */}
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="md:hidden p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
            >
              {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-sm">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                CampusAI Assistant
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 font-medium">
                  Grounded RAG
                </span>
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Official document search & grounded Q&A
              </p>
            </div>
          </div>

          <button
            onClick={handleNewChat}
            className="md:hidden px-3 py-1.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" /> New
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-3 p-3 rounded-xl bg-red-50 border border-red-200 dark:bg-red-950/40 dark:border-red-900 text-red-700 dark:text-red-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="font-semibold underline">
              Dismiss
            </button>
          </div>
        )}

        {/* Messages Feed */}
        <div className="flex-1 overflow-y-auto pr-2 space-y-5">
          {isMessagesLoading ? (
            <div className="h-full flex items-center justify-center text-slate-400 text-sm gap-2">
              <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
              <span>Fetching message history...</span>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 my-auto">
              <div className="w-14 h-14 rounded-2xl bg-indigo-50 dark:bg-slate-800 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-3 shadow-sm">
                <Sparkles className="w-7 h-7" />
              </div>
              <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-1">
                Ask CampusAI Anything
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mb-6">
                Get precise answers grounded directly in official college handbooks and announcements.
              </p>

              <div className="w-full max-w-md">
                <p className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">
                  Suggested Questions
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                  {SUGGESTED_QUESTIONS.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(q)}
                      className="p-2.5 text-xs rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-indigo-400 text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition shadow-sm flex items-start gap-2"
                    >
                      <BookOpen className="w-3.5 h-3.5 text-indigo-500 shrink-0 mt-0.5" />
                      <span>{q}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg) => {
              const fb = feedbackState[msg.id];
              return (
                <div
                  key={msg.id}
                  className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.sender === 'assistant' && (
                    <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shrink-0 mt-1 shadow-sm">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className="max-w-[85%] sm:max-w-[75%] space-y-2">
                    <div
                      className={`p-3.5 rounded-2xl ${
                        msg.sender === 'user'
                          ? 'bg-indigo-600 text-white rounded-br-none'
                          : 'bg-slate-50 dark:bg-slate-800/90 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700/80 rounded-bl-none shadow-sm'
                      }`}
                    >
                      <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                      <span
                        className={`block text-[10px] mt-1.5 ${
                          msg.sender === 'user' ? 'text-indigo-200 text-right' : 'text-slate-400 dark:text-slate-500'
                        }`}
                      >
                        {msg.timestamp}
                      </span>
                    </div>

                    {/* Sources Referenced */}
                    {msg.sender === 'assistant' && msg.sources && msg.sources.length > 0 && (
                      <div className="bg-slate-50 dark:bg-slate-900/60 rounded-xl p-2.5 border border-slate-200 dark:border-slate-800">
                        <button
                          onClick={() => toggleSourceExpand(msg.id)}
                          className="w-full flex items-center justify-between text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
                        >
                          <div className="flex items-center gap-1.5">
                            <FileText className="w-3.5 h-3.5" />
                            <span>Sources ({msg.sources.length})</span>
                          </div>
                          {expandedSources[msg.id] ? (
                            <ChevronUp className="w-3.5 h-3.5" />
                          ) : (
                            <ChevronDown className="w-3.5 h-3.5" />
                          )}
                        </button>

                        {expandedSources[msg.id] && (
                          <div className="mt-2 space-y-1.5">
                            {msg.sources.map((src, idx) => (
                              <div
                                key={idx}
                                className="p-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/60 text-xs space-y-0.5"
                              >
                                <div className="flex items-center justify-between font-medium text-slate-800 dark:text-slate-200">
                                  <span className="truncate max-w-[180px]">{src.document_title}</span>
                                  <span className="px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 text-[10px]">
                                    Page {src.page_number} ({(src.similarity * 100).toFixed(0)}%)
                                  </span>
                                </div>
                                <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 italic">
                                  "{src.snippet}"
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Answer Feedback Component */}
                    {msg.sender === 'assistant' && (
                      <div className="flex items-center gap-2 text-xs text-slate-400 pt-0.5">
                        {fb?.submitted ? (
                          <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 text-[11px] font-medium">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Feedback recorded!</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2 text-[11px]">
                            <span className="text-slate-400">Was this helpful?</span>
                            <button
                              onClick={() => handleFeedback(msg.id, 'helpful')}
                              className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-emerald-600 transition"
                              title="Helpful"
                            >
                              <ThumbsUp className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleFeedback(msg.id, 'unhelpful')}
                              className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-red-500 transition"
                              title="Not helpful"
                            >
                              <ThumbsDown className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {msg.sender === 'user' && (
                    <div className="w-7 h-7 rounded-lg bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300 shrink-0 mt-1">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {/* Loading state for incoming answer */}
          {isLoading && (
            <div className="flex gap-2.5 justify-start">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shrink-0 mt-1 shadow-sm">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700/80 rounded-bl-none shadow-sm flex items-center gap-2.5">
                <Loader2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400 animate-spin" />
                <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                  Generating grounded answer...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="pt-3 border-t border-slate-200 dark:border-slate-800 mt-2">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              placeholder="Ask a question about campus rules, exams, admissions..."
              disabled={isLoading}
              className="flex-1 px-4 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-60 shadow-sm"
            />
            <button
              type="submit"
              disabled={!inputQuestion.trim() || isLoading}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs sm:text-sm flex items-center gap-1.5 disabled:opacity-50 transition shadow-sm"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
