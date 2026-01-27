interface AnomalyScoreProps {
  score: number
}

export function AnomalyScore({ score }: AnomalyScoreProps) {
  const getStatusColor = (s: number) => {
    if (s > -0.5) return { color: 'text-green-400', bg: 'bg-green-950', status: 'Normal' }
    if (s > -0.7) return { color: 'text-yellow-400', bg: 'bg-yellow-950', status: 'Warning' }
    return { color: 'text-red-400', bg: 'bg-red-950', status: 'Critical' }
  }

  const { color, bg, status } = getStatusColor(score)

  return (
    <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
      <h2 className="text-lg font-semibold mb-3">System Health</h2>
      <div className={`p-4 rounded-lg ${bg}`}>
        <p className={`text-4xl font-bold ${color}`}>{score.toFixed(2)}</p>
        <p className={`text-sm mt-2 font-medium ${color}`}>{status}</p>
        <div className="mt-3 w-full bg-gray-800 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              score > -0.5 ? 'bg-green-500' : score > -0.7 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${Math.max(0, Math.min(100, (score + 1) * 50))}%` }}
          />
        </div>
      </div>
    </div>
  )
}
