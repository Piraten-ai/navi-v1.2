"""AADS FastAPI Application - Main entry point."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.dependencies import lifespan_context, verify_system_health
from app.core.logging import get_logger

# Import modules
from app.modules import vakten, navi, navigator, legen, psykologen, ingenioren
from app.modules.nmea_gps import nmea_gps
from app.modules.signalk_client import signalk
from app.modules.autopilot_controller import autopilot
from app.modules.track_control import track
from app.modules.emergency_behaviors import emergency
from app.modules.autopilot_telemetry import telemetry_logger
from app.modules.voice_system import voice_system
from app.modules.bridge_logger import BridgeLogger

# Initialize logger
logger = get_logger(__name__)


# Pydantic models for request bodies
class NaviChatRequest(BaseModel):
    """Chat message request for Navi AI assistant"""
    message: str
    context: dict = None


# Bridge models for Arduino analog ingestion
class BridgeAnalogPayload(BaseModel):
    """Analog bridge payload from Raspberry Pi."""
    timestamp: str | None = None
    signals: dict[str, float | int]
    source: str | None = "arduino"


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> bool:
        """Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket connection to register

        Returns:
            True if connection accepted, False if limit reached
        """
        async with self._lock:
            if len(self.active_connections) >= settings.WS_MAX_CONNECTIONS:
                logger.warning("WebSocket connection limit reached", extra={"max_connections": settings.WS_MAX_CONNECTIONS})
                return False

            await websocket.accept()
            self.active_connections.append(websocket)

            logger.info(
                "WebSocket client connected",
                extra={
                    "client": websocket.client.host if websocket.client else "unknown",
                    "active_connections": len(self.active_connections),
                },
            )
            return True

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

                logger.info("WebSocket client disconnected", extra={"active_connections": len(self.active_connections)})

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast message to all connected clients.

        Args:
            message: Message to broadcast (will be JSON serialized)
        """
        if not self.active_connections:
            return

        async with self._lock:
            disconnected = []

            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(
                        f"Failed to send message to client: {e}",
                        extra={"client": connection.client.host if connection.client else "unknown"},
                    )
                    disconnected.append(connection)

            # Clean up disconnected clients
            for connection in disconnected:
                self.active_connections.remove(connection)

    async def send_personal(self, message: dict[str, Any], websocket: WebSocket) -> None:
        """Send message to a specific client.

        Args:
            message: Message to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            await self.disconnect(websocket)

    async def get_connection_count(self) -> int:
        """Get number of active connections.

        Returns:
            Number of active WebSocket connections
        """
        async with self._lock:
            return len(self.active_connections)


# Global connection manager
connection_manager = ConnectionManager()
bridge_logger = BridgeLogger()

# Latest bridge payload (in-memory)
last_bridge_payload: dict[str, Any] | None = None


async def _nmea_broadcast_loop():
    """Background task to broadcast NMEA data to WebSocket clients."""
    logger.info("Starting NMEA broadcast loop")

    try:
        while True:
            try:
                # Get current NMEA data
                nmea_data = nmea_gps.get_data()

                # Only broadcast if we have valid data
                if nmea_data.get("latitude") is not None:
                    # Broadcast to all connected clients
                    await connection_manager.broadcast(
                        {
                            "type": "nmea",
                            "data": nmea_data,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                    logger.debug(
                        "Broadcasted NMEA data",
                        extra={
                            "clients": len(connection_manager.active_connections),
                            "lat": nmea_data.get("latitude"),
                            "lon": nmea_data.get("longitude"),
                        },
                    )

                # Wait before next broadcast
                await asyncio.sleep(settings.NMEA_UPDATE_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in NMEA broadcast loop: {e}", exc_info=True)
                await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info("NMEA broadcast loop cancelled")
    finally:
        logger.info("NMEA broadcast loop stopped")


async def _signalk_broadcast_loop():
    """Background task to broadcast Signal K data to WebSocket clients."""
    logger.info("Starting Signal K broadcast loop")

    try:
        while True:
            try:
                # Get current Signal K data
                signalk_data = signalk.get_data()

                # Only broadcast if we have valid data
                if signalk_data.get("navigation", {}).get("latitude") is not None:
                    # Broadcast to all connected clients
                    await connection_manager.broadcast(
                        {
                            "type": "signalk",
                            "data": signalk_data,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                    logger.debug(
                        "Broadcasted Signal K data",
                        extra={
                            "clients": len(connection_manager.active_connections),
                            "lat": signalk_data.get("navigation", {}).get("latitude"),
                            "lon": signalk_data.get("navigation", {}).get("longitude"),
                        },
                    )

                # Wait before next broadcast
                await asyncio.sleep(settings.SIGNALK_UPDATE_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in Signal K broadcast loop: {e}", exc_info=True)
                await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info("Signal K broadcast loop cancelled")
    finally:
        logger.info("Signal K broadcast loop stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events including:
    - Database initialization
    - Redis connection setup
    - NMEA GPS module startup
    - Signal K module startup
    - Graceful shutdown with timeout
    """
    # Startup
    logger.info(
        "Starting AADS Backend",
        extra={
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "dev_mode": settings.DEV_MODE,
        },
    )

    # Use the lifespan context from dependencies
    async with lifespan_context():
        # Start NMEA GPS module
        if settings.NMEA_ENABLED:
            logger.info("Starting NMEA GPS module")
            await nmea_gps.start()

            # Start NMEA broadcasting task
            nmea_broadcast_task = asyncio.create_task(_nmea_broadcast_loop())
        else:
            nmea_broadcast_task = None

        # Start Signal K module
        if settings.SIGNALK_ENABLED:
            logger.info("Starting Signal K module")
            await signalk.start()

            # Start Signal K broadcasting task
            signalk_broadcast_task = asyncio.create_task(_signalk_broadcast_loop())
        else:
            signalk_broadcast_task = None

        # Enable bridge logger (InfluxDB)
        bridge_logger.enable()

        # Configure and start Autopilot controller if enabled
        autopilot_task = None
        try:
            autopilot.configure(
                signalk_provider=signalk.get_data,
                broadcast=connection_manager.broadcast,
                output_sink=None,
            )
            if settings.AUTOPILOT_ENABLED:
                await autopilot.start()
                autopilot_task = True  # marker
                logger.info("Autopilot controller initialized")
                # Enable telemetry logging if InfluxDB available
                state_provider = lambda: {
                    **autopilot.get_status(),
                    **track.get_status(),
                    **emergency.get_status(),
                }
                if telemetry_logger.enable(state_provider):
                    await telemetry_logger.start(interval_sec=1.0)
        except Exception as e:
            logger.warning(f"Autopilot setup failed: {e}")

        # Initialize voice system if enabled
        voice_task = None
        if settings.VOICE_ENABLED:
            try:
                # Create state provider for voice context-aware responses
                voice_state_provider = lambda: {
                    **autopilot.get_status(),
                    **track.get_status(),
                    **emergency.get_status(),
                }
                await voice_system.initialize(state_provider=voice_state_provider)
                logger.info("Voice system initialized")
            except Exception as e:
                logger.warning(f"Voice system initialization failed: {e}")

        logger.info("All systems initialized")

        yield

        # Additional shutdown tasks
        logger.info("Initiating graceful shutdown")

        # Stop NMEA broadcasting
        if nmea_broadcast_task:
            nmea_broadcast_task.cancel()
            try:
                await nmea_broadcast_task
            except asyncio.CancelledError:
                pass

        # Stop NMEA GPS module
        if settings.NMEA_ENABLED:
            await nmea_gps.stop()

        # Stop Signal K broadcasting
        if signalk_broadcast_task:
            signalk_broadcast_task.cancel()
            try:
                await signalk_broadcast_task
            except asyncio.CancelledError:
                pass

        # Stop Signal K module
        if settings.SIGNALK_ENABLED:
            await signalk.stop()

        # Stop Autopilot controller
        try:
            await autopilot.stop()
        except Exception:
            pass

        # Stop telemetry logger
        try:
            await telemetry_logger.stop()
        except Exception:
            pass

        # Close bridge logger
        bridge_logger.close()

        # Close all WebSocket connections
        try:
            count = await connection_manager.get_connection_count()
            if count > 0:
                await connection_manager.broadcast(
                    {"type": "system", "event": "shutdown", "message": "Server is shutting down"}
                )
                logger.info(f"Notified {count} WebSocket clients of shutdown")
        except Exception as e:
            logger.error(f"Error closing WebSocket connections: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced Autonomous Driving System - Backend API",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled exception",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc) if settings.DEV_MODE else "An error occurred"},
    )


