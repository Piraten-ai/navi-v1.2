import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketMessage {
  type: string;
  data: unknown;
  timestamp?: string;
}

interface UseWebSocketReturn {
  ws: WebSocket | null;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: WebSocketMessage) => void;
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
}

export const useWebSocket = (url: string): UseWebSocketReturn => {
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    try {
      setConnectionStatus('connecting');
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          setLastMessage(message);
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        setConnectionStatus('error');
      };

      ws.onclose = () => {
        console.log('[WebSocket] Disconnected');
        setIsConnected(false);
        setConnectionStatus('disconnected');
        wsRef.current = null;

        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current++;
        
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log(`[WebSocket] Reconnecting... (attempt ${reconnectAttempts.current})`);
          connect();
        }, delay);
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('[WebSocket] Connection failed:', err);
      setConnectionStatus('error');
    }
  }, [url]);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Cannot send message: not connected');
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    lastMessage,
    sendMessage,
    isConnected,
    connectionStatus,
    ws: wsRef.current,
  };
};
