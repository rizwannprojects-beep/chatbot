import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert } from 'lucide-react';

export default function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (user.role !== 'admin') {
    return (
      <div className="max-w-md mx-auto my-20 p-8 rounded-2xl bg-slate-900 border border-red-500/30 text-center space-y-4">
        <div className="inline-flex p-3 rounded-full bg-red-500/10 text-red-400">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-white">403 — Access Denied</h2>
        <p className="text-slate-400 text-sm">
          Administrator privileges are required to access this portal. Your current role is <span className="text-amber-400 font-semibold uppercase">{user.role}</span>.
        </p>
      </div>
    );
  }

  return children;
}
