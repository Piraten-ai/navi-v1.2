import React from 'react';

type StatusType = 'online' | 'offline' | 'warning' | 'standby';

interface StatusBadgeProps {
  status: StatusType;
  label: string;
  showLabel?: boolean;
}

const statusColors: Record<StatusType, string> = {
  online: 'var(--arctic-green)',
  offline: '#ff2020',
  warning: '#ffa500',
  standby: 'var(--arctic-grey)',
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  label, 
  showLabel = true 
}) => {
  const color = statusColors[status];
  
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
      <div
        className={`status-indicator ${status}`}
        role="status"
        aria-label={`${label}: ${status}`}
        style={{
          display: 'inline-block',
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: color,
          boxShadow: `0 0 10px ${color}`,
        }}
      />
      {showLabel && <span>{label}</span>}
    </div>
  );
};

// Common status indicator for system components
interface SystemStatusProps {
  gpsActive?: boolean;
  compassActive?: boolean;
  backendOnline?: boolean;
  cameraStatus?: 'active' | 'standby' | 'error';
}

export const SystemStatusBar: React.FC<SystemStatusProps> = ({
  gpsActive = false,
  compassActive = false,
  backendOnline = false,
  cameraStatus = 'standby',
}) => {
  const getCameraStatusType = (status: 'active' | 'standby' | 'error'): StatusType => {
    if (status === 'active') return 'online';
    if (status === 'error') return 'offline';
    return 'warning';
  };

  return (
    <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', fontSize: '12px' }}>
      <StatusBadge 
        status={gpsActive ? 'online' : 'standby'} 
        label={`GPS ${gpsActive ? 'ACTIVE' : 'STANDBY'}`} 
      />
      <StatusBadge 
        status={compassActive ? 'online' : 'standby'} 
        label={`COMPASS ${compassActive ? 'ACTIVE' : 'STANDBY'}`} 
      />
      <StatusBadge 
        status={backendOnline ? 'online' : 'offline'} 
        label={`BACKEND ${backendOnline ? 'ONLINE' : 'OFFLINE'}`} 
      />
      <StatusBadge 
        status={getCameraStatusType(cameraStatus)} 
        label={`CAMERA ${cameraStatus.toUpperCase()}`} 
      />
    </div>
  );
};
