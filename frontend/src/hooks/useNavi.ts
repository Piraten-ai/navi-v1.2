import axios from 'axios';
import { useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface NaviMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface NaviResponse {
  response: string;
  timestamp: string;
}

export const useNavi = () => {
  const sendMessage = useCallback(async (message: string): Promise<NaviResponse> => {
    const response = await api.post<NaviResponse>('/api/v1/navi/chat', {
      message,
      context: {}
    });
    return response.data;
  }, []);

  const getHistory = useCallback(async (): Promise<NaviMessage[]> => {
    const response = await api.get<{ history: NaviMessage[] }>('/api/v1/navi/history');
    return response.data.history;
  }, []);

  return {
    sendMessage,
    getHistory,
  };
};
