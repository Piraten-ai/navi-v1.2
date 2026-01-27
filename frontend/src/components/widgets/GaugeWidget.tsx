import React from 'react';

interface GaugeWidgetProps {
  value: number;
  max: number;
  min?: number;
  unit: string;
  label: string;
}

export const GaugeWidget: React.FC<GaugeWidgetProps> = ({ value, max, min = 0, unit, label }) => {
  // Ensure value is a valid number
  const numValue = typeof value === 'number' && !isNaN(value) ? value : 0;
  const range = max - min;
  const percentage = ((numValue - min) / range) * 100;
  const angle = (percentage / 100) * 270 - 135; // -135° to 135° (270° arc)

  // Determine color based on value
  const getColor = () => {
    if (percentage > 80) return '#ff2020'; // Warning red
    if (percentage > 60) return '#ffb000'; // Caution orange
    return 'var(--primary-color)'; // Normal cyan
  };

  return (
    <div className="gauge-widget">
      <div className="gauge-label">{label}</div>
      <div className="gauge-display">
        <svg viewBox="0 0 200 200" className="gauge-svg">
          {/* Background arc */}
          <path
            d="M 30 170 A 90 90 0 1 1 170 170"
            fill="none"
            stroke="rgba(0, 212, 255, 0.2)"
            strokeWidth="15"
            strokeLinecap="round"
          />
          {/* Value arc */}
          <path
            d="M 30 170 A 90 90 0 1 1 170 170"
            fill="none"
            stroke={getColor()}
            strokeWidth="15"
            strokeLinecap="round"
            strokeDasharray={`${(percentage / 100) * 424} 424`}
            style={{
              filter: `drop-shadow(0 0 8px ${getColor()})`,
            }}
          />
          {/* Center circle */}
          <circle
            cx="100"
            cy="100"
            r="60"
            fill="rgba(10, 21, 32, 0.9)"
            stroke={getColor()}
            strokeWidth="2"
          />
          {/* Needle */}
          <line
            x1="100"
            y1="100"
            x2="100"
            y2="40"
            stroke={getColor()}
            strokeWidth="3"
            strokeLinecap="round"
            transform={`rotate(${angle} 100 100)`}
            style={{
              filter: `drop-shadow(0 0 6px ${getColor()})`,
            }}
          />
          {/* Center dot */}
          <circle
            cx="100"
            cy="100"
            r="6"
            fill={getColor()}
            style={{
              filter: `drop-shadow(0 0 8px ${getColor()})`,
            }}
          />
        </svg>
        <div className="gauge-value" style={{ color: getColor() }}>
          {numValue.toFixed(1)}
          <span className="gauge-unit">{unit}</span>
        </div>
      </div>
      <div className="gauge-range">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
};
