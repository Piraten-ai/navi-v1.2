import axios from 'axios';
import { useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface CheckInResponse {
  checkin: {
    timestamp: string;
    mood_score: number;
    has_notes: boolean;
    user_id: string;
  };
  response: string;
}

export interface SessionResponse {
  session: {
    timestamp: string;
    topic: string;
    user_id: string;
    has_content: boolean;
  };
  response: string;
}

export interface PsykologenStatus {
  module: string;
  status: string;
  privacy_mode: string;
  total_checkins: number;
  total_sessions: number;
  avg_mood_7d: number;
  data_location: string;
}

export const usePsykologen = () => {
  const checkin = useCallback(async (moodScore: number, notes?: string, userId: string = 'crew'): Promise<CheckInResponse> => {
    const params: Record<string, string | number> = {
      mood_score: moodScore,
      user_id: userId
    };
    if (notes) {
      params.notes = notes;
    }
    const response = await api.post<CheckInResponse>('/api/v1/psykologen/checkin', null, { params });
    return response.data;
  }, []);

  const session = useCallback(async (topic: string, message: string, userId: string = 'crew'): Promise<SessionResponse> => {
    const response = await api.post<SessionResponse>('/api/v1/psykologen/session', null, {
      params: {
        topic,
        message,
        user_id: userId
      }
    });
    return response.data;
  }, []);

  const getStatus = useCallback(async (): Promise<PsykologenStatus> => {
    const response = await api.get<PsykologenStatus>('/api/v1/psykologen/status');
    return response.data;
  }, []);

  return {
    checkin,
    session,
    getStatus,
  };
};
