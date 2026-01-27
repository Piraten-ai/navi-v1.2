import { Info, AlertTriangle, XCircle } from 'lucide-react'

interface Alert {
  severity: 'info' | 'warning' | 'critical'
  title: string
  message: string
  timestamp: string
}

interface AlertPanelProps {
  alerts: Alert[]
  maxHeight?: string
}

export function AlertPanel({ alerts, maxHeight = 'max-h-96' }: AlertPanelProps) {
  return (
    <div className={`bg-gray-900 p-4 rounded-lg border border-gray-700 ${maxHeight} overflow-y-auto`}>
      <h2 className="text-lg font-semibold mb-3">Alerts</h2>
      {alerts.length === 0 ? (
        <p className="text-gray-500">No active alerts</p>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert, i) => (
            <div
              key={i}
              className={`p-3 rounded border animate-fadeIn ${
                alert.severity === 'critical'
                  ? 'bg-red-950 border-red-700 text-red-300'
                  : alert.severity === 'warning'
                    ? 'bg-yellow-950 border-yellow-700 text-yellow-300'
                    : 'bg-blue-950 border-blue-700 text-blue-300'
              }`}
            >
              <div className="flex items-center gap-2">
                {alert.severity === 'critical' && <XCircle size={20} />}
                {alert.severity === 'warning' && <AlertTriangle size={20} />}
                {alert.severity === 'info' && <Info size={20} />}
                <h3 className="font-medium">{alert.title}</h3>
              </div>
              <p className="mt-1 text-sm">{alert.message}</p>
              <p className="text-xs mt-1 opacity-70">
                {new Date(alert.timestamp).toLocaleTimeString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
