import React, { useState, useEffect } from 'react';
import { useNMEA } from '../hooks/useNMEA';
import { WarningAlert } from './Alert';

export const Instruments: React.FC = () => {
  const nmeaData = useNMEA();
  const [dataAge, setDataAge] = useState<number>(0);

  useEffect(() => {
    const interval = setInterval(() => {
      if (nmeaData.timestamp) {
        const age = Math.floor((Date.now() - new Date(nmeaData.timestamp).getTime()) / 1000);
        setDataAge(age);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [nmeaData.timestamp]);

  const speed = nmeaData.speed ?? 0;
  const heading = nmeaData.heading ?? 0;
  const isDataStale = dataAge > 30;
  const hasData = nmeaData.timestamp !== undefined;

  const getSpeedColor = (spd: number): string => {
    if (spd > 20) return '#ff2020';
    if (spd > 10) return '#ffa500';
    return 'var(--arctic-green)';
  };

  return (
    <div className="hud-panel">
      <h2>INSTRUMENTS</h2>
      <div className="corner-br"></div>

      <WarningAlert 
        message="NO DATA - Waiting for instrument readings..." 
        show={!hasData} 
      />

      <WarningAlert 
        message={`STALE DATA - Last update ${dataAge} seconds ago`}
        show={isDataStale && hasData} 
      />
      
      <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '20px', flexWrap: 'wrap', gap: '20px' }}>
        <div className="gauge" role="img" aria-label={`Speed: ${speed.toFixed(1)} knots`}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '12px', opacity: 0.7 }}>SPEED</div>
            <div 
              className="gauge-value" 
              style={{ color: getSpeedColor(speed) }}
            >
              {speed.toFixed(1)}
            </div>
            <div style={{ fontSize: '12px', opacity: 0.7 }}>KTS</div>
          </div>
        </div>

        <div className="gauge" role="img" aria-label={`Heading: ${heading.toFixed(0)} degrees`}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '12px', opacity: 0.7 }}>HEADING</div>
            <div className="gauge-value">{heading.toFixed(0)}</div>
            <div style={{ fontSize: '12px', opacity: 0.7 }}>DEG</div>
          </div>
        </div>

        <div className="gauge" role="img" aria-label="Depth: standby">
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '12px', opacity: 0.7 }}>DEPTH</div>
            <div className="gauge-value" style={{ opacity: 0.5 }}>--</div>
            <div style={{ fontSize: '12px', opacity: 0.7 }}>M</div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '30px' }}>
        <h3 style={{ fontSize: '14px', marginBottom: '10px' }}>SYSTEM STATUS</h3>
        <div className="terminal">
          <div className="terminal-line">
            GPS: {nmeaData.latitude ? (
              <span style={{ color: 'var(--arctic-green)' }}>ACTIVE</span>
            ) : (
              <span style={{ color: 'var(--arctic-grey)' }}>STANDBY</span>
            )}
          </div>
          <div className="terminal-line">
            COMPASS: {nmeaData.heading !== undefined ? (
              <span style={{ color: 'var(--arctic-green)' }}>ACTIVE</span>
            ) : (
              <span style={{ color: 'var(--arctic-grey)' }}>STANDBY</span>
            )}
          </div>
          <div className="terminal-line">
            SPEED LOG: {nmeaData.speed !== undefined ? (
              <span style={{ color: 'var(--arctic-green)' }}>ACTIVE</span>
            ) : (
              <span style={{ color: 'var(--arctic-grey)' }}>STANDBY</span>
            )}
          </div>
          <div className="terminal-line">
            DEPTH SOUNDER: <span style={{ color: 'var(--arctic-grey)' }}>STANDBY</span>
          </div>
          {isDataStale && hasData && (
            <div className="terminal-line" style={{ color: '#ffa500' }}>
              WARNING: DATA STALE ({dataAge}s)
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
