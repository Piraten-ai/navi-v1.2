# AADS NAVI - Arctic Autonomy Decision Support System

> **Runs everywhere**: Production on Jetson hardware, Development on any laptop

🧊 **"When satellites fail, we survive."** ⚓

---

## 🎯 Overview

**AADS (Arctic Autonomy Decision Support)** is a production-ready, offline-first AI system for maritime autonomous operations in Arctic waters. Built for NVIDIA Jetson hardware, but also runs in light[...]  

**Philosophy**: "Tools for Amundsen" - Built for isolation, not connectivity.

---

## ✨ Key Features

✅ **100% Offline-First** - Full functionality without internet  
✅ **Laptop Dev Mode** - Lightweight version for testing  
✅ **6 AI Modules** - Specialized intelligence for every need  
✅ **Real-Time Vision** - YOLOv8 ice/ship/obstacle detection  
✅ **AI Assistant** - Ollama-powered conversational AI  
✅ **Privacy-First** - Mental health data stays local  
✅ **Battle Mode** - Red theme optimized for night vision  
✅ **Jetson Optimized** - Runs on Nano 8GB & Orin NX 16GB  

---

## 🚀 Quick Start

### Production: Single Command Deploy to Jetson

Deploy to any Jetson device with ONE command (for 1, 10, or 1000 units):

```bash
curl -sSL https://raw.githubusercontent.com/Piraten-ai/navi-main/main/deploy/install_complete.sh | sudo bash
```

That's it! The system will:
- Install Docker if needed
- Build all containers
- Start 7 services (backend, frontend, databases, AI, storage)
- Verify health
- Show you the access URL

**Access:** Open browser to `http://[jetson-ip]:3000`

---

### Development Mode (Laptop)

Perfect for testing and development on any modern laptop:

```bash
# Clone repository
git clone https://github.com/Piraten-ai/navi-main.git
cd navi-main

# Start lightweight development stack
docker-compose -f docker-compose.dev.yml up -d

# Check health
curl http://localhost:8000/health

# Access dashboard
open http://localhost:3000
```

**Lightweight Mode Features:**
- Uses CPU-only inference (no GPU required)
- Smaller Ollama models (llama3.2:1b)
- Mock camera feed for Vakten testing
- Reduced resource requirements (4GB RAM minimum)
- All core functionality preserved

---

## 📦 The 6 AI Modules

### 1. **Vakten (The Guard)** 👁️
- Ice floe detection & classification
- Ship tracking & AIS correlation
- Person overboard detection

### 2. **Navi (The Navigator AI)** 🤖
- Natural language interaction
- Context-aware responses
- Emergency escalation

### 3. **Navigator (Route Intelligence)** ��️
- NAVTEX message parsing
- Route optimization

### 4. **Legen (The Doctor)** 🏥
- Symptom assessment
- Emergency protocols

### 5. **Psykologen (The Psychologist)** 🧠
- CBT-based therapy
- **All data stays local**

### 6. **Ingeniøren (The Engineer)** ⚙️
- System diagnostics
- Performance optimization

---

## 🌊 Marine Data Integration

### NMEA GPS
- Real-time position, speed, and heading
- Standard NMEA 0183 sentences (GGA, RMC, VTG, HDT)
- Mock mode for development

### Signal K
- Comprehensive marine data (navigation, environment, propulsion)
- Modern JSON-based protocol
- WebSocket streaming
- Water depth, wind, engine data
- Mock mode for development

---

## 📚 Documentation

- **Quick Start**: [START_HERE.md](START_HERE.md)
- **Build Specification**: [BUILD_SPEC.md](BUILD_SPEC.md)
- **NMEA Integration**: [NMEA_INTEGRATION.md](NMEA_INTEGRATION.md)
- **Signal K Integration**: [SIGNALK_INTEGRATION.md](SIGNALK_INTEGRATION.md)
- **API Documentation**: http://localhost:8000/docs

---

## 🔍 Development & Linting

### Code Quality

The project uses automated linting to ensure code quality and consistency:

**Backend (Python):**
- `flake8` for style checking
- `black` for code formatting (max line length: 127)
- No critical errors (F-series, E9 series)
- Complexity warnings (C901) are monitored but don't block

**Frontend (TypeScript/React):**
- ESLint with TypeScript and React plugins
- Zero warnings policy for production

### Running Linting Checks

```bash
# Run all linting checks
./lint.sh

# Backend only
cd backend
flake8 app --max-line-length=127

# Frontend only
cd frontend
npm run lint
```

---

## 🧊 AADS/NAVI – Copilot multi‑agent system

Dette repoet bruker et definert sett med Copilot‑roller for å sikre kvalitet, sikkerhet og robusthet i all kode.

### Agenter

- **Sentinel‑01 — Chief Integrity & Security Officer**  
  Har ansvar for sikkerhet, kodeintegritet, risiko og robusthet.  
  Stopper, korrigerer og flagger alt som er utrygt, skjørt eller dårlig testet.

- **Architect‑01 — System Design & Topology Commander**  
  Har ansvar for arkitektur, modulstruktur, dataflyt og systemtopologi.  
  Sikrer at løsninger er logiske, skalerbare og vedlikeholdbare.

- **Ops‑01 — Runtime, Docker & Deployment Overseer**  
  Har ansvar for drift, Docker, logging, observability og runtime‑stabilitet.  
  Sikrer at det som bygges faktisk kan kjøre trygt over tid.

### Filosofi

- Robusthet over hastighet  
- Sikkerhet over komfort  
- Klarhet over “smart” hacks  
- Autonomi over manuell drift  

Se `COPILOT.md` for full rollebeskrivelse.

---

🧊 **"When satellites fail, we survive."** ⚓