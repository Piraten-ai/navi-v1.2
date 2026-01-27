import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker } from 'react-leaflet'
import type { MapContainerProps, TileLayerProps } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useWebSocket } from './hooks/useWebSocket'
import { SettingsProvider } from './hooks/useSettings'
import { AlertPanel } from './components/AlertPanel'
import { AutopilotStatus } from './components/AutopilotStatus'
import { WindDisplay } from './components/WindDisplay'
import { AnomalyScore } from './components/AnomalyScore'
import { AISOverlay } from './components/AISOverlay'
import { BattleModeToggle } from './components/BattleModeToggle'
import { VoiceControls } from './components/VoiceControls'
import { Map } from './components/Map'
import { Instruments } from './components/Instruments'
import { Vakten } from './components/Vakten'
import { Navi } from './components/Navi'
import { Navigator } from './components/Navigator'
import { Legen } from './components/Legen'
import { Psykologen } from './components/Psykologen'
import { Ingenioren } from './components/Ingenioren'
import { Dashboard } from './components/Dashboard'
import { Settings } from './components/Settings'

type Module = 'autonomy' | 'dashboard' | 'map' | 'instruments' | 'vakten' | 'navi' | 'navigator' | 'legen' | 'psykologen' | 'ingenioren'

// Derive WebSocket URL from API URL or current hostname
const API_URL = (import.meta.env.VITE_API_URL as string | undefined) || `http://${window.location.hostname}:8000`
const WS_URL = (import.meta.env.VITE_WS_URL as string | undefined) || `${API_URL.replace(/^http/, 'ws')}/ws`

