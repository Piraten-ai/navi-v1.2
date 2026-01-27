"""
Data Collection API Endpoints
Allows frontend to submit training data, health records, system logs, etc.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Optional
from app.core.data_collector import DataCollector

router = APIRouter(prefix="/api/v1/data", tags=["data-collection"])
collector = DataCollector()


# ====== YOLO TRAINING DATA ======

@router.post("/yolo/annotation")
async def create_yolo_annotation(
    image_filename: str,
    detections: List[Dict],
    metadata: Optional[Dict] = None
):
    """Create YOLO format annotation for image"""
    try:
        annotation_path = collector.create_yolo_annotation(
            image_filename=image_filename,
            detections=detections,
            image_metadata=metadata
        )
        return {
            "status": "success",
            "annotation_path": annotation_path,
            "detections_count": len(detections)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/yolo/image")
async def upload_yolo_image(file: UploadFile = File(...)):
    """Upload image for YOLO training"""
    try:
        import shutil
        from pathlib import Path
        
        image_path = collector.yolo_path / "images" / "raw" / file.filename
        image_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(image_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        return {
            "status": "success",
            "filename": file.filename,
            "size": image_path.stat().st_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/yolo/config")
async def get_yolo_config():
    """Get YOLO dataset configuration"""
    config_path = collector.create_yolo_dataset_config()
    return {
        "config_path": config_path,
        "status": "ready"
    }


# ====== OLLAMA TRAINING DATA ======

@router.post("/ollama/training-pair")
async def create_training_pair(
    question: str,
    answer: str,
    category: str,
    source: str = "manual"
):
    """Create Q&A pair for Ollama fine-tuning"""
    try:
        pair = collector.create_ollama_training_pair(
            question=question,
            answer=answer,
            category=category,
            source=source
        )
        # Save immediately
        collector.save_ollama_training_data([pair])
        return {
            "status": "success",
            "pair": pair
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ollama/templates")
async def get_ollama_templates():
    """Get Q&A templates for easy data collection"""
    templates = collector.get_ollama_training_templates()
    return {
        "templates": templates,
        "categories": list(templates.keys()),
        "total_pairs": sum(len(v) for v in templates.values())
    }


@router.post("/ollama/bulk-upload")
async def bulk_upload_training_pairs(pairs: List[Dict]):
    """Upload multiple training pairs at once"""
    try:
        path = collector.save_ollama_training_data(pairs)
        return {
            "status": "success",
            "pairs_uploaded": len(pairs),
            "path": path
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ====== HEALTH & WELLNESS DATA ======

@router.post("/health/vitals")
async def record_vitals(
    crew_id: str,
    heart_rate: int,
    blood_pressure: str,
    temperature: float,
    notes: str = ""
):
    """Record crew vital signs"""
    try:
        record = collector.create_health_record(
            crew_id=crew_id,
            vital_signs={
                "heart_rate": heart_rate,
                "blood_pressure": blood_pressure,
                "temperature": temperature
            },
            notes=notes,
            record_type="health"
        )
        collector.save_health_records([record])
        return {
            "status": "success",
            "record": record
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/health/mental-assessment")
async def record_mental_health(
    crew_id: str,
    stress_level: int,
    sleep_quality: int,
    mood: str,
    notes: str = ""
):
    """Record crew mental health assessment"""
    if not (1 <= stress_level <= 10):
        raise HTTPException(status_code=400, detail="stress_level must be 1-10")
    if not (1 <= sleep_quality <= 10):
        raise HTTPException(status_code=400, detail="sleep_quality must be 1-10")
    
    try:
        record = collector.create_health_record(
            crew_id=crew_id,
            vital_signs={
                "stress_level": stress_level,
                "sleep_quality": sleep_quality,
                "mood": mood
            },
            notes=notes,
            record_type="psychological"
        )
        collector.save_health_records([record])
        return {
            "status": "success",
            "record": record
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ====== SYSTEMS & RESOURCES DATA ======

@router.post("/systems/log")
async def log_system_event(
    system: str,
    status: str,
    details: Optional[Dict] = None,
    severity: str = "info"
):
    """Log system status event"""
    try:
        log = collector.create_system_log(
            system=system,
            status=status,
            details=details or {},
            severity=severity
        )
        collector.save_system_logs([log])
        return {
            "status": "success",
            "log": log
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resources/inventory")
async def log_inventory(
    resource: str,
    quantity: float,
    unit: str = "liters"
):
    """Log resource inventory level"""
    try:
        log = collector.create_system_log(
            system=f"resource_{resource}",
            status="inventory",
            details={
                "quantity": quantity,
                "unit": unit
            }
        )
        collector.save_system_logs([log])
        return {
            "status": "success",
            "log": log
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ====== DATA STATISTICS ======

@router.get("/stats")
async def get_data_stats():
    """Get statistics on collected data"""
    stats = collector.get_collection_stats()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": stats,
        "ready_for_training": {
            "yolo": stats["yolo"]["images"] > 100,
            "ollama": stats["ollama"]["training_pairs"] > 50
        }
    }


@router.get("/export/{format}")
async def export_data(format: str):
    """Export data in training format"""
    valid_formats = ["yolo", "ollama"]
    if format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"format must be one of {valid_formats}")
    
    try:
        export_path = collector.export_for_training(format=format)
        return {
            "status": "ready",
            "format": format,
            "path": export_path
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    from datetime import datetime
    print("Data Collection API initialized")
