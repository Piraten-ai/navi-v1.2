"""
Image generation API endpoints
Uses Stable Diffusion for maps, weather, alerts, and training data
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/images", tags=["image_generation"])

# Placeholder for SD module instance (injected from main.py)
sd_module = None


class MapVisualizationRequest(BaseModel):
    location: str
    route_description: str
    hazards: Optional[List[str]] = None
    width: int = 768
    height: int = 768


class WeatherVisualizationRequest(BaseModel):
    location: str
    wind_speed: str
    wave_height: str
    visibility: str
    width: int = 512
    height: int = 512


class SafetyAlertRequest(BaseModel):
    alert_type: str
    severity: str  # critical, high, medium, low
    description: str
    width: int = 512
    height: int = 512


class TrainingDataRequest(BaseModel):
    scenario: str
    variations: int = 5
    width: int = 512
    height: int = 512


@router.post("/generate-map")
async def generate_map_visualization(request: MapVisualizationRequest):
    """Generate nautical map visualization"""
    if not sd_module:
        raise HTTPException(status_code=503, detail="Image generation service not available")
    
    try:
        image_path = await sd_module.generate_map_visualization(
            location=request.location,
            route_description=request.route_description,
            hazards=request.hazards,
            width=request.width,
            height=request.height
        )
        return {
            "status": "success",
            "image_path": image_path,
            "type": "map"
        }
    except Exception as e:
        logger.error(f"Map generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-weather")
async def generate_weather_visualization(request: WeatherVisualizationRequest):
    """Generate weather condition visualization"""
    if not sd_module:
        raise HTTPException(status_code=503, detail="Image generation service not available")
    
    try:
        conditions = {
            "wind_speed": request.wind_speed,
            "wave_height": request.wave_height,
            "visibility": request.visibility
        }
        image_path = await sd_module.generate_weather_visualization(
            conditions=conditions,
            location=request.location,
            width=request.width,
            height=request.height
        )
        return {
            "status": "success",
            "image_path": image_path,
            "type": "weather"
        }
    except Exception as e:
        logger.error(f"Weather visualization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-alert")
async def generate_safety_alert(request: SafetyAlertRequest):
    """Generate safety alert visualization"""
    if not sd_module:
        raise HTTPException(status_code=503, detail="Image generation service not available")
    
    try:
        image_path = await sd_module.generate_safety_alert_image(
            alert_type=request.alert_type,
            severity=request.severity,
            description=request.description,
            width=request.width,
            height=request.height
        )
        return {
            "status": "success",
            "image_path": image_path,
            "type": "alert",
            "severity": request.severity
        }
    except Exception as e:
        logger.error(f"Alert generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-training-data")
async def generate_training_data(request: TrainingDataRequest):
    """Generate synthetic training data for ML models"""
    if not sd_module:
        raise HTTPException(status_code=503, detail="Image generation service not available")
    
    try:
        images = await sd_module.generate_training_data(
            scenario=request.scenario,
            variations=request.variations,
            width=request.width,
            height=request.height
        )
        return {
            "status": "success",
            "images": images,
            "count": len(images),
            "type": "training_data"
        }
    except Exception as e:
        logger.error(f"Training data generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check if image generation service is healthy"""
    if not sd_module:
        return {"status": "unavailable", "service": "stable-diffusion"}
    
    return {
        "status": "healthy" if sd_module.initialized else "initializing",
        "service": "stable-diffusion",
        "initialized": sd_module.initialized
    }
