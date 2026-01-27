import React, { ReactNode } from 'react';

interface PanelProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export const Panel: React.FC<PanelProps> = ({ title, children, className = '' }) => {
  return (
    <div className={`hud-panel ${className}`}>
      <h2>{title}</h2>
      <div className="corner-br"></div>
      {children}
    </div>
  );
};

// Terminal line interface for type safety
export interface TerminalLine {
  label: string;
  value: string | ReactNode;
  color?: string;
}

// Terminal display component for system information
interface TerminalProps {
  lines: TerminalLine[];
}

export const Terminal: React.FC<TerminalProps> = ({ lines }) => {
  return (
    <div className="terminal">
      {lines.map((line, idx) => (
        <div key={idx} className="terminal-line">
          {line.label}: {typeof line.value === 'string' ? (
            <span style={{ color: line.color }}>{line.value}</span>
          ) : (
            line.value
          )}
        </div>
      ))}
    </div>
  );
};

// Data stream component for logs and messages
interface DataStreamProps {
  children: ReactNode;
  maxHeight?: string;
  emptyMessage?: string;
  isEmpty?: boolean;
  ariaLabel?: string;
}

export const DataStream: React.FC<DataStreamProps> = ({ 
  children, 
  maxHeight = '300px',
  emptyMessage = 'NO DATA',
  isEmpty = false,
  ariaLabel = 'Data stream',
}) => {
  return (
    <div 
      className="data-stream" 
      style={{ maxHeight }}
      role="log"
      aria-live="polite"
      aria-label={ariaLabel}
    >
      {isEmpty ? (
        <div style={{ opacity: 0.5 }}>{emptyMessage}</div>
      ) : (
        children
      )}
    </div>
  );
};

// Button group component
interface ButtonGroupProps {
  children: ReactNode;
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({ children }) => {
  return (
    <div style={{ marginTop: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
      {children}
    </div>
  );
};
