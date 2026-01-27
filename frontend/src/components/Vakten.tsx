import React, { useState, useEffect, useRef } from 'react';
import { ErrorAlert } from './Alert';

export const Vakten: React.FC = () => {
  const [detections, setDetections] = useState<string[]>([
    'SCANNING SECTOR 001...',
    'SCANNING SECTOR 002...',
    'SCANNING SECTOR 003...',
  ]);
  const [isScanning, setIsScanning] = useState(false);
  const [cameraStatus, setCameraStatus] = useState<'standby' | 'active' | 'error'>('standby');
  const [cameraSource, setCameraSource] = useState<'webcam' | 'ip'>('webcam');
  const [ipCameraUrl, setIpCameraUrl] = useState('');
  const [showIpCameraInput, setShowIpCameraInput] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    // Cleanup camera stream on unmount
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startWebcam = async () => {
    try {
      addDetection('Requesting webcam access...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraStatus('active');
        setCameraSource('webcam');
        addDetection('Webcam activated successfully');
      }
    } catch (error) {
      console.error('Webcam error:', error);
      setCameraStatus('error');
      const errorMessage = error instanceof Error ? error.message : String(error);
      addDetection('ERROR: Failed to access webcam - ' + errorMessage);
    }
  };

  const startIpCamera = () => {
    if (!ipCameraUrl.trim()) {
      addDetection('ERROR: Please enter IP camera URL');
      return;
    }

    try {
      addDetection(`Connecting to IP camera: ${ipCameraUrl}`);
      
      if (videoRef.current) {
        // Stop any existing webcam stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
        
        videoRef.current.src = ipCameraUrl;
        setCameraStatus('active');
        setCameraSource('ip');
        addDetection('IP camera connected successfully');
        setShowIpCameraInput(false);
      }
    } catch (error) {
      console.error('IP Camera error:', error);
      setCameraStatus('error');
      addDetection('ERROR: Failed to connect to IP camera');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.src = '';
    }
    
    setCameraStatus('standby');
    addDetection(`Camera ${cameraSource === 'webcam' ? '(Webcam)' : '(IP)'} deactivated`);
  };

  const handleScan = () => {
    if (cameraStatus === 'error') {
      addDetection('ERROR: Cannot scan - Camera offline');
      return;
    }

    setIsScanning(true);
    addDetection('MANUAL SCAN INITIATED');
    
    // Simulate scan duration
    setTimeout(() => {
      addDetection('SCAN COMPLETE - NO THREATS DETECTED');
      setIsScanning(false);
    }, 2000);
  };

  const addDetection = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setDetections(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const handleClearLog = () => {
    if (window.confirm('Clear detection log?')) {
      setDetections([]);
    }
  };

  return (
    <div className="hud-panel">
      <h2>VAKTEN - VISION SYSTEM</h2>
      <div className="corner-br"></div>
      
      <div style={{ marginBottom: '20px' }}>
        <div className="terminal">
          <div className="terminal-line">AI MODEL: YOLO v8</div>
          <div className="terminal-line">DETECTION CLASSES: 80</div>
          <div className="terminal-line">CONFIDENCE THRESHOLD: 0.65</div>
          <div className="terminal-line">
            CAMERA: {cameraStatus === 'active' ? (
              <span style={{ color: 'var(--arctic-green)' }}>
                ACTIVE ({cameraSource === 'webcam' ? 'WEBCAM' : 'IP CAMERA'})
              </span>
            ) : cameraStatus === 'error' ? (
              <span style={{ color: '#ff2020' }}>ERROR</span>
            ) : (
              <span style={{ color: 'var(--arctic-grey)' }}>STANDBY</span>
            )}
          </div>
          <div className="terminal-line">
            STATUS: {isScanning ? (
              <span style={{ color: 'var(--arctic-blue)' }}>SCANNING...</span>
            ) : (
              <span style={{ color: 'var(--arctic-green)' }}>READY</span>
            )}
          </div>
        </div>
      </div>

      <ErrorAlert 
        message="CAMERA ERROR - Vision system offline. Check camera connection."
        show={cameraStatus === 'error'} 
      />

      <div className="vision-feed">
        {cameraStatus === 'active' ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              width: '100%',
              height: 'auto',
              maxHeight: '400px',
              border: '2px solid var(--primary-color)',
              background: '#000',
            }}
            onError={() => {
              setCameraStatus('error');
              addDetection('ERROR: Camera feed failed');
            }}
          />
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--primary-color)', opacity: 0.5, padding: '60px 20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '10px' }}>
              {isScanning ? '◉' : '○'}
            </div>
            <div>
              {cameraStatus === 'error' ? 'CAMERA OFFLINE' : 'CAMERA FEED STANDBY'}
            </div>
            <div style={{ fontSize: '12px', marginTop: '10px' }}>360° VISION DETECTION</div>
            {isScanning && (
              <div style={{ 
                marginTop: '15px', 
                fontSize: '14px',
                color: 'var(--arctic-blue)',
                animation: 'pulse-green 2s infinite'
              }}>
                SCANNING IN PROGRESS...
              </div>
            )}
          </div>
        )}
      </div>

      {showIpCameraInput && (
        <div style={{ 
          marginTop: '15px', 
          marginBottom: '15px',
          padding: '15px', 
          border: '2px solid var(--arctic-blue)',
          background: 'rgba(0, 212, 255, 0.05)'
        }}>
          <h4 style={{ fontSize: '12px', marginBottom: '10px' }}>IP CAMERA CONFIGURATION</h4>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input
              id="ip-camera-url"
              name="ipCameraUrl"
              type="text"
              className="hud-input"
              placeholder="Enter IP camera URL (e.g., http://192.168.1.100:8080/video)"
              value={ipCameraUrl}
              onChange={(e) => setIpCameraUrl(e.target.value)}
              style={{ flex: 1 }}
              aria-label="IP camera URL"
            />
            <button 
              className="hud-button" 
              onClick={startIpCamera}
              aria-label="Connect to IP camera"
            >
              CONNECT
            </button>
            <button 
              className="hud-button" 
              onClick={() => setShowIpCameraInput(false)}
              aria-label="Cancel"
            >
              CANCEL
            </button>
          </div>
          <div style={{ fontSize: '11px', opacity: 0.7 }}>
            Examples: http://192.168.1.100:8080/video, rtsp://camera.local/stream
          </div>
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <h3 style={{ fontSize: '14px', marginBottom: '10px' }}>DETECTION LOG</h3>
        <div 
          className="data-stream"
          role="log"
          aria-live="polite"
          aria-label="Detection log"
        >
          {detections.length === 0 ? (
            <div style={{ opacity: 0.5 }}>NO DETECTIONS LOGGED</div>
          ) : (
            detections.map((detection, idx) => (
              <div key={idx} style={{ marginBottom: '5px' }}>
                {detection}
              </div>
            ))
          )}
        </div>
      </div>

      <div style={{ marginTop: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {cameraStatus === 'standby' ? (
          <>
            <button 
              className="hud-button" 
              onClick={startWebcam}
              aria-label="Activate webcam"
            >
              ACTIVATE WEBCAM
            </button>
            <button 
              className="hud-button" 
              onClick={() => setShowIpCameraInput(!showIpCameraInput)}
              aria-label="Configure IP camera"
            >
              IP CAMERA
            </button>
          </>
        ) : (
          <button 
            className="hud-button"
            onClick={stopCamera}
            aria-label="Deactivate camera"
            style={{ borderColor: '#ff2020', color: '#ff2020' }}
          >
            DEACTIVATE CAMERA
          </button>
        )}
        <button 
          className="hud-button" 
          onClick={handleScan}
          disabled={isScanning || cameraStatus !== 'active'}
          aria-label={isScanning ? 'Scanning in progress' : 'Start manual scan'}
        >
          {isScanning ? 'SCANNING...' : 'SCAN'}
        </button>
        <button 
          className="hud-button" 
          onClick={handleClearLog}
          disabled={detections.length === 0}
          aria-label="Clear detection log"
        >
          CLEAR LOG
        </button>
      </div>
    </div>
  );
};
