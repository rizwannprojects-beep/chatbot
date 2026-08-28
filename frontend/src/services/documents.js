import apiClient from './api';

export const documentService = {
  getDocuments: async (category = '', statusFilter = '') => {
    let url = '/documents';
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (statusFilter) params.append('status_filter', statusFilter);
    if (params.toString()) url += `?${params.toString()}`;

    const response = await apiClient.get(url);
    return response.data;
  },

  uploadDocument: async (formData) => {
    const response = await apiClient.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getDocumentById: async (id) => {
    const response = await apiClient.get(`/documents/${id}`);
    return response.data;
  },

  deleteDocument: async (id) => {
    const response = await apiClient.delete(`/documents/${id}`);
    return response.data;
  },

  processDocument: async (id) => {
    const response = await apiClient.post(`/documents/${id}/process`);
    return response.data;
  },

  getAdminStats: async () => {
    const response = await apiClient.get('/admin/stats');
    return response.data;
  }
};
