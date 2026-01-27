**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# Adding New Modules to AADS Backend

This guide shows how to add new feature modules to the AADS backend core.

## Module Structure

Each module should follow this structure:

```
app/modules/<module_name>/
â”œâ”€â”€ __init__.py          # Module initialization
â”œâ”€â”€ routes.py            # FastAPI routes
â”œâ”€â”€ models.py            # Database models (optional)
â”œâ”€â”€ schemas.py           # Pydantic schemas
â”œâ”€â”€ service.py           # Business logic
â””â”€â”€ dependencies.py      # Module-specific dependencies (optional)
```

## Example: Camera Module

### 1. Create Module Directory

```bash
mkdir -p app/modules/camera
touch app/modules/camera/__init__.py
```

### 2. Create Schemas (`schemas.py`)

```python
"""Camera module Pydantic schemas."""

from pydantic import BaseModel, Field


class CameraConfig(BaseModel):
    """Camera configuration schema."""
    
    width: int = Field(ge=640, le=3840)
    height: int = Field(ge=480, le=2160)
    fps: int = Field(ge=1, le=60)
    device_id: int = Field(ge=0, le=10)


class FrameResponse(BaseModel):
    """Camera frame response."""
    
    frame_id: str
    timestamp: str
    width: int
    height: int
    format: str
```

### 3. Create Service (`service.py`)

```python
"""Camera service with business logic."""

import logging
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CameraService:
    """Camera service for video capture."""
    
    def __init__(self):
        self.camera = None
        self.is_running = False
    
    async def start(self) -> None:
        """Start camera capture."""
        if settings.MOCK_CAMERA:
            logger.info("Starting mock camera")
            # Mock implementation
        else:
            logger.info("Starting real camera")
            # Real camera implementation
        
        self.is_running = True
    
    async def stop(self) -> None:
        """Stop camera capture."""
        logger.info("Stopping camera")
        self.is_running = False
    
    async def capture_frame(self) -> Optional[bytes]:
        """Capture a single frame."""
        if not self.is_running:
            return None
        
        # Capture logic here
        return b"frame_data"


# Global camera service instance
camera_service = CameraService()
```

### 4. Create Routes (`routes.py`)

```python
"""Camera module API routes."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.dependencies import LoggerDep
from app.modules.camera.schemas import CameraConfig, FrameResponse
from app.modules.camera.service import camera_service

router = APIRouter()


@router.post("/start")
async def start_camera(logger: LoggerDep):
    """Start camera capture."""
    try:
        await camera_service.start()
        logger.info("Camera started successfully")
        return {"status": "started", "message": "Camera capture started"}
    except Exception as e:
        logger.error(f"Failed to start camera: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start camera: {str(e)}"
        )


@router.post("/stop")
async def stop_camera(logger: LoggerDep):
    """Stop camera capture."""
    try:
        await camera_service.stop()
        logger.info("Camera stopped successfully")
        return {"status": "stopped", "message": "Camera capture stopped"}
    except Exception as e:
        logger.error(f"Failed to stop camera: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop camera: {str(e)}"
        )


@router.get("/status")
async def get_camera_status():
    """Get camera status."""
    return {
        "is_running": camera_service.is_running,
        "mock_mode": settings.MOCK_CAMERA,
    }


@router.get("/frame", response_model=FrameResponse)
async def get_frame(logger: LoggerDep):
    """Capture and return a single frame."""
    frame_data = await camera_service.capture_frame()
    
    if frame_data is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Camera is not running"
        )
    
    return FrameResponse(
        frame_id="abc123",
        timestamp="2024-01-18T12:00:00",
        width=1920,
        height=1080,
        format="jpeg"
    )
```

### 5. Register Routes in Main App

Edit `app/main.py` and add:

```python
# Add import at the top
from app.modules.camera.routes import router as camera_router

# Add after app creation and before the root endpoint
app.include_router(
    camera_router,
    prefix=f"{settings.API_PREFIX}/camera",
    tags=["camera"]
)
```

### 6. Test the Module

