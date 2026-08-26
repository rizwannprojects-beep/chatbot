import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AdminDocumentsPage from './pages/AdminDocumentsPage';
import AdminDocumentUploadPage from './pages/AdminDocumentUploadPage';
import AdminDocumentDetailPage from './pages/AdminDocumentDetailPage';
import ChatPage from './pages/ChatPage';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <MainLayout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Protected Student Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <ChatPage />
                </ProtectedRoute>
              }
            />

            {/* Protected Admin Routes */}
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminDashboardPage />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/documents"
              element={
                <AdminRoute>
                  <AdminDocumentsPage />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/documents/upload"
              element={
                <AdminRoute>
                  <AdminDocumentUploadPage />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/documents/:id"
              element={
                <AdminRoute>
                  <AdminDocumentDetailPage />
                </AdminRoute>
              }
            />
          </Routes>
        </MainLayout>
      </Router>
    </AuthProvider>
  );
}
