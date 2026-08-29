import axios from 'axios';

// Normalize API_BASE_URL: strip trailing slash and optional trailing /api
let rawBase = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').trim().replace(/\/+$/, '');
if (rawBase.endsWith('/api')) {
  rawBase = rawBase.slice(0, -4);
}
const API_BASE_URL = `${rawBase}/api`;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000, // 45s timeout to handle Render free-tier cold starts
});

// Automatic REQUEST interceptor: attach Authorization header dynamically on EVERY request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('campusai_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Automatic RESPONSE interceptor: handle 401 Unauthorized globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('campusai_token');
      delete apiClient.defaults.headers.common['Authorization'];
    }
    return Promise.reject(error);
  }
);

export const healthService = {
  getHealth: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch health status:', error);
      throw error;
    }
  },
};

export default apiClient;
