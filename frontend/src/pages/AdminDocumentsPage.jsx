import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Upload, Trash2, Eye, Play, Filter, AlertCircle, CheckCircle2, Clock, XCircle, Search, RefreshCw } from 'lucide-react';
import { documentService } from '../services/documents';

const CATEGORIES = [
  'All',
  'Admissions',
  'Academics',
  'Examination',
  'Fees',
  'Scholarships',
  'Hostel',
  'Library',
  'Placements',
  'Departments',
  'Policies',
  'Events',
  'General'
];

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [sortOrder, setSortOrder] = useState('newest');
  const [searchTerm, setSearchTerm] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const catParam = selectedCategory === 'All' ? '' : selectedCategory;
      const statusParam = selectedStatus === 'All' ? '' : selectedStatus;
      const data = await documentService.getDocuments(catParam, statusParam);
      setDocuments(data || []);
      setError('');
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError('Failed to fetch documents. Please check backend authorization.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [selectedCategory, selectedStatus]);

  const handleClearFilters = () => {
    setSelectedCategory('All');
    setSelectedStatus('All');
    setSearchTerm('');
    setSortOrder('newest');
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete "${title}"?`)) return;

    try {
      await documentService.deleteDocument(id);
      setActionSuccess(`Document "${title}" deleted successfully.`);
      fetchDocs();
      setTimeout(() => setActionSuccess(''), 3000);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  const handleStartProcess = async (id, title) => {
    try {
      await documentService.processDocument(id);
      setActionSuccess(`Document "${title}" processing started.`);
      fetchDocs();
      setTimeout(() => setActionSuccess(''), 3000);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to start processing');
    }
  };

  let filteredDocs = documents.filter((doc) =>
    doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.file_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (sortOrder === 'newest') {
    filteredDocs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  } else {
    filteredDocs.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  }

  const renderStatusBadge = (status) => {
    switch (status) {
      case 'UPLOADED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Clock className="w-3 h-3" /> UPLOADED
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">
            <Clock className="w-3 h-3" /> PROCESSING
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" /> COMPLETED
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
            <XCircle className="w-3 h-3" /> FAILED
          </span>
        );
      default:
        return <span className="text-xs text-slate-400">{status}</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText className="w-6 h-6 text-indigo-400" /> College Document Knowledge Base
          </h1>
          <p className="text-slate-400 text-sm mt-1">Upload, search, filter, and process official campus PDFs.</p>
        </div>
        <Link
          to="/admin/documents/upload"
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition shadow-lg shadow-indigo-500/20 flex items-center gap-2 self-start sm:self-auto"
        >
          <Upload className="w-4 h-4" /> Upload Document
        </Link>
      </div>

      {actionSuccess && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" /> {actionSuccess}
        </div>
      )}

      {error && (
        <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      {/* Filter & Search Controls */}
      <div className="flex flex-col md:flex-row items-center gap-3 bg-slate-900 p-4 rounded-2xl border border-slate-800">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by title or file name..."
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <div className="flex items-center gap-1.5">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg text-slate-200 text-xs py-2 px-2.5 focus:outline-none focus:border-indigo-500"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg text-slate-200 text-xs py-2 px-2.5 focus:outline-none focus:border-indigo-500"
          >
            <option value="All">All Statuses</option>
            <option value="UPLOADED">UPLOADED</option>
            <option value="PROCESSING">PROCESSING</option>
            <option value="COMPLETED">COMPLETED</option>
            <option value="FAILED">FAILED</option>
          </select>

          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg text-slate-200 text-xs py-2 px-2.5 focus:outline-none focus:border-indigo-500"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>

          {(selectedCategory !== 'All' || selectedStatus !== 'All' || searchTerm || sortOrder !== 'newest') && (
            <button
              onClick={handleClearFilters}
              className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center gap-1 transition"
            >
              <RefreshCw className="w-3 h-3" /> Clear
            </button>
          )}
        </div>
      </div>

      {/* Document Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-12 text-center text-slate-400 space-y-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="text-xs">Loading documents...</p>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FileText className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-base font-semibold text-white">No matching documents found</h3>
            <p className="text-slate-400 text-xs">Try clearing search filters or upload a new PDF.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Document</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Size</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4 font-medium text-white">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                          <FileText className="w-4 h-4" />
                        </div>
                        <div>
                          <div>{doc.title}</div>
                          <div className="text-xs font-mono text-slate-400">{doc.file_name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded-md text-xs bg-slate-800 border border-slate-700 text-slate-300">
                        {doc.category}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {renderStatusBadge(doc.status)}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-400">
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/admin/documents/${doc.id}`}
                          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                        {doc.status === 'UPLOADED' && (
                          <button
                            onClick={() => handleStartProcess(doc.id, doc.title)}
                            className="p-2 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 transition"
                            title="Start Processing"
                          >
                            <Play className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(doc.id, doc.title)}
                          className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 transition"
                          title="Delete Document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
