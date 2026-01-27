import { useEffect, useState } from 'react';

export interface NavData {
  speed?: number;
  heading?: number;
  depth?: number;
  wind?: number;
  [key: string]: any;
}

export function useSignalK(): { navData: NavData; connected: boolean; } {
  const [navData, setNavData] = useState<NavData>({});
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const signalkHost = import.meta.env.VITE_SIGNALK_HOST || `http://${window.location.hostname}:3001`;

    const fetchNavData = async () => {
      try {
        const response = await fetch(`${signalkHost}/api/v1/navigation`);
        if (response.ok) {
          const data = await response.json();
          setNavData(data);
          setConnected(true);
        } else {
          setConnected(false);
        }
      } catch (error) {
        console.warn('SignalK connection failed:', error);
        setConnected(false);
      }
    };

    // Initial fetch
    fetchNavData();

    // Poll for updates every 1 second
    const interval = setInterval(fetchNavData, 1000);

    return () => clearInterval(interval);
  }, []);

  return { navData, connected };
}
