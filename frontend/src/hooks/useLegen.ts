import axios from 'axios';
import { useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface MedicalAssessment {
  timestamp: string;
  symptoms: string[];
  severity: string;
  triage_level: string;
  recommendations: string[];
  evacuation_needed: boolean;
  protocol?: string;
}

export interface MedicalProtocol {
  protocol_type: string;
  protocol: Record<string, unknown>;
}

export interface LegenStatus {
  module: string;
  status: string;
  total_assessments: number;
  red_triage: number;
  protocols_available: number;
}

export const useLegen = () => {
  const assess = useCallback(async (symptoms: string[], severity: string = 'medium'): Promise<MedicalAssessment> => {
    const response = await api.post<MedicalAssessment>('/api/v1/legen/assess', {
      symptoms,
      severity
    });
    return response.data;
  }, []);

  const getProtocol = useCallback(async (protocolType: string): Promise<MedicalProtocol> => {
    const response = await api.get<MedicalProtocol>(`/api/v1/legen/protocol/${protocolType}`);
    return response.data;
  }, []);

  const getStatus = useCallback(async (): Promise<LegenStatus> => {
    const response = await api.get<LegenStatus>('/api/v1/legen/status');
    return response.data;
  }, []);

  return {
    assess,
    getProtocol,
    getStatus,
  };
};
