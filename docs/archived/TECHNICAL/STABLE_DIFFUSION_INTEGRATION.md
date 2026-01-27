# Stable Diffusion Integration - Complete

## Changes Made

### 1. New Backend Module: `backend/app/modules/stable_diffusion.py`
- **StableDiffusionModule** class for image generation
- Methods:
  - `generate_map_visualization()` - Create nautical charts
  - `generate_weather_visualization()` - Render weather conditions
  - `generate_safety_alert_image()` - Generate alert graphics
  - `generate_training_data()` - Create synthetic training data
- Async initialization and cleanup
- Mock mode for development

### 2. New API Router: `backend/app/routers/image_generation.py`
- **Endpoints:**
  - `POST /api/v1/images/generate-map` - Map visualization
  - `POST /api/v1/images/generate-weather` - Weather rendering
  - `POST /api/v1/images/generate-alert` - Safety alerts
  - `POST /api/v1/images/generate-training-data` - Training data
  - `GET /api/v1/images/health` - Service health check

### 3. Docker Compose Updates
- Added **sd-api** service
  - Image: `klud/stable-diffusion-api:latest`
  - Port: 5000
  - GPU support: NVIDIA runtime
  - Volume: `./models/stable-diffusion`
- Backend now depends on `sd-api`
- Added env var: `STABLE_DIFFUSION_URL=http://sd-api:5000`

### 4. Backend Main Updates
- Import `StableDiffusionModule` and `image_generation` router
- Initialize SD module on startup
- Register image generation router
- Cleanup SD module on shutdown

## Usage

### Example API Call - Generate Weather Visualization
```bash
curl -X POST http://localhost:8000/api/v1/images/generate-weather \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Atlantic Ocean",
    "wind_speed": "25 knots",
    "wave_height": "2.5m",
    "visibility": "5km"
  }'
```

### Example API Call - Generate Training Data
```bash
curl -X POST http://localhost:8000/api/v1/images/generate-training-data \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "Ship detection on rough seas",
    "variations": 5
  }'
```

## Deployment

Start with updated docker-compose:
```bash
docker-compose down
docker-compose up -d
```

This will:
1. Start Stable Diffusion API service
2. Wait for SD API health check
3. Backend connects to SD API on initialization
4. Image generation endpoints ready

## Architecture

```
Frontend Request
  ↓
Backend API (/api/v1/images/*)
  ↓
StableDiffusionModule (asyncio)
  ↓
Stable Diffusion API (sd-api:5000)
  ↓
Generated Image (PNG/JPG)
  ↓
API Response with image_path
```

## Features

✅ Async/await for non-blocking image generation
✅ Graceful error handling with mock fallback
✅ NVIDIA GPU support for fast generation
✅ Multiple image types: maps, weather, alerts, training data
✅ Mock mode for development without GPU
✅ Proper cleanup on shutdown

## Next Steps (Optional)

1. Add image caching/persistence to MinIO
2. Implement image batch processing
3. Add model selection (different Stable Diffusion versions)
4. Create frontend UI for image generation
5. Add image processing pipeline (enhancement, annotation)
