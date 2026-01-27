# Data Collection Framework

Complete framework for gathering training data for YOLO vision models and Ollama LLM fine-tuning, plus consolidated module data.

## Overview

### Three Data Streams

#### 1. **YOLO Vision Training** (For Vakten improvements)
- Collect labeled Arctic maritime images
- Format: YOLO (.txt annotations + images)
- Use case: Train custom YOLOv8 for ice, ships, whales, etc.
- Status: Ready to collect

#### 2. **Ollama Fine-tuning** (For Navi AI improvements)
- Collect Q&A pairs for Arctic maritime domain
- Format: JSONL (one JSON object per line)
- Use case: Fine-tune Mistral/Llama for better responses
- Status: Ready to collect

#### 3. **Module Consolidation Data**
- Health & Wellness (Legen + Psykologen)
- Systems & Resources (Ingenioren + Quartermaster)
- Status: Collecting crew and system metrics

## YOLO Vision Training Data

### Classes (8 total)

```
0: ice_floe        - Ice chunks in water
1: ship            - Other vessels
2: person          - Crew/rescue personnel
3: obstacle        - Rocks, debris, hazards
4: buoy            - Navigation markers
5: whale           - Marine mammals (safety)
6: seal            - Marine mammals (observation)
7: debris          - Floating garbage/wreckage
```

### Data Collection Process

**Step 1: Capture Images**
```python
# Upload images via API or directly to data/collected/yolo/images/raw/
POST /api/v1/data/yolo/image
  file: image.jpg
```

**Step 2: Annotate Images**
```python
# Create YOLO format annotations
POST /api/v1/data/yolo/annotation
{
  "image_filename": "arctic_001.jpg",
  "detections": [
    {
      "class": "ice_floe",
      "x_center": 0.45,  # normalized 0-1
      "y_center": 0.30,
      "width": 0.25,
      "height": 0.35
    },
    {
      "class": "ship",
      "x_center": 0.75,
      "y_center": 0.50,
      "width": 0.15,
      "height": 0.20
    }
  ]
}
```

**Step 3: Generate Dataset Config**
```python
GET /api/v1/data/yolo/config
# Returns dataset.yaml ready for YOLOv8 training
```

### Annotation Tools

**Manual Annotation (Web UI)**
- Frontend tool to draw bounding boxes
- Auto-generates YOLO format
- (Frontend component to be created)

**Export Format**
```
data/collected/yolo/
├── images/
│   ├── raw/              (uploaded images)
│   ├── train/            (80% split)
│   ├── val/              (10% split)
│   └── test/             (10% split)
├── annotations/          (YOLO .txt files)
├── metadata/             (image metadata)
└── dataset.yaml          (YOLOv8 config)
```

### Training When Ready

```bash
# Requires 100+ labeled images
yolo detect train data=data/collected/yolo/dataset.yaml model=yolov8n.pt epochs=100

# Deploy trained model
cp runs/detect/train/weights/best.pt backend/models/yolov8_arctic.pt
```

## Ollama Fine-tuning Data

### Data Categories

1. **Navigation** - Course, positioning, route planning
2. **Safety** - Emergency protocols, collision avoidance
3. **Maintenance** - Equipment care, troubleshooting
4. **Health** - First aid, medical procedures
5. **Psychology** - Crew morale, stress management
6. **Resources** - Inventory, fuel management

### Collection Methods

**Method 1: Use Templates**
```python
GET /api/v1/data/ollama/templates
# Returns 40+ pre-filled Q&A pairs by category
```

Edit and submit:
```python
POST /api/v1/data/ollama/training-pair
{
  "question": "How do I avoid ice in Arctic waters?",
  "answer": "Monitor Vakten vision system. Reduce speed. Check ice charts.",
  "category": "navigation",
  "source": "manual"
}
```

**Method 2: Bulk Upload**
```python
POST /api/v1/data/ollama/bulk-upload
[
  {
    "question": "Q1",
    "answer": "A1",
    "category": "navigation"
  },
  ...
]
```

### Data Format (JSONL)

```json
{"question": "What is the emergency protocol?", "answer": "1) Sound alarm. 2) Alert crew. 3) Prepare life jackets.", "category": "safety", "timestamp": "2026-01-22T10:30:00"}
{"question": "How do I check fuel levels?", "answer": "Check Systems & Resources dashboard", "category": "resources", "timestamp": "2026-01-22T10:31:00"}
```

### Training When Ready

```bash
# Requires 50+ Q&A pairs minimum

# Create custom model with Modelfile
cat > Modelfile <<EOF
FROM mistral
PARAMETER temperature 0.7
SYSTEM """You are NAVI, an Arctic maritime AI assistant...
EOF

# Create and train
ollama create navi-custom -f Modelfile

# Use in backend
# Update OLLAMA_MODEL=navi-custom in .env
```

## Health & Wellness Module (Legen + Psykologen)

### Data Collection Points

**Vital Signs (Legen)**
```python
POST /api/v1/data/health/vitals
{
  "crew_id": "crew_001",
  "heart_rate": 72,
  "blood_pressure": "120/80",
  "temperature": 37.2,
  "notes": "Normal morning check"
}
```

