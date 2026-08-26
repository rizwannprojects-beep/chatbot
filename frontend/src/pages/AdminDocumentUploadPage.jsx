import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Upload, FileText, ArrowLeft, AlertCircle, CheckCircle2, ShieldCheck } from 'lucide-react';
import { documentService } from '../services/documents';

const CATEGORIES = [
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

export default function AdminDocumentUploadPage() {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('General');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setError('');

    if (!selectedFile) {
      setFile(null);
      return;
    }

    // 1. Validate file extension
    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (ext !== 'pdf') {
      setError(`Invalid file type '.${ext}'. Only PDF documents (.pdf) are allowed.`);
      setFile(null);
      return;
    }

    // 2. Validate file size (10 MB max)
    const maxSize = 10 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      setError(`File size (${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB) exceeds 10 MB limit.`);
      setFile(null);
      return;
    }

    setFile(selectedFile);
    if (!title) {
      // Auto-fill title from filename
      const baseName = selectedFile.name.replace(/\.[^/.]+$/, "");
      setTitle(baseName.replace(/[_-]/g, ' '));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!file) {
      setError('Please select a valid PDF document to upload.');
      return;
    }

    if (!title.trim()) {
      setError('Please enter a document title.');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title.trim());
      formData.append('category', category);
      if (description.trim()) {
        formData.append('description', description.trim());
      }

      await documentService.uploadDocument(formData);
      navigate('/admin/documents');
    } catch (err) {
      console.error('Upload error:', err);
      const msg = err.response?.data?.detail || 'Failed to upload document. Please check file and permissions.';
      setError(msg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex items-center gap-4 border-b border-slate-800 pb-6">
        <Link
          to="/admin/documents"
          className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Upload className="w-6 h-6 text-indigo-400" /> Upload College Document
          </h1>
          <p className="text-slate-400 text-sm mt-1">Add official PDF files to the CampusAI knowledge base.</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
        {/* File Input Box */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">PDF Document File *</label>
          <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 transition rounded-2xl p-8 text-center bg-slate-950/50 space-y-3">
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
              id="file-upload"
              className="hidden"
            />
            <label htmlFor="file-upload" className="cursor-pointer space-y-2 block">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 mx-auto flex items-center justify-center">
                <FileText className="w-6 h-6" />
              </div>
              {file ? (
                <div className="text-sm font-semibold text-emerald-400 flex items-center justify-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" /> {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </div>
              ) : (
                <>
                  <div className="text-sm font-medium text-white">Click to browse or drop PDF here</div>
                  <div className="text-xs text-slate-400">PDF files only (max 10 MB)</div>
                </>
              )}
            </label>
          </div>
        </div>

        {/* Title Input */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">Document Title *</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Academic Regulations Handbook 2026"
            className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Category Dropdown */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">Category *</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {/* Optional Description */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">Description (Optional)</label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Brief summary of what this document covers..."
            className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500 resize-none"
          />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Link
            to="/admin/documents"
            className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={uploading}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition shadow-lg shadow-indigo-500/25 disabled:opacity-50 flex items-center gap-2"
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> Uploading...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" /> Save & Upload
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
