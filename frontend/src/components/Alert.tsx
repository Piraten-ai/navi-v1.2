import React from 'react';

type AlertType = 'warning' | 'error' | 'success' | 'info';

interface AlertProps {
  type: AlertType;
  message: string;
  show?: boolean;
}

const alertStyles: Record<AlertType, { border: string; background: string; color: string }> = {
  warning: {
    border: '2px solid #ffa500',
    background: 'rgba(255, 165, 0, 0.1)',
    color: '#ffa500',
  },
  error: {
    border: '2px solid #ff2020',
    background: 'rgba(255, 32, 32, 0.1)',
    color: '#ff2020',
  },
  success: {
    border: '2px solid var(--arctic-green)',
    background: 'rgba(0, 255, 65, 0.1)',
    color: 'var(--arctic-green)',
  },
  info: {
    border: '2px solid var(--arctic-blue)',
    background: 'rgba(0, 212, 255, 0.1)',
    color: 'var(--arctic-blue)',
  },
};

const alertIcons: Record<AlertType, string> = {
  warning: '⚠',
  error: '⚠',
  success: '✓',
  info: 'ℹ',
};

export const Alert: React.FC<AlertProps> = ({ type, message, show = true }) => {
  if (!show) return null;

  const styles = alertStyles[type];
  const icon = alertIcons[type];

  return (
    <div
      style={{
        marginBottom: '15px',
        padding: '10px',
        ...styles,
      }}
      role="alert"
      aria-live={type === 'error' || type === 'warning' ? 'assertive' : 'polite'}
    >
      {icon} {message}
    </div>
  );
};

// Specialized alert components for common use cases
export const WarningAlert: React.FC<{ message: string; show?: boolean }> = ({ message, show }) => (
  <Alert type="warning" message={message} show={show} />
);

export const ErrorAlert: React.FC<{ message: string; show?: boolean }> = ({ message, show }) => (
  <Alert type="error" message={message} show={show} />
);

export const SuccessAlert: React.FC<{ message: string; show?: boolean }> = ({ message, show }) => (
  <Alert type="success" message={message} show={show} />
);

export const InfoAlert: React.FC<{ message: string; show?: boolean }> = ({ message, show }) => (
  <Alert type="info" message={message} show={show} />
);
