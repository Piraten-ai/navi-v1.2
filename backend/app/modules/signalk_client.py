"""
Signal K Client Module
======================
Connects to Signal K server and provides real-time marine data.
Supports navigation, environment, and propulsion data streams.

Features:
- Real-time navigation, environment, and propulsion data
- Mock data generation for testing and development
- AIS target simulation with CPA calculations
- Haversine distance calculations
- Redis caching for AIS targets (3600s TTL)
- Comprehensive error handling and reconnection logic
- Timestamp validation and conversion
- Wind direction randomization for realistic data
"""

import asyncio
import json
import random
import math
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import websockets
from websockets.exceptions import ConnectionClosed
from app.core.config import settings
from app.core.logging import get_logger
from app.core.flight_recorder import recorder

# Optional Redis support
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = get_logger(__name__)


def _record_metric(key: str, value: float) -> None:
    try:
        recorder.log(key, value)
    except Exception as exc:
        logger.debug("Flight recorder log failed", extra={"key": key, "error": str(exc)})


class SignalKData:
    """Container for parsed Signal K data."""

    def __init__(self):
        # Navigation data
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.speed_over_ground: Optional[float] = None  # Speed in knots
        self.speed_through_water: Optional[float] = None  # Speed in knots
        self.course_over_ground: Optional[float] = None  # True course in degrees
        self.heading: Optional[float] = None  # True heading in degrees
        self.altitude: Optional[float] = None  # Altitude in meters

        # Environment data
        self.water_depth: Optional[float] = None  # Depth in meters
        self.water_temperature: Optional[float] = None  # Temperature in Celsius
        self.wind_speed: Optional[float] = None  # Wind speed in m/s
        self.wind_direction: Optional[float] = None  # Wind direction in degrees (0-360)
        self.air_temperature: Optional[float] = None  # Air temperature in Celsius
        self.air_pressure: Optional[float] = None  # Pressure in Pascals

        # Propulsion data
        self.engine_rpm: Optional[float] = None
        self.engine_temperature: Optional[float] = None  # Temperature in Celsius
        self.fuel_level: Optional[float] = None  # Fuel level as percentage (0-100)

        # Metadata
        self.timestamp: Optional[str] = None
        self.source: Optional[str] = None
        self._timestamp_dt: Optional[datetime] = None  # For validation

    def set_timestamp(self, ts: Optional[str]) -> None:
        """Set and validate timestamp."""
        if ts is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
            self._timestamp_dt = datetime.now(timezone.utc)
            return

        try:
            # Try parsing ISO format
            if isinstance(ts, str):
                self._timestamp_dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                self.timestamp = ts
            else:
                # Assume it's already a datetime
                self._timestamp_dt = ts
                self.timestamp = ts.isoformat() if isinstance(ts, datetime) else str(ts)
        except (ValueError, AttributeError) as e:
            logger.warning(f"Invalid timestamp format: {ts}, using current time. Error: {e}")
            self.timestamp = datetime.now(timezone.utc).isoformat()
            self._timestamp_dt = datetime.now(timezone.utc)

    def get_age_seconds(self) -> float:
        """Get age of data in seconds."""
        if self._timestamp_dt is None:
            return 0.0
        return (datetime.now(timezone.utc) - self._timestamp_dt).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "navigation": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "speed_over_ground": self.speed_over_ground,
                "speed_through_water": self.speed_through_water,
                "course_over_ground": self.course_over_ground,
                "heading": self.heading,
                "altitude": self.altitude,
            },
            "environment": {
                "water_depth": self.water_depth,
                "water_temperature": self.water_temperature,
                "wind_speed": self.wind_speed,
                "wind_direction": self.wind_direction,
                "air_temperature": self.air_temperature,
                "air_pressure": self.air_pressure,
            },
            "propulsion": {
                "engine_rpm": self.engine_rpm,
                "engine_temperature": self.engine_temperature,
                "fuel_level": self.fuel_level,
            },
            "timestamp": self.timestamp,
            "source": self.source,
        }

    def is_valid(self) -> bool:
        """Check if we have valid position data."""
        return self.latitude is not None and self.longitude is not None


