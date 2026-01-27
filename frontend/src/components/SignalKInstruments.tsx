import React, { useState, useEffect } from 'react';

interface AutopilotData {
  state: string;
  target: number;
  mode: string;
}

export const SignalKInstruments: React.FC = () => {
  const [autopilot, setAutopilot] = useState<AutopilotData | null>(null);
  
  const signalkHost = import.meta.env.VITE_SIGNALK_HOST || `http://${window.location.hostname}:3001`;

  // Fetch autopilot data
  useEffect(() => {
    const fetchAutopilot = async () => {
      try {
        const response = await fetch(`${signalkHost}/signalk/v1/api/vessels/self/steering/autopilot`);
        if (response.ok) {
          const data = await response.json();
          setAutopilot({
            state: data.state?.value || 'unknown',
            target: data.target?.value || 0,
            mode: data.mode?.value || 'standby'
          });
        }
      } catch (error) {
        console.error('Failed to fetch autopilot data:', error);
      }
    };

    fetchAutopilot();
    const interval = setInterval(fetchAutopilot, 2000);
    return () => clearInterval(interval);
  }, [signalkHost]);

  return (
    <div className="signalk-container">
      <div className="signalk-header">
        <h2>Signal K Navigation</h2>
        {autopilot && (
          <div className="autopilot-status">
            <span className={`status-indicator ${autopilot.state}`}>
              {autopilot.state.toUpperCase()}
            </span>
            <span className="autopilot-target">
              Target: {autopilot.target.toFixed(0)}°
            </span>
            <span className="autopilot-mode">
              Mode: {autopilot.mode}
            </span>
          </div>
        )}
      </div>

      <div className="signalk-panels">
        {/* Freeboard Map */}
        <div className="signalk-panel">
          <h3>Freeboard Map</h3>
          <iframe
            src={`${signalkHost}/@signalk/freeboard-sk`}
            title="Freeboard Map"
            className="signalk-iframe iframe-full"
          />
        </div>

        {/* Instrument Panel */}
        <div className="signalk-panel">
          <h3>Instruments</h3>
          <iframe
            src={`${signalkHost}/admin/#/dashboard`}
            title="Signal K Instruments"
            className="signalk-iframe iframe-full"
          />
        </div>

        {/* Admin Panel Link */}
        <div className="signalk-links">
          <a 
            href={`${signalkHost}/admin/#/documentation`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="signalk-link"
          >
            📖 API Documentation
          </a>
          <a 
            href={`${signalkHost}/admin`} 
            target="_blank" 
            rel="noopener noreferrer"
            className="signalk-link"
          >
            ⚙️ Admin Panel
          </a>
        </div>
      </div>
    </div>
  );
};
