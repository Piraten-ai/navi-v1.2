# AADS Build Specification

## Complete Technical Specifications for Arctic Autonomy Decision Support System

Version: 1.0  
Target: NVIDIA Jetson Nano 8GB / Orin NX 16GB  
Status: Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Module Specifications](#module-specifications)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Deployment Configuration](#deployment-configuration)
8. [Testing Requirements](#testing-requirements)
9. [Security](#security)
10. [Performance Targets](#performance-targets)

---

## 1. System Overview

### 1.1 Core Technology Stack

**Backend:**
- Python 3.10+
- FastAPI 0.104+
- Uvicorn (ASGI server)
- WebSocket support
- SQLAlchemy ORM

**Frontend:**
- React 18+
- TypeScript 5+
- Vite build tool
- Tailwind CSS
- WebSocket client

**Databases:**
- PostgreSQL 15+ (persistent data)
- InfluxDB 2.7+ (time-series metrics)
- Redis 7+ (pub/sub, caching)
- MinIO (S3-compatible object storage)

**AI/ML:**
- Ollama (LLM inference)
- YOLOv8 (object detection)
- Whisper (speech-to-text, optional)
- Coral TPU support (optional)

### 1.2 Design Principles

1. **Offline-First**: All core functionality works without internet
2. **Fault Tolerant**: Graceful degradation when services unavailable
3. **Privacy First**: Sensitive data stays local
4. **Real-Time**: Low-latency WebSocket communication
5. **Modular**: Independent services with clear interfaces
6. **Observable**: Comprehensive logging and metrics
7. **Recoverable**: Automatic reconnection and recovery

---

## 2. Backend Architecture

### 2.1 Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── dependencies.py  # Dependency injection
│   │   ├── logging.py       # Logging infrastructure
│   │   └── cloud_sync.py    # Cloud backup service
│   └── modules/
│       ├── __init__.py
│       ├── vakten.py        # Vision AI module
│       ├── navi.py          # Conversational AI
│       ├── navigator.py     # Navigation intelligence
│       ├── legen.py         # Medical support
│       ├── psykologen.py    # Mental health
│       └── ingenioren.py    # Engineering diagnostics
├── requirements.txt
├── Dockerfile
└── .env.example
```

### 2.2 Core Services (backend/app/core/)

#### config.py
**Purpose**: Centralized configuration management using Pydantic Settings

**Key Features:**
- Environment variable loading
- Type validation
- Default values
- Secret management

**Configuration Variables:**
```python
DATABASE_URL: str = "postgresql://..."
INFLUXDB_URL: str = "http://influxdb:8086"
REDIS_URL: str = "redis://redis:6379"
MINIO_ENDPOINT: str = "minio:9000"
OLLAMA_BASE_URL: str = "http://ollama:11434"
LOG_LEVEL: str = "INFO"
ENVIRONMENT: str = "production"
```

#### logging.py
**Purpose**: Structured logging with multiple backends

**Features:**
- JSON structured logs
- Multiple destinations (console, file, InfluxDB)
- Log rotation (30-day retention)
- Module-specific loggers
- Performance metrics tracking

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General system events
- WARNING: Warning messages
- ERROR: Error events
- CRITICAL: Critical failures

#### cloud_sync.py
**Purpose**: Optional encrypted backup to Google Drive

**Features:**
- Periodic sync when online
- Priority queue (alerts > logs > metrics)
- Encryption at rest
- Bandwidth throttling
- Conflict resolution
- 24h+ local buffering

### 2.3 Main Application (backend/app/main.py)

**FastAPI Application Structure:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="AADS NAVI Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routes
@app.get("/health")
async def health_check()

@app.get("/api/v1/status")
async def system_status()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket)

# Module endpoints
app.include_router(vakten_router, prefix="/api/v1/vakten")
app.include_router(navi_router, prefix="/api/v1/navi")
# ... other modules
```

**Startup/Shutdown Events:**
- Database connection pool initialization
- Redis connection setup
- Module initialization
- Graceful shutdown handling

---

## 3. Frontend Architecture

### 3.1 Directory Structure

```
frontend/
├── src/
│   ├── App.tsx              # Main application
│   ├── index.tsx            # Entry point
│   ├── components/
│   │   ├── Map.tsx          # Position display
│   │   ├── Instruments.tsx  # HUD gauges
│   │   ├── Vakten.tsx       # Vision interface
│   │   ├── Navi.tsx         # Chat interface
│   │   ├── Navigator.tsx    # Navigation view
│   │   ├── Legen.tsx        # Medical interface
│   │   ├── Psykologen.tsx   # Mental health
│   │   └── Ingenioren.tsx   # Engineering view
│   ├── hooks/
│   │   ├── useWebSocket.ts  # WebSocket hook
│   │   ├── useNMEA.ts       # NMEA data hook
│   │   └── useNavi.ts       # API client hook
│   └── themes/
│       └── arctic.css       # Arctic HUD theme
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile
```

### 3.2 Design System - Arctic HUD Theme

**Color Palette:**
```css
--arctic-blue: #00d4ff
--toxic-green: #00ff41
--battle-red: #ff0000
--ice-white: #e0f7ff
--deep-black: #0a0e14
--warning-amber: #ffb800
```

**Typography:**
- Primary: 'Orbitron', monospace
- Secondary: 'Share Tech Mono', monospace
- Sizes: 12px (small), 14px (body), 18px (heading), 24px (title)

**UI Elements:**
- Scanline animation overlay
- Grid background pattern
- Glowing borders on focus
- Battle mode (red theme)
- Responsive breakpoints: 768px, 1024px, 1440px

### 3.3 Key Components

#### App.tsx
**Main application component with:**
- Battle mode toggle (press 'B' key)
- Navigation between 8 views
- Real-time status displays
- Threat level indicator
- Online/offline status

#### WebSocket Hook (useWebSocket.ts)
**Features:**
- Auto-reconnect with exponential backoff
- Heartbeat mechanism
- Message queueing when offline
- Type-safe message handling
- Connection state management

#### NMEA Hook (useNMEA.ts)
**Provides:**
- GPS position (latitude, longitude)
- Course over ground (COG)
- Speed over ground (SOG)
- Heading (HDG)
- Time (UTC)

---

## 4. Module Specifications

### 4.1 Vakten (Vision AI)

**File**: `backend/app/modules/vakten.py`

**Purpose**: Real-time video analysis for maritime threats

**Features:**
- YOLOv8 object detection
- Coral TPU acceleration (optional)
- Camera feed: /dev/video0
- Frame rate: 10-30 FPS
- Detection classes:
  - Ice floes
  - Ships
  - People
  - Obstacles
  - Shadow ships (AIS spoofing)

**API Endpoints:**
```
GET  /api/v1/vakten/status
GET  /api/v1/vakten/detections
POST /api/v1/vakten/start
POST /api/v1/vakten/stop
WS   /api/v1/vakten/stream
```

**Detection Output:**
```json
{
  "timestamp": "2026-01-18T18:00:00Z",
  "frame_id": 12345,
  "detections": [
    {
      "class": "ice_floe",
      "confidence": 0.92,
      "bbox": [100, 200, 300, 400],
      "distance_m": 150,
      "threat_score": 0.6
    }
  ],
  "total_threats": 3,
  "max_threat_score": 0.8
}
```

**Performance Targets:**
- Latency: <100ms per frame
- Throughput: 20+ FPS on Jetson Orin
- Accuracy: >85% mAP@0.5

### 4.2 Navi (Conversational AI)

**File**: `backend/app/modules/navi.py`

**Purpose**: AI assistant for crew support

**Features:**
- Ollama integration (LLaMA 3.1 8B or similar)
- Context awareness (GPS, weather, threats)
- Personality: Professional, concise, maritime-focused
- Emergency escalation
- Optional TTS/STT

**API Endpoints:**
```
POST /api/v1/navi/chat
GET  /api/v1/navi/history
POST /api/v1/navi/clear_history
WS   /api/v1/navi/stream
```

**Chat Request:**
```json
{
  "message": "What's our current status?",
  "context": {
    "position": {"lat": 78.2, "lng": 15.6},
    "threats": ["ice_floe"],
    "weather": "clear"
  }
}
```

**Chat Response:**
```json
{
  "response": "Currently at 78.2°N, 15.6°E. One ice floe detected ahead. Weather clear. All systems nominal.",
  "timestamp": "2026-01-18T18:00:00Z",
  "confidence": 0.95
}
```

### 4.3 Navigator (Route Intelligence)

**File**: `backend/app/modules/navigator.py`

**Purpose**: Navigation planning and NAVTEX parsing

**Features:**
- NAVTEX message parsing
- Weather hazard extraction
- Ice chart integration
- Route optimization
- Waypoint management
- ETA calculation

**API Endpoints:**
```
GET  /api/v1/navigator/route
POST /api/v1/navigator/plan
GET  /api/v1/navigator/navtex
GET  /api/v1/navigator/hazards
```

**Route Planning:**
```json
{
  "origin": {"lat": 78.0, "lng": 15.0},
  "destination": {"lat": 79.0, "lng": 16.0},
  "waypoints": [
    {"lat": 78.5, "lng": 15.5}
  ],
  "avoid_ice": true,
  "optimize_for": "fuel"
}
```

### 4.4 Legen (Medical Support)

**File**: `backend/app/modules/legen.py`

**Purpose**: Medical triage and emergency protocols

**Features:**
- Symptom assessment tree
- Maritime medical guidelines
- Emergency protocols (DCS, hypothermia, trauma)
- Telemedicine integration
- Treatment recommendations

**API Endpoints:**
```
POST /api/v1/legen/assess
GET  /api/v1/legen/protocols/{type}
GET  /api/v1/legen/history
```

**Assessment Request:**
```json
{
  "symptoms": ["chest_pain", "shortness_of_breath"],
  "severity": "high",
  "patient_age": 45,
  "patient_gender": "M"
}
```

### 4.5 Psykologen (Mental Health)

**File**: `backend/app/modules/psykologen.py`

**Purpose**: Privacy-first mental wellness support

**Features:**
- Local-only storage (NEVER sent to cloud)
- CBT-based techniques
- Wellness check-ins
- Isolation mitigation
- Crisis intervention
- Encrypted at rest

**API Endpoints:**
```
POST /api/v1/psykologen/checkin
GET  /api/v1/psykologen/status
POST /api/v1/psykologen/session
```

**Privacy Guarantees:**
- All data stored locally
- Encrypted SQLite database
- No cloud sync
- Session timeouts
- Consent required

### 4.6 Ingeniøren (Engineering Diagnostics)

**File**: `backend/app/modules/ingenioren.py`

**Purpose**: System health and acoustic monitoring

**Features:**
- Engine acoustic analysis
- Anomaly detection
- Performance optimization
- Resource monitoring (CPU, GPU, memory)
- Predictive maintenance

**API Endpoints:**
```
GET  /api/v1/ingenioren/diagnostics
GET  /api/v1/ingenioren/metrics
POST /api/v1/ingenioren/optimize
GET  /api/v1/ingenioren/alerts
```

**Metrics Collected:**
- CPU usage %
- GPU usage %
- Memory usage %
- Temperature (°C)
- Disk I/O
- Network bandwidth
- Engine RPM
- Acoustic signature

---

## 5. Database Schema

### 5.1 PostgreSQL Tables

#### module_status
```sql
CREATE TABLE module_status (
  id SERIAL PRIMARY KEY,
  module VARCHAR(50) NOT NULL UNIQUE,
  status VARCHAR(20) NOT NULL,
  health VARCHAR(20) NOT NULL,
  uptime INTEGER DEFAULT 0,
  last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metrics JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### alerts
```sql
CREATE TABLE alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  module VARCHAR(50) NOT NULL,
  severity VARCHAR(20) NOT NULL,
  message TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  resolved BOOLEAN DEFAULT FALSE,
  resolved_at TIMESTAMP,
  metadata JSONB
);
```

#### routes
```sql
CREATE TABLE routes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin_lat DOUBLE PRECISION NOT NULL,
  origin_lng DOUBLE PRECISION NOT NULL,
  destination_lat DOUBLE PRECISION NOT NULL,
  destination_lng DOUBLE PRECISION NOT NULL,
  waypoints JSONB,
  distance DOUBLE PRECISION,
  duration INTEGER,
  instructions JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### mental_health_sessions (local only)
```sql
CREATE TABLE mental_health_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_type VARCHAR(50) NOT NULL,
  notes TEXT ENCRYPTED,
  mood_score INTEGER CHECK (mood_score BETWEEN 1 AND 10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 InfluxDB Measurements

#### system_metrics
```
measurement: system_metrics
tags: module, host
fields: cpu_percent, gpu_percent, memory_percent, temperature_c
```

#### detections
```
measurement: detections
tags: class, module
fields: confidence, distance_m, threat_score
```

---

## 6. API Endpoints

### 6.1 Core Endpoints

```
GET  /health                    # Health check
GET  /api/v1/status             # System status
GET  /api/v1/modules            # List modules
GET  /api/v1/config             # Get configuration
PUT  /api/v1/config             # Update configuration
WS   /ws                        # WebSocket connection
```

### 6.2 Module Endpoints

Each module exposes:
```
GET  /api/v1/{module}/status    # Module status
GET  /api/v1/{module}/data      # Module data
POST /api/v1/{module}/action    # Module action
GET  /api/v1/{module}/logs      # Module logs
```

### 6.3 WebSocket Messages

**Client → Server:**
```json
{
  "type": "subscribe",
  "channels": ["vakten", "navi"],
  "user_id": "uuid"
}
```

**Server → Client:**
```json
{
  "type": "detection",
  "module": "vakten",
  "data": {
    "timestamp": "2026-01-18T18:00:00Z",
    "detections": [...]
  }
}
```

---

## 7. Deployment Configuration

### 7.1 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://aads:aads@postgres:5432/aads
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - influxdb
      - redis
      - minio
      - ollama

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=aads
      - POSTGRES_USER=aads
      - POSTGRES_PASSWORD=aads
    volumes:
      - postgres_data:/var/lib/postgresql/data

  influxdb:
    image: influxdb:2.7-alpine
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb2

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  influxdb_data:
  minio_data:
  ollama_data:
```

### 7.2 Jetson Optimization

**Nano (Scout Edition):**
- Swap: 4GB
- GPU clocks: Default
- CPU governor: schedutil
- Max power mode: 10W

**Orin NX (Pro Edition):**
- Swap: 8GB
- GPU clocks: Maximum
- CPU governor: performance
- Max power mode: 25W

---

## 8. Testing Requirements

### 8.1 Unit Tests
- Module initialization
- API endpoint responses
- Database operations
- WebSocket connections

### 8.2 Integration Tests
- End-to-end workflows
- Module communication
- Database persistence
- Cloud sync

### 8.3 Performance Tests
- Latency benchmarks
- Throughput tests
- Memory profiling
- GPU utilization

### 8.4 Security Tests
- Authentication
- Authorization
- Input validation
- SQL injection prevention

---

## 9. Security

### 9.1 Authentication
- JWT tokens
- 24-hour expiration
- Refresh token rotation

### 9.2 Data Protection
- TLS/HTTPS only
- Encrypted at rest (mental health data)
- Input sanitization
- SQL injection prevention
- XSS protection

### 9.3 Privacy
- Mental health data: local-only
- Consent required
- Data minimization
- Right to deletion

---

## 10. Performance Targets

### 10.1 Latency
- API response: <50ms (p95)
- WebSocket message: <10ms
- Vision detection: <100ms per frame
- LLM inference: <2s per response

### 10.2 Throughput
- API requests: 1000 req/s
- WebSocket messages: 10k msg/s
- Vision processing: 20+ FPS
- Log ingestion: 10k events/s

### 10.3 Resource Usage
- Nano: CPU <70%, GPU <80%, Memory <6GB
- Orin: CPU <50%, GPU <60%, Memory <12GB

### 10.4 Reliability
- Uptime: 99.9%
- Data retention: 30 days (logs), 90 days (video)
- Recovery time: <30s

---

## Success Criteria

✅ All 6 modules operational and tested  
✅ Backend compiles without errors  
✅ Frontend builds successfully  
✅ Docker compose starts all services  
✅ Health endpoints respond correctly  
✅ WebSocket connections stable  
✅ Vision detection working at 20+ FPS  
✅ LLM responses within 2 seconds  
✅ Privacy compliance verified  
✅ Deployment scripts tested on Jetson  
✅ Documentation complete  
✅ No critical security vulnerabilities  

---

**Build Status: READY FOR IMPLEMENTATION**
