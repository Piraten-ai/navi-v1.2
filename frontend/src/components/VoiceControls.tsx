import { Mic, Volume2, VolumeX, Loader } from 'lucide-react'
import { useRef, useState } from 'react'

interface VoiceControlsProps {
  ws: WebSocket | null
}

export function VoiceControls({ ws }: VoiceControlsProps) {
  const [recording, setRecording] = useState(false)
  const [muted, setMuted] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })

      streamRef.current = stream
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' })

        // Send to backend via WebSocket
        if (ws && ws.readyState === WebSocket.OPEN) {
          const reader = new FileReader()
          reader.onload = (e) => {
            if (e.target?.result instanceof ArrayBuffer) {
              ws.send(
                JSON.stringify({
                  type: 'voice_input',
                  audio: Array.from(new Uint8Array(e.target.result))
                })
              )
            }
          }
          reader.readAsArrayBuffer(audioBlob)
        }

        // Clean up
        stream.getTracks().forEach((track) => track.stop())
        setRecording(false)
      }

      mediaRecorder.start()
      setRecording(true)

      // Auto-stop after 5 seconds
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop()
        }
      }, 5000)
    } catch (err) {
      console.error('Microphone access error:', err)
      alert('Microphone access denied. Please enable microphone permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      setRecording(false)
    }
  }

  return (
    <div className="flex items-center gap-3 p-4 bg-gray-900/80 backdrop-blur rounded-lg border border-gray-700">
      <button
        onClick={recording ? stopRecording : startRecording}
        disabled={!ws}
        className={`p-3 rounded-full transition-all transform hover:scale-110 ${
          recording ? 'bg-red-600 animate-pulse text-white' : 'bg-blue-600 hover:bg-blue-700 text-white'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
        title={recording ? 'Stop Recording' : 'Speak to NAVI'}
      >
        {recording ? <Loader size={24} className="animate-spin" /> : <Mic size={24} />}
      </button>

      <button
        onClick={() => setMuted(!muted)}
        className="p-3 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors"
        title={muted ? 'Unmute Alerts' : 'Mute Alerts'}
      >
        {muted ? <VolumeX size={24} /> : <Volume2 size={24} />}
      </button>

      <div className="flex-1">
        {recording && (
          <div className="flex items-center gap-2">
            <span className="text-red-400 font-medium text-sm">Listening...</span>
            <div className="flex gap-1">
              <div className="h-2 w-1 bg-red-500 rounded animate-pulse" />
              <div className="h-2 w-1 bg-red-500 rounded animate-pulse animation-delay-200" />
              <div className="h-2 w-1 bg-red-500 rounded animate-pulse animation-delay-400" />
            </div>
          </div>
        )}
        {!ws && <span className="text-gray-500 text-sm">WebSocket disconnected</span>}
        {muted && <span className="text-gray-400 text-sm">Alerts muted</span>}
      </div>
    </div>
  )
}
