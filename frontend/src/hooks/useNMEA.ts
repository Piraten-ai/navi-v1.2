import { useState, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';

interface NMEAData {
  latitude?: number;
  longitude?: number;
  speed?: number;
  heading?: number;
  timestamp?: string;
  raw?: string;
}

export const useNMEA = () => {
  const [nmeaData, setNmeaData] = useState<NMEAData>({});
  // Build WS URL from env or current hostname
  const apiUrl = (import.meta.env.VITE_API_URL as string | undefined) || `http://${window.location.hostname}:8000`;
  const wsUrl = (import.meta.env.VITE_WS_URL as string | undefined) || `${apiUrl.replace(/^http/, 'ws')}/ws`;
  const { lastMessage } = useWebSocket(wsUrl);

  useEffect(() => {
    if (lastMessage?.type === 'nmea') {
      setNmeaData(lastMessage.data as NMEAData);
    }
  }, [lastMessage]);

  return nmeaData;
};
