import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/api';
import { authService } from '../services/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('campusai_token') || null);
  const [loading, setLoading] = useState(true);

  // Set default authorization header whenever token changes
  useEffect(() => {
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('campusai_token', token);
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
      localStorage.removeItem('campusai_token');
    }
  }, [token]);

  // Load user profile on mount if token exists
  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await authService.getMe();
          setUser(userData);
        } catch (error) {
          console.error('Failed to authenticate session token:', error);
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email, password) => {
    const data = await authService.login({ email, password });
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const register = async (name, email, password, role = 'student') => {
    const data = await authService.register({ name, email, password, role });
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    await authService.logout();
    setToken(null);
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
