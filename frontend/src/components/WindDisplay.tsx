interface WindData {
  true_speed?: number
  true_direction?: number
  apparent_wind_speed?: number
  apparent_wind_angle?: number
  pred_speed?: number
  pred_dir?: number
  gust_speed?: number
  [key: string]: number | undefined
}

interface WindDisplayProps {
  data: WindData
}

export function WindDisplay({ data }: WindDisplayProps) {
  return (
    <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
      <h2 className="text-lg font-semibold mb-3">Wind</h2>
      <div className="space-y-2 text-sm">
        <div>
          <p className="text-gray-400">True Wind</p>
          <p className="text-lg font-bold">
            {data.true_speed?.toFixed(1) || '--'} kn @ {data.true_direction?.toFixed(0) || '--'}°
          </p>
        </div>
        {data.apparent_wind_speed !== undefined && (
          <div>
            <p className="text-gray-400">Apparent Wind</p>
            <p className="text-lg font-bold text-yellow-400">
              {data.apparent_wind_speed.toFixed(1)} kn @ {data.apparent_wind_angle?.toFixed(0) || '--'}°
            </p>
          </div>
        )}
        {data.gust_speed !== undefined && (
          <div>
            <p className="text-gray-400">Wind Gust</p>
            <p className="text-lg font-bold text-orange-400">{data.gust_speed.toFixed(1)} kn</p>
          </div>
        )}
        {data.pred_speed !== undefined && (
          <div>
            <p className="text-gray-400 text-xs">ML Prediction</p>
            <p className="text-sm font-bold text-purple-400">
              {data.pred_speed.toFixed(1)} kn @ {data.pred_dir?.toFixed(0) || '--'}°
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
