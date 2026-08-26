import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, FileText, Database, Bot, ArrowRight, ShieldCheck, Sparkles, Search, CheckCircle2 } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="space-y-24 pb-12">
      {/* Hero Section */}
      <section className="relative pt-16 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wide">
          <Sparkles className="w-4 h-4" /> AI-Powered Campus RAG Chatbot
        </div>
        
        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight max-w-4xl mx-auto">
          Instant, Grounded Answers for Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400">College Knowledge Base</span>
        </h1>
        
        <p className="text-slate-400 text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed">
          CampusAI retrieves reliable facts directly from official college PDFs, rules, circulars, and handbooks before generating grounded AI responses with page citations.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            to="/register"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-base shadow-lg shadow-blue-500/25 transition flex items-center justify-center gap-2"
          >
            Get Started Free <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-base border border-slate-700 transition"
          >
            Log In to Account
          </Link>
        </div>
      </section>

      {/* How RAG Works Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 sm:p-12 space-y-10">
          <div className="text-center space-y-3">
            <h2 className="text-2xl sm:text-3xl font-bold text-white">How RAG Pipeline Works</h2>
            <p className="text-slate-400 text-sm sm:text-base">Retrieval-Augmented Generation ensures CampusAI answers remain accurate and grounded.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold">1</div>
              <h3 className="font-semibold text-white">Document Processing</h3>
              <p className="text-slate-400 text-xs leading-relaxed">Admins upload official PDFs. Text is extracted, cleaned, and split into indexed chunks.</p>
            </div>

            <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center font-bold">2</div>
              <h3 className="font-semibold text-white">Vector Embeddings</h3>
              <p className="text-slate-400 text-xs leading-relaxed">Chunk content is converted into embeddings and stored in Supabase pgvector.</p>
            </div>

            <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center font-bold">3</div>
              <h3 className="font-semibold text-white">Semantic Search</h3>
              <p className="text-slate-400 text-xs leading-relaxed">Student questions query the vector database to retrieve the top relevant document chunks.</p>
            </div>

            <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-600/20 text-emerald-400 flex items-center justify-center font-bold">4</div>
              <h3 className="font-semibold text-white">Grounded AI Answer</h3>
              <p className="text-slate-400 text-xs leading-relaxed">Gemini generates an accurate response strictly bounded by the retrieved context with source citations.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Main Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-2xl sm:text-3xl font-bold text-white">Key Features</h2>
          <p className="text-slate-400 text-sm sm:text-base">Designed for student success and administrative efficiency.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <Search className="w-6 h-6 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Natural Language Queries</h3>
            <p className="text-slate-400 text-sm">Ask about courses, exams, fees, hostel rules, or admission criteria in plain English or multilingual phrasing.</p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <FileText className="w-6 h-6 text-indigo-400" />
            <h3 className="text-lg font-semibold text-white">Source Verification</h3>
            <p className="text-slate-400 text-sm">Every response includes document titles and page numbers for verified fact-checking.</p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            <h3 className="text-lg font-semibold text-white">Zero Hallucinations</h3>
            <p className="text-slate-400 text-sm">If context is unavailable, CampusAI clearly states information is not in the official knowledge base.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 pt-8 max-w-7xl mx-auto px-4 text-center text-xs text-slate-500">
        <p>© 2026 CampusAI — RAG-Based College Chatbot System. Built with Vite, React, FastAPI, Supabase pgvector & Google Gemini.</p>
      </footer>
    </div>
  );
}
