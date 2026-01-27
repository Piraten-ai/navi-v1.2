**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# AADS Backend Core - Quick Reference

## ðŸš€ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run development server
uvicorn app.main:app --reload

# Visit documentation
open http://localhost:8000/api/v1/docs
```

## ðŸ“ Structure

```
backend/app/
â”œâ”€â”€ main.py              # FastAPI application (entry point)
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ config.py        # Pydantic settings (44 options)
â”‚   â”œâ”€â”€ logging.py       # Structured logging
â”‚   â””â”€â”€ dependencies.py  # Dependency injection
â””â”€â”€ modules/             # Feature modules (add here)
```

## ðŸ”§ Configuration

### Development Mode (Laptop)
```bash
DEV_MODE=true
DATABASE_URL=sqlite+aiosqlite:///./aads.db
MOCK_CAMERA=true
LOG_JSON=false
```

### Production Mode (Jetson)
```bash
DEV_MODE=false
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
MOCK_CAMERA=false
LOG_JSON=true
SECRET_KEY=<generate-with-openssl-rand-hex-32>
```

## ðŸ›£ï¸ API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check (200/503) |
| GET | `/api/v1/status` | System status |
| WS | `/ws` | WebSocket real-time |
| GET | `/api/v1/docs` | OpenAPI docs |

## ðŸ’‰ Using Dependencies

```python
from fastapi import APIRouter
from app.core.dependencies import DatabaseDep, RedisDep, LoggerDep

router = APIRouter()

@router.get("/items")
async def get_items(
    db: DatabaseDep,
    redis: RedisDep,
    logger: LoggerDep
):
    logger.info("Fetching items")
    # Use db and redis...
```

## ðŸ“ Logging

```python
from app.core.logging import get_logger, get_contextual_logger

# Standard logger
logger = get_logger(__name__)
logger.info("Message", extra={"key": "value"})

# Contextual logger (adds context to all logs)
logger = get_contextual_logger(__name__, request_id="123")
logger.info("Message")  # Includes request_id automatically
```

## ðŸŒ WebSocket

```python
from app.main import connection_manager

# Broadcast to all clients
await connection_manager.broadcast({
    "type": "event",
    "data": {...},
    "timestamp": datetime.utcnow().isoformat()
})

# Send to specific client
await connection_manager.send_personal(message, websocket)
```

## ðŸ¥ Health Checks

```python
from app.core.dependencies import verify_system_health

health = await verify_system_health()
# Returns: {"status": "healthy", "database": "healthy", "redis": "healthy"}
```

## ðŸ” Configuration Access

```python
from app.core.config import settings

if settings.DEV_MODE:
    print("Running in dev mode")

if settings.is_production:
    print("Running in production")

database_url = settings.DATABASE_URL
log_level = settings.LOG_LEVEL
```

## ðŸ³ Docker

```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose up -d
```

## ðŸ§ª Testing

```bash
# Verify setup
python verify_core.py

# Syntax check
python -m py_compile app/**/*.py

# Run server
uvicorn app.main:app --reload

# Check health
curl http://localhost:8000/health
```

## ðŸ“Š Key Features

âœ… **Dual-mode support** (dev/prod)  
âœ… **Structured logging** (JSON + console)  
âœ… **Health monitoring** (DB, Redis)  
âœ… **WebSocket** (real-time updates)  
âœ… **Dependency injection** (DB, Redis, Logger)  
âœ… **CORS middleware** (configurable)  
âœ… **Type hints** (full coverage)  
âœ… **Error handling** (global handler)  
âœ… **Graceful shutdown** (cleanup)  
âœ… **Auto-reload** (development)  

## ðŸ” Security

- Change `SECRET_KEY` in production
- Use environment variables for secrets
- Configure CORS origins
- Enable HTTPS in production
- Set up firewall rules

## ðŸ“¦ Dependencies

Core packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `sqlalchemy` - ORM
- `aiosqlite` - Async SQLite
- `redis` - Caching
- `python-json-logger` - Structured logs

## ðŸŽ¯ Next Steps

1. Add database models
2. Create feature modules (camera, detection, LLM)
3. Implement authentication
4. Add Alembic migrations
5. Write tests
6. Set up CI/CD

## ðŸ“š Documentation

- **README**: `backend/app/README.md` (comprehensive guide)
- **Summary**: `backend/IMPLEMENTATION_SUMMARY.md` (detailed summary)
- **Quick Ref**: This file (quick reference)
- **OpenAPI**: `http://localhost:8000/api/v1/docs` (interactive docs)

## ðŸ› Troubleshooting

### Import errors
```bash
pip install -r requirements.txt
```

### Database connection errors
Check `DATABASE_URL` in `.env`

### Redis connection errors
App continues without Redis in dev mode

### Port already in use
```bash
# Change port
uvicorn app.main:app --port 8001
```

## ðŸ“ž Support

See `backend/app/README.md` for detailed troubleshooting guide.

---

**Version:** 1.0.0  
**Updated:** 2024-01-18

