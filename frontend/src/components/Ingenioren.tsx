import React, { useState, useEffect } from 'react';
import { Cpu, Zap, Database, AlertTriangle, Thermometer, Activity } from 'lucide-react';

interface SystemMetrics {
  timestamp: string;
  cpu: {
    usage_percent: number;
    frequency_mhz: number | null;
    cores: number;
  };
  memory: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    usage_percent: number;
  };
  disk: {
    total_gb: number;
    used_gb: number;
    free_gb: number;
    usage_percent: number;
  };
  temperature: {
    cpu_temp_c?: number;
    available?: boolean;
  };
  system: {
    process_count: number;
    uptime_seconds: number;
    boot_time?: string;
  };
  fan: {
    mode: string;
    speed: number;
  };
  physics: {
    leeway_angle_deg: number;
    drift_speed_knot: number;
  };
}

interface HealthStatus {
  status: 'healthy' | 'warning' | 'critical' | 'unknown';
  health_score: number;
  factors: string[];
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  fan_speed: number;
  timestamp: string;
}

export const Ingenioren: React.FC<{ ws: WebSocket | null }> = ({ ws }) => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    if (!ws) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'ingenioren_metrics') {
          setMetrics(data.data);
          setLoading(false);
        } else if (data.type === 'ingenioren_health') {
          setHealth(data.health);
        } else if (data.type === 'ingenioren_alert') {
          setAlerts(prev => [...prev, data.alert].slice(-10));
        }
      } catch (e) {
        console.error('WebSocket parse error:', e);
      }
    };

    ws.addEventListener('message', handleMessage);
    return () => ws.removeEventListener('message', handleMessage);
  }, [ws]);

  const getHealthColor = (value: number, threshold: number = 80) => {
    if (value > threshold) return 'border-red-500 bg-red-950/30';
    if (value > threshold * 0.7) return 'border-yellow-500 bg-yellow-950/30';
    return 'border-green-500 bg-green-950/30';
  };

  const getHealthStatus = (): string => {
    if (!health) return 'unknown';
    if (health.status === 'critical') return '🔴 CRITICAL';
    if (health.status === 'warning') return '🟡 WARNING';
    if (health.status === 'healthy') return '🟢 HEALTHY';
    return '⚪ UNKNOWN';
  };

  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-b from-gray-900 to-black text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p className="text-lg text-gray-400">Linking to GORDON...</p>
          <p className="text-sm text-gray-600 mt-2">Initializing system diagnostics</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-gradient-to-b from-gray-900 to-black text-white">
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Cpu size={36} className="text-cyan-400" />
            <div>
              <h1 className="text-4xl font-bold">GORDON</h1>
              <p className="text-gray-400">System Engineer • Ingeniøren • Infrastructure Monitor</p>
            </div>
          </div>
          
          {health && (
            <div className="text-right">
              <div className="text-2xl font-bold">{getHealthStatus()}</div>
              <div className="text-cyan-400 text-lg">Score: {health.health_score}/100</div>
            </div>
          )}
        </div>

        {metrics && (
          <>
            {/* Critical Alerts */}
            {alerts.length > 0 && (
              <div className="mb-6 bg-red-950/50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="font-bold text-red-400 mb-2 flex items-center gap-2">
                  <AlertTriangle size={20} />
                  System Alerts ({alerts.length})
                </h3>
                <div className="space-y-1 text-sm">
                  {alerts.slice(-3).map((alert, i) => (
                    <div key={i} className="text-red-300">
                      • {alert.type}: {alert.message}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {/* CPU */}
              <div className={`p-4 rounded-lg border-2 ${getHealthColor(metrics.cpu.usage_percent)}`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-300 text-sm">CPU Usage</h3>
                  <Cpu size={18} className="text-cyan-400" />
                </div>
                <div className="text-3xl font-bold mb-2">{metrics.cpu.usage_percent.toFixed(1)}%</div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-cyan-500 h-2 rounded-full transition-all"
                    data-width={metrics.cpu.usage_percent}
                    ref={(el) => el && (el.style.width = `${metrics.cpu.usage_percent}%`)}
                  />
                </div>
                <div className="text-xs text-gray-400 mt-2">
                  {metrics.cpu.cores} cores • {metrics.cpu.frequency_mhz?.toFixed(0)} MHz
                </div>
              </div>

              {/* Memory */}
              <div className={`p-4 rounded-lg border-2 ${getHealthColor(metrics.memory.usage_percent)}`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-300 text-sm">Memory</h3>
                  <Database size={18} className="text-blue-400" />
                </div>
                <div className="text-3xl font-bold mb-2">{metrics.memory.usage_percent.toFixed(1)}%</div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    data-width={metrics.memory.usage_percent}
                    ref={(el) => el && (el.style.width = `${metrics.memory.usage_percent}%`)}
                  />
                </div>
                <div className="text-xs text-gray-400 mt-2">
                  {metrics.memory.used_gb} / {metrics.memory.total_gb} GB
                </div>
              </div>

              {/* Disk */}
              <div className={`p-4 rounded-lg border-2 ${getHealthColor(metrics.disk.usage_percent)}`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-300 text-sm">Disk Space</h3>
                  <Database size={18} className="text-orange-400" />
                </div>
                <div className="text-3xl font-bold mb-2">{metrics.disk.usage_percent.toFixed(1)}%</div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-orange-500 h-2 rounded-full transition-all"
                    data-width={metrics.disk.usage_percent}
                    ref={(el) => el && (el.style.width = `${metrics.disk.usage_percent}%`)}
                  />
                </div>
                <div className="text-xs text-gray-400 mt-2">
                  {metrics.disk.free_gb} GB free
                </div>
              </div>

              {/* Temperature */}
              <div className={`p-4 rounded-lg border-2 ${
                metrics.temperature.cpu_temp_c
                  ? getHealthColor(metrics.temperature.cpu_temp_c, 80)
                  : 'border-gray-700 bg-gray-800'
              }`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-300 text-sm">Temperature</h3>
                  <Thermometer size={18} className="text-red-400" />
                </div>
                <div className="text-3xl font-bold mb-2">
                  {metrics.temperature.cpu_temp_c?.toFixed(1) || 'N/A'}°C
                </div>
                {metrics.temperature.cpu_temp_c && (
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full transition-all"
                      data-width={Math.min(100, (metrics.temperature.cpu_temp_c / 100) * 100)}
                      ref={(el) => el && metrics.temperature.cpu_temp_c && (el.style.width = `${Math.min(100, (metrics.temperature.cpu_temp_c / 100) * 100)}%`)}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* System Info Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              {/* Uptime */}
              <div className="p-4 rounded-lg border-2 border-gray-700 bg-gray-800">
                <h3 className="font-semibold text-gray-300 text-sm mb-2">System Uptime</h3>
                <div className="text-2xl font-bold text-cyan-400">
                  {formatUptime(metrics.system.uptime_seconds)}
                </div>
                <div className="text-xs text-gray-400 mt-2">
                  Boot: {metrics.system.boot_time ? new Date(metrics.system.boot_time).toLocaleDateString() : 'N/A'}
                </div>
              </div>

              {/* Processes */}
              <div className="p-4 rounded-lg border-2 border-gray-700 bg-gray-800">
                <h3 className="font-semibold text-gray-300 text-sm mb-2">Processes</h3>
                <div className="text-2xl font-bold text-green-400">
                  {metrics.system.process_count}
                </div>
                <div className="text-xs text-gray-400 mt-2">Running</div>
              </div>

              {/* Fan Control */}
              <div className="p-4 rounded-lg border-2 border-gray-700 bg-gray-800">
                <h3 className="font-semibold text-gray-300 text-sm mb-2 flex items-center gap-2">
                  <Zap size={16} className="text-yellow-400" />
                  Fan Control
                </h3>
                <div className="text-2xl font-bold text-yellow-400">
                  {metrics.fan.speed}%
                </div>
                <div className="text-xs text-gray-400 mt-2">
                  Mode: {metrics.fan.mode}
                </div>
              </div>
            </div>

            {/* Physics Data */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="p-4 rounded-lg border-2 border-purple-700 bg-purple-950/30">
                <h3 className="font-semibold text-gray-300 text-sm mb-2 flex items-center gap-2">
                  <Activity size={16} className="text-purple-400" />
                  Leeway Angle
                </h3>
                <div className="text-2xl font-bold text-purple-400">
                  {metrics.physics.leeway_angle_deg.toFixed(2)}°
                </div>
                <div className="text-xs text-gray-400 mt-2">Wind-induced drift</div>
              </div>

              <div className="p-4 rounded-lg border-2 border-indigo-700 bg-indigo-950/30">
                <h3 className="font-semibold text-gray-300 text-sm mb-2 flex items-center gap-2">
                  <Activity size={16} className="text-indigo-400" />
                  Drift Speed
                </h3>
                <div className="text-2xl font-bold text-indigo-400">
                  {metrics.physics.drift_speed_knot.toFixed(2)} kt
                </div>
                <div className="text-xs text-gray-400 mt-2">Estimated speed loss</div>
              </div>
            </div>

            {/* Last Update */}
            <div className="text-center text-xs text-gray-500">
              Last update: {new Date(metrics.timestamp).toLocaleTimeString()}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
