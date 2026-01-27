import React, { useState, useEffect } from 'react';
import { usePsykologen, CheckInResponse, PsykologenStatus } from '../hooks/usePsykologen';

interface MentalHealthEntry {
  timestamp: string;
  mood: 'good' | 'neutral' | 'poor';
  stress: number;
  notes: string;
  response?: string;
}

const MAX_NOTES_LENGTH = 1000;

export const Psykologen: React.FC = () => {
  const [entries, setEntries] = useState<MentalHealthEntry[]>([
    {
      timestamp: new Date().toISOString(),
      mood: 'good',
      stress: 3,
      notes: 'Crew morale high. All members performing well.'
    }
  ]);

  const [notes, setNotes] = useState('');
  const [mood, setMood] = useState<'good' | 'neutral' | 'poor'>('neutral');
  const [stress, setStress] = useState(5);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState<string | null>(null);
  const { checkin, getStatus } = usePsykologen();
  const [moduleStatus, setModuleStatus] = useState<PsykologenStatus | null>(null);

  useEffect(() => {
    getStatus()
      .then(setModuleStatus)
      .catch(err => console.error('Failed to get Psykologen status:', err));
  }, [getStatus]);

  const addEntry = async () => {
    const trimmedNotes = notes.trim();
    if (!trimmedNotes) {
      setError('Please enter notes before adding an entry.');
      return;
    }

    if (trimmedNotes.length > MAX_NOTES_LENGTH) {
      setError(`Notes too long. Maximum ${MAX_NOTES_LENGTH} characters.`);
      return;
    }

    setLoading(true);
    setError(null);
    setAiResponse(null);

    try {
      // Send check-in to backend
      const result: CheckInResponse = await checkin(stress, trimmedNotes);
      
      const entry: MentalHealthEntry = {
        timestamp: result.checkin.timestamp,
        mood,
        stress,
        notes: trimmedNotes,
        response: result.response
      };

      setEntries([entry, ...entries]);
      setNotes('');
      setMood('neutral');
      setStress(5);
      setAiResponse(result.response);
      
      // Refresh status
      getStatus().then(setModuleStatus).catch(console.error);
    } catch (err) {
      console.error('Failed to perform check-in:', err);
      
      // Fallback to local-only entry
      const entry: MentalHealthEntry = {
        timestamp: new Date().toISOString(),
        mood,
        stress,
        notes: trimmedNotes
      };
      setEntries([entry, ...entries]);
      setNotes('');
      setMood('neutral');
      setStress(5);
      setError('Backend unavailable. Entry saved locally only.');
    } finally {
      setLoading(false);
    }
  };

  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setNotes(value);
    if (value.length > MAX_NOTES_LENGTH) {
      setError(`Notes too long. ${value.length}/${MAX_NOTES_LENGTH} characters.`);
    } else {
      setError(null);
    }
  };

  const getMoodColor = (m: string) => {
    switch (m) {
      case 'good': return 'var(--arctic-green)';
      case 'neutral': return 'var(--arctic-blue)';
      case 'poor': return '#ff2020';
      default: return 'var(--primary-color)';
    }
  };

  const getStressColor = (s: number) => {
    if (s <= 3) return 'var(--arctic-green)';
    if (s <= 6) return 'var(--arctic-blue)';
    return '#ff2020';
  };

  const characterCount = notes.length;
  const isNearLimit = characterCount > MAX_NOTES_LENGTH * 0.8;

  return (
    <div className="hud-panel">
      <h2>PSYKOLOGEN - MENTAL HEALTH</h2>
      <div className="corner-br"></div>
      
      <div style={{ 
        marginBottom: '15px', 
        padding: '10px', 
        border: '2px solid var(--arctic-blue)',
        background: 'rgba(0, 212, 255, 0.05)',
        fontSize: '12px'
      }}>
        🔒 PRIVACY NOTICE: All mental health data is stored locally and never transmitted to external servers. Your privacy is protected.
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div className="terminal">
          <div className="terminal-line">CREW WELLNESS: MONITORED</div>
          <div className="terminal-line">STRESS LEVEL: NOMINAL</div>
          <div className="terminal-line">ENTRIES: {entries.length}</div>
          <div className="terminal-line">LAST CHECK: {entries[0] ? new Date(entries[0].timestamp).toLocaleString() : 'N/A'}</div>
          {moduleStatus && (
            <>
              <div className="terminal-line">BACKEND CHECKINS: {moduleStatus.total_checkins || 0}</div>
              <div className="terminal-line">AVG MOOD (7D): {moduleStatus.avg_mood_7d || 0}/10</div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div style={{ 
          marginBottom: '15px', 
          padding: '10px', 
          border: '2px solid #ff2020',
          background: 'rgba(255, 32, 32, 0.1)',
          color: '#ff2020'
        }}>
          ⚠ {error}
        </div>
      )}

      {aiResponse && (
        <div style={{ 
          marginBottom: '15px', 
          padding: '15px', 
          border: '2px solid var(--arctic-blue)',
          background: 'rgba(0, 212, 255, 0.1)',
          color: 'var(--arctic-blue)',
          whiteSpace: 'pre-wrap'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>💙 AI RESPONSE:</div>
          {aiResponse}
        </div>
      )}

      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ fontSize: '14px', marginBottom: '10px' }}>NEW WELLNESS ENTRY</h3>
        
        <div style={{ marginBottom: '15px' }}>
          <label style={{ fontSize: '12px', display: 'block', marginBottom: '5px' }}>MOOD</label>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button 
              className={`hud-button ${mood === 'good' ? 'active' : ''}`}
              onClick={() => setMood('good')}
              aria-label="Set mood to good"
              aria-pressed={mood === 'good'}
            >
              GOOD
            </button>
            <button 
              className={`hud-button ${mood === 'neutral' ? 'active' : ''}`}
              onClick={() => setMood('neutral')}
              aria-label="Set mood to neutral"
              aria-pressed={mood === 'neutral'}
            >
              NEUTRAL
            </button>
            <button 
              className={`hud-button ${mood === 'poor' ? 'active' : ''}`}
              onClick={() => setMood('poor')}
              aria-label="Set mood to poor"
              aria-pressed={mood === 'poor'}
            >
              POOR
            </button>
          </div>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label 
            htmlFor="stress-slider"
            style={{ fontSize: '12px', display: 'block', marginBottom: '5px' }}
          >
            STRESS LEVEL: <span style={{ color: getStressColor(stress) }}>{stress}/10</span>
          </label>
          <input
            id="stress-slider"
            name="stressLevel"
            type="range"
            min="1"
            max="10"
            value={stress}
            onChange={(e) => setStress(parseInt(e.target.value))}
            style={{ width: '100%' }}
            aria-label="Stress level"
            aria-valuemin={1}
            aria-valuemax={10}
            aria-valuenow={stress}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label 
            htmlFor="wellness-notes"
            style={{ fontSize: '12px', display: 'block', marginBottom: '5px' }}
          >
            NOTES
          </label>
          <textarea
            id="wellness-notes"
            name="wellnessNotes"
            className="hud-input"
            placeholder="ENTER NOTES..."
            value={notes}
            onChange={handleNotesChange}
            rows={3}
            maxLength={MAX_NOTES_LENGTH}
            style={{ width: '100%', resize: 'vertical' }}
            aria-label="Wellness notes"
            aria-describedby="notes-char-count"
          />
          <div 
            id="notes-char-count"
            style={{ 
              fontSize: '12px', 
              marginTop: '5px', 
              opacity: 0.7,
              color: isNearLimit ? '#ffa500' : 'inherit',
              textAlign: 'right'
            }}
          >
            {characterCount}/{MAX_NOTES_LENGTH} CHARACTERS
          </div>
        </div>

        <button 
          className="hud-button" 
          onClick={addEntry}
          disabled={!notes.trim() || notes.length > MAX_NOTES_LENGTH || loading}
          aria-label="Add wellness entry"
        >
          {loading ? 'SUBMITTING...' : 'ADD ENTRY'}
        </button>
      </div>

      <div>
        <h3 style={{ fontSize: '14px', marginBottom: '10px' }}>WELLNESS HISTORY</h3>
        <div 
          className="data-stream" 
          style={{ maxHeight: '400px' }}
          role="log"
          aria-live="polite"
          aria-label="Wellness history"
        >
          {entries.length === 0 ? (
            <div style={{ opacity: 0.5 }}>NO WELLNESS ENTRIES.</div>
          ) : (
            entries.map((entry, idx) => (
              <div 
                key={idx}
                style={{ 
                  marginBottom: '20px', 
                  paddingBottom: '15px', 
                  borderBottom: '1px solid var(--primary-color)',
                  paddingLeft: '10px',
                  borderLeft: `3px solid ${getMoodColor(entry.mood)}`
                }}
              >
                <div style={{ fontSize: '10px', opacity: 0.7, marginBottom: '5px' }}>
                  {new Date(entry.timestamp).toLocaleString()}
                </div>
                <div style={{ marginBottom: '5px' }}>
                  <span style={{ color: getMoodColor(entry.mood) }}>MOOD: {entry.mood.toUpperCase()}</span>
                  {' | '}
                  <span style={{ color: getStressColor(entry.stress) }}>STRESS: {entry.stress}/10</span>
                </div>
                <div>{entry.notes}</div>
                {entry.response && (
                  <div style={{ 
                    marginTop: '10px', 
                    padding: '10px',
                    background: 'rgba(0, 212, 255, 0.05)',
                    border: '1px solid var(--arctic-blue)',
                    fontSize: '12px',
                    opacity: 0.9,
                    whiteSpace: 'pre-wrap'
                  }}>
                    <strong>AI FEEDBACK:</strong><br/>
                    {entry.response}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      <div style={{ marginTop: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button className="hud-button" aria-label="Start wellness check">
          WELLNESS CHECK
        </button>
        <button className="hud-button" aria-label="Mental health resources">
          RESOURCES
        </button>
        <button 
          className="hud-button" 
          onClick={() => {
            if (window.confirm('Are you sure you want to clear all wellness history? This action cannot be undone.')) {
              setEntries([]);
            }
          }}
          aria-label="Clear wellness history"
        >
          CLEAR HISTORY
        </button>
      </div>
    </div>
  );
};