# Root endpoint
@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_PREFIX}/docs",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint for monitoring and load balancers.

    Returns:
        Health status of the application and its dependencies
    """
    try:
        health = await verify_system_health()

        status_code = status.HTTP_200_OK if health["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

        return JSONResponse(status_code=status_code, content=health)
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


# System status endpoint
@app.get(f"{settings.API_PREFIX}/status")
async def system_status() -> dict[str, Any]:
    """Detailed system status endpoint.

    Returns:
        Comprehensive system information including configuration and health
    """
    health = await verify_system_health()
    ws_count = await connection_manager.get_connection_count()

    return {
        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "dev_mode": settings.DEV_MODE,
        },
        "health": health,
        "websocket": {
            "active_connections": ws_count,
            "max_connections": settings.WS_MAX_CONNECTIONS,
        },
        "features": {
            "mock_camera": settings.MOCK_CAMERA,
            "ollama_enabled": bool(settings.OLLAMA_BASE_URL),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time bidirectional communication.

    Supports:
    - Real-time telemetry updates
    - Detection events
    - System notifications
    - Client heartbeat/ping-pong

    Message format (JSON):
        {
            "type": "telemetry" | "detection" | "system" | "ping",
            "data": {...},
            "timestamp": "ISO-8601"
        }
    """
    # Accept connection
    if not await connection_manager.connect(websocket):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Connection limit reached")
        return

    # Send welcome message
    await connection_manager.send_personal(
        {
            "type": "system",
            "event": "connected",
            "message": "Connected to AADS Backend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        websocket,
    )

    try:
        # Heartbeat task
        async def heartbeat():
            """Send periodic heartbeat to detect dead connections."""
            while True:
                try:
                    await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
                    await websocket.send_json(
                        {
                            "type": "ping",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                except Exception:
                    break

        # Start heartbeat task
        heartbeat_task = asyncio.create_task(heartbeat())

        # Message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()

                # Handle different message types
                msg_type = data.get("type")

                if msg_type == "pong":
                    # Client responding to heartbeat
                    logger.debug("Received pong from client")
                elif msg_type == "subscribe":
                    # Client subscribing to specific events
                    topics = data.get("topics", [])
                    logger.info(f"Client subscribed to topics: {topics}")
                    await connection_manager.send_personal(
                        {
                            "type": "system",
                            "event": "subscribed",
                            "topics": topics,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                        websocket,
                    )
                elif msg_type == "voice_input":
                    # Handle voice input from client (audio bytes)
                    if not settings.VOICE_ENABLED:
                        await connection_manager.send_personal(
                            {
                                "type": "error",
                                "message": "Voice system not enabled",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            },
                            websocket,
                        )
                        continue

                    try:
                        # Extract audio bytes and convert to numpy array
                        audio_bytes = data.get("audio", [])
                        audio_data = np.array(audio_bytes, dtype=np.int16)

                        # Process voice input
                        command = await voice_system.process_audio(audio_data)

                        if command:
                            # Send voice input and response back to client
                            await connection_manager.broadcast(
                                {
                                    "type": "voice_command_received",
                                    "command": command,
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                }
                            )
                    except Exception as e:
                        logger.error(f"Voice input processing error: {e}")
                        await connection_manager.send_personal(
                            {
                                "type": "error",
                                "message": f"Voice processing failed: {e}",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            },
                            websocket,
                        )
                else:
                    # Echo or log unknown message types
                    logger.debug(f"Received WebSocket message: {msg_type}")

            except WebSocketDisconnect:
                logger.info("Client disconnected normally")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}", exc_info=True)
                break

        # Cancel heartbeat task
        heartbeat_task.cancel()

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}", exc_info=True)
    finally:
        await connection_manager.disconnect(websocket)


# ============================================================================
# MODULE API ENDPOINTS
# ============================================================================


# Vakten (Vision) Endpoints
@app.get(f"{settings.API_PREFIX}/vakten/status", tags=["vakten"])
async def get_vakten_status():
    """Get Vakten vision module status"""
    return vakten.vakten.get_status()


@app.get(f"{settings.API_PREFIX}/vakten/detections", tags=["vakten"])
async def get_vakten_detections():
    """Get latest Vakten detections"""
    return {"detections": vakten.vakten.get_detections(), "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post(f"{settings.API_PREFIX}/vakten/start", tags=["vakten"])
async def start_vakten():
    """Start Vakten detection loop"""
    asyncio.create_task(vakten.vakten.start())
    return {"status": "started"}


@app.post(f"{settings.API_PREFIX}/vakten/stop", tags=["vakten"])
async def stop_vakten():
    """Stop Vakten detection loop"""
    await vakten.vakten.stop()
    return {"status": "stopped"}


# Navi (AI Assistant) Endpoints
@app.get(f"{settings.API_PREFIX}/navi/status", tags=["navi"])
async def get_navi_status():
    """Get Navi AI assistant status"""
    return navi.navi.get_status()


@app.post(f"{settings.API_PREFIX}/navi/chat", tags=["navi"])
async def chat_with_navi(request: NaviChatRequest):
    """Chat with Navi AI assistant

    Request body:
    {
        "message": "What is my status?",
        "context": {}  # optional
    }
    """
    logger.info(f"Received Navi chat request: {request.message}")
    try:
        message_type = navi.navi._detect_message_type(request.message)
        response_text = await navi.navi.chat(request.message, request.context)
        response_data = {
            "message": request.message,
            "response": response_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": message_type,
        }
        logger.info(f"Navi response prepared: {response_data['response'][:50]}...")
        return response_data
    except Exception as e:
        logger.error(f"Navi chat error: {e}")
        return {
            "message": request.message,
            "response": f"Error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "chat"
        }


@app.get(f"{settings.API_PREFIX}/navi/chat", tags=["navi"])
async def chat_get(message: str):
    """Simple GET endpoint for Navi chat (legacy/testing)"""
    try:
        message_type = navi.navi._detect_message_type(message)
        response_text = await navi.navi.chat(message)
        return {
            "message": message,
            "response": response_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": message_type,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get(f"{settings.API_PREFIX}/navi/history", tags=["navi"])
async def get_navi_history(limit: int = 50):
    """Get Navi conversation history"""
    return {"history": navi.navi.get_history(limit)}


@app.post(f"{settings.API_PREFIX}/navi/clear", tags=["navi"])
async def clear_navi_history():
    """Clear Navi conversation history"""
    await navi.navi.clear_history()
    return {"status": "cleared"}


# Navigator (NAVTEX) Endpoints
@app.get(f"{settings.API_PREFIX}/navigator/status", tags=["navigator"])
async def get_navigator_status():
    """Get Navigator module status"""
    return navigator.navigator.get_status()


@app.post(f"{settings.API_PREFIX}/navigator/parse_navtex", tags=["navigator"])
async def parse_navtex(message: str):
    """Parse NAVTEX message"""
    parsed = navigator.navigator.parse_navtex(message)
    return parsed.to_dict()

@app.get(f"{settings.API_PREFIX}/navigator/navtex/latest", tags=["navigator"])
async def navtex_latest():
    """Get latest NAVTEX message"""
    latest = navigator.navigator.get_navtex_latest()
    if latest is None:
        return {"status": "empty"}
    return latest


@app.get(f"{settings.API_PREFIX}/navigator/navtex/history", tags=["navigator"])
async def navtex_history(limit: int = 20):
    """Get recent NAVTEX messages"""
    return {"history": navigator.navigator.get_navtex_messages(limit)}


@app.get(f"{settings.API_PREFIX}/navigator/navtex/summary", tags=["navigator"])
async def navtex_summary(limit: int = 10):
    """Get NAVTEX summary"""
    return navigator.navigator.get_navtex_summary(limit)


@app.post(f"{settings.API_PREFIX}/navigator/plan_route", tags=["navigator"])
async def plan_route(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, avoid_ice: bool = True):
    """Plan route with hazard avoidance"""
    route = navigator.navigator.plan_route(
        (origin_lat, origin_lng),
        (dest_lat, dest_lng),
        avoid_ice=avoid_ice,
        include_map_hazards=True,
    )
    return route


@app.get(f"{settings.API_PREFIX}/navigator/hazards", tags=["navigator"])
async def get_hazards(severity: str = None):
    """Get current navigation hazards"""
    return {"hazards": navigator.navigator.get_hazards(severity)}


@app.get(f"{settings.API_PREFIX}/navigator/map_info", tags=["navigator"])
async def get_map_info(lat: float, lon: float):
    """Get map data for a specific position (sea areas, waypoints, ice zones, harbors)"""
    return navigator.navigator.get_map_info(lat, lon)


# Legen (Medical) Endpoints
@app.get(f"{settings.API_PREFIX}/legen/status", tags=["legen"])
async def get_legen_status():
    """Get Legen medical module status"""
    return legen.legen.get_status()


@app.post(f"{settings.API_PREFIX}/legen/assess", tags=["legen"])
async def medical_assessment(symptoms: list[str], severity: str = "medium"):
    """Perform medical assessment"""
    assessment = legen.legen.assess(symptoms, severity)
    return assessment


@app.get(f"{settings.API_PREFIX}/legen/protocol/{{protocol_type}}", tags=["legen"])
async def get_medical_protocol(protocol_type: str):
    """Get specific medical protocol"""
    protocol = legen.legen.get_protocol(protocol_type)
    return {"protocol_type": protocol_type, "protocol": protocol}


# Psykologen (Mental Health) Endpoints
@app.get(f"{settings.API_PREFIX}/psykologen/status", tags=["psykologen"])
async def get_psykologen_status():
    """Get Psykologen module status"""
    return psykologen.psykologen.get_status()


@app.post(f"{settings.API_PREFIX}/psykologen/checkin", tags=["psykologen"])
async def mental_health_checkin(mood_score: int, notes: str = None, user_id: str = "crew"):
    """Quick wellness check-in"""
    result = psykologen.psykologen.checkin(mood_score, notes, user_id)
    return result


@app.post(f"{settings.API_PREFIX}/psykologen/session", tags=["psykologen"])
async def therapy_session(topic: str, message: str, user_id: str = "crew"):
    """Private therapy session"""
    result = psykologen.psykologen.session(topic, message, user_id)
    return result


# Ingeniøren (Engineering) Endpoints
@app.get(f"{settings.API_PREFIX}/ingenioren/status", tags=["ingenioren"])
async def get_ingenioren_status():
    """Get Ingeniøren module status"""
    return ingenioren.ingenioren.get_status()


@app.get(f"{settings.API_PREFIX}/ingenioren/diagnostics", tags=["ingenioren"])
async def get_system_diagnostics():
    """Get comprehensive system diagnostics"""
    return ingenioren.ingenioren.get_diagnostics()


@app.get(f"{settings.API_PREFIX}/ingenioren/metrics", tags=["ingenioren"])
async def get_metrics(hours: int = 24):
    """Get historical metrics"""
    return {"metrics": ingenioren.ingenioren.get_metrics(hours)}


@app.post(f"{settings.API_PREFIX}/ingenioren/optimize", tags=["ingenioren"])
async def optimize_system():
    """Run system optimization"""
    return ingenioren.ingenioren.optimize()


@app.get(f"{settings.API_PREFIX}/ingenioren/alerts", tags=["ingenioren"])
async def get_alerts(severity: str = None):
    """Get system alerts"""
    return {"alerts": ingenioren.ingenioren.get_alerts(severity)}


@app.post(f"{settings.API_PREFIX}/ingenioren/calibrate_acoustic", tags=["ingenioren"])
async def calibrate_acoustic(duration_seconds: int = 60):
    """Calibrate acoustic baseline"""
    return ingenioren.ingenioren.calibrate_acoustic(duration_seconds)


@app.post(f"{settings.API_PREFIX}/ingenioren/detect_acoustic_anomaly", tags=["ingenioren"])
async def detect_acoustic_anomaly():
    """Detect acoustic anomalies"""
    return ingenioren.ingenioren.detect_acoustic_anomaly()


# NMEA GPS Endpoints
@app.get(f"{settings.API_PREFIX}/nmea/status", tags=["nmea"])
async def get_nmea_status():
    """Get NMEA GPS module status"""
    return nmea_gps.get_status()


@app.get(f"{settings.API_PREFIX}/nmea/data", tags=["nmea"])
async def get_nmea_data():
    """Get current NMEA GPS data"""
    return {"data": nmea_gps.get_data(), "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post(f"{settings.API_PREFIX}/nmea/start", tags=["nmea"])
async def start_nmea():
    """Start NMEA GPS module"""
    await nmea_gps.start()
    return {"status": "started"}


@app.post(f"{settings.API_PREFIX}/nmea/stop", tags=["nmea"])
async def stop_nmea():
    """Stop NMEA GPS module"""
    await nmea_gps.stop()
    return {"status": "stopped"}


# Signal K Endpoints
@app.get(f"{settings.API_PREFIX}/signalk/status", tags=["signalk"])
async def get_signalk_status():
    """Get Signal K module status"""
    return signalk.get_status()


@app.get(f"{settings.API_PREFIX}/signalk/data", tags=["signalk"])
async def get_signalk_data():
    """Get current Signal K data"""
    return {"data": signalk.get_data(), "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post(f"{settings.API_PREFIX}/signalk/start", tags=["signalk"])
async def start_signalk():
    """Start Signal K module"""
    await signalk.start()
    return {"status": "started"}


@app.post(f"{settings.API_PREFIX}/signalk/stop", tags=["signalk"])
async def stop_signalk():
    """Stop Signal K module"""
    await signalk.stop()
    return {"status": "stopped"}


# Bridge (Arduino analog) Endpoints
@app.post(f"{settings.API_PREFIX}/bridge/analog", tags=["bridge"])
async def ingest_bridge_analog(payload: BridgeAnalogPayload = Body(...)):
    """Ingest analog signals from Raspberry Pi bridge."""
    global last_bridge_payload

    if not payload.signals:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "signals must not be empty"},
        )

    # Ensure all values are numeric
    for key, value in payload.signals.items():
        if not isinstance(value, (int, float)):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": f"signal '{key}' must be numeric"},
            )

    timestamp = payload.timestamp or datetime.now(timezone.utc).isoformat()
    message = {
        "type": "bridge",
        "data": {
            "signals": payload.signals,
            "source": payload.source or "arduino",
        },
        "timestamp": timestamp,
    }

    last_bridge_payload = message
    await connection_manager.broadcast(message)
    bridge_logger.write(payload.signals, payload.source or "arduino", timestamp)

    return {"status": "accepted", "timestamp": timestamp}


@app.get(f"{settings.API_PREFIX}/bridge/analog", tags=["bridge"])
async def get_latest_bridge_analog():
    """Get latest analog payload ingested by the bridge."""
    if not last_bridge_payload:
        return {"status": "empty"}
    return last_bridge_payload


# Track Control Endpoints
@app.get(f"{settings.API_PREFIX}/autopilot/track/status", tags=["autopilot"])
async def get_track_status():
    """Get track control status"""
    return track.get_status()


class _SetTrackReq(BaseModel):
    from_lat: float
    from_lon: float
    to_lat: float
    to_lon: float
    from_name: str = "FROM"
    to_name: str = "TO"


@app.post(f"{settings.API_PREFIX}/autopilot/track/set", tags=["autopilot"])
async def set_track(req: _SetTrackReq):
    """Set active track leg"""
    from app.modules.track_control import Waypoint
    from_wp = Waypoint(req.from_lat, req.from_lon, req.from_name)
    to_wp = Waypoint(req.to_lat, req.to_lon, req.to_name)
    track.set_route(from_wp, to_wp)
    return track.get_status()


# Emergency Behaviors Endpoints
@app.get(f"{settings.API_PREFIX}/autopilot/emergency/status", tags=["autopilot"])
async def get_emergency_status():
    """Get emergency behaviors status"""
    return emergency.get_status()


if __name__ == "__main__":

    import uvicorn

    # Run application
    # Note: For production with multiple workers, use Gunicorn with uvicorn workers:
    # gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEV_MODE,
        log_level=settings.LOG_LEVEL.lower(),
        workers=1,  # Always use 1 worker with uvicorn.run() to avoid shared state issues
    )

# Autopilot Endpoints
@app.get(f"{settings.API_PREFIX}/autopilot/status", tags=["autopilot"])
async def get_autopilot_status():
    return autopilot.get_status()


class _AutopilotEnableReq(BaseModel):
    enabled: bool
    desired_heading_deg: float | None = None


@app.post(f"{settings.API_PREFIX}/autopilot/enable", tags=["autopilot"])
async def set_autopilot_enabled(req: _AutopilotEnableReq):
    if req.enabled:
        autopilot.enable(desired_heading_deg=req.desired_heading_deg)
        return {"status": "enabled", "desired_heading_deg": autopilot.get_status().get("desired_heading_deg")}
    else:
        autopilot.disable()
        return {"status": "disabled"}


class _AutopilotHeadingReq(BaseModel):
    heading_deg: float


@app.post(f"{settings.API_PREFIX}/autopilot/heading", tags=["autopilot"])
async def set_autopilot_heading(req: _AutopilotHeadingReq):
    autopilot.set_heading(req.heading_deg)
    return {"status": "ok", "desired_heading_deg": autopilot.get_status().get("desired_heading_deg")}
