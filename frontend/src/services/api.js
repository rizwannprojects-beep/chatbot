import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const healthService = {
  getHealth: async () => {
    try {
      const response = await apiClient.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch health status:', error);
      throw error;
    }
  },
};

export default apiClient;
