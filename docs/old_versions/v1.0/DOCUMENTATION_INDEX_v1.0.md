# AADS NAVI - Documentation Index

Welcome to the AADS NAVI documentation hub. This index will help you navigate all available documentation for the Arctic Autonomy Decision Support System.

## 📚 Core Documentation

### **[COMPLETE_TECHNICAL_REFERENCE.md](COMPLETE_TECHNICAL_REFERENCE.md)** ⭐ START HERE
**3,000+ lines of comprehensive technical documentation**

The complete reference manual covering:
- System architecture and design
- All 6 AI modules (Vakten, Navi, Navigator, Legen, Psykologen, Ingenioren)
- Database schema and models
- API reference and endpoints
- Frontend architecture and hooks
- Configuration and environment variables
- Build and deployment procedures
- Testing strategy
- Troubleshooting and maintenance
- Extension and modification guide

**Use this as your master prompt** for understanding, modifying, or rebuilding the system.

---

## 📋 Quick Reference Guides

### [README.md](README.md)
**High-level overview and quick start**
- System features and philosophy
- Quick start for production and development
- Module descriptions
- 6-module architecture overview

### [SIGNAL_K_INTEGRATION_COMPLETE.md](SIGNAL_K_INTEGRATION_COMPLETE.md)
**Maritime data integration documentation**
- Signal K server setup and configuration
- Real-time navigation data streaming
- Autopilot integration
- Freeboard map integration
- WebSocket data flow

### [docs/SIGNAL_K_IMPLEMENTATION_GUIDE.md](docs/SIGNAL_K_IMPLEMENTATION_GUIDE.md) ⭐ NEW
**Production-ready Signal K implementation with advanced features**
- Complete SignalKModule with CPA calculations
- AIS target simulation (5 mock vessels)
- Haversine distance calculations
- Collision avoidance analysis
- Redis caching for AIS targets
- Timestamp validation and error handling
- Usage examples and integration checklist
- Comprehensive testing guide
- Troubleshooting and performance tuning

### [START_HERE.md](START_HERE.md)
**Getting started guide**
- First-time setup steps
- Basic commands
- Deployment walkthrough

---

## 🔧 Technical Specifications

