/// <reference types="vite/client" />

import { useCallback } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

export interface NaviMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface NaviResponse {
  message: string;
  response: string;
  timestamp: string;
}

export function useNavi() {
  const sendMessage = useCallback(async (message: string): Promise<NaviResponse> => {
    const response = await fetch(`${API_BASE}/api/v1/navi/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Navi API error: ${response.statusText}`);
    }

    return response.json();
  }, []);

  const getHistory = useCallback(async (limit: number = 50): Promise<NaviMessage[]> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/navi/history?limit=${limit}`);
      
      if (!response.ok) {
        console.warn('Failed to load history, returning empty');
        return [];
      }

      const data = await response.json();
      return data.history || [];
    } catch (error) {
      console.error('Failed to load history:', error);
      return [];
    }
  }, []);

  const clearHistory = useCallback(async (): Promise<void> => {
    await fetch(`${API_BASE}/api/v1/navi/clear`, {
      method: 'POST',
    });
  }, []);

  return {
    sendMessage,
    getHistory,
    clearHistory,
  };
}