function AutonomyDashboard({ ws }: { ws: any, isConnected: boolean }) {
  const [position, setPosition] = useState<[number, number] | null>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [aisTargets, setAisTargets] = useState<any[]>([])
  const [_autopilot, setAutopilot] = useState<any>({})
  const [_wind, setWind] = useState<any>({})
  const [_anomaly, setAnomaly] = useState<number>(0)
  const [_hwData, setHwData] = useState<any>({})

  useEffect(() => {
    if (!ws) return

    const handleMessage = (event: MessageEvent) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'gps_update' || msg.type === 'gnss_update') {
          setPosition([msg.latitude, msg.longitude])
        } else if (msg.type === 'hardware_monitor_update') {
          setHwData(msg.data)
        } else if (msg.type === 'autopilot_status') {
          setAutopilot(msg)
        } else if (msg.type === 'wind_update') {
          setWind(msg)
        } else if (msg.type === 'anomaly_score') {
          setAnomaly(msg.score)
        } else if (msg.type === 'ais_target_update') {
          setAisTargets(prev => {
            const exists = prev.find(t => t.mmsi === msg.data.mmsi)
            if (exists) return prev.map(t => t.mmsi === msg.data.mmsi ? msg.data : t)
            return [...prev, msg.data]
          })
        } else if (msg.type === 'alert') {
          setAlerts(prev => [msg, ...prev].slice(0, 50))
        }
      } catch (_err) { console.error(_err) }
    }

    ws.addEventListener('message', handleMessage)
    return () => ws.removeEventListener('message', handleMessage)
  }, [ws])

  return (
    <div className="grid grid-cols-1 gap-6">
      <div className="h-[400px] bg-black/40 rounded border border-cyan-900/50 overflow-hidden relative">
        <MapContainer
          {...({
            center: position || [59.0, 10.5],
            zoom: 13,
            style: { height: '100%', width: '100%', filter: 'invert(1) hue-rotate(180deg) brightness(0.6)' }
          } as MapContainerProps)}
        >
          <TileLayer {...({ url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' } as TileLayerProps)} />
          {position && <Marker position={position} />}
          <AISOverlay targets={aisTargets} />
        </MapContainer>
        <div className="absolute top-4 right-4 z-[1000] bg-black/80 p-2 border border-cyan-500 text-[10px] font-mono">
          RADAR ACTIVE | AIS: {aisTargets.length} TARGETS
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-black/20 p-4 border border-cyan-900/30 rounded">
          <h3 className="text-xs font-bold mb-4 text-cyan-400">VOICE COMMAND INTERFACE</h3>
          <VoiceControls ws={ws} />
        </div>
        <AlertPanel alerts={alerts} maxHeight="max-h-[200px]" />
      </div>
    </div>
  )
}

function AppContent() {
  const [activeModule, setActiveModule] = useState<Module>('autonomy')
  const [battleMode, setBattleMode] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const { ws, isConnected } = useWebSocket(WS_URL)
  
  const [hwData, setHwData] = useState<any>({})
  const [autopilot, setAutopilot] = useState<any>({})
  const [wind, setWind] = useState<any>({})
  const [anomaly, setAnomaly] = useState<number>(0)

  useEffect(() => {
    if (!ws) return
    const handleMessage = (event: MessageEvent) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'hardware_monitor_update') setHwData(msg.data)
        else if (msg.type === 'autopilot_status') setAutopilot(msg)
        else if (msg.type === 'wind_update') setWind(msg)
        else if (msg.type === 'anomaly_score') setAnomaly(msg.score)
      } catch {}
    }
    ws.addEventListener('message', handleMessage)
    return () => ws.removeEventListener('message', handleMessage)
  }, [ws])

  const modules: { id: Module; label: string; icon: string }[] = [
    { id: 'autonomy', label: 'AUTONOMY', icon: '🤖' },
    { id: 'dashboard', label: 'DASHBOARD', icon: '📊' },
    { id: 'map', label: 'MAP', icon: '🗺️' },
    { id: 'instruments', label: 'BRIDGE', icon: '⚙️' },
    { id: 'vakten', label: 'VISION', icon: '👁️' },
    { id: 'navi', label: 'NAVI AI', icon: '💬' },
    { id: 'navigator', label: 'NAVTEX', icon: '📡' },
    { id: 'legen', label: 'MEDIC', icon: '⚕️' },
    { id: 'psykologen', label: 'PSYCH', icon: '🧠' },
    { id: 'ingenioren', icon: '🔧', label: 'ENGIN' }
  ]

  const renderModule = () => {
    switch (activeModule) {
      case 'autonomy': return <AutonomyDashboard ws={ws} isConnected={isConnected} />
      case 'dashboard': return <Dashboard />
      case 'map': return <Map />
      case 'instruments': return <Instruments />
      case 'vakten': return <Vakten />
      case 'navi': return <Navi ws={ws} />
      case 'navigator': return <Navigator />
      case 'legen': return <Legen />
      case 'psykologen': return <Psykologen />
      case 'ingenioren': return <Ingenioren ws={ws} />
      default: return <AutonomyDashboard ws={ws} isConnected={isConnected} />
    }
  }

  return (
    <div className={`arctic-hud ${battleMode ? 'battle-mode' : ''}`}>
      {battleMode && <div className="battle-mode-indicator">⚠ BATTLE MODE ACTIVE ⚠</div>}

      <header className="hud-header-bar">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-black tracking-tighter">AADS PRO <span className="text-xs font-normal opacity-50 ml-2">v4.2.0-JETSON</span></h1>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex gap-4 text-[10px] font-mono">
            <span className={isConnected ? 'online' : 'offline'}>● BACKEND</span>
            <span className="online">● NMEA</span>
            <span className="online">● GPU-ACCEL</span>
          </div>
          <BattleModeToggle enabled={battleMode} onToggle={() => setBattleMode(!battleMode)} />
          <button className="bg-cyan-500/10 border border-cyan-500/50 px-3 py-1 text-[10px] hover:bg-cyan-500/30" onClick={() => setShowSettings(true)}>⚙ SETTINGS</button>
        </div>
      </header>

      <main className="center-command">
        <div className="module-content">
          {renderModule()}
        </div>
      </main>

      <aside className="right-panels">
        <div className="panel-box">
          <div className="panel-title">MISSION STATUS</div>
          <div className="status-grid font-mono">
            <div className="status-item"><span>UPTIME</span><span>04:12:44</span></div>
            <div className="status-item"><span>CPU LOAD</span><span>{hwData.cpu_percent || 0}%</span></div>
            <div className="status-item"><span>MEM USED</span><span>{hwData.memory_percent || 0}%</span></div>
            <div className="status-item"><span>TEMP</span><span>{hwData.cpu_temp || 42}°C</span></div>
          </div>
        </div>
        
        <AutopilotStatus data={autopilot} />
        <WindDisplay data={wind} />
        <AnomalyScore score={anomaly} />
      </aside>

      <nav className="bottom-modules">
        {modules.map((m) => (
          <button
            key={m.id}
            className={`module-icon-btn ${activeModule === m.id ? 'active' : ''}`}
            onClick={() => setActiveModule(m.id)}
          >
            <span className="icon-circle">{m.icon}</span>
            <span className="icon-label">{m.label}</span>
          </button>
        ))}
      </nav>

      {showSettings && <Settings onClose={() => setShowSettings(false)} />}
    </div>
  )
}

export default function App() {
  return (
    <SettingsProvider>
      <AppContent />
    </SettingsProvider>
  )
}
