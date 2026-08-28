import apiClient from './api';

export const authService = {
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  logout: async () => {
    try {
      const response = await apiClient.post('/auth/logout');
      return response.data;
    } catch (e) {
      // Return success on client side regardless
      return { success: true };
    }
  },

  getMe: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  checkAdminOnly: async () => {
    const response = await apiClient.get('/auth/admin-only');
    return response.data;
  }
};
