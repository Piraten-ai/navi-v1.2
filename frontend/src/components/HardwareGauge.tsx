interface HardwareData {
  cpu_temp?: number
  gpu_temp?: number
  fan_rpm?: number
  battery_voltage?: number
  [key: string]: number | string | undefined
}

interface HardwareGaugeProps {
  data: HardwareData
}

export function HardwareGauge({ data }: HardwareGaugeProps) {
  const metrics = [
    { label: 'CPU Temp', value: data.cpu_temp, unit: '°C', warn: 80, crit: 95 },
    { label: 'GPU Temp', value: data.gpu_temp, unit: '°C', warn: 80, crit: 95 },
    { label: 'Fan RPM', value: data.fan_rpm, unit: 'RPM', warn: 5000, crit: 7000 },
    { label: 'Battery', value: data.battery_voltage, unit: 'V', warn: 11.8, crit: 10.5 }
  ]

  const getColor = (value?: number, warn?: number, crit?: number) => {
    if (!value) return 'text-gray-400'
    if (warn && value > warn) {
      if (crit && value > crit) return 'text-red-400'
      return 'text-yellow-400'
    }
    return 'text-green-400'
  }

  return (
    <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
      <h2 className="text-lg font-semibold mb-3">Hardware Status</h2>
      <div className="grid grid-cols-2 gap-4">
        {metrics.map((metric) => (
          <div key={metric.label}>
            <p className="text-sm text-gray-400">{metric.label}</p>
            <p className={`text-2xl font-bold ${getColor(metric.value, metric.warn, metric.crit)}`}>
              {metric.value?.toFixed(metric.unit === 'RPM' ? 0 : 1) || '--'}
              <span className="text-sm ml-1">{metric.unit}</span>
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
