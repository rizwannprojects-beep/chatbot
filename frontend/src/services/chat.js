import api from './api';

export const sendChatMessage = async (question, conversationId = null) => {
  const response = await api.post('/chat', {
    question,
    conversation_id: conversationId,
  });
  return response.data;
};

export const getUserConversations = async () => {
  const response = await api.get('/conversations');
  return response.data;
};

export const getConversationMessages = async (conversationId) => {
  const response = await api.get(`/conversations/${conversationId}/messages`);
  return response.data;
};

export const deleteConversation = async (conversationId) => {
  const response = await api.delete(`/conversations/${conversationId}`);
  return response.data;
};

export const submitFeedback = async (messageId, rating, comment = null) => {
  const response = await api.post('/feedback', {
    message_id: messageId,
    rating,
    comment,
  });
  return response.data;
};
