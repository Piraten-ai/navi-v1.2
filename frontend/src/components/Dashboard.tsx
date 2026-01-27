import React from 'react';
import { useSettings } from '../hooks/useSettingsContext';
import { useSignalK } from '../hooks/useSignalK';
import { useBridgeSignals } from '../hooks/useBridgeSignals';
import { GaugeWidget } from './widgets/GaugeWidget';

export const Dashboard: React.FC = () => {
  const { settings } = useSettings();
  const { navData, connected } = useSignalK();
  const bridgeData = useBridgeSignals();

  // Real data from Signal K only - no mock data in production
  const gaugeData = {
    speed: {
      value: navData?.speed ?? 0,
      max: 30,
      unit: 'KN',
      label: 'SPEED'
    },
    heading: {
      value: navData?.heading ?? 0,
      max: 360,
      unit: 'Â°',
      label: 'HEADING'
    },
    depth: {
      value: navData?.depth ?? 0,
      max: 200,
      unit: 'M',
      label: 'DEPTH'
    },
    temp: {
      value: navData?.temperature ?? 0,
      max: 20,
      unit: 'Â°C',
      label: 'TEMP',
      min: -40
    },
  };

  return (
    <div className="dashboard-container">
      {!connected && (
        <div className="dashboard-warning" role="alert">
          âš ï¸ Not connected to Signal K - Displaying last known values
        </div>
      )}
      {navData && (
        <div className="dashboard-info">
          <div className="dashboard-info-text">
            Position: {navData.position && typeof navData.position.latitude === 'number' && typeof navData.position.longitude === 'number' ?
              `${navData.position.latitude.toFixed(4)}Â°N, ${navData.position.longitude.toFixed(4)}Â°E` : 'N/A'} |
            Last Update: {navData.timestamp ? new Date(navData.timestamp).toLocaleTimeString() : 'N/A'}
          </div>
        </div>
      )}
      {bridgeData && (
        <div className="bridge-panel">
          <div className="bridge-panel-title">Analog Bridge</div>
          <div className="bridge-panel-meta">
            Source: {bridgeData.source || 'arduino'} |
            Last Update: {bridgeData.timestamp ? new Date(bridgeData.timestamp).toLocaleTimeString() : 'N/A'}
          </div>
          <div className="bridge-panel-grid">
            {Object.entries(bridgeData.signals || {}).map(([key, value]) => (
              <div key={key} className="bridge-panel-item">
                <span className="bridge-key">{key}</span>
                <span className="bridge-value">{Number(value).toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}      <div className="dashboard-grid">
        {settings.widgets
          .filter(w => w.visible)
          .map(widget => {
            const data = gaugeData[widget.id as keyof typeof gaugeData];
            if (!data) return null;

            return (
              <div
                key={widget.id}
                className="dashboard-widget"
                data-grid-column={`${widget.position.x + 1} / span ${widget.size.w}`}
                data-grid-row={`${widget.position.y + 1} / span ${widget.size.h}`}
              >
                <GaugeWidget {...data} />
              </div>
            );
          })}
      </div>
    </div>
  );
};

