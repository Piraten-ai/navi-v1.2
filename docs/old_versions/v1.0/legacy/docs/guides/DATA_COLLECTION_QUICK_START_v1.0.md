**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# Data Collection Quick Start

## What You Need

1. **Arctic maritime images** (for YOLO)
2. **Q&A pairs** about Arctic operations (for Ollama)
3. **Crew health/system data** (for consolidation)

## Quick Commands

### 1. Download Updated Code
```bash
cd ~/navi-main
git pull
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### 2. Check API is Ready
```bash
curl http://localhost:8000/api/v1/data/stats
```

### 3. Get Ollama Q&A Templates
```bash
curl http://localhost:8000/api/v1/data/ollama/templates
```

Response will show 40+ pre-filled Arctic maritime Q&A pairs you can edit and use.

### 4. Submit Training Data

**Single Q&A Pair:**
```bash
curl -X POST http://localhost:8000/api/v1/data/ollama/training-pair \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I avoid ice floes?",
    "answer": "Monitor Vakten vision system continuously. Maintain safe distance from ice. Reduce speed in ice-prone areas.",
    "category": "navigation"
  }'
```

**Bulk Upload (JSON file):**
```bash
curl -X POST http://localhost:8000/api/v1/data/ollama/bulk-upload \
  -H "Content-Type: application/json" \
  -d @training_pairs.json
```

### 5. Upload YOLO Images
```bash
# Single image
curl -X POST http://localhost:8000/api/v1/data/yolo/image \
  -F "file=@arctic_ice_001.jpg"

# Create annotation
curl -X POST http://localhost:8000/api/v1/data/yolo/annotation \
  -H "Content-Type: application/json" \
  -d '{
    "image_filename": "arctic_ice_001.jpg",
    "detections": [
      {
        "class": "ice_floe",
        "x_center": 0.5,
        "y_center": 0.5,
        "width": 0.3,
        "height": 0.4
      }
    ]
  }'
```

### 6. Log Health Data
```bash
# Vital signs
curl -X POST http://localhost:8000/api/v1/data/health/vitals \
  -H "Content-Type: application/json" \
  -d '{
    "crew_id": "crew_001",
    "heart_rate": 72,
    "blood_pressure": "120/80",
    "temperature": 37.2
  }'

# Mental health
curl -X POST http://localhost:8000/api/v1/data/health/mental-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "crew_id": "crew_001",
    "stress_level": 5,
    "sleep_quality": 7,
    "mood": "good"
  }'
```

### 7. Log System Status
```bash
curl -X POST http://localhost:8000/api/v1/data/systems/log \
  -H "Content-Type: application/json" \
  -d '{
    "system": "engine",
    "status": "ready",
    "details": {
      "temperature": 85,
      "pressure": 4.0
    }
  }'
```

## Data Collection Statistics

Check progress:
```bash
curl http://localhost:8000/api/v1/data/stats
```

Shows:
- YOLO images collected
- Ollama training pairs
- Health records
- System logs

## Ready for Training?

When you have:
- **100+ YOLO images** with annotations
- **50+ Ollama Q&A pairs**

Then:

### Train YOLO
```bash
docker exec aads-backend python3 << 'EOF'
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model.train(
    data='app/core/../../../data/collected/yolo/dataset.yaml',
    epochs=100,
    imgsz=640,
    device=0
)
EOF
```

### Fine-tune Ollama
```bash
# Create Modelfile with your training data
docker exec aads-navi-ollama ollama create navi-custom -f Modelfile
```

## File Locations

**Data collected at:**
```
~/navi-main/data/collected/
â”œâ”€â”€ yolo/           (images + annotations)
â”œâ”€â”€ ollama/         (Q&A pairs)
â”œâ”€â”€ health_wellness/  (crew health)
â””â”€â”€ systems_resources/ (system logs)
```

## Module Consolidation

### Health & Wellness (Legen + Psykologen)
- Combines medical and psychological crew monitoring
- Tracks vitals, mental health, fitness
- Provides health scores and recommendations

### Systems & Resources (Ingenioren + Quartermaster)
- Combines engine maintenance and inventory management
- Tracks system status and resource levels
- Generates diagnostics and supply recommendations

## Next Steps

1. âœ… Data collection framework deployed
2. â³ Collect YOLO training images (100+ needed)
3. â³ Collect Ollama Q&A pairs (50+ needed)
4. â³ Start crew health/system tracking
5. â³ Train models when data ready
6. â³ Deploy trained models

---

**Framework Version**: 1.0.0
**Status**: Ready for data collection

