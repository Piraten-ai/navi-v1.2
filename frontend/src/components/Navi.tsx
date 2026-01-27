import React, { useState, useEffect, useRef } from 'react';
import { Send, AlertCircle, Loader } from 'lucide-react';
import { useNavi, NaviMessage } from '../hooks/useNavi';
import { useSettings } from '../hooks/useSettingsContext';

const MAX_MESSAGE_LENGTH = 1000;

type MessageType = 'chat' | 'medical' | 'wellness' | 'weather' | 'alert' | 'system';
type ActiveTab = 'chat' | 'medical' | 'wellness' | 'weather';

// Navi prompts (like Zelda's "Hey! Listen!") - THE SOUL OF THE PROJECT
const NAVI_PROMPTS = [
  "HEY! LISTEN!",
  "HEY!",
  "LISTEN!",
  "WATCH OUT!",
  "LOOK!",
  "HEY! OVER HERE!",
];

const TAB_ICONS: Record<ActiveTab, string> = {
  chat: '💬',
  medical: '⚕️',
  wellness: '🧠',
  weather: '🌊',
};

const MESSAGE_TYPE_COLORS: Record<MessageType, string> = {
  chat: 'bg-gray-800 border-l-4 border-blue-500',
  medical: 'bg-blue-950 border-l-4 border-blue-500',
  wellness: 'bg-purple-950 border-l-4 border-purple-500',
  weather: 'bg-cyan-950 border-l-4 border-cyan-500',
  alert: 'bg-red-950 border-l-4 border-red-500',
  system: 'bg-yellow-950 border-l-4 border-yellow-500',
};

