import axios from 'axios';
import { useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SystemDiagnostics {
  timestamp: string;
  cpu: {
    usage_percent: number;
    frequency_mhz: number | null;
    cores: number;
  };
  memory: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
  };
  swap: {
    total_gb: number;
    used_gb: number;
    usage_percent: number;
  };
  disk: {
    total_gb: number;
    used_gb: number;
    free_gb: number;
    usage_percent: number;
  };
  network: Record<string, unknown>;
  temperature: Record<string, unknown>;
}

export interface OptimizationResult {
  timestamp: string;
  optimizations: Array<{
    type: string;
    action: string;
    priority: string;
  }>;
  current_diagnostics: SystemDiagnostics;
}

export interface Alert {
  type: string;
  message: string;
  severity: string;
  timestamp: string;
}

export interface IngeniørenStatus {
  module: string;
  status: string;
  acoustic_calibrated: boolean;
  metrics_stored: number;
  total_alerts: number;
  alerts_last_hour: number;
}

export const useIngenioren = () => {
  const getDiagnostics = useCallback(async (): Promise<SystemDiagnostics> => {
    const response = await api.get<SystemDiagnostics>('/api/v1/ingenioren/diagnostics');
    return response.data;
  }, []);

  const getMetrics = useCallback(async (hours: number = 24) => {
    const response = await api.get<{ metrics: SystemDiagnostics[] }>('/api/v1/ingenioren/metrics', {
      params: { hours }
    });
    return response.data.metrics;
  }, []);

  const optimize = useCallback(async (): Promise<OptimizationResult> => {
    const response = await api.post<OptimizationResult>('/api/v1/ingenioren/optimize');
    return response.data;
  }, []);

  const getAlerts = useCallback(async (severity?: string): Promise<{ alerts: Alert[] }> => {
    const response = await api.get<{ alerts: Alert[] }>('/api/v1/ingenioren/alerts', {
      params: severity ? { severity } : undefined
    });
    return response.data;
  }, []);

  const calibrateAcoustic = useCallback(async (durationSeconds: number = 60): Promise<Record<string, unknown>> => {
    const response = await api.post('/api/v1/ingenioren/calibrate_acoustic', null, {
      params: { duration_seconds: durationSeconds }
    });
    return response.data;
  }, []);

  const detectAcousticAnomaly = useCallback(async (): Promise<Record<string, unknown>> => {
    const response = await api.post('/api/v1/ingenioren/detect_acoustic_anomaly');
    return response.data;
  }, []);

  const getStatus = useCallback(async (): Promise<IngeniørenStatus> => {
    const response = await api.get<IngeniørenStatus>('/api/v1/ingenioren/status');
    return response.data;
  }, []);

  return {
    getDiagnostics,
    getMetrics,
    optimize,
    getAlerts,
    calibrateAcoustic,
    detectAcousticAnomaly,
    getStatus,
  };
};
