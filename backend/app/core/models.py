"""
AADS - SQLAlchemy Database Models
==================================
Database models for the Autonomous Arctic Digital Skipper system.
Supports PostgreSQL for production and SQLite for development.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Index, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


# Enums for type safety
class ThreatType(str, enum.Enum):
    """Vision detection threat types"""

    ICE = "ice"
    SHIP = "ship"
    PERSON = "person"
    OBSTACLE = "obstacle"
    SHADOW_SHIP = "shadow_ship"
    UNKNOWN = "unknown"


class NAVTEXCategory(str, enum.Enum):
    """NAVTEX message categories"""

    NAVIGATIONAL_WARNING = "A"
    METEOROLOGICAL_WARNING = "B"
    ICE_REPORT = "C"
    SAR_INFO = "D"
    METEOROLOGICAL_FORECAST = "E"
    PILOT_SERVICE = "F"
    DECCA_MESSAGES = "G"
    LORAN_MESSAGES = "H"
    OMEGA_MESSAGES = "I"
    SATNAV_MESSAGES = "J"
    OTHER_ELECTRONIC = "K"
    NAVIGATIONAL_WARNING_SUPP = "L"
    SPECIAL_SERVICES = "V"
    TEST_MESSAGES = "W"
    NOTICES_TO_FISHERMEN = "Z"


class SensorType(str, enum.Enum):
    """Sensor types"""

    GPS = "gps"
    IMU = "imu"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    HUMIDITY = "humidity"
    COMPASS = "compass"
    DEPTH = "depth"
    WIND = "wind"


# Database Models


class VisionDetection(Base):
    """
    Vision detection events from Vakten module
    Stores all visual threat detections (ice, ships, obstacles)
    """

    __tablename__ = "vision_detections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    threat_type = Column(SQLEnum(ThreatType), nullable=True)
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    bbox = Column(Text, nullable=True)  # JSON string: {"x": 0, "y": 0, "w": 100, "h": 100}
    logged_by = Column(String(50), default="vakten")

    # Additional fields for enhanced tracking
    distance_meters = Column(Float, nullable=True)  # Distance to threat
    bearing_degrees = Column(Float, nullable=True)  # Bearing to threat
    image_path = Column(String(255), nullable=True)  # Path to saved detection image
    notes = Column(Text, nullable=True)

    # Indexes for performance
    __table_args__ = (
        Index("idx_detection_timestamp", "timestamp"),
        Index("idx_detection_type", "threat_type"),
    )

    def __repr__(self):
        return f"<VisionDetection(id={self.id}, type={self.threat_type}, confidence={self.confidence})>"


class NAVTEXMessage(Base):
    """
    NAVTEX messages from Navigator module
    Stores decoded radio navigation and weather messages
    """

    __tablename__ = "navtex_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    message_id = Column(String(10), unique=True, nullable=True)  # e.g., "A123"
    category = Column(SQLEnum(NAVTEXCategory), nullable=True)
    category_name = Column(String(100), nullable=True)
    body = Column(Text, nullable=True)
    is_critical = Column(Boolean, default=False)

    # Additional metadata
    station_id = Column(String(10), nullable=True)
    frequency_khz = Column(Float, nullable=True)
    signal_strength = Column(Float, nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_navtex_timestamp", "timestamp"),
        Index("idx_navtex_critical", "is_critical"),
        Index("idx_navtex_category", "category"),
    )

    def __repr__(self):
        return f"<NAVTEXMessage(id={self.message_id}, category={self.category}, critical={self.is_critical})>"


class AudioAnomaly(Base):
    """
    Audio anomalies from Engineer module
    Stores detected unusual engine/mechanical sounds
    """

    __tablename__ = "audio_anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    description = Column(Text, nullable=True)
    features = Column(Text, nullable=True)  # JSON string of audio features

    # Additional fields
    audio_file_path = Column(String(255), nullable=True)
    frequency_hz = Column(Float, nullable=True)
    amplitude_db = Column(Float, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    severity = Column(String(20), nullable=True)  # low, medium, high, critical

    # Indexes
    __table_args__ = (
        Index("idx_audio_timestamp", "timestamp"),
        Index("idx_audio_severity", "severity"),
    )

    def __repr__(self):
        return f"<AudioAnomaly(id={self.id}, confidence={self.confidence}, severity={self.severity})>"


class SensorReading(Base):
    """
    Sensor readings from GPS, IMU, and other sensors
    Time-series data for navigation and monitoring
    """

    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    sensor_type = Column(SQLEnum(SensorType), nullable=False, index=True)

    # Generic value fields
    value = Column(Float, nullable=True)
    value_json = Column(Text, nullable=True)  # For complex readings (GPS, IMU)

    # GPS-specific fields
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    altitude_meters = Column(Float, nullable=True)
    speed_knots = Column(Float, nullable=True)
    heading_degrees = Column(Float, nullable=True)

    # IMU-specific fields
    acceleration_x = Column(Float, nullable=True)
    acceleration_y = Column(Float, nullable=True)
    acceleration_z = Column(Float, nullable=True)
    gyro_x = Column(Float, nullable=True)
    gyro_y = Column(Float, nullable=True)
    gyro_z = Column(Float, nullable=True)

    # Environmental sensors
    temperature_celsius = Column(Float, nullable=True)
    pressure_hpa = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)

    # Quality indicators
    quality = Column(String(20), nullable=True)  # good, fair, poor
    satellites = Column(Integer, nullable=True)  # For GPS

    # Indexes
    __table_args__ = (
        Index("idx_sensor_timestamp", "timestamp"),
        Index("idx_sensor_type_timestamp", "sensor_type", "timestamp"),
    )

    def __repr__(self):
        return f"<SensorReading(id={self.id}, type={self.sensor_type}, value={self.value})>"


class SystemLog(Base):
    """
    System-wide event logging
    General purpose log table for all modules
    """

    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    level = Column(String(10), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    module = Column(String(50), nullable=False, index=True)  # vakten, navigator, engineer, etc.
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON string for additional context

    # Indexes
    __table_args__ = (
        Index("idx_log_timestamp", "timestamp"),
        Index("idx_log_level", "level"),
        Index("idx_log_module", "module"),
    )

    def __repr__(self):
        return f"<SystemLog(id={self.id}, level={self.level}, module={self.module})>"


class AIInteraction(Base):
    """
    AI assistant interactions (Psychologist, Doctor, Navi)
    Stores conversations and responses from AI modules
    """

    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    module = Column(String(50), nullable=False)  # psychologist, doctor, navi
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)

    # Context
    session_id = Column(String(100), nullable=True, index=True)
    user_id = Column(String(100), nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative

    # Performance metrics
    response_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_ai_timestamp", "timestamp"),
        Index("idx_ai_module", "module"),
        Index("idx_ai_session", "session_id"),
    )

    def __repr__(self):
        return f"<AIInteraction(id={self.id}, module={self.module}, session={self.session_id})>"


class Voyage(Base):
    """
    Voyage tracking
    Stores information about individual voyages/trips
    """

    __tablename__ = "voyages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    # Route information
    departure_port = Column(String(100), nullable=True)
    destination_port = Column(String(100), nullable=True)
    route_waypoints = Column(Text, nullable=True)  # JSON array of waypoints

    # Statistics
    distance_nm = Column(Float, nullable=True)  # Nautical miles
    max_speed_knots = Column(Float, nullable=True)
    avg_speed_knots = Column(Float, nullable=True)

    # Conditions
    max_ice_thickness_cm = Column(Float, nullable=True)
    weather_summary = Column(Text, nullable=True)

    # Status
    status = Column(String(20), default="active")  # active, completed, aborted
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Voyage(id={self.id}, from={self.departure_port}, to={self.destination_port})>"


class Alert(Base):
    """
    System alerts and notifications
    Critical events that require crew attention
    """

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    category = Column(String(50), nullable=False)  # vision, navigation, mechanical, weather, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Source information
    source_module = Column(String(50), nullable=True)
    source_id = Column(Integer, nullable=True)  # Reference to original detection/event

    # Resolution
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_alert_timestamp", "timestamp"),
        Index("idx_alert_severity", "severity"),
        Index("idx_alert_resolved", "resolved"),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, severity={self.severity}, title={self.title})>"


# Helper functions for database initialization


def init_database(engine):
    """
    Initialize database schema
    Creates all tables if they don't exist

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """
    Drop all tables (use with caution!)

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)
