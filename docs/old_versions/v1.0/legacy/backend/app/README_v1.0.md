**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# AADS Backend Core

Production-ready FastAPI backend core for the Advanced Autonomous Driving System (AADS).

## Overview

This backend core provides a bulletproof foundation with:

- **FastAPI Application** - High-performance async API with automatic OpenAPI docs
- **Flexible Configuration** - Pydantic Settings supporting dev/prod environments
- **Bulletproof Logging** - Structured JSON logging with rotation and console output
- **Dependency Injection** - Clean database, Redis, and logger dependencies
- **WebSocket Support** - Real-time bidirectional communication
- **Graceful Shutdown** - Proper cleanup of connections and resources
- **Health Checks** - Comprehensive health and status endpoints

## Architecture

```
backend/app/
â”œâ”€â”€ __init__.py              # Package initialization
â”œâ”€â”€ main.py                  # FastAPI application entry point
â”œâ”€â”€ core/                    # Core application components
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ config.py           # Pydantic settings with validation
â”‚   â”œâ”€â”€ dependencies.py     # Dependency injection (DB, Redis, Logger)
â”‚   â””â”€â”€ logging.py          # Structured logging setup
â””â”€â”€ modules/                 # Feature modules (to be added)
    â””â”€â”€ __init__.py
```

## Features

### 1. Configuration (`core/config.py`)

- **Environment-based settings** using Pydantic Settings
- **Dev/Prod mode support** - SQLite for laptop, PostgreSQL for Jetson
- **Feature flags** - MOCK_CAMERA, DEV_MODE
- **Validation** - Automatic type checking and validation
- **Secure defaults** - Safe defaults with production warnings

```python
from app.core.config import settings

if settings.DEV_MODE:
    print("Running in development mode")
```

### 2. Logging (`core/logging.py`)

- **JSON structured logging** for production machine parsing
- **Colored console output** for development readability
- **Rotating file handler** - Automatic log rotation (10MB, 5 backups)
- **Module-specific loggers** - Organized logging per module
- **Contextual logging** - Add context to all log records

```python
from app.core.logging import get_logger, get_contextual_logger

# Standard logger
logger = get_logger(__name__)
logger.info("Processing request")

# Contextual logger (adds context to all logs)
logger = get_contextual_logger(__name__, request_id="abc-123", user_id=456)
logger.info("User action")  # Will include request_id and user_id
```

### 3. Dependency Injection (`core/dependencies.py`)

- **Database sessions** - Async SQLAlchemy with automatic transaction management
- **Redis connections** - Connection pooling with fallback
- **Logger instances** - Module-specific loggers
- **Health checks** - Verify all dependencies

```python
from fastapi import APIRouter
from app.core.dependencies import DatabaseDep, RedisDep, LoggerDep

router = APIRouter()

@router.get("/items")
async def get_items(db: DatabaseDep, redis: RedisDep, logger: LoggerDep):
    logger.info("Fetching items")
    # Use db and redis...
```

### 4. FastAPI Application (`main.py`)

- **CORS middleware** - Configurable cross-origin support
- **WebSocket manager** - Real-time connection management
- **Health endpoints** - `/health` and `/api/v1/status`
- **Global exception handler** - Graceful error handling
- **Graceful shutdown** - Clean resource cleanup

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and customize:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Development mode (uses SQLite)
DEV_MODE=true
DATABASE_URL=sqlite+aiosqlite:///./aads.db