### Database & Storage
- **Database Models**: See [COMPLETE_TECHNICAL_REFERENCE.md § Database Schema](#database-schema)
- **InfluxDB Time-Series**: Configuration and retention policies
- **MinIO S3 Storage**: Object storage for videos and images
- **Redis Pub/Sub**: Real-time messaging

### APIs & Protocols
- **REST API**: All endpoints documented in technical reference
- **WebSocket**: Real-time data streaming
- **NMEA 0183**: GPS serial protocol
- **Signal K**: Maritime data standard
- **NAVTEX**: Navigation text broadcasts

### Hardware
- **NVIDIA Jetson Orin NX**: Primary production platform
- **NVIDIA Jetson Nano**: Legacy support
- **Laptop Development**: Any x86_64 with 4GB+ RAM

---

## 🚀 Deployment

### One-Command Production Deploy
```bash
curl -sSL https://raw.githubusercontent.com/Piraten-ai/navi-main/main/deploy/install_complete.sh | sudo bash
```

See [COMPLETE_TECHNICAL_REFERENCE.md § Build & Deployment](#build--deployment) for detailed instructions.

### Development Setup
```bash
docker-compose -f docker-compose.dev.yml up -d
# Access at http://localhost:3000
```

---

## 🧠 Understanding the 6 AI Modules

| Module | File | Purpose | Tech |
|--------|------|---------|------|
| **Vakten** | `app/modules/vakten.py` | Vision/ice detection | YOLOv8 neural network |
| **Navi** | `app/modules/navi.py` | Conversational AI | Ollama LLM (llama3.2) |
| **Navigator** | `app/modules/navigator.py` | Route planning & NAVTEX | Regex parsing + pathfinding |
| **Legen** | `app/modules/legen.py` | Medical triage | Protocol lookup |
| **Psykologen** | `app/modules/psykologen.py` | Mental health support | CBT-based, privacy-first |
| **Ingenioren** | `app/modules/ingenioren.py` | System diagnostics | System monitoring |

Details: [COMPLETE_TECHNICAL_REFERENCE.md § Detailed Component Documentation](#detailed-component-documentation)

---

## 🔌 API Endpoints Quick Reference

```
Health & Status:
  GET /health                           → System status
  GET /api/v1/status                    → Detailed status

Vision (Vakten):
  GET /api/v1/vakten/latest            → Latest detections
  POST /api/v1/vakten/test             → Test vision system

Chat (Navi):
  POST /api/v1/navi/chat               → Send message
  GET /api/v1/navi/history             → Chat history
  POST /api/v1/navi/clear              → Clear conversation

Navigation (Navigator):
  GET /api/v1/navigator/navtex         → NAVTEX messages
  GET /api/v1/navigator/route          → Current route

Medical (Legen):
  POST /api/v1/legen/assess            → Medical assessment
  GET /api/v1/legen/protocols          → Medical protocols

Mental Health (Psykologen):
  POST /api/v1/psykologen/checkin      → Mood check-in
  GET /api/v1/psykologen/history       → Session history

Engineering (Ingenioren):
  GET /api/v1/ingenioren/status        → System diagnostics
  GET /api/v1/ingenioren/metrics       → Performance metrics

Real-Time Data:
  WS /ws                               → WebSocket stream
```

Complete reference: [COMPLETE_TECHNICAL_REFERENCE.md § API Reference](#api-reference)

---

## 🎨 Frontend Components

All React components are located in `frontend/src/components/`:

- **Dashboard**: Customizable gauge widgets with Signal K data
- **Map**: GPS position and navigation display
- **Instruments**: Speed, heading, depth, temperature gauges
- **Vakten**: Vision detection display and threat alerts
- **Navi**: Chat interface for AI assistant
- **Navigator**: NAVTEX messages and route planning
- **Legen**: Medical triage and assessment
- **Psykologen**: Mental health support and tracking
- **Ingenioren**: System health and diagnostics
- **SignalKInstruments**: Maritime data display with Freeboard map

All hooks documented in: [COMPLETE_TECHNICAL_REFERENCE.md § Frontend Architecture](#frontend-architecture)

---

## ⚙️ Configuration

### Environment Variables
```
ENVIRONMENT=production|development|testing
DATABASE_URL=postgresql://user:pass@host:5432/db
OLLAMA_MODEL=llama3.2|llama3.2:1b|mistral
INFLUXDB_TOKEN=<token>
MINIO_ACCESS_KEY=minioadmin
NMEA_ENABLED=true|false
SIGNALK_ENABLED=true|false
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL
```

Full reference: [COMPLETE_TECHNICAL_REFERENCE.md § Configuration & Environment](#configuration--environment)

---

## 🐛 Troubleshooting

Common issues and solutions in: [COMPLETE_TECHNICAL_REFERENCE.md § Troubleshooting & Maintenance](#troubleshooting--maintenance)

### Quick Checks
```bash
# Health status
curl http://localhost:8000/health

# Service status
docker-compose ps

# Logs
docker-compose logs -f backend

# Database connection
psql -h localhost -U aads -d aads -c "SELECT COUNT(*) FROM vision_detections;"

# WebSocket connection
wscat -c ws://localhost:8000/ws
```

---

## 📖 Adding Features & Modifications

See: [COMPLETE_TECHNICAL_REFERENCE.md § Extension & Modification Guide](#extension--modification-guide)

### Adding a New Module
1. Create module file in `backend/app/modules/`
2. Implement required methods (initialize, process, stop, get_status)
3. Add to main.py lifespan
4. Create REST endpoints
5. Add tests
6. Create frontend component
7. Deploy (rebuild + restart)

### Database Schema Changes
1. Edit models.py
2. Create alembic migration
3. Apply migration in production
4. Test thoroughly before deploying

---

## 🧪 Testing

### Backend Tests
```bash
pytest                              # All tests
pytest -m unit                      # Unit tests only
pytest tests/test_navi.py          # Specific module
pytest --cov=app                   # With coverage
```

### Frontend Tests
```bash
npm test                           # Run tests
npm run test:ui                    # Interactive UI
npm run test:coverage              # Coverage report
```

Full test strategy: [COMPLETE_TECHNICAL_REFERENCE.md § Testing Strategy](#testing-strategy)

---

## 🔐 Security

- **Privacy-First**: Mental health data never leaves the vessel
- **Offline-First**: No external APIs or cloud dependencies
- **Non-Root**: All containers run as unprivileged users
- **Encrypted Storage**: Psykologen data encrypted at rest
- **JWT Tokens**: Authentication implemented (can be enabled)

---

## 📊 System Architecture

```
Frontend (React)
    ↓ WebSocket
Backend (FastAPI)
    ├─ 6 AI Modules
    ├─ Sensor Integration (NMEA GPS, Signal K)
    └─ Databases:
        ├─ PostgreSQL (relational)
        ├─ InfluxDB (time-series)
        ├─ Redis (pub/sub)
        └─ MinIO (S3-compatible storage)
```

Detailed architecture: [COMPLETE_TECHNICAL_REFERENCE.md § Architecture & Design](#architecture--design)

---

## 🌍 Deployment Environments

### Production (Jetson Orin)
- Full GPU support
- 8+ GB memory
- PostgreSQL backend
- Large language models (7B)
- Real sensors (GPS, camera)

### Development (Docker Compose)
- CPU inference
- 4+ GB memory
- SQLite or PostgreSQL
- Small models (1B)
- Mock camera and GPS

### Laptop Development (Local)
- No containers
- SQLite database
- Python/Node development servers
- Mock everything

---

## 📞 Support & Troubleshooting

### Health Check Command
```bash
curl -s http://localhost:8000/health | jq .
```

### View All Service Logs
```bash
docker-compose logs -f
```

### Common Errors
- "Could not connect to database" → PostgreSQL not running
- "Ollama API error" → Model not loaded, run `ollama pull llama3.2`
- "Port already in use" → Another service using port, stop it
- "GPU not available" → Install NVIDIA Docker runtime

See [COMPLETE_TECHNICAL_REFERENCE.md § Troubleshooting](#troubleshooting--maintenance) for comprehensive guide.

---

## 📝 Documentation Files

```
Root Documentation:
├── README.md                            # Overview & quick start
├── COMPLETE_TECHNICAL_REFERENCE.md      # Master technical reference ⭐
├── START_HERE.md                        # Getting started guide
├── SIGNAL_K_INTEGRATION_COMPLETE.md     # Maritime data integration
│
├── Implementation Guides:
├── IMPLEMENTATION_SUMMARY.md
├── IMPLEMENTATION_SUMMARY_OLLAMA_FRONTEND.md
├── ADDING_MODULES.md
│
├── Deployment & Infrastructure:
├── AADS_DEPLOYMENT_READY.md
├── JETSON_DEPLOYMENT_READY.md
├── PRODUCTION_DEPLOYMENT.md
├── DOCKER_BOTS_FIX_SUMMARY.md
├── GITHUB_ACTIONS_DOCKER.md
│
├── Testing & Verification:
├── TESTING_COMPLETE.md
├── TESTING_QUICK_START.md
├── PHASE_2_TESTS_COMPLETE.md
├── RUN_TESTS_GUIDE.md
├── QUICK_TEST_REFERENCE.md
├── VERIFICATION_CHECKLIST.md
│
├── Features & Improvements:
├── GUI_REDESIGN.md
├── IMPROVEMENTS.md
├── SETTINGS_DASHBOARD_SUMMARY.md
├── FEATURES.md
│
├── Data & Protocols:
├── DATA_COLLECTION.md
├── DATA_COLLECTION_QUICK_START.md
├── MAP_DATA.md
├── NMEA_INTEGRATION.md
│
└── Summaries & References:
    ├── AADS_WIKI.md
    ├── FINAL_DELIVERY_SUMMARY.md
    ├── QUICK_REFERENCE.md
    └── TEST_SUITE_SUMMARY.md
```

---

## ⚓ Signal K Integration - Latest Improvements

### New Features (January 23, 2026)

**Enhanced Signal K Implementation** - [See Full Guide](docs/SIGNAL_K_IMPLEMENTATION_GUIDE.md)

✅ **Advanced Navigation Calculations**
- Haversine distance formula (nautical miles accuracy)
- Bearing calculations (0-360°)
- Closest Point of Approach (CPA) with Time to CPA (TCPA)
- Collision risk assessment (critical/high/medium/low)

✅ **AIS Target Simulation**
- 5 realistic mock AIS targets around Svalbard
- Automatic position updates based on course/speed
- Realistic vessel characteristics (length, beam, draft)

✅ **Robust Error Handling**
- Redis caching with error graceful degradation
- Timestamp validation and ISO 8601 conversion
- Comprehensive exception handling
- Detailed logging for troubleshooting

✅ **Realistic Data Generation**
- Gaussian wind direction changes (gradual variations)
- Environmental sensor simulation
- Propulsion data with realistic variations
- Timestamp validation on all incoming messages

### Getting Started with Signal K

```bash
# 1. Enable Signal K in environment
export SIGNALK_ENABLED=true
export SIGNALK_MOCK_DATA=false  # Use real server in production

# 2. Check API endpoints
curl http://localhost:8000/api/signalk/data
curl http://localhost:8000/api/signalk/collision-risk

# 3. Monitor WebSocket stream
# Frontend automatically connects to WS /ws endpoint
```

### Documentation Structure

| Document | Purpose | Audience |
|----------|---------|----------|
| [SIGNAL_K_IMPLEMENTATION_GUIDE.md](docs/SIGNAL_K_IMPLEMENTATION_GUIDE.md) | Complete reference with examples | Developers, integrators |
| [SIGNAL_K_INTEGRATION_COMPLETE.md](SIGNAL_K_INTEGRATION_COMPLETE.md) | Setup and configuration guide | DevOps, operators |
| [COMPLETE_TECHNICAL_REFERENCE.md](COMPLETE_TECHNICAL_REFERENCE.md) | Full system context | System architects |

---

└── Summaries & References:
    ├── AADS_WIKI.md
    ├── FINAL_DELIVERY_SUMMARY.md
    ├── QUICK_REFERENCE.md
    └── TEST_SUITE_SUMMARY.md
```

---

## 🎯 Where to Start

1. **First Time?** → Read [README.md](README.md) and [START_HERE.md](START_HERE.md)
2. **Need Technical Details?** → [COMPLETE_TECHNICAL_REFERENCE.md](COMPLETE_TECHNICAL_REFERENCE.md) (3000+ lines)
3. **Implementing Signal K?** → [docs/SIGNAL_K_IMPLEMENTATION_GUIDE.md](docs/SIGNAL_K_IMPLEMENTATION_GUIDE.md) (Complete reference with CPA/AIS)
4. **Troubleshooting Issue?** → [COMPLETE_TECHNICAL_REFERENCE.md § Troubleshooting](#troubleshooting--maintenance)
5. **Deploying to Jetson?** → One-command: `curl -sSL https://... | sudo bash`
6. **Adding Features?** → [COMPLETE_TECHNICAL_REFERENCE.md § Extension Guide](#extension--modification-guide)
7. **Understanding Architecture?** → [COMPLETE_TECHNICAL_REFERENCE.md § Architecture](#architecture--design)

---

## 📄 Using as Master Prompt

The **COMPLETE_TECHNICAL_REFERENCE.md** document contains everything needed to:
- ✅ Understand the complete system architecture
- ✅ Rebuild or extend the system
- ✅ Troubleshoot and maintain the system
- ✅ Explain the system to others

The **SIGNAL_K_IMPLEMENTATION_GUIDE.md** provides:
- ✅ Complete Signal K module implementation details
- ✅ Advanced navigation calculations (CPA, bearing, distance)
- ✅ AIS target management and collision avoidance
- ✅ Redis caching patterns and error handling
- ✅ Production deployment checklist
- ✅ Onboard new developers
- ✅ Make informed design decisions

**Use it as your master prompt** when asking for modifications, explanations, or help with this codebase.

---

**Last Updated**: January 23, 2026  
**Status**: Production Ready ✓  
**Version**: AADS NAVI 1.0.0

