import { Monitor, Skull } from 'lucide-react'

interface BattleModeToggleProps {
  enabled: boolean
  onToggle: () => void
}

export function BattleModeToggle({ enabled, onToggle }: BattleModeToggleProps) {
  return (
    <button
      onClick={onToggle}
      className={`px-4 py-2 rounded-lg flex items-center gap-2 font-semibold transition-all transform hover:scale-105 ${
        enabled
          ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-600/50 border border-red-500'
          : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/50 border border-blue-500'
      }`}
    >
      {enabled ? <Skull size={20} /> : <Monitor size={20} />}
      <span>{enabled ? 'Battle Mode ON' : 'Battle Mode OFF'}</span>
    </button>
  )
}
