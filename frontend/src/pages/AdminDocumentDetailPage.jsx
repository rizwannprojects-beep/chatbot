import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FileText, ArrowLeft, Trash2, Play, Clock, CheckCircle2, XCircle, AlertCircle, HardDrive, Calendar, Tag, User } from 'lucide-react';
import { documentService } from '../services/documents';

export default function AdminDocumentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadDoc = async () => {
    setLoading(true);
    try {
      const data = await documentService.getDocumentById(id);
      setDocument(data);
      setError('');
    } catch (err) {
      console.error('Failed to load document details:', err);
      setError(err.response?.data?.detail || 'Document not found.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDoc();
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${document.title}"?`)) return;

    try {
      await documentService.deleteDocument(id);
      navigate('/admin/documents');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  const handleStartProcess = async () => {
    try {
      const updated = await documentService.processDocument(id);
      setDocument(updated);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to start processing');
    }
  };

  const renderStatusBadge = (status) => {
    switch (status) {
      case 'UPLOADED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Clock className="w-3.5 h-3.5" /> UPLOADED
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">
            <Clock className="w-3.5 h-3.5" /> PROCESSING
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" /> COMPLETED
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
            <XCircle className="w-3.5 h-3.5" /> FAILED
          </span>
        );
      default:
        return <span className="text-xs text-slate-400">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 rounded-2xl bg-slate-900 border border-red-500/30 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-red-400 mx-auto" />
        <h2 className="text-lg font-bold text-white">Error Loading Document</h2>
        <p className="text-slate-400 text-xs">{error}</p>
        <Link to="/admin/documents" className="inline-block px-4 py-2 rounded-lg bg-slate-800 text-slate-200 text-xs font-semibold">
          Back to Documents
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div className="flex items-center gap-3">
          <Link
            to="/admin/documents"
            className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <FileText className="w-6 h-6 text-indigo-400" /> {document.title}
            </h1>
            <p className="text-slate-400 text-xs font-mono mt-1">{document.file_name}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {document.status === 'UPLOADED' && (
            <button
              onClick={handleStartProcess}
              className="px-4 py-2 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30 font-medium text-xs flex items-center gap-1.5 hover:bg-blue-600/30 transition"
            >
              <Play className="w-3.5 h-3.5" /> Start Processing
            </button>
          )}
          <button
            onClick={handleDelete}
            className="px-4 py-2 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 font-medium text-xs flex items-center gap-1.5 hover:bg-red-500/20 transition"
          >
            <Trash2 className="w-3.5 h-3.5" /> Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <Tag className="w-4 h-4 text-indigo-400" />
          <div className="text-xs text-slate-400">Category</div>
          <div className="text-sm font-semibold text-white">{document.category}</div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <Clock className="w-4 h-4 text-blue-400" />
          <div className="text-xs text-slate-400">Processing Status</div>
          <div>{renderStatusBadge(document.status)}</div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <HardDrive className="w-4 h-4 text-emerald-400" />
          <div className="text-xs text-slate-400">File Size</div>
          <div className="text-sm font-semibold text-white font-mono">{(document.file_size / 1024).toFixed(1)} KB</div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
        <h3 className="text-base font-semibold text-white">Document Information</h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-xs text-slate-400 block mb-1">MIME Type</span>
            <span className="font-mono text-slate-200">{document.mime_type}</span>
          </div>
          <div>
            <span className="text-xs text-slate-400 block mb-1">Uploaded Date</span>
            <span className="text-slate-200">{new Date(document.created_at).toLocaleString()}</span>
          </div>
          <div>
            <span className="text-xs text-slate-400 block mb-1">Uploaded By</span>
            <span className="font-mono text-xs text-slate-300">{document.uploaded_by || 'System Admin'}</span>
          </div>
          <div>
            <span className="text-xs text-slate-400 block mb-1">Processed Date</span>
            <span className="text-slate-200">{document.processed_at ? new Date(document.processed_at).toLocaleString() : 'Not Processed Yet'}</span>
          </div>
        </div>

        {document.description && (
          <div className="border-t border-slate-800 pt-4">
            <span className="text-xs text-slate-400 block mb-1">Description</span>
            <p className="text-slate-300 text-sm">{document.description}</p>
          </div>
        )}

        {document.error_message && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs space-y-1">
            <div className="font-semibold flex items-center gap-1">
              <AlertCircle className="w-4 h-4" /> Processing Error Details
            </div>
            <p>{document.error_message}</p>
          </div>
        )}
      </div>
    </div>
  );
}
