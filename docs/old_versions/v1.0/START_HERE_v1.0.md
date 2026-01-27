# AADS - Arctic Autonomy Decision Support System

## Quick Overview

Welcome to AADS (Arctic Autonomy Decision Support) - a comprehensive AI-powered system for maritime autonomous operations in Arctic waters, optimized for NVIDIA Jetson hardware.

## What is AADS?

AADS is an offline-first, production-ready system that provides:

- **Real-time Vision Processing** (Vakten) - Ice/ship/obstacle detection
- **AI Assistant** (Navi) - Conversational AI for crew support
- **Navigation Intelligence** (Navigator) - NAVTEX parsing and route optimization
- **Medical Support** (Legen) - Emergency triage and medical guidance
- **Mental Health Support** (Psykologen) - Privacy-first wellness monitoring
- **Engineering Diagnostics** (Ingeniøren) - System health and acoustic monitoring

## System Architecture

```
┌─────────────────────────────────────────────┐
│         NVIDIA Jetson Device                │
│  ┌───────────────────────────────────────┐  │
│  │     Docker Compose Stack              │  │
│  │  ┌─────────────┐  ┌────────────────┐ │  │
│  │  │   Backend   │  │    Frontend     │ │  │
│  │  │  (FastAPI)  │  │  (React+TS)     │ │  │
│  │  └──────┬──────┘  └────────┬────────┘ │  │
│  │         │                   │          │  │
│  │  ┌──────┴───────────────────┴────────┐ │  │
│  │  │   PostgreSQL │ InfluxDB │ Redis  │ │  │
│  │  │   MinIO      │ Ollama   │        │ │  │
│  │  └────────────────────────────────────┘ │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Hardware Requirements

### Scout Edition (Training/Development)
- **Device**: NVIDIA Jetson Nano 8GB
- **Performance**: 40 TOPS
- **Storage**: 128GB+ SD card or SSD
- **Optional**: Coral TPU USB accelerator

### Pro Edition (Production)
- **Device**: NVIDIA Jetson Orin NX 16GB
- **Performance**: 100 TOPS
- **Storage**: 256GB+ NVMe SSD
- **Optional**: Coral TPU M.2 accelerator

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Piraten-ai/navi-main.git
cd navi-main
```

### 2. Choose Your Deployment

#### For Jetson Nano (Scout Edition)
```bash
cd deploy
sudo bash install_scout.sh
```

#### For Jetson Orin (Pro Edition)
```bash
cd deploy
sudo bash install_pro.sh
```

### 3. Start the System
```bash
# After installation completes
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Access dashboard
open http://localhost:3000
```

## Directory Structure

```
navi-main/
├── START_HERE.md              # This file
├── BUILD_SPEC.md              # Complete technical specifications
├── README.md                  # Project documentation
├── docker-compose.yml         # Service orchestration
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── main.py           # Application entry point
│   │   ├── core/             # Core services
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── cloud_sync.py
│   │   └── modules/          # AI modules
│   │       ├── vakten.py     # Vision system
│   │       ├── navi.py       # AI assistant
│   │       ├── navigator.py  # Navigation
│   │       ├── legen.py      # Medical
│   │       ├── psykologen.py # Mental health
│   │       └── ingenioren.py # Engineering
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.tsx           # Main application
│   │   ├── components/       # UI components
│   │   ├── hooks/            # React hooks
│   │   └── themes/           # Arctic HUD styling
│   ├── package.json
│   └── Dockerfile
└── deploy/                    # Deployment scripts
    ├── install_scout.sh      # Jetson Nano installer
    ├── install_pro.sh        # Jetson Orin installer
    └── README.md             # Deployment guide
```

## The 6 AI Modules

### 1. Vakten (The Guard)
**Vision AI for threat detection**
- Real-time camera feed processing
- Ice floe detection and classification
- Ship and obstacle tracking
- Person overboard detection
- Threat scoring and alerting

### 2. Navi (The Navigator AI)
**Conversational AI assistant**
- Natural language interaction
- Context-aware responses
- System status queries
- Emergency command escalation
- Personality-driven communication

### 3. Navigator (Route Intelligence)
**Navigation and hazard awareness**
- NAVTEX message parsing
- Weather hazard extraction
- Route optimization
- Waypoint management
- Ice chart integration

### 4. Legen (The Doctor)
**Medical triage and support**
- Symptom assessment
- Emergency protocols
- Maritime medical guidelines
- Telemedicine integration
- Treatment recommendations

### 5. Psykologen (The Psychologist)
**Mental health support**
- Privacy-first local storage
- Wellness check-ins
- CBT-based support
- Isolation mitigation
- Crisis intervention

### 6. Ingeniøren (The Engineer)
**System diagnostics**
- Engine acoustic monitoring
- Anomaly detection
- Performance optimization
- Predictive maintenance
- Resource management

## Key Features

✅ **Offline-First** - Full functionality without internet  
✅ **Real-Time AI** - YOLOv8 vision + Ollama LLM  
✅ **Privacy Compliant** - Local-only mental health data  
✅ **Arctic Optimized** - Jetson Nano/Orin deployment  
✅ **Battle Ready** - Military HUD aesthetic  
✅ **Production Grade** - Error handling, logging, graceful shutdown  
✅ **Modular Design** - Independent AI services  
✅ **Cloud Sync** - Optional encrypted backup  

## What's Next?

1. **Read BUILD_SPEC.md** for complete technical specifications
2. **Run deployment script** for your Jetson device
3. **Access dashboard** at http://localhost:3000
4. **Test modules** using the testing guide
5. **Customize configuration** in docker-compose.yml

## Support & Documentation

- **Technical Specs**: See BUILD_SPEC.md
- **Deployment Guide**: See deploy/README.md
- **Testing Guide**: See TESTING.md
- **API Documentation**: http://localhost:8000/docs (when running)

## License

MIT License - See LICENSE file for details

---

**Ready to deploy Arctic autonomy? Start with your Jetson installer in `deploy/`**
