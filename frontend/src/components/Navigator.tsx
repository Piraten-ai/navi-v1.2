import React, { useState } from 'react';
import { ErrorAlert } from './Alert';

interface NavtexMessage {
  id: string;
  timestamp: string;
  station: string;
  content: string;
  priority: 'routine' | 'important' | 'urgent';
}

export const Navigator: React.FC = () => {
  const [messages, setMessages] = useState<NavtexMessage[]>([
    {
      id: '1',
      timestamp: new Date().toISOString(),
      station: 'ZCZC FA01',
      content: 'GALE WARNING ISSUED FOR AREA VIKING. SW GALE FORCE 8 EXPECTED.',
      priority: 'urgent'
    }
  ]);
  const [filter, setFilter] = useState<'all' | 'urgent' | 'important' | 'routine'>('all');

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return '#ff2020';
      case 'important': return '#ffa500';
      default: return 'var(--primary-color)';
    }
  };

  const filteredMessages = filter === 'all' 
    ? messages 
    : messages.filter(msg => msg.priority === filter);

  const urgentCount = messages.filter(m => m.priority === 'urgent').length;
  const importantCount = messages.filter(m => m.priority === 'important').length;

  return (
    <div className="hud-panel">
      <h2>NAVTEX MARITIME MESSAGES</h2>
      <div className="corner-br"></div>
      
      <div className="terminal-compact">
        <div className="terminal-row">
          <span className="terminal-label">RECEIVER:</span>
          <span className="terminal-value">ACTIVE</span>
        </div>
        <div className="terminal-row">
          <span className="terminal-label">FREQ:</span>
          <span className="terminal-value">518 kHz</span>
        </div>
        <div className="terminal-row">
          <span className="terminal-label">STATIONS:</span>
          <span className="terminal-value">12 MONITORED</span>
        </div>
        <div className="terminal-row">
          <span className="terminal-label">TOTAL:</span>
          <span className="terminal-value">{messages.length}</span>
          {urgentCount > 0 && (
            <>
              <span className="terminal-separator">|</span>
              <span className="terminal-urgent">URGENT: {urgentCount}</span>
            </>
          )}
          {importantCount > 0 && (
            <>
              <span className="terminal-separator">|</span>
              <span className="terminal-important">IMPORTANT: {importantCount}</span>
            </>
          )}
        </div>
      </div>

      <ErrorAlert 
        message={`${urgentCount} URGENT MESSAGE${urgentCount > 1 ? 'S' : ''} REQUIRING ATTENTION`}
        show={urgentCount > 0} 
      />

      <div className="filter-bar">
        <button 
          className={`filter-button ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          ALL ({messages.length})
        </button>
        <button 
          className={`filter-button urgent ${filter === 'urgent' ? 'active' : ''}`}
          onClick={() => setFilter('urgent')}
        >
          URGENT ({urgentCount})
        </button>
        <button 
          className={`filter-button important ${filter === 'important' ? 'active' : ''}`}
          onClick={() => setFilter('important')}
        >
          IMPORTANT ({importantCount})
        </button>
        <button 
          className={`filter-button ${filter === 'routine' ? 'active' : ''}`}
          onClick={() => setFilter('routine')}
        >
          ROUTINE ({messages.filter(m => m.priority === 'routine').length})
        </button>
      </div>

      <div 
        className="data-stream" 
        style={{ maxHeight: '500px' }}
        role="log"
        aria-live="polite"
        aria-label="NAVTEX messages"
      >
        {filteredMessages.length === 0 ? (
          <div style={{ opacity: 0.5 }}>
            NO {filter !== 'all' ? filter.toUpperCase() : ''} MESSAGES
          </div>
        ) : (
          filteredMessages.map((msg) => (
            <div 
              key={msg.id} 
              style={{ 
                marginBottom: '20px', 
                paddingBottom: '15px', 
                borderBottom: `2px solid ${getPriorityColor(msg.priority)}`,
                borderLeft: `4px solid ${getPriorityColor(msg.priority)}`,
                paddingLeft: '10px'
              }}
            >
              <div style={{ fontSize: '10px', opacity: 0.7, marginBottom: '5px' }}>
                <span style={{ color: getPriorityColor(msg.priority) }}>
                  [{msg.priority.toUpperCase()}]
                </span>
                {' '}
                {new Date(msg.timestamp).toLocaleString()}
              </div>
              <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '5px', color: getPriorityColor(msg.priority) }}>
                {msg.station}
              </div>
              <div style={{ fontSize: '14px' }}>
                {msg.content}
              </div>
            </div>
          ))
        )}
      </div>

      <div style={{ marginTop: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button 
          className="hud-button" 
          onClick={() => console.log('Refresh messages')}
          aria-label="Refresh NAVTEX messages"
        >
          REFRESH
        </button>
        <button 
          className="hud-button" 
          onClick={() => {
            if (window.confirm('Are you sure you want to clear all messages?')) {
              setMessages([]);
            }
          }}
          aria-label="Clear all messages"
        >
          CLEAR ALL
        </button>
      </div>

      <div style={{ marginTop: '20px', fontSize: '12px', opacity: 0.5 }}>
        NAVTEX provides maritime safety information including weather warnings, navigational warnings, and search and rescue notices.
      </div>
    </div>
  );
};
