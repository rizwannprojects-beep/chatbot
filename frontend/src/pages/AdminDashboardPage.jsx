import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  Users,
  FileText,
  Upload,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  XCircle
} from 'lucide-react';
import { authService } from '../services/auth';
import { documentService } from '../services/documents';

export default function AdminDashboardPage() {
  const [adminAuthCheck, setAdminAuthCheck] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      authService.checkAdminOnly().catch(() => null),
      documentService.getAdminStats().catch(() => null)
    ]).then(([authData, statsData]) => {
      setAdminAuthCheck(authData);
      setStats(statsData);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-indigo-400" /> Admin Control Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">Manage documents, process knowledge-base chunks, and view system analytics.</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/admin/documents/upload"
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-500/20 flex items-center gap-1.5 transition"
          >
            <Upload className="w-3.5 h-3.5" /> Upload PDF
          </Link>
          <Link
            to="/admin/documents"
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs border border-slate-700 flex items-center gap-1.5 transition"
          >
            <FileText className="w-3.5 h-3.5" /> View All Documents
          </Link>
        </div>
      </div>

      {/* Admin Route Protection Verification Box */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          {loading ? (
            <span className="text-slate-400">Verifying Admin API Authorization...</span>
          ) : adminAuthCheck ? (
            <span className="flex items-center gap-2 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" /> Backend Admin Authorization Confirmed
            </span>
          ) : (
            <span className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-4 h-4" /> Admin API Check Failed
            </span>
          )}
        </h2>
        {adminAuthCheck && (
          <p className="text-xs text-slate-400 font-mono">
            {adminAuthCheck.message}
          </p>
        )}
      </div>

      {/* Admin Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
          <Users className="w-5 h-5 text-indigo-400 mb-2" />
          <h3 className="text-xs font-medium text-slate-400">Total Registered Users</h3>
          <p className="text-2xl font-extrabold text-white">{stats?.total_students ?? '-'}</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
          <FileText className="w-5 h-5 text-blue-400 mb-2" />
          <h3 className="text-xs font-medium text-slate-400">Total Documents</h3>
          <p className="text-2xl font-extrabold text-white">{stats?.total_documents ?? '-'}</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 mb-2" />
          <h3 className="text-xs font-medium text-slate-400">Processed Knowledge Docs</h3>
          <p className="text-2xl font-extrabold text-white">{stats?.completed_documents ?? '-'}</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
          <XCircle className="w-5 h-5 text-red-400 mb-2" />
          <h3 className="text-xs font-medium text-slate-400">Failed Processing</h3>
          <p className="text-2xl font-extrabold text-white">{stats?.failed_documents ?? '-'}</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
          <MessageSquare className="w-5 h-5 text-purple-400 mb-2" />
          <h3 className="text-xs font-medium text-slate-400">Total Chat Conversations</h3>
          <p className="text-2xl font-extrabold text-white">{stats?.total_conversations ?? '-'}</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
          <MessageSquare className="w-5 h-5 text-amber-400 mb-2" />
          <h3 className="text-xs font-medium text-slate-400">Total Q&A Messages</h3>
          <p className="text-2xl font-extrabold text-white">{stats?.total_messages ?? '-'}</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
          <ThumbsUp className="w-5 h-5 text-emerald-400 mb-2" />
          <h3 className="text-xs font-medium text-slate-400">Helpful Feedback 👍</h3>
          <p className="text-2xl font-extrabold text-white">{stats?.positive_feedback ?? '-'}</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
          <ThumbsDown className="w-5 h-5 text-rose-400 mb-2" />
          <h3 className="text-xs font-medium text-slate-400">Not Helpful Feedback 👎</h3>
          <p className="text-2xl font-extrabold text-white">{stats?.negative_feedback ?? '-'}</p>
        </div>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-white">College Knowledge-Base Management</h3>
          <p className="text-slate-400 text-xs mt-1">Upload, review metadata, filter, and process campus PDF documents.</p>
        </div>
        <Link
          to="/admin/documents"
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center gap-2 transition"
        >
          Manage Documents <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
