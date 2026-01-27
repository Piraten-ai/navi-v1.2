import { useEffect, useState } from 'react';
import { useWebSocket } from './useWebSocket';

export interface BridgeSignals {
  [key: string]: number;
}

export interface BridgePayload {
  signals: BridgeSignals;
  source?: string;
  timestamp?: string;
}

export const useBridgeSignals = () => {
  const [bridgeData, setBridgeData] = useState<BridgePayload | null>(null);
  const apiUrl = (import.meta.env.VITE_API_URL as string | undefined) || `http://${window.location.hostname}:8000`;
  const wsUrl = (import.meta.env.VITE_WS_URL as string | undefined) || `${apiUrl.replace(/^http/, 'ws')}/ws`;
  const { lastMessage } = useWebSocket(wsUrl);

  useEffect(() => {
    if (lastMessage?.type === 'bridge') {
      setBridgeData(lastMessage.data as BridgePayload);
    }
  }, [lastMessage]);

  return bridgeData;
};
