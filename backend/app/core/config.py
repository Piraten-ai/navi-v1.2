"""Application configuration using Pydantic Settings."""

from __future__ import annotations

from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment-based configuration.

    Supports both development (laptop/SQLite) and production (Jetson/PostgreSQL) modes.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")

    # Application
    APP_NAME: str = "AADS Backend"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # Environment
    ENVIRONMENT: Literal["development", "production", "testing"] = Field(
        default="development", description="Deployment environment"
    )

    # Feature Flags
    DEV_MODE: bool = Field(default=True, description="Development mode - uses SQLite, mock services")
    MOCK_CAMERA: bool = Field(default=True, description="Use mock camera instead of real hardware")

    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./aads.db", description="Database connection URL")
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=20)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=30)
    DB_ECHO: bool = Field(default=False, description="Echo SQL queries")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_ENABLED: bool = Field(default=True, description="Enable Redis caching")
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    REDIS_DB: int = Field(default=0, ge=0, le=15, description="Redis database number")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, ge=1, le=50)
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, ge=1, le=30)
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(default=5, ge=1, le=30)

    # InfluxDB
    INFLUXDB_URL: str = Field(default="http://localhost:8086", description="InfluxDB server URL")
    INFLUXDB_TOKEN: str = Field(default="", description="InfluxDB authentication token")
    INFLUXDB_ORG: str = Field(default="aads", description="InfluxDB organization")
    INFLUXDB_BUCKET: str = Field(default="telemetry", description="InfluxDB bucket")

    # MinIO / S3
    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO server endpoint")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO access key")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", description="MinIO secret key")
    MINIO_SECURE: bool = Field(default=False, description="Use HTTPS for MinIO")
    MINIO_BUCKET: str = Field(default="aads-data", description="MinIO bucket name")

    # Ollama
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    OLLAMA_MODEL: str = Field(default="llama2", description="Default Ollama model for LLM tasks")
    OLLAMA_TIMEOUT: int = Field(default=120, ge=10, le=600)

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Application log level"
    )
    LOG_FILE: str = Field(default="logs/aads.log", description="Log file path")
    LOG_MAX_BYTES: int = Field(default=10 * 1024 * 1024, description="Maximum log file size in bytes (10MB)")
    LOG_BACKUP_COUNT: int = Field(default=5, ge=1, le=20, description="Number of log file backups to keep")
    LOG_JSON: bool = Field(default=True, description="Use JSON formatting for logs")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000"
        ],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: list[str] = Field(default=["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default=["*"])

    # Security
    SECRET_KEY: str = Field(
        default="change-me-in-production-use-openssl-rand-hex-32", description="Secret key for JWT and encryption"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=5, le=1440)

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, ge=10, le=120, description="WebSocket heartbeat interval in seconds")
    WS_MAX_CONNECTIONS: int = Field(default=100, ge=1, le=1000, description="Maximum concurrent WebSocket connections")

    # Camera
    CAMERA_WIDTH: int = Field(default=1920, ge=640, le=3840)
    CAMERA_HEIGHT: int = Field(default=1080, ge=480, le=2160)
    CAMERA_FPS: int = Field(default=30, ge=1, le=60)
    CAMERA_DEVICE_ID: int = Field(default=0, ge=0, le=10)

    # IP Camera (ONVIF/PTZ)
    CAMERA_IP: str = Field(default="192.168.39.200", description="IP camera network address")
    CAMERA_PORT: int = Field(default=8000, ge=1, le=65535, description="ONVIF service port")
    CAMERA_USER: str = Field(default="admin", description="Camera username")
    CAMERA_PASS: str = Field(default="admin", description="Camera password")
    PTZ_ENABLED: bool = Field(default=False, description="Enable PTZ (Pan/Tilt/Zoom) control")

    # NMEA GPS Configuration
    NMEA_ENABLED: bool = Field(default=True, description="Enable NMEA GPS data reading")
    NMEA_SERIAL_PORT: str = Field(default="/dev/ttyUSB0", description="Serial port for NMEA GPS device")
    NMEA_BAUD_RATE: int = Field(default=4800, description="Baud rate for NMEA serial communication")
    NMEA_TIMEOUT: float = Field(default=1.0, ge=0.1, le=10.0, description="Serial read timeout in seconds")
    NMEA_MOCK_DATA: bool = Field(
        default=False, description="Use mock NMEA data for testing (False for production with real GPS hardware)"
    )
    NMEA_UPDATE_INTERVAL: float = Field(default=1.0, ge=0.1, le=10.0, description="NMEA data broadcast interval in seconds")
    NMEA0183_OUTPUT_ENABLED: bool = Field(default=False, description="Enable NMEA 0183 autopilot output")
    NMEA0183_OUTPUT_PORT: str = Field(default="/dev/ttyUSB1", description="Serial port for NMEA 0183 autopilot output")
    NMEA0183_OUTPUT_BAUD: int = Field(default=4800, description="Baud rate for NMEA 0183 output")

    # NMEA2000 GPS Configuration (CAN bus)
    NMEA2000_ENABLED: bool = Field(default=False, description="Enable NMEA2000 GPS data reading via CAN bus")
    NMEA2000_INTERFACE: str = Field(default="can0", description="CAN bus interface name (e.g., can0, vcan0)")
    NMEA2000_GPS_PGN_129025_ENABLED: bool = Field(default=True, description="Enable PGN 129025 (Position Rapid Update)")
    NMEA2000_GPS_PGN_129029_ENABLED: bool = Field(default=True, description="Enable PGN 129029 (GNSS Position Data)")
    NMEA2000_TIMEOUT: float = Field(default=2.0, ge=0.5, le=10.0, description="CAN bus message timeout in seconds")
    NMEA2000_LOG_UNKNOWN_PGNS: bool = Field(default=False, description="Log unknown PGN messages for debugging")

    # Hardware Monitoring Configuration (Jetson)
    HARDWARE_MONITOR_ENABLED: bool = Field(default=False, description="Enable hardware monitoring (temps, fan, power)")
    HARDWARE_FAN_TACH_GPIO: int = Field(default=208, ge=0, le=255, description="GPIO pin for fan tachometer (Orin Nano: GPIO208)")
    HARDWARE_I2C_BUS: int = Field(default=1, ge=0, le=10, description="I2C bus number for power monitoring")
    HARDWARE_INA219_ENABLED: bool = Field(default=False, description="Enable INA219 power monitoring via I2C")
    HARDWARE_POLL_INTERVAL: float = Field(default=2.0, ge=0.5, le=10.0, description="Hardware polling interval in seconds")
    HARDWARE_LOG_METRICS: bool = Field(default=True, description="Log hardware metrics to InfluxDB")

    # Fan PID Control Configuration (Jetson)
    FAN_CONTROL_ENABLED: bool = Field(default=False, description="Enable automatic fan PID control")
    FAN_PWM_GPIO: int = Field(default=206, ge=0, le=255, description="GPIO pin for fan PWM output (Orin Nano: GPIO206)")
    FAN_TARGET_TEMP: float = Field(default=60.0, ge=40.0, le=85.0, description="Target temperature for fan control (Celsius)")
    FAN_PID_KP: float = Field(default=2.0, ge=0.1, le=10.0, description="PID proportional gain")
    FAN_PID_KI: float = Field(default=0.5, ge=0.0, le=5.0, description="PID integral gain")
    FAN_PID_KD: float = Field(default=0.1, ge=0.0, le=2.0, description="PID derivative gain")
    FAN_MIN_PWM: int = Field(default=20, ge=0, le=100, description="Minimum PWM duty cycle (%)")
    FAN_MAX_PWM: int = Field(default=100, ge=0, le=100, description="Maximum PWM duty cycle (%)")
    FAN_UPDATE_INTERVAL: float = Field(default=1.0, ge=0.1, le=5.0, description="Fan control update interval (seconds)")

    # Autopilot PID Configuration
    AUTOPILOT_ENABLED: bool = Field(default=False, description="Enable Autopilot PID controller")
    AUTOPILOT_UPDATE_INTERVAL: float = Field(default=0.5, ge=0.1, le=2.0, description="Autopilot update interval (seconds)")
    AUTOPILOT_KP_XTE: float = Field(default=1.2, ge=0.0, le=10.0, description="Proportional gain for Cross-Track Error (deg/nautical mile)")
    AUTOPILOT_KI_XTE: float = Field(default=0.0, ge=0.0, le=5.0, description="Integral gain for Cross-Track Error")
    AUTOPILOT_KD_XTE: float = Field(default=0.3, ge=0.0, le=5.0, description="Derivative gain for Cross-Track Error")
    AUTOPILOT_KP_HDGT: float = Field(default=1.0, ge=0.0, le=10.0, description="Proportional gain for Heading error (deg/deg)")
    AUTOPILOT_MAX_RUDDER_DEG: float = Field(default=30.0, ge=5.0, le=45.0, description="Maximum rudder angle command (degrees)")
    AUTOPILOT_MIN_RUDDER_DEG: float = Field(default=2.0, ge=0.0, le=10.0, description="Minimum effective rudder command (deadband overcome)")
    AUTOPILOT_WIND_COMPENSATION: bool = Field(default=True, description="Apply wind leeway compensation to heading error")
    AUTOPILOT_WIND_GAIN: float = Field(default=0.2, ge=0.0, le=2.0, description="Gain to convert apparent wind angle offset to rudder assist (deg/deg)")

    # Leeway Model Configuration
    LEWAY_ENABLED: bool = Field(default=False, description="Enable leeway (sideforce) modeling")
    LEWAY_METHOD: Literal["simple", "visir2"] = Field(default="simple", description="Leeway model selection")
    LEWAY_K: float = Field(
        default=0.8,
        ge=0.0,
        le=5.0,
        description="Scaling coefficient for leeway magnitude; higher means more drift",
    )
    LEWAY_MAX_DEG: float = Field(default=10.0, ge=0.0, le=30.0, description="Maximum absolute leeway angle (degrees)")

    # Wind Estimator Configuration
    WIND_ESTIMATOR_ENABLED: bool = Field(default=False, description="Enable wind estimator (smoothing & gusts)")
    WIND_ESTIMATOR_METHOD: Literal["ewma", "window"] = Field(
        default="ewma", description="Wind estimator method: EWMA (exponential) or time window"
    )
    WIND_EWMA_ALPHA: float = Field(default=0.2, ge=0.01, le=0.99, description="EWMA alpha smoothing factor")
    WIND_WINDOW_SECONDS: float = Field(default=60.0, ge=5.0, le=600.0, description="Sliding window duration (seconds)")
    WIND_GUST_PERCENTILE: float = Field(default=0.95, ge=0.5, le=1.0, description="Percentile for gust estimation")

    # Voice System Configuration (Piper TTS + Whisper STT)
    VOICE_ENABLED: bool = Field(default=False, description="Enable voice system (TTS + STT)")
    PIPER_VOICE_MODEL: str = Field(
        default="/app/models/piper/en_US-lessac-medium.onnx",
        description="Path to Piper TTS voice model (ONNX format)"
    )
    WHISPER_MODEL_SIZE: str = Field(
        default="tiny.en", 
        description="Whisper STT model size (tiny.en, base.en, small.en, etc.)"
    )
    VOICE_NAVI_ALERT_MP3: str = Field(
        default="/app/audio/hey_listen.mp3",
        description="Path to Zelda 'Hey Listen!' MP3 for critical alerts"
    )
    VOICE_SAMPLE_RATE: int = Field(default=22050, ge=8000, le=48000, description="Audio sample rate (Hz)")
    VOICE_RECORD_DURATION: float = Field(default=5.0, ge=1.0, le=30.0, description="Voice input recording duration (seconds)")

    # Signal K Configuration
    SIGNALK_ENABLED: bool = Field(default=True, description="Enable Signal K data streaming")
    SIGNALK_SERVER_URL: str = Field(
        default="ws://localhost:3000/signalk/v1/stream", description="Signal K server WebSocket URL"
    )
    SIGNALK_MOCK_DATA: bool = Field(
        default=False, description="Use mock Signal K data for testing (False for production)"
    )
    SIGNALK_UPDATE_INTERVAL: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Signal K data update interval in seconds"
    )
    SIGNALK_TIMEOUT: float = Field(
        default=10.0, ge=1.0, le=60.0, description="Signal K WebSocket connection timeout in seconds"
    )
    SIGNALK_SUBSCRIBE_PATHS: list[str] = Field(
        default=[
            "navigation.*",
            "environment.depth.*",
            "environment.water.*",
            "environment.wind.*",
            "environment.outside.*",
            "propulsion.*.revolutions",
            "propulsion.*.temperature",
            "tanks.fuel.*",
        ],
        description="Signal K paths to subscribe to",
    )

    # Object Detection
    YOLO_MODEL: str = Field(default="yolov8n.pt", description="YOLO model file path or name")
    YOLO_CONFIDENCE_THRESHOLD: float = Field(default=0.5, ge=0.0, le=1.0, description="Detection confidence threshold")
    YOLO_IOU_THRESHOLD: float = Field(default=0.45, ge=0.0, le=1.0, description="Non-maximum suppression IOU threshold")

    # System
    MAX_WORKERS: int = Field(default=4, ge=1, le=32, description="Maximum number of worker threads")
    SHUTDOWN_TIMEOUT: int = Field(default=10, ge=1, le=60, description="Graceful shutdown timeout in seconds")

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """Validate and adjust database URL based on DEV_MODE."""
        # Ensure PostgreSQL uses async driver
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)

        return v

    @field_validator("REDIS_URL")
    @classmethod
    def validate_redis_url(cls, v: str, info) -> str:
        """Validate Redis URL format."""
        if not v.startswith(("redis://", "rediss://")):
            raise ValueError("REDIS_URL must start with redis:// or rediss://")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development" or self.DEV_MODE

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production" and not self.DEV_MODE

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT == "testing"

    def get_database_url_sync(self) -> str:
        """Get synchronous database URL (for Alembic migrations)."""
        url = self.DATABASE_URL
        if "+aiosqlite" in url:
            return url.replace("+aiosqlite", "")
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "")
        return url


# Global settings instance
settings = Settings()
