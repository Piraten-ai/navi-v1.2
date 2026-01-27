interface AutopilotData {
  enabled?: boolean
  xte_m?: number
  xte_nm?: number
  rudder_target_deg?: number
  rudder_deg?: number
  desired_heading_deg?: number
  current_heading_deg?: number
  wind_compensation_deg?: number
  leeway_deg?: number
  leeway_psi?: number
  [key: string]: number | boolean | undefined
}

interface AutopilotStatusProps {
  data: AutopilotData
}

export function AutopilotStatus({ data }: AutopilotStatusProps) {
  const xte = data.xte_nm ? (data.xte_nm * 1852).toFixed(1) : data.xte_m?.toFixed(1) || '--'
  const xteSuffix = data.xte_nm ? 'nm' : 'm'

  return (
    <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">Autopilot</h2>
        <span
          className={`text-sm font-medium ${
            data.enabled ? 'text-green-400 bg-green-950 px-2 py-1 rounded' : 'text-gray-500'
          }`}
        >
          {data.enabled ? 'Active' : 'Standby'}
        </span>
      </div>
      <div className="space-y-2 text-sm">
        <p>
          XTE: <span className="font-bold text-blue-400">{xte} {xteSuffix}</span>
        </p>
        <p>
          Heading: <span className="font-bold text-blue-400">{data.desired_heading_deg?.toFixed(0) || '--'}°</span>
          {data.current_heading_deg && (
            <span className="ml-2 text-gray-500">(current: {data.current_heading_deg.toFixed(0)}°)</span>
          )}
        </p>
        <p>
          Rudder: <span className="font-bold text-orange-400">{data.rudder_target_deg?.toFixed(1) || '--'}°</span>
        </p>
        {data.wind_compensation_deg !== undefined && (
          <p>
            Wind Comp: <span className="font-bold text-yellow-400">{data.wind_compensation_deg.toFixed(1)}°</span>
          </p>
        )}
        {data.leeway_deg !== undefined && (
          <p>
            Leeway: <span className="font-bold text-yellow-400">{data.leeway_deg.toFixed(2)}°</span>
            {data.leeway_psi && <span className="ml-1 text-gray-500">@ {data.leeway_psi.toFixed(0)}°</span>}
          </p>
        )}
      </div>
    </div>
  )
}
