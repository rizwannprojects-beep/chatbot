import React from 'react';
import Navbar from '../components/Navbar';

export default function MainLayout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <main className="flex-1">
        {children}
      </main>
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        CampusAI — RAG-Based College Information Assistant &copy; 2026
      </footer>
    </div>
  );
}