export const Navi: React.FC<{ ws: WebSocket | null }> = ({ ws }) => {
  const { settings } = useSettings();
  const [messages, setMessages] = useState<(NaviMessage & { type?: MessageType })[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [_showPrompt, setShowPrompt] = useState(false);
  const [_promptText, setPromptText] = useState('');
  const [activeTab, setActiveTab] = useState<ActiveTab>('chat');
  const [retryCount, setRetryCount] = useState(0);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const prevMessagesLengthRef = useRef<number>(0);
  const { sendMessage, getHistory } = useNavi();

  useEffect(() => {
    getHistory()
      .then(hist => setMessages(hist.map(m => ({ ...m, type: 'chat' as MessageType }))))
      .catch(err => {
        console.error('Failed to load history:', err);
        setError('Failed to load message history');
      });
  }, [getHistory]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Listen for WebSocket alerts
  useEffect(() => {
    if (!ws) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'navi_anomaly_alert') {
          const alertMsg: typeof messages[0] = {
            role: 'assistant',
            content: data.message,
            timestamp: data.timestamp,
            type: 'alert',
          };
          setMessages(prev => [...prev, alertMsg]);
        } else if (data.type === 'navi_medical_alert') {
          const medicalMsg: typeof messages[0] = {
            role: 'assistant',
            content: data.message,
            timestamp: data.timestamp,
            type: 'medical',
          };
          setMessages(prev => [...prev, medicalMsg]);
        } else if (data.type === 'navi_weather_update') {
          const weatherMsg: typeof messages[0] = {
            role: 'assistant',
            content: data.message,
            timestamp: data.timestamp,
            type: 'weather',
          };
          setMessages(prev => [...prev, weatherMsg]);
        }
      } catch (e) {
        console.error('WebSocket parse error:', e);
      }
    };

    ws.addEventListener('message', handleMessage);
    return () => ws.removeEventListener('message', handleMessage);
  }, [ws]);

  // "Hey Listen!" prompt - THE SOUL OF THE PROJECT (now with settings toggle)
  useEffect(() => {
    if (!settings.naviPrompts) return;

    if (messages.length > prevMessagesLengthRef.current && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];

      if (lastMessage.role === 'assistant') {
        const randomPrompt = NAVI_PROMPTS[Math.floor(Math.random() * NAVI_PROMPTS.length)];
        setPromptText(randomPrompt);
        setShowPrompt(true);

        const timeoutId = setTimeout(() => {
          setShowPrompt(false);
        }, 3000);

        return () => clearTimeout(timeoutId);
      }

      prevMessagesLengthRef.current = messages.length;
    }
  }, [messages, settings.naviPrompts]);

  const getQuickActions = (tab: ActiveTab): { label: string; cmd: string }[] => {
    const actions = {
      chat: [
        { label: 'Status Report', cmd: "What's the current status?" },
        { label: 'Weather Update', cmd: "What's the weather like?" },
        { label: 'Help', cmd: 'What can you help with?' }
      ],
      medical: [
        { label: 'Hypothermia Protocol', cmd: 'I might have hypothermia' },
        { label: 'Chest Pain', cmd: "I'm having chest pain" },
        { label: 'Wound Care', cmd: 'I have a bleeding wound' }
      ],
      wellness: [
        { label: 'Mood Check', cmd: "Let's do a mood check" },
        { label: 'Feeling Stressed', cmd: "I'm feeling stressed" },
        { label: 'Coping Strategies', cmd: 'Give me coping strategies' }
      ],
      weather: [
        { label: 'Current Conditions', cmd: 'What are current weather conditions?' },
        { label: 'Storm Warning', cmd: 'Is there a storm coming?' },
        { label: 'Wind Speed', cmd: "What's the wind speed?" }
      ]
    };
    return actions[tab];
  };

  const handleSend = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    if (trimmedInput.length > MAX_MESSAGE_LENGTH) {
      setError(`Message too long. Maximum ${MAX_MESSAGE_LENGTH} characters.`);
      return;
    }

    const userMessage: typeof messages[0] = {
      role: 'user',
      content: trimmedInput,
      timestamp: new Date().toISOString(),
      type: activeTab as MessageType,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);
    setRetryCount(0);

    try {
      const response = await sendMessage(trimmedInput);
      const assistantMessage: typeof messages[0] = {
        role: 'assistant',
        content: typeof response.response === 'string' ? response.response : JSON.stringify(response.response),
        timestamp: response.timestamp,
        type: activeTab as MessageType,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error('Failed to send message:', err);
      let errorMsg = 'ERROR: Failed to reach NAVI. System may be offline.';
      let canRetry = false;

      if (err.message?.includes('Network Error') || err.code === 'ECONNREFUSED') {
        errorMsg = 'ERROR: Cannot connect to backend server. Please ensure backend is running.';
        canRetry = true;
      } else if (err.response?.status === 503) {
        errorMsg = 'ERROR: AI service unavailable. Ollama may not be running.';
        canRetry = true;
      } else if (err.response?.status >= 500) {
        errorMsg = 'ERROR: Server error occurred. Check backend logs.';
        canRetry = retryCount < 3;
      }

      const errorMessage: typeof messages[0] = {
        role: 'system',
        content: errorMsg + (canRetry ? ' Retry available.' : ''),
        timestamp: new Date().toISOString(),
        type: 'alert',
      };
      setMessages(prev => [...prev, errorMessage]);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    if (retryCount >= 3) {
      setError('Max retries exceeded');
      return;
    }
    setRetryCount(r => r + 1);
    await handleSend();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);
    if (value.length > MAX_MESSAGE_LENGTH) {
      setError(`Message too long. ${value.length}/${MAX_MESSAGE_LENGTH} characters.`);
    } else {
      setError(null);
    }
  };

  const handleQuickAction = (cmd: string) => {
    setInput(cmd);
    setTimeout(() => handleSend(), 100);
  };

  const characterCount = input.length;
  const _isNearLimit = characterCount > MAX_MESSAGE_LENGTH * 0.8;
  const filteredMessages = messages.filter(m => {
    if (activeTab === 'chat') return true;
    return m.type === activeTab || m.type === 'alert' || m.type === 'system';
  });

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-gray-900 to-black text-white">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span className="text-2xl">🧚</span>
            NAVI - Doctor • Weather Girl • Anomaly Screamer
          </h2>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 flex-wrap">
          {(['chat', 'medical', 'wellness', 'weather'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-semibold transition-all text-sm ${
                activeTab === tab
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {TAB_ICONS[tab]} {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {filteredMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <div className="text-6xl mb-4">🧚</div>
              <p className="text-lg">Hey! I'm NAVI!</p>
              <p className="text-sm mt-2">Talk to me about anything - I'm doctor, weather expert, and your friend.</p>
            </div>
          </div>
        ) : (
          filteredMessages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg ${msg.type ? MESSAGE_TYPE_COLORS[msg.type] : MESSAGE_TYPE_COLORS.chat}`}
            >
              <div className="flex items-start gap-3">
                {msg.role === 'assistant' && (
                  <div className="text-2xl flex-shrink-0">
                    {msg.type === 'alert' && '🚨'}
                    {msg.type === 'medical' && '⚕️'}
                    {msg.type === 'wellness' && '💙'}
                    {msg.type === 'weather' && '🌊'}
                    {!msg.type && '🧚'}
                  </div>
                )}
                <div className="flex-1">
                  <p className="text-sm text-gray-400 mb-2">
                    {msg.role === 'user' ? 'You' : 'NAVI'} • {new Date(msg.timestamp || Date.now()).toLocaleTimeString()}
                  </p>
                  <p className="whitespace-pre-wrap text-sm">
                    {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="p-4 bg-gray-800 rounded-lg mr-12 animate-pulse flex items-center gap-2">
            <Loader size={16} className="animate-spin" />
            <p className="text-gray-400">NAVI is thinking... 🧚✨</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {!loading && filteredMessages.length > 0 && (
        <div className="bg-gray-900 border-t border-gray-700 p-3 max-h-24 overflow-y-auto">
          <p className="text-xs text-gray-500 mb-2">Quick actions:</p>
          <div className="flex gap-2 flex-wrap">
            {getQuickActions(activeTab).map(action => (
              <button
                key={action.cmd}
                onClick={() => handleQuickAction(action.cmd)}
                className="text-xs px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-900 border-t border-red-700 p-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-300">
            <AlertCircle size={16} />
            <span className="text-sm">{error}</span>
          </div>
          {retryCount < 3 && (
            <button
              onClick={handleRetry}
              className="text-xs px-3 py-1 bg-red-700 hover:bg-red-600 rounded transition-colors"
            >
              Retry
            </button>
          )}
        </div>
      )}

      {/* Input Area */}
      <div className="bg-gray-900 border-t border-gray-700 p-4">
        <div className="flex gap-2 mb-2">
          <input
            id="navi-message-input"
            name="naviMessage"
            type="text"
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Talk to NAVI..."
            className="flex-1 bg-gray-800 text-white px-4 py-3 rounded-lg outline-none focus:ring-2 focus:ring-cyan-500 text-sm disabled:opacity-50"
            disabled={loading}
            maxLength={MAX_MESSAGE_LENGTH}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim() || input.length > MAX_MESSAGE_LENGTH}
            className="bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-700 text-white px-4 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2 disabled:cursor-not-allowed"
          >
            {loading ? <Loader size={16} className="animate-spin" /> : <Send size={16} />}
          </button>
        </div>
        <div className="text-xs text-gray-500 text-right">
          {characterCount}/{MAX_MESSAGE_LENGTH}
        </div>
      </div>
    </div>
  );
};