class AISTarget:
    """AIS target vessel for collision avoidance calculations."""

    def __init__(self, mmsi: int, name: str, lat: float, lon: float,
                 cog: float, sog: float, length: float = 50.0, width: float = 10.0):
        self.mmsi = mmsi
        self.name = name
        self.latitude = lat
        self.longitude = lon
        self.course_over_ground = cog  # degrees
        self.speed_over_ground = sog  # knots
        self.length = length  # meters
        self.width = width  # meters
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mmsi": self.mmsi,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "course_over_ground": self.course_over_ground,
            "speed_over_ground": self.speed_over_ground,
            "length": self.length,
            "width": self.width,
            "timestamp": self.timestamp,
        }


class SignalKMath:
    """Mathematical utilities for Signal K calculations."""

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in nautical miles using Haversine formula."""
        R = 3440.065  # Earth radius in nautical miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

    @staticmethod
    def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing from point 1 to point 2 (0-360 degrees)."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon1_rad = math.radians(lon1)
        lon2_rad = math.radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        
        x = math.sin(dlon) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
        
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360

    @staticmethod
    def calculate_cpa(own_lat: float, own_lon: float, own_cog: float, own_sog: float,
                      target_lat: float, target_lon: float, target_cog: float, target_sog: float) -> Dict[str, float]:
        """Calculate Closest Point of Approach (CPA) and time to CPA."""
        # Convert knots to m/s for calculation
        own_sog_ms = own_sog * 0.51444
        target_sog_ms = target_sog * 0.51444

        # Convert courses to radians
        own_cog_rad = math.radians(own_cog)
        target_cog_rad = math.radians(target_cog)

        # Own vessel velocity
        own_vx = own_sog_ms * math.sin(own_cog_rad)
        own_vy = own_sog_ms * math.cos(own_cog_rad)

        # Target velocity
        target_vx = target_sog_ms * math.sin(target_cog_rad)
        target_vy = target_sog_ms * math.cos(target_cog_rad)

        # Relative velocity
        rel_vx = target_vx - own_vx
        rel_vy = target_vy - own_vy

        # Distance between vessels
        distance = SignalKMath.haversine_distance(own_lat, own_lon, target_lat, target_lon)
        distance_m = distance * 1852  # Convert nautical miles to meters

        # Bearing to target
        bearing = SignalKMath.calculate_bearing(own_lat, own_lon, target_lat, target_lon)
        bearing_rad = math.radians(bearing)

        # Position relative to own vessel
        rel_x = distance_m * math.sin(bearing_rad)
        rel_y = distance_m * math.cos(bearing_rad)

        # Time to CPA
        rel_v_sq = rel_vx ** 2 + rel_vy ** 2
        if rel_v_sq < 0.01:  # Avoid division by zero
            tcpa = float('inf')
        else:
            tcpa = max(0, -(rel_x * rel_vx + rel_y * rel_vy) / rel_v_sq)

        # CPA distance
        closest_x = rel_x + rel_vx * tcpa
        closest_y = rel_y + rel_vy * tcpa
        cpa_distance = math.sqrt(closest_x ** 2 + closest_y ** 2) / 1852  # Convert back to nautical miles

        return {
            "distance": distance,
            "bearing": bearing,
            "cpa_distance": cpa_distance,
            "time_to_cpa": tcpa,
        }


class SignalKModule:
    """Signal K client module for marine data streaming."""

    def __init__(self):
        self.running = False
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.current_data = SignalKData()
        self._read_task: Optional[asyncio.Task] = None
        
        # AIS targets (simulated or real)
        self.ais_targets: Dict[int, AISTarget] = {}
        self._ais_update_task: Optional[asyncio.Task] = None

        # Mock data state for testing
        self._mock_latitude = 78.2232  # Svalbard
        self._mock_longitude = 15.6267
        self._mock_heading = 45.0
        self._mock_speed = 5.5
        self._mock_depth = 42.5
        self._mock_wind_speed = 8.3
        self._mock_wind_direction = 135.0

        # Redis client for AIS caching (optional)
        self._redis_client: Optional[Any] = None
        self._init_redis()

    def _init_redis(self) -> None:
        """Initialize Redis client if available and configured."""
        if not REDIS_AVAILABLE or not settings.REDIS_ENABLED:
            return

        try:
            self._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            # Test connection
            self._redis_client.ping()
            logger.info(f"Redis client initialized: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis: {e}. AIS caching disabled.")
            self._redis_client = None

    def _cache_ais_targets(self) -> None:
        """Cache AIS targets in Redis."""
        if not self._redis_client:
            return

        try:
            for mmsi, target in self.ais_targets.items():
                key = f"ais:{mmsi}"
                ttl = 3600  # 1 hour
                self._redis_client.setex(
                    key,
                    ttl,
                    json.dumps(target.to_dict())
                )
            logger.debug(f"Cached {len(self.ais_targets)} AIS targets")
        except Exception as e:
            logger.warning(f"Failed to cache AIS targets: {e}. Continuing without cache.")

    def _load_ais_targets_from_redis(self) -> None:
        """Load AIS targets from Redis cache."""
        if not self._redis_client:
            return

        try:
            keys = self._redis_client.keys("ais:*")
            for key in keys:
                try:
                    data = self._redis_client.get(key)
                    if data:
                        target_dict = json.loads(data)
                        mmsi = target_dict['mmsi']
                        self.ais_targets[mmsi] = AISTarget(
                            mmsi=mmsi,
                            name=target_dict['name'],
                            lat=target_dict['latitude'],
                            lon=target_dict['longitude'],
                            cog=target_dict['course_over_ground'],
                            sog=target_dict['speed_over_ground'],
                        )
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse AIS target from {key}: {e}")
                    continue
            logger.info(f"Loaded {len(self.ais_targets)} AIS targets from Redis cache")
        except Exception as e:
            logger.warning(f"Failed to load AIS targets from Redis: {e}")

    def generate_mock_ais_targets(self) -> None:
        """Generate realistic mock AIS targets for testing."""
        mock_targets = [
            AISTarget(
                mmsi=230245890,
                name="POLAR EXPLORER",
                lat=78.2250,
                lon=15.6400,
                cog=270.0,
                sog=8.5,
                length=120.0,
                width=20.0,
            ),
            AISTarget(
                mmsi=230445120,
                name="NORTH STAR",
                lat=78.2100,
                lon=15.5900,
                cog=90.0,
                sog=6.2,
                length=85.0,
                width=15.0,
            ),
            AISTarget(
                mmsi=257055670,
                name="ARCTIC QUEEN",
                lat=78.2500,
                lon=15.6100,
                cog=180.0,
                sog=5.8,
                length=95.0,
                width=18.0,
            ),
            AISTarget(
                mmsi=210435240,
                name="SVALBARD HUNTER",
                lat=78.1950,
                lon=15.6500,
                cog=0.0,
                sog=7.1,
                length=65.0,
                width=12.0,
            ),
            AISTarget(
                mmsi=258012345,
                name="ICE BREAKER NORDICA",
                lat=78.2350,
                lon=15.5800,
                cog=135.0,
                sog=9.3,
                length=140.0,
                width=25.0,
            ),
        ]

        for target in mock_targets:
            self.ais_targets[target.mmsi] = target

        logger.info(f"Generated {len(mock_targets)} mock AIS targets")
        self._cache_ais_targets()

    def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "module": "signalk",
            "enabled": settings.SIGNALK_ENABLED,
            "running": self.running,
            "mock_mode": settings.SIGNALK_MOCK_DATA,
            "server_url": settings.SIGNALK_SERVER_URL if not settings.SIGNALK_MOCK_DATA else None,
            "connected": self.ws is not None and self.running,
            "has_data": self.current_data.is_valid(),
            "last_update": self.current_data.timestamp,
            "ais_targets": len(self.ais_targets),
            "redis_cache": self._redis_client is not None,
        }

    def get_data(self) -> Dict[str, Any]:
        """Get current Signal K data."""
        return self.current_data.to_dict()

    def get_ais_targets(self) -> Dict[int, Dict[str, Any]]:
        """Get all AIS targets."""
        return {mmsi: target.to_dict() for mmsi, target in self.ais_targets.items()}

    def get_ais_target(self, mmsi: int) -> Optional[Dict[str, Any]]:
        """Get specific AIS target."""
        if mmsi in self.ais_targets:
            return self.ais_targets[mmsi].to_dict()
        return None

    def calculate_collision_risk(self) -> Dict[int, Dict[str, Any]]:
        """Calculate collision risk for all AIS targets (CPA and TCPA)."""
        if not self.current_data.is_valid():
            return {}

        risks = {}
        for mmsi, target in self.ais_targets.items():
            try:
                cpa_data = SignalKMath.calculate_cpa(
                    self.current_data.latitude,
                    self.current_data.longitude,
                    self.current_data.course_over_ground or 0,
                    self.current_data.speed_over_ground or 0,
                    target.latitude,
                    target.longitude,
                    target.course_over_ground,
                    target.speed_over_ground,
                )
                
                # Determine collision risk level
                cpa_nm = cpa_data['cpa_distance']
                risk_level = 'low'
                if cpa_nm < 0.5:
                    risk_level = 'critical'
                elif cpa_nm < 1.0:
                    risk_level = 'high'
                elif cpa_nm < 2.0:
                    risk_level = 'medium'

                risks[mmsi] = {
                    'target': target.to_dict(),
                    'collision_risk': risk_level,
                    'distance': cpa_data['distance'],
                    'bearing': cpa_data['bearing'],
                    'cpa_distance': cpa_data['cpa_distance'],
                    'time_to_cpa': cpa_data['time_to_cpa'],
                }
            except Exception as e:
                logger.warning(f"Failed to calculate CPA for target {mmsi}: {e}")
                continue

        return risks

    async def start(self) -> None:
        """Start reading Signal K data."""
        if self.running:
            logger.warning("Signal K module already running")
            return

        if not settings.SIGNALK_ENABLED:
            logger.info("Signal K module disabled in configuration")
            return

        self.running = True
        logger.info(
            "Starting Signal K module",
            extra={
                "mock_mode": settings.SIGNALK_MOCK_DATA,
                "server_url": settings.SIGNALK_SERVER_URL,
                "update_interval": settings.SIGNALK_UPDATE_INTERVAL,
            },
        )

        # Load AIS targets from Redis cache if available
        self._load_ais_targets_from_redis()
        
        # Generate mock AIS targets if empty
        if not self.ais_targets:
            self.generate_mock_ais_targets()

        # Start reading task
        if settings.SIGNALK_MOCK_DATA:
            self._read_task = asyncio.create_task(self._read_mock_data())
        else:
            self._read_task = asyncio.create_task(self._read_real_data())

        # Start AIS update task
        self._ais_update_task = asyncio.create_task(self._update_ais_targets())

    async def stop(self) -> None:
        """Stop reading Signal K data."""
        if not self.running:
            logger.warning("Signal K module not running")
            return

        self.running = False
        logger.info("Stopping Signal K module")

        # Cancel reading task
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            self._read_task = None

        # Cancel AIS update task
        if self._ais_update_task:
            self._ais_update_task.cancel()
            try:
                await self._ais_update_task
            except asyncio.CancelledError:
                pass
            self._ais_update_task = None

        # Close WebSocket connection
        if self.ws and not self.ws.closed:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"Error closing Signal K WebSocket: {e}")

        # Cache AIS targets before closing
        self._cache_ais_targets()

        self.ws = None
        logger.info("Signal K module stopped")

    async def _read_mock_data(self) -> None:
        """Generate mock Signal K data for testing."""
        logger.info("Starting mock Signal K data generation")

        try:
            while self.running:
                try:
                    # Generate realistic mock data with random variations
                    self._mock_latitude += random.uniform(-0.001, 0.001)
                    self._mock_longitude += random.uniform(-0.001, 0.001)
                    self._mock_heading = (self._mock_heading + random.uniform(-2, 2)) % 360
                    self._mock_speed = max(0, self._mock_speed + random.uniform(-0.2, 0.2))
                    self._mock_depth = max(0, self._mock_depth + random.uniform(-1, 1))
                    self._mock_wind_speed = max(0, self._mock_wind_speed + random.uniform(-0.5, 0.5))
                    
                    # Improved wind direction randomization with gradual changes
                    wind_change = random.gauss(0, 3)  # Gaussian distribution for realistic changes
                    self._mock_wind_direction = (self._mock_wind_direction + wind_change) % 360
                    if self._mock_wind_direction < 0:
                        self._mock_wind_direction += 360

                    # Update current data
                    self.current_data.latitude = self._mock_latitude
                    self.current_data.longitude = self._mock_longitude
                    self.current_data.speed_over_ground = self._mock_speed
                    self.current_data.speed_through_water = self._mock_speed * 0.98  # Slightly different
                    self.current_data.course_over_ground = self._mock_heading
                    self.current_data.heading = self._mock_heading
                    self.current_data.altitude = 5.0

                    # Environment data
                    self.current_data.water_depth = self._mock_depth
                    self.current_data.water_temperature = 4.2 + random.uniform(-0.2, 0.2)
                    self.current_data.wind_speed = self._mock_wind_speed
                    self.current_data.wind_direction = self._mock_wind_direction
                    self.current_data.air_temperature = -2.5 + random.uniform(-0.5, 0.5)
                    self.current_data.air_pressure = 101325 + random.uniform(-100, 100)

                    # Propulsion data
                    self.current_data.engine_rpm = 1800 + random.uniform(-50, 50)
                    self.current_data.engine_temperature = 82.0 + random.uniform(-2, 2)
                    self.current_data.fuel_level = 75.0 + random.uniform(-1, 1)

                    _record_metric("nav.speed", self.current_data.speed_over_ground)
                    _record_metric("nav.depth", self.current_data.water_depth)
                    _record_metric("engine.rpm", self.current_data.engine_rpm)
                    _record_metric("engine.temp", self.current_data.engine_temperature)

                    # Set timestamp with validation
                    self.current_data.set_timestamp(datetime.now(timezone.utc).isoformat())
                    self.current_data.source = "mock"

                    logger.debug(
                        "Generated mock Signal K data",
                        extra={
                            "lat": self.current_data.latitude,
                            "lon": self.current_data.longitude,
                            "depth": self.current_data.water_depth,
                            "wind_dir": self.current_data.wind_direction,
                        },
                    )

                    await asyncio.sleep(settings.SIGNALK_UPDATE_INTERVAL)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error generating mock Signal K data: {e}", exc_info=True)
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Mock Signal K data generation cancelled")
        finally:
            logger.info("Mock Signal K data generation stopped")

    async def _read_real_data(self) -> None:
        """Read real Signal K data from server."""
        logger.info(f"Connecting to Signal K server at {settings.SIGNALK_SERVER_URL}")

        try:
            while self.running:
                try:
                    # Connect to Signal K WebSocket using async client
                    async with websockets.connect(
                        settings.SIGNALK_SERVER_URL, open_timeout=settings.SIGNALK_TIMEOUT, close_timeout=5
                    ) as websocket:
                        self.ws = websocket
                        logger.info("Connected to Signal K server")

                        # Subscribe to specific paths if configured
                        if settings.SIGNALK_SUBSCRIBE_PATHS:
                            subscribe_msg = {
                                "context": "vessels.self",
                                "subscribe": [
                                    {"path": path, "period": int(settings.SIGNALK_UPDATE_INTERVAL * 1000)}
                                    for path in settings.SIGNALK_SUBSCRIBE_PATHS
                                ],
                            }
                            await websocket.send(json.dumps(subscribe_msg))
                            logger.info(f"Subscribed to {len(settings.SIGNALK_SUBSCRIBE_PATHS)} Signal K paths")

                        # Read messages
                        while self.running:
                            try:
                                message = await websocket.recv()

                                if message:
                                    await self._parse_signalk_message(message)

                            except asyncio.CancelledError:
                                break
                            except ConnectionClosed:
                                logger.warning("Signal K WebSocket connection closed")
                                break
                            except Exception as e:
                                logger.error(f"Error reading Signal K message: {e}")
                                break

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error connecting to Signal K server: {e}")
                    self.ws = None

                    if self.running:
                        logger.info("Reconnecting to Signal K server in 5 seconds...")
                        await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("Signal K data reading cancelled")
        finally:
            self.ws = None
            logger.info("Signal K data reading stopped")

    async def _parse_signalk_message(self, message: str) -> None:
        """Parse Signal K delta message and update current data."""
        try:
            data = json.loads(message)

            if "updates" not in data:
                return

            for update in data["updates"]:
                source = update.get("source", {}).get("label", "unknown")
                timestamp = update.get("timestamp", None)

                for value in update.get("values", []):
                    path = value.get("path")
                    val = value.get("value")

                    if val is None:
                        continue

                    # Navigation data
                    if path == "navigation.position":
                        self.current_data.latitude = val.get("latitude")
                        self.current_data.longitude = val.get("longitude")
                    elif path == "navigation.speedOverGround":
                        self.current_data.speed_over_ground = val * 1.94384  # m/s to knots
                        _record_metric("nav.speed", self.current_data.speed_over_ground)
                    elif path == "navigation.speedThroughWater":
                        self.current_data.speed_through_water = val * 1.94384
                    elif path == "navigation.courseOverGroundTrue":
                        self.current_data.course_over_ground = val * 57.2958  # radians to degrees
                    elif path == "navigation.headingTrue":
                        self.current_data.heading = val * 57.2958
                    elif path == "navigation.altitude":
                        self.current_data.altitude = val

                    # Environment data
                    elif path == "environment.depth.belowTransducer":
                        self.current_data.water_depth = val
                        _record_metric("nav.depth", self.current_data.water_depth)
                    elif path == "environment.water.temperature":
                        self.current_data.water_temperature = val - 273.15  # Kelvin to Celsius
                    elif path == "environment.wind.speedTrue":
                        self.current_data.wind_speed = val
                    elif path == "environment.wind.directionTrue":
                        self.current_data.wind_direction = val * 57.2958
                    elif path == "environment.outside.temperature":
                        self.current_data.air_temperature = val - 273.15
                    elif path == "environment.outside.pressure":
                        self.current_data.air_pressure = val

                    # Propulsion data
                    elif path == "propulsion.main.revolutions":
                        self.current_data.engine_rpm = val * 60  # rev/s to RPM
                        _record_metric("engine.rpm", self.current_data.engine_rpm)
                    elif path == "propulsion.main.temperature":
                        self.current_data.engine_temperature = val - 273.15
                        _record_metric("engine.temp", self.current_data.engine_temperature)
                    elif path == "tanks.fuel.0.currentLevel":
                        self.current_data.fuel_level = val * 100  # ratio to percentage

                # Use validated timestamp setter
                self.current_data.set_timestamp(timestamp)
                self.current_data.source = source

            logger.debug(
                "Parsed Signal K message",
                extra={
                    "updates": len(data["updates"]),
                    "source": source,
                },
            )

        except Exception as e:
            logger.error(f"Error parsing Signal K message: {e}", exc_info=True)

    async def _update_ais_targets(self) -> None:
        """Update AIS targets with realistic motion."""
        logger.info("Starting AIS targets update task")

        try:
            while self.running:
                try:
                    for mmsi, target in self.ais_targets.items():
                        # Update target position based on course and speed
                        # Using simple linear projection (not great for long distances, but good for testing)
                        bearing_rad = math.radians(target.course_over_ground)
                        
                        # Calculate distance change per update (in degrees)
                        # 1 nautical mile ≈ 0.01667 degrees of latitude
                        distance_change = (target.speed_over_ground * settings.SIGNALK_UPDATE_INTERVAL) / 3600 * 0.01667
                        
                        # Update position
                        target.latitude += distance_change * math.cos(bearing_rad)
                        target.longitude += distance_change * math.sin(bearing_rad) / math.cos(math.radians(target.latitude))
                        
                        # Random course and speed variations
                        target.course_over_ground = (target.course_over_ground + random.uniform(-1, 1)) % 360
                        target.speed_over_ground = max(0, target.speed_over_ground + random.uniform(-0.1, 0.1))
                        
                        target.timestamp = datetime.now(timezone.utc).isoformat()

                    logger.debug(f"Updated {len(self.ais_targets)} AIS targets")
                    
                    # Cache targets periodically
                    if int(datetime.now().timestamp()) % 60 == 0:
                        self._cache_ais_targets()

                    await asyncio.sleep(settings.SIGNALK_UPDATE_INTERVAL * 10)  # Update AIS less frequently

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning(f"Error updating AIS targets: {e}")
                    await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("AIS targets update task cancelled")
        finally:
            logger.info("AIS targets update task stopped")


# Global Signal K module instance
signalk = SignalKModule()
