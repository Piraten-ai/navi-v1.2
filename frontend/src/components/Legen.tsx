import React, { useState, useEffect } from 'react';
import { useLegen } from '../hooks/useLegen';
import type { MedicalAssessment, LegenStatus } from '../hooks/useLegen';

interface MedicalRecord {
  timestamp: string;
  type: 'vitals' | 'medication' | 'injury' | 'checkup' | 'assessment' | 'protocol';
  data: string;
  severity: 'low' | 'medium' | 'high';
  assessment?: MedicalAssessment;
  protocol?: string;
}

const MEDICAL_PROTOCOLS = {
  'HYPOTHERMIA': 'Remove wet clothing, wrap blankets, warm beverages, horizontal position, MEDEVAC if severe',
  'COLD IMMERSION': '0-3 min: exit water. 3-30 min: cold incapacitation. Immersion suit & buddy system',
  'SEASICKNESS': 'Fresh air, focus horizon, ginger, electrolytes, Ondansetron, rest in calm area',
  'BLEEDING': 'Direct pressure (10-15 min), elevation, pressure points, tourniquet if limb',
  'FRACTURE': 'RICE (Rest/Ice/Compression/Elevation), immobilize, pain control, evacuate if severe',
  'BURNS': 'Cool water NOT ice, sterile dressing, pain relief, IV fluids if >10% body area',
  'CPR': '30 compressions : 2 breaths, 100-120 BPM, push hard/fast, continue until help arrives',
  'SHOCK': 'Horizontal, elevate legs, keep warm, IV fluids, oxygen, MEDEVAC URGENT',
  'DROWNING': 'Remove from water, clear airway, CPR, oxygen, monitor for pulmonary edema',
  'CHOKING': '5 back blows + 5 abdominal thrusts, repeat until dislodged',
};

const MAX_RECORD_LENGTH = 500;

