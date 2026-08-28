import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/api';
import { authService } from '../services/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('campusai_token') || null);
  const [loading, setLoading] = useState(true);

  // Synchronously update Axios authorization header and localStorage whenever token state changes
  const updateToken = (newToken) => {
    if (newToken) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      localStorage.setItem('campusai_token', newToken);
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
      localStorage.removeItem('campusai_token');
    }
    setToken(newToken);
  };

  // Initialize session on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('campusai_token');
    if (savedToken) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
      authService.getMe()
        .then((userData) => {
          setUser(userData);
          setLoading(false);
        })
        .catch((error) => {
          console.warn('Session profile check outcome:', error?.response?.status || error.message);
          // ONLY clear session if server explicitly rejects token with 401 Unauthorized.
          // DO NOT clear session on cold-start timeouts, 502/503 gateway errors, or network glitches.
          if (error.response && error.response.status === 401) {
            delete apiClient.defaults.headers.common['Authorization'];
            localStorage.removeItem('campusai_token');
            setToken(null);
            setUser(null);
          }
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const data = await authService.login({ email, password });
    updateToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const register = async (name, email, password, role = 'student') => {
    const data = await authService.register({ name, email, password, role });
    updateToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch {
      // Ignore network errors during logout
    }
    updateToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