**Mental Health (Psykologen)**
```python
POST /api/v1/data/health/mental-assessment
{
  "crew_id": "crew_001",
  "stress_level": 5,      # 1-10
  "sleep_quality": 7,     # 1-10
  "mood": "good",
  "notes": "Slept well, ready for shift"
}
```

### Health Dashboard Metrics

- Heart rate trends
- Sleep quality tracking
- Stress level monitoring
- Mood trends
- Fitness activity logs
- Health score (0-100)

### Storage

```
data/collected/health_wellness/
├── health_records.jsonl     (vitals)
├── mental_assessments.jsonl (psych)
└── fitness_logs.jsonl       (activities)
```

## Systems & Resources Module (Ingenioren + Quartermaster)

### System Status Logging (Ingenioren)

```python
POST /api/v1/data/systems/log
{
  "system": "engine",
  "status": "warning",
  "details": {
    "temperature": 95,
    "pressure": 4.2
  },
  "severity": "warning"
}
```

### Inventory Management (Quartermaster)

```python
POST /api/v1/data/resources/inventory
{
  "resource": "fuel",
  "quantity": 2500.0,  # liters
  "unit": "liters"
}
```

### System Categories

- **Engine**: temperature, pressure, RPM
- **Generator**: load, voltage, fuel consumption
- **Hydraulics**: pressure, leaks, flow rate
- **Navigation**: GPS, compass, radar
- **Communication**: radio, satphone, internet
- **Ballast**: water level, pump status
- **Pumps**: flow rate, pressure, temperature

### Storage

```
data/collected/systems_resources/
├── system_logs.jsonl       (engine, hydraulics, etc.)
└── inventory_logs.jsonl    (fuel, water, food, supplies)
```

## API Reference

### Data Collection Endpoints

#### YOLO
- `POST /api/v1/data/yolo/image` - Upload training image
- `POST /api/v1/data/yolo/annotation` - Create annotation
- `GET /api/v1/data/yolo/config` - Get dataset config

#### Ollama
- `GET /api/v1/data/ollama/templates` - Get Q&A templates
- `POST /api/v1/data/ollama/training-pair` - Add single Q&A
- `POST /api/v1/data/ollama/bulk-upload` - Add multiple Q&A

#### Health & Wellness
- `POST /api/v1/data/health/vitals` - Record vitals
- `POST /api/v1/data/health/mental-assessment` - Record mental health

#### Systems & Resources
- `POST /api/v1/data/systems/log` - Log system event
- `POST /api/v1/data/resources/inventory` - Log inventory

#### Statistics
- `GET /api/v1/data/stats` - Collection statistics
- `GET /api/v1/data/export/{format}` - Export data

## Minimum Data Requirements

### For YOLO Training
- **100+ images** with annotations
- All 8 classes represented
- Variety of lighting/weather conditions
- Train/val/test split: 80/10/10

### For Ollama Fine-tuning
- **50+ Q&A pairs** minimum
- Balanced across 6 categories
- Clear, accurate answers
- Domain-specific (Arctic maritime)

### For Health & Wellness
- Daily vital signs tracking
- Weekly mental assessments
- Crew fitness logs

### For Systems & Resources
- Daily system status checks
- Inventory tracking
- Maintenance logs

## Data Organization

```
data/collected/
├── yolo/
│   ├── images/
│   │   ├── raw/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   ├── annotations/
│   ├── metadata/
│   └── dataset.yaml
├── ollama/
│   ├── training_data.jsonl
│   └── custom_models/
├── health_wellness/
│   ├── health_records.jsonl
│   ├── mental_assessments.jsonl
│   └── fitness_logs.jsonl
└── systems_resources/
    ├── system_logs.jsonl
    └── inventory_logs.jsonl
```

## Collection Timeline

**Week 1-2: Data Foundation**
- Deploy data collection API
- Create frontend annotation tool
- Establish daily logging routine

**Week 3-4: Initial Collection**
- Collect 100+ YOLO images
- Gather 50+ Ollama Q&A pairs
- Start health/systems tracking

**Week 5-6: Training Preparation**
- Check data quality
- Generate dataset configs
- Prepare training scripts

**Week 7-8: Model Training**
- Train YOLO on Arctic data
- Fine-tune Ollama on Q&A
- Evaluate and iterate

## Quality Assurance

### YOLO Data
- [ ] All bounding boxes are accurate
- [ ] All 8 classes represented
- [ ] No duplicate images
- [ ] Good lighting/visibility
- [ ] Proper coordinate normalization

### Ollama Data
- [ ] Q&A pairs are accurate
- [ ] Answers are complete
- [ ] Domain-appropriate
- [ ] No duplicate questions
- [ ] Proper JSON formatting

### Health Data
- [ ] Regular collection schedule
- [ ] No missing fields
- [ ] Reasonable values
- [ ] Privacy-compliant

## Next Steps

1. **Deploy data collection backend** (done)
2. **Create frontend annotation UI** (next)
3. **Start collecting data** (ongoing)
4. **Monitor collection stats** (weekly)
5. **Train models when thresholds met** (iterative)

## Status

✅ Backend data collector created
✅ API endpoints ready
✅ Data schema defined
⏳ Frontend annotation UI (needed)
⏳ YOLO training pipeline (ready for data)
⏳ Ollama fine-tuning pipeline (ready for data)

---

**Last Updated**: January 22, 2026
**Version**: 1.0.0
