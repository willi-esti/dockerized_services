import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const kronosApi = {
  // Chat endpoints
  sendMessage: async (message, conversationId = null) => {
    const response = await api.post('/chat', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  },

  // Ollama status
  getOllamaStatus: async () => {
    const response = await api.get('/ollama/status');
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get conversations
  getConversations: async () => {
    const response = await api.get('/conversations');
    return response.data;
  },

  // Get tags
  getTags: async () => {
    const response = await api.get('/tags');
    return response.data;
  },
};

export default api;
