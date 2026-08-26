import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus, User, Mail, Lock, ShieldCheck, AlertCircle, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState('student');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await register(name, email, password, role);
      if (res.user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Registration error:', err);
      const msg = err.response?.data?.detail || 'Failed to register. Please check your details.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-10 p-8 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 shadow-xl">
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-2xl bg-indigo-500/10 text-indigo-400 mb-1">
          <UserPlus className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-white">Create an Account</h1>
        <p className="text-slate-400 text-xs">Join CampusAI to ask grounded college questions</p>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">Full Name</label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs sm:text-sm focus:outline-none focus:border-indigo-500 transition"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address</label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@college.edu"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs sm:text-sm focus:outline-none focus:border-indigo-500 transition"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type={showPassword ? 'text' : 'password'}
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs sm:text-sm focus:outline-none focus:border-indigo-500 transition"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3.5 top-3 text-slate-500 hover:text-slate-300 transition"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" /> Account Role
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setRole('student')}
              className={`py-2 rounded-xl text-xs font-semibold border transition ${
                role === 'student'
                  ? 'bg-blue-600/20 border-blue-500 text-blue-400'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              Student
            </button>
            <button
              type="button"
              onClick={() => setRole('admin')}
              className={`py-2 rounded-xl text-xs font-semibold border transition ${
                role === 'admin'
                  ? 'bg-indigo-600/20 border-indigo-500 text-indigo-400'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              Administrator
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs sm:text-sm transition shadow-lg shadow-indigo-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Creating Account...</span>
            </>
          ) : (
            <span>Register Account</span>
          )}
        </button>
      </form>

      <div className="text-center text-xs text-slate-400">
        Already have an account?{' '}
        <Link to="/login" className="text-indigo-400 hover:underline font-semibold">
          Log in here
        </Link>
      </div>
    </div>
  );
}
