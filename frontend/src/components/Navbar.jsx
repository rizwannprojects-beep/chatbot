import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { GraduationCap, Activity, CheckCircle, AlertTriangle, LogOut, LayoutDashboard, ShieldCheck, MessageSquare } from 'lucide-react';
import { healthService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [backendHealth, setBackendHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    healthService.getHealth()
      .then((data) => {
        setBackendHealth(data);
        setLoading(false);
      })
      .catch(() => {
        setBackendHealth(null);
        setLoading(false);
      });
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 font-bold text-xl text-white hover:opacity-90 transition">
          <div className="p-2 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <GraduationCap className="w-5 h-5" />
          </div>
          <span>Campus<span className="text-blue-400">AI</span></span>
        </Link>

        <div className="flex items-center gap-4 text-sm font-medium">
          {/* Backend Status Badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs text-slate-300">
            <Activity className="w-3.5 h-3.5 text-blue-400" />
            <span>API:</span>
            {loading ? (
              <span className="text-slate-400 animate-pulse">Checking...</span>
            ) : backendHealth ? (
              <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                <CheckCircle className="w-3 h-3" /> Online
              </span>
            ) : (
              <span className="flex items-center gap-1 text-amber-400 font-semibold">
                <AlertTriangle className="w-3 h-3" /> Offline
              </span>
            )}
          </div>

          {user ? (
            <div className="flex items-center gap-3">
              <Link
                to="/chat"
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                  location.pathname === '/chat' ? 'bg-indigo-600 text-white' : 'text-indigo-300 bg-indigo-950/50 hover:bg-indigo-900/60 border border-indigo-700/50'
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5" /> Campus Chat
              </Link>

              <Link
                to="/dashboard"
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                  location.pathname === '/dashboard' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" /> Dashboard
              </Link>

              {user.role === 'admin' && (
                <Link
                  to="/admin"
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                    location.pathname === '/admin' ? 'bg-purple-600 text-white' : 'text-purple-400 border border-purple-500/30 hover:bg-purple-500/10'
                  }`}
                >
                  <ShieldCheck className="w-3.5 h-3.5" /> Admin
                </Link>
              )}

              <button
                onClick={handleLogout}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-red-500/10 hover:text-red-400 text-slate-300 text-xs font-semibold transition border border-slate-700 flex items-center gap-1.5"
              >
                <LogOut className="w-3.5 h-3.5" /> Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className={`px-4 py-2 rounded-lg transition ${
                  location.pathname === '/login'
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                Log In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition shadow-sm font-medium"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