# Production mode (uses PostgreSQL)
DEV_MODE=false
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/aads
```

### 3. Run the Application

**Development mode with auto-reload:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
python app/main.py
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health
- **System Status**: http://localhost:8000/api/v1/status
- **WebSocket**: ws://localhost:8000/ws

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Deployment environment |
| `DEV_MODE` | true | Development mode flag |
| `MOCK_CAMERA` | true | Use mock camera |
| `DATABASE_URL` | sqlite+aiosqlite:///./aads.db | Database connection |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API URL |
| `LOG_LEVEL` | INFO | Logging level |
| `LOG_FILE` | logs/aads.log | Log file path |
| `LOG_JSON` | true | JSON log format |
| `CORS_ORIGINS` | http://localhost:3000,... | Allowed origins |
| `SECRET_KEY` | change-me... | JWT secret key |
| `WS_MAX_CONNECTIONS` | 100 | Max WebSocket connections |

See `.env.example` for complete configuration options.

## API Endpoints

### Health & Status

```
GET  /                    - API information
GET  /health             - Health check (for load balancers)
GET  /api/v1/status      - Detailed system status
```

### WebSocket

```
WS   /ws                 - Real-time updates
```

#### WebSocket Message Format

**Client -> Server:**
```json
{
  "type": "pong" | "subscribe",
  "topics": ["telemetry", "detection"]  // for subscribe
}
```

**Server -> Client:**
```json
{
  "type": "system" | "telemetry" | "detection" | "ping",
  "event": "connected" | "shutdown" | ...,
  "data": {...},
  "timestamp": "2024-01-18T12:00:00"
}
```

## Development vs Production

### Development Mode (Laptop)

```bash
DEV_MODE=true
DATABASE_URL=sqlite+aiosqlite:///./aads.db
MOCK_CAMERA=true
LOG_JSON=false  # Colored console output
```

- Uses SQLite database (no PostgreSQL needed)
- Mock camera for testing without hardware
- Colored console logs for readability
- Auto-reload on code changes
- Relaxed error handling

### Production Mode (Jetson)

```bash
DEV_MODE=false
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/aads
MOCK_CAMERA=false
LOG_JSON=true  # Structured JSON logs
```

- PostgreSQL database with connection pooling
- Real camera hardware
- JSON structured logs for parsing
- Multiple worker processes
- Strict error handling

## Logging

### Log Levels

- **DEBUG** - Detailed diagnostic information
- **INFO** - General informational messages (default)
- **WARNING** - Warning messages (non-critical issues)
- **ERROR** - Error messages (handled errors)
- **CRITICAL** - Critical errors (system failures)

### Log Format

**JSON (Production):**
```json
{
  "timestamp": "2024-01-18T12:00:00",
  "level": "INFO",
  "logger": "app.modules.camera",
  "module": "camera",
  "function": "capture_frame",
  "line": 42,
  "message": "Frame captured",
  "environment": "production"
}
```

**Console (Development):**
```
2024-01-18 12:00:00 | INFO     | app.modules.camera | Frame captured
```

## Database

### Connection Management

- **Async SQLAlchemy** - Non-blocking database operations
- **Connection pooling** - Efficient connection reuse (PostgreSQL)
- **Auto-reconnect** - Automatic recovery from connection loss
- **Transaction management** - Automatic commit/rollback

### Usage

```python
from sqlalchemy import select
from app.core.dependencies import DatabaseDep
from app.models import Item

@router.get("/items")
async def get_items(db: DatabaseDep):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items
```

## Redis

### Features

- **Connection pooling** - Efficient connection reuse
- **Graceful fallback** - Continues without Redis in dev mode
- **Async operations** - Non-blocking Redis calls

### Usage

```python
from app.core.dependencies import RedisDep

@router.get("/cached-data")
async def get_cached_data(redis: RedisDep):
    if redis:
        cached = await redis.get("key")
        if cached:
            return cached
    # Fetch from database...
```

## WebSocket

### Connection Manager

The `ConnectionManager` handles all WebSocket connections:

- **Connection limits** - Configurable max connections
- **Broadcasting** - Send to all connected clients
- **Personal messages** - Send to specific client
- **Heartbeat** - Automatic ping/pong to detect dead connections
- **Graceful shutdown** - Notify clients before shutdown

### Broadcasting Example

```python
from app.main import connection_manager

# Broadcast to all clients
await connection_manager.broadcast({
    "type": "detection",
    "data": {"object": "person", "confidence": 0.95},
    "timestamp": datetime.utcnow().isoformat()
})
```

## Error Handling

- **Global exception handler** - Catches unhandled errors
- **Structured error responses** - Consistent error format
- **Detailed logging** - Full traceback in logs
- **Dev/Prod differences** - Detailed errors in dev, generic in prod

## Health Checks

### Health Endpoint (`/health`)

Returns 200 if healthy, 503 if unhealthy:

```json
{
  "status": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "timestamp": "2024-01-18T12:00:00"
}
```

### Status Endpoint (`/api/v1/status`)

Detailed system information:

```json
{
  "application": {
    "name": "AADS Backend",
    "version": "1.0.0",
    "environment": "development",
    "dev_mode": true
  },
  "health": {...},
  "websocket": {
    "active_connections": 5,
    "max_connections": 100
  },
  "features": {
    "mock_camera": true,
    "ollama_enabled": true
  },
  "timestamp": "2024-01-18T12:00:00"
}
```

## Testing

```bash
# Import test
python -c "from app.main import app; print('âœ“ App loaded')"

# Run with uvicorn
uvicorn app.main:app --reload

# Check logs
tail -f logs/aads.log
```

## Next Steps

After setting up the core, add feature modules:

1. **Camera Module** - Video capture and streaming
2. **Detection Module** - Object detection with YOLO
3. **LLM Module** - Ollama integration for analysis
4. **Telemetry Module** - InfluxDB time-series data
5. **Storage Module** - MinIO/S3 for media storage

Each module will have its own router that gets included in `main.py`.

## Troubleshooting

**Database connection errors:**
- Check `DATABASE_URL` is correct
- Ensure database server is running (PostgreSQL)
- In dev mode, SQLite file will be created automatically

**Redis connection errors:**
- Check `REDIS_URL` is correct
- Ensure Redis server is running
- In dev mode, app will continue without Redis

**Import errors:**
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.11+ recommended)

**WebSocket connection limit:**
- Increase `WS_MAX_CONNECTIONS` in settings
- Monitor active connections via `/api/v1/status`

## License

Part of the AADS (Advanced Autonomous Driving System) project.

