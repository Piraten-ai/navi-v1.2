import React, { useState, useEffect } from 'react';
import { useNMEA } from '../hooks/useNMEA';
import { WarningAlert } from './Alert';

export const Map: React.FC = () => {
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

  const formatCoordinate = (value: number | undefined, isLat: boolean): string => {
    if (value === undefined) return 'N/A';
    const direction = isLat ? (value >= 0 ? 'N' : 'S') : (value >= 0 ? 'E' : 'W');
    return `${Math.abs(value).toFixed(6)}° ${direction}`;
  };

  const isDataStale = dataAge > 30;
  const hasValidPosition = nmeaData.latitude !== undefined && nmeaData.longitude !== undefined;

  return (
    <div className="hud-panel">
      <h2>GPS POSITION</h2>
      <div className="corner-br"></div>
      
      <WarningAlert 
        message="NO GPS FIX - Waiting for position data..." 
        show={!hasValidPosition} 
      />

      <WarningAlert 
        message={`STALE DATA - Last update ${dataAge}s ago`}
        show={isDataStale && hasValidPosition} 
      />
      
      <div className="map-grid">
        <div className="position-data">
          <div className="data-row">
            <span className="data-label">LAT</span>
            <span className="data-value">{formatCoordinate(nmeaData.latitude, true)}</span>
          </div>
          
          <div className="data-row">
            <span className="data-label">LON</span>
            <span className="data-value">{formatCoordinate(nmeaData.longitude, false)}</span>
          </div>

          <div className="data-row-group">
            {nmeaData.speed !== undefined && (
              <div className="data-row compact">
                <span className="data-label">SPEED</span>
                <span className="data-value-small">{nmeaData.speed.toFixed(1)} kts</span>
              </div>
            )}

            {nmeaData.heading !== undefined && (
              <div className="data-row compact">
                <span className="data-label">HDG</span>
                <span className="data-value-small">
                  {nmeaData.heading.toFixed(0)}° ({getCardinalDirection(nmeaData.heading)})
                </span>
              </div>
            )}
          </div>
        </div>
        
        <div className="map-placeholder">
          <div className="map-placeholder-text">
            <div style={{ fontSize: '48px', marginBottom: '10px' }}>📍</div>
            <div>REAL-TIME MAP</div>
            <div style={{ fontSize: '10px', opacity: 0.5, marginTop: '5px' }}>
              Integration: OpenStreetMap / Leaflet
            </div>
            {hasValidPosition && (
              <div style={{ fontSize: '11px', marginTop: '10px', color: 'var(--secondary-color)' }}>
                Position: {nmeaData.latitude?.toFixed(4)}°, {nmeaData.longitude?.toFixed(4)}°
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="footer-info">
        <div style={{ fontSize: '11px', opacity: 0.6 }}>
          {nmeaData.timestamp ? (
            <>UPDATED: {new Date(nmeaData.timestamp).toLocaleTimeString()}</>
          ) : (
            <>WAITING...</>
          )}
        </div>
        {hasValidPosition && (
          <div 
            className="status-indicator" 
            style={{ 
              display: 'inline-block',
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              background: isDataStale ? '#ffa500' : 'var(--arctic-green)',
              boxShadow: isDataStale ? '0 0 10px #ffa500' : '0 0 10px var(--arctic-green)',
            }}
            aria-label={isDataStale ? 'GPS data stale' : 'GPS active'}
          />
        )}
      </div>
    </div>
  );
};

function getCardinalDirection(heading: number): string {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const index = Math.round(((heading % 360) / 45)) % 8;
  return directions[index];
}
