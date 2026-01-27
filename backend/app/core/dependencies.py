"""Dependency injection for FastAPI endpoints."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Any

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.logging import get_logger

# Module logger
logger = get_logger(__name__)

# Database engine (initialized on startup)
_engine = None
_async_session_maker = None

# Redis connection pool (initialized on startup)
_redis_pool = None


def get_database_engine():
    """Get or create database engine with appropriate pool settings."""
    global _engine

    if _engine is not None:
        return _engine

    # Engine configuration based on database type and environment
    engine_kwargs = {
        "echo": settings.DB_ECHO,
        "future": True,
    }

    # SQLite-specific configuration
    if settings.DATABASE_URL.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
        # Use StaticPool for SQLite to avoid connection issues
        engine_kwargs["poolclass"] = StaticPool
        logger.info("Configuring SQLite database with StaticPool")
    else:
        # PostgreSQL configuration with connection pooling
        engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
        engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
        engine_kwargs["pool_pre_ping"] = True  # Verify connections before using
        engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour
        logger.info(
            "Configuring PostgreSQL database",
            extra={"pool_size": settings.DB_POOL_SIZE, "max_overflow": settings.DB_MAX_OVERFLOW},
        )

    try:
        _engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)
        logger.info("Database engine created successfully")
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}", exc_info=True)
        raise

    return _engine


def get_session_maker():
    """Get or create async session maker."""
    global _async_session_maker

    if _async_session_maker is not None:
        return _async_session_maker

    engine = get_database_engine()

    _async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    logger.info("Async session maker created")
    return _async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session.

    Yields:
        Database session with automatic transaction management

    Example:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            await session.close()


async def get_redis_pool():
    """Get or create Redis connection pool."""
    global _redis_pool

    if _redis_pool is not None:
        return _redis_pool

    try:
        _redis_pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            decode_responses=True,
            encoding="utf-8",
        )

        # Test connection
        redis_client = aioredis.Redis(connection_pool=_redis_pool)
        await redis_client.ping()
        await redis_client.close()

        logger.info("Redis connection pool created successfully")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Running without cache.", exc_info=True)
        # In dev mode, we can continue without Redis
        if settings.DEV_MODE:
            _redis_pool = None
        else:
            raise

    return _redis_pool


async def get_redis() -> AsyncGenerator[aioredis.Redis | None, None]:
    """Dependency to get Redis client.

    Yields:
        Redis client or None if Redis is unavailable

    Example:
        @router.get("/cached-data")
        async def get_cached_data(redis: Redis = Depends(get_redis)):
            if redis:
                cached = await redis.get("key")
                if cached:
                    return cached
            # Fetch from database...
    """
    pool = await get_redis_pool()

    if pool is None:
        yield None
        return

    redis_client = aioredis.Redis(connection_pool=pool)
    try:
        yield redis_client
    except Exception as e:
        logger.error(f"Redis operation error: {e}", exc_info=True)
        raise
    finally:
        await redis_client.close()


def get_logger_dependency(name: str | None = None) -> logging.Logger:
    """Dependency to get logger instance.

    Args:
        name: Logger name (defaults to calling module)

    Returns:
        Logger instance

    Example:
        @router.get("/items")
        async def get_items(logger: Logger = Depends(get_logger_dependency(__name__))):
            logger.info("Fetching items")
    """
    return get_logger(name or __name__)


# Typed dependencies for FastAPI
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[aioredis.Redis | None, Depends(get_redis)]
LoggerDep = Annotated[logging.Logger, Depends(get_logger_dependency)]


@asynccontextmanager
async def lifespan_context():
    """Context manager for application lifespan (startup/shutdown).

    Handles:
    - Database connection initialization
    - Redis connection pool setup
    - Graceful shutdown and cleanup
    """
    logger.info("Application startup initiated")

    # Initialize database
    try:
        engine = get_database_engine()
        async with engine.begin() as conn:
            # Test database connection
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        if not settings.DEV_MODE:
            raise

    # Initialize Redis
    try:
        await get_redis_pool()
    except Exception as e:
        logger.warning(f"Redis initialization failed: {e}")
        if not settings.DEV_MODE:
            raise

    # Initialize AI Modules
    try:
        from app.modules import navi, vakten
        await navi.navi.initialize()
        await vakten.vakten.initialize()
        logger.info("AI modules initialized (Navi, Vakten)")
    except Exception as e:
        logger.error(f"AI modules initialization failed: {e}", exc_info=True)

    logger.info("Application startup completed successfully")

    yield

    # Shutdown
    logger.info("Application shutdown initiated")

    try:
        # Close Redis connections
        if _redis_pool is not None:
            await _redis_pool.disconnect()
            logger.info("Redis connections closed")

        # Close database connections
        if _engine is not None:
            await _engine.dispose()
            logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)

    logger.info("Application shutdown completed")


async def verify_system_health() -> dict[str, Any]:
    """Verify system health by checking all dependencies.

    Returns:
        Dictionary with health status of each component
    """
    health = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "timestamp": None,
    }

    # Check database
    try:
        engine = get_database_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health["database"] = "healthy"
    except Exception as e:
        health["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        pool = await get_redis_pool()
        if pool is not None:
            redis_client = aioredis.Redis(connection_pool=pool)
            await redis_client.ping()
            await redis_client.close()
            health["redis"] = "healthy"
        else:
            health["redis"] = "not configured"
    except Exception as e:
        health["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
        logger.error(f"Redis health check failed: {e}")

    # Add timestamp
    health["timestamp"] = datetime.utcnow().isoformat()

    return health
