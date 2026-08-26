import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, BookOpen, Clock, HelpCircle, User, ArrowRight, Sparkles, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getUserConversations } from '../services/chat';

export default function DashboardPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUserConversations()
      .then((data) => {
        setConversations(data || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch user conversations for dashboard:', err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <LayoutDashboard className="w-6 h-6 text-indigo-400" /> Student Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Welcome back, <span className="text-white font-semibold">{user?.name}</span>! Access your grounded college assistant.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/chat"
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-500/20 flex items-center gap-2 transition"
          >
            <MessageSquare className="w-4 h-4" /> Open Campus Chat <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <MessageSquare className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-semibold text-slate-300">Total Chat Threads</h3>
          <p className="text-3xl font-extrabold text-white">{loading ? '...' : conversations.length}</p>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <BookOpen className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-semibold text-slate-300">Knowledge Base</h3>
          <p className="text-3xl font-extrabold text-white">Active</p>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <Clock className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-semibold text-slate-300">Account Role</h3>
          <p className="text-xl font-bold text-white capitalize">{user?.role || 'Student'}</p>
        </div>
      </div>

      {/* Recent Activity & Quick Access */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Conversations */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-indigo-400" /> Recent Conversations
            </h2>
            <Link to="/chat" className="text-xs text-indigo-400 hover:underline font-semibold">
              View All
            </Link>
          </div>

          {loading ? (
            <div className="py-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-500" /> Loading threads...
            </div>
          ) : conversations.length === 0 ? (
            <div className="py-8 text-center text-slate-500 text-xs space-y-2">
              <p>No previous chat conversations yet.</p>
              <Link to="/chat" className="inline-block text-indigo-400 hover:underline font-semibold">
                Start your first chat thread →
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.slice(0, 4).map((conv) => (
                <Link
                  key={conv.id}
                  to="/chat"
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 hover:border-indigo-500/50 transition text-xs"
                >
                  <span className="truncate font-medium text-slate-200">{conv.title}</span>
                  <span className="text-[10px] text-slate-500 shrink-0 ml-2">
                    {new Date(conv.updated_at).toLocaleDateString()}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Useful Categories */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" /> Knowledge Categories
          </h2>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-indigo-400">Admissions</div>
              <p className="text-slate-400 text-[11px]">Certificates, deadlines & requirements</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-purple-400">Examinations</div>
              <p className="text-slate-400 text-[11px]">Semester schedules & grading rules</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-emerald-400">Hostel & Housing</div>
              <p className="text-slate-400 text-[11px]">Curfew times & check-in guidelines</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-blue-400">Library Services</div>
              <p className="text-slate-400 text-[11px]">Textbook borrowing & quiet hours</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