export const Legen: React.FC = () => {
  const [records, setRecords] = useState<MedicalRecord[]>([
    {
      timestamp: new Date().toISOString(),
      type: 'vitals',
      data: 'HEART RATE: 72 BPM | BP: 120/80 | TEMP: 36.8°C',
      severity: 'low'
    }
  ]);

  const [newRecord, setNewRecord] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { assess, getStatus } = useLegen();
  const [moduleStatus, setModuleStatus] = useState<LegenStatus | null>(null);

  useEffect(() => {
    getStatus()
      .then(setModuleStatus)
      .catch(err => console.error('Failed to get Legen status:', err));
  }, [getStatus]);

  const performAssessment = async () => {
    const trimmedRecord = newRecord.trim();
    if (!trimmedRecord) {
      setError('Please enter symptoms before performing assessment.');
      return;
    }

    if (trimmedRecord.length > MAX_RECORD_LENGTH) {
      setError(`Record too long. Maximum ${MAX_RECORD_LENGTH} characters.`);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Parse symptoms from input (simple comma-separated for now)
      const symptoms = trimmedRecord.toLowerCase().split(',').map(s => s.trim());
      
      const assessment = await assess(symptoms, 'medium');
      
      const record: MedicalRecord = {
        timestamp: assessment.timestamp,
        type: 'assessment',
        data: `ASSESSMENT: ${symptoms.join(', ')} | TRIAGE: ${assessment.triage_level} | ${assessment.evacuation_needed ? 'EVACUATION REQUIRED' : 'NO EVACUATION'}`,
        severity: assessment.triage_level === 'RED' ? 'high' : assessment.triage_level === 'YELLOW' ? 'medium' : 'low',
        assessment
      };

      setRecords([record, ...records]);
      setNewRecord('');
      
      // Refresh status
      getStatus().then(setModuleStatus).catch(console.error);
    } catch (err) {
      console.error('Failed to perform assessment:', err);
      setError('Failed to perform medical assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const addRecord = () => {
    const trimmedRecord = newRecord.trim();
    if (!trimmedRecord) {
      setError('Please enter medical data before adding a record.');
      return;
    }

    if (trimmedRecord.length > MAX_RECORD_LENGTH) {
      setError(`Record too long. Maximum ${MAX_RECORD_LENGTH} characters.`);
      return;
    }
    
    const record: MedicalRecord = {
      timestamp: new Date().toISOString(),
      type: 'checkup',
      data: trimmedRecord,
      severity: 'low'
    };

    setRecords([record, ...records]);
    setNewRecord('');
    setError(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addRecord();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setNewRecord(value);
    if (value.length > MAX_RECORD_LENGTH) {
      setError(`Record too long. ${value.length}/${MAX_RECORD_LENGTH} characters.`);
    } else {
      setError(null);
    }
  };


  const characterCount = newRecord.length;
  const isNearLimit = characterCount > MAX_RECORD_LENGTH * 0.8;

  return (
    <div className="hud-panel">
      <h2>LEGEN - MEDICAL SYSTEM</h2>
      <div className="corner-br"></div>
      
      <div className="legen-status">
        <div className="terminal">
          <div className="terminal-line">CREW MEMBERS: 4</div>
          <div className="terminal-line">HEALTH STATUS: ALL NOMINAL</div>
          <div className="terminal-line">MEDICAL RECORDS: {records.length}</div>
          <div className="terminal-line">EMERGENCY PROTOCOLS: READY</div>
          {moduleStatus && (
            <>
              <div className="terminal-line">BACKEND ASSESSMENTS: {moduleStatus.total_assessments || 0}</div>
              <div className="terminal-line">RED TRIAGE: {moduleStatus.red_triage || 0}</div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="legen-error-message">
          ⚠ {error}
        </div>
      )}

      <div className="legen-input-section">
        <h3 className="legen-input-header">ADD MEDICAL RECORD / ASSESSMENT</h3>
        <div className="legen-input-container">
          <input
            id="medical-record-input"
            name="medicalRecord"
            type="text"
            className="hud-input legen-input-flex"
            placeholder="ENTER SYMPTOMS (comma-separated)..."
            value={newRecord}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            maxLength={MAX_RECORD_LENGTH}
            disabled={loading}
            aria-label="Medical record input"
            aria-describedby="record-char-count"
          />
          <button 
            className="hud-button" 
            onClick={addRecord}
            disabled={!newRecord.trim() || newRecord.length > MAX_RECORD_LENGTH || loading}
            aria-label="Add medical record"
          >
            ADD
          </button>
          <button 
            className="hud-button legen-assess-button" 
            onClick={performAssessment}
            disabled={!newRecord.trim() || newRecord.length > MAX_RECORD_LENGTH || loading}
            aria-label="Perform AI assessment"
          >
            {loading ? 'ASSESSING...' : 'ASSESS'}
          </button>
        </div>
        <div 
          id="record-char-count"
          className={`legen-char-count ${isNearLimit ? 'legen-char-count-warning' : ''}`}
        >
          {characterCount}/{MAX_RECORD_LENGTH} CHARACTERS
        </div>
      </div>

      <div>
        <h3 className="legen-history-header">MEDICAL HISTORY</h3>
        <div 
          className="data-stream legen-history-stream" 
          role="log"
          aria-live="polite"
          aria-label="Medical history"
        >
          {records.length === 0 ? (
            <div className="legen-history-empty">NO MEDICAL RECORDS.</div>
          ) : (
            records.map((record, idx) => (
              <div 
                key={idx}
                className={`legen-record legen-record-severity-${record.severity}`}
              >
                <div className="legen-record-header">
                  [{record.type.toUpperCase()}] {new Date(record.timestamp).toLocaleString()}
                </div>
                <div className={`legen-record-data-${record.severity}`}>
                  {record.data}
                </div>
                {record.assessment && (
                  <div className="legen-assessment">
                    <div><strong>RECOMMENDATIONS:</strong></div>
                    {record.assessment.recommendations.map((rec, i) => (
                      <div key={i} className="legen-assessment-rec">• {rec}</div>
                    ))}
                    {record.assessment.protocol && (
                      <div className="legen-assessment-protocol">
                        <strong>PROTOCOL:</strong> {record.assessment.protocol}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="legen-actions">
        <button className="hud-button" aria-label="Perform vital scan">
          VITAL SCAN
        </button>
        <button className="hud-button" aria-label="Emergency protocols">
          EMERGENCY
        </button>
        <button 
          className="hud-button" 
          onClick={() => {
            if (window.confirm('Are you sure you want to clear all medical history?')) {
              setRecords([]);
            }
          }}
          aria-label="Clear medical history"
        >
          CLEAR HISTORY
        </button>
      </div>

      <div className="legen-protocols">
        <h3 className="legen-protocols-header">⚡ QUICK MEDICAL PROTOCOLS</h3>
        <div className="legen-protocols-grid">
          {Object.entries(MEDICAL_PROTOCOLS).map(([protocol, steps]) => (
            <button
              key={protocol}
              onClick={() => {
                const record: MedicalRecord = {
                  timestamp: new Date().toISOString(),
                  type: 'protocol',
                  data: steps,
                  severity: protocol.includes('EMERGENCY') || protocol.includes('CPR') || protocol.includes('SHOCK') ? 'high' : 'medium',
                  protocol: protocol
                };
                setRecords([record, ...records]);
              }}
              className="legen-protocol-button"
            >
              {protocol}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