```bash
# Start the server
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/api/v1/camera/status
curl -X POST http://localhost:8000/api/v1/camera/start
curl http://localhost:8000/api/v1/camera/frame
curl -X POST http://localhost:8000/api/v1/camera/stop

# Check OpenAPI docs
open http://localhost:8000/api/v1/docs
```

## Module with Database Models

### 1. Create Models (`models.py`)

```python
"""Camera module database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CameraSession(Base):
    """Camera capture session model."""
    
    __tablename__ = "camera_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    frame_count = Column(Integer, default=0)
    device_id = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Integer)
```

### 2. Use Database in Routes

```python
from sqlalchemy import select
from app.core.dependencies import DatabaseDep
from app.modules.camera.models import CameraSession


@router.get("/sessions")
async def get_sessions(db: DatabaseDep):
    """Get all camera sessions."""
    result = await db.execute(select(CameraSession))
    sessions = result.scalars().all()
    return sessions


@router.post("/sessions")
async def create_session(db: DatabaseDep, config: CameraConfig):
    """Create a new camera session."""
    session = CameraSession(
        session_id="session-123",
        device_id=config.device_id,
        width=config.width,
        height=config.height,
        fps=config.fps
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
```

## Module with WebSocket Support

```python
from app.main import connection_manager

@router.websocket("/stream")
async def stream_camera(websocket: WebSocket):
    """Stream camera frames via WebSocket."""
    await websocket.accept()
    
    try:
        while True:
            frame_data = await camera_service.capture_frame()
            
            if frame_data:
                await websocket.send_bytes(frame_data)
            
            await asyncio.sleep(1/30)  # 30 FPS
            
    except WebSocketDisconnect:
        logger.info("Client disconnected from camera stream")
```

## Module with Background Tasks

```python
from fastapi import BackgroundTasks


def process_frame_background(frame_data: bytes):
    """Process frame in background."""
    # Heavy processing here
    pass


@router.post("/capture")
async def capture_with_processing(background_tasks: BackgroundTasks):
    """Capture frame and process in background."""
    frame_data = await camera_service.capture_frame()
    
    if frame_data:
        background_tasks.add_task(process_frame_background, frame_data)
    
    return {"status": "captured", "processing": "queued"}
```

## Module Lifecycle (Startup/Shutdown)

Add to `app/main.py` lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    
    # Startup
    async with lifespan_context():
        # Initialize camera service
        from app.modules.camera.service import camera_service
        logger.info("Initializing camera service")
        # camera_service initialization here
        
        yield
        
        # Shutdown
        logger.info("Shutting down camera service")
        await camera_service.stop()
```

## Best Practices

1. **Use dependency injection** for database, Redis, logger
2. **Separate concerns**: routes, schemas, services, models
3. **Add docstrings** to all public functions
4. **Use type hints** everywhere
5. **Log important events** with appropriate levels
6. **Handle errors gracefully** with try-except
7. **Return proper HTTP status codes**
8. **Use Pydantic schemas** for validation
9. **Write async functions** for I/O operations
10. **Test endpoints** after creation

## Module Checklist

- [ ] Create module directory structure
- [ ] Define Pydantic schemas
- [ ] Implement service logic
- [ ] Create API routes
- [ ] Add database models (if needed)
- [ ] Register routes in main.py
- [ ] Add startup/shutdown logic (if needed)
- [ ] Test all endpoints
- [ ] Add logging
- [ ] Handle errors
- [ ] Document in OpenAPI (docstrings)
- [ ] Write tests (future)

## Example Modules to Create

1. **Camera Module** - Video capture and streaming
2. **Detection Module** - YOLO object detection
3. **LLM Module** - Ollama integration
4. **Telemetry Module** - InfluxDB time-series data
5. **Storage Module** - MinIO/S3 file storage
6. **Auth Module** - JWT authentication
7. **Config Module** - Runtime configuration
8. **Monitoring Module** - Prometheus metrics

## Resources

- FastAPI docs: https://fastapi.tiangolo.com
- SQLAlchemy docs: https://docs.sqlalchemy.org
- Pydantic docs: https://docs.pydantic.dev

---

**Need help?** Check `backend/app/README.md` for more details.

