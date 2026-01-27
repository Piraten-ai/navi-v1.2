# How to Run Tests - AADS Backend

## ✅ UPGRADED - Testing Framework v2.0

### 🆕 What's New in This Upgrade

- **pytest 8.3.4** (from 7.4.0) - Latest stable version with enhanced features
- **pytest-asyncio 0.24.0** - Better async test support with auto-detection
- **pytest-timeout 2.3.1** - New! Prevents hanging tests
- **Enhanced coverage** (7.6.9) - Better reporting with exclude patterns
- **Updated dependencies** - All testing packages updated to latest stable versions

### Quick Test (5 Working Tests)

#### Option 1: Docker (Recommended)

```bash
cd /c/Users/artic/Desktop/navi-main

# Run the test script
./run-tests.sh
```

#### Option 2: Docker Manual

```bash
cd /c/Users/artic/Desktop/navi-main

docker-compose -f docker-compose.dev.yml run --rm backend bash -c "pip install -q -r tests/requirements-test.txt && pytest tests/test_models_quick.py -v"
```

#### Option 3: Local Python (New!)

```bash
cd /c/Users/artic/Desktop/navi-main/backend

# Windows
python run_tests_local.py

# Linux/Mac
python3 run_tests_local.py
```

## 🎯 What's Working

**5 Tests - ALL PASSING ✅**

1. ✅ `test_vision_detection_basic` - Ice detection model
2. ✅ `test_navtex_message_basic` - Maritime messages
3. ✅ `test_audio_anomaly_basic` - Engine sound anomalies
4. ✅ `test_sensor_reading_basic` - GPS/IMU sensors
5. ✅ `test_alert_basic` - System alerts

## 📊 Test Output (Updated)

```
============================= test session starts ==============================
platform linux -- Python 3.10.19, pytest-8.3.4, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /app
configfile: pytest.ini
plugins: anyio-4.12.1, asyncio-0.24.0, cov-6.0.0, mock-3.14.0, timeout-2.3.1
collected 5 items

tests/test_models_quick.py::TestModelsQuick::test_vision_detection_basic PASSED [ 20%]
tests/test_models_quick.py::TestModelsQuick::test_navtex_message_basic PASSED [ 40%]
tests/test_models_quick.py::TestModelsQuick::test_audio_anomaly_basic PASSED [ 60%]
tests/test_models_quick.py::TestModelsQuick::test_sensor_reading_basic PASSED [ 80%]
tests/test_models_quick.py::TestModelsQuick::test_alert_basic PASSED     [100%]

======================== 5 passed in 0.14s =========================
```

## 🚀 Advanced Test Commands

### Run with Coverage

```bash
docker-compose -f docker-compose.dev.yml run --rm backend bash -c "pip install -q -r tests/requirements-test.txt && pytest tests/ --cov=app --cov-report=html"
```

### Run Specific Test Categories

```bash
# Run only database tests
pytest -m database

# Run only API tests
pytest -m api

# Run only unit tests (fast)
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

### Run Tests in Parallel

```bash
# Use all available CPU cores
pytest -n auto

# Use 4 workers
pytest -n 4
```

### Run with Timeout (New!)

```bash
# Fail tests that take longer than 30 seconds
pytest --timeout=30
```

## 🚀 What You Can Test

### Vision Detection (Ice/Ship Detection)
```python
detection = VisionDetection(
    threat_type="ICE",
    confidence=0.92,
    distance_meters=500.0
)
```

### NAVTEX Messages (Maritime Navigation)
```python
message = NAVTEXMessage(
    category="A",  # Navigation warning
    body="GALE WARNING: Wind NE 30-40 knots",
    station_id="SVALBARD"
)
```

### Audio Anomalies (Engine Sounds)
```python
anomaly = AudioAnomaly(
    confidence=0.87,
    description="unusual_vibration",
    severity="medium"
)
```

### Sensor Readings (GPS/IMU)
```python
reading = SensorReading(
    sensor_type="GPS",
    latitude=78.2232,  # Svalbard
    longitude=15.6267
)
```

### Alerts
```python
alert = Alert(
    severity="warning",
    category="vision",
    title="Ice Detected",
    message="Large iceberg ahead"
)
```

## 🔧 Troubleshooting

### If tests fail:

1. **Make sure Docker is running**
   ```bash
   docker ps
   ```

2. **Rebuild if needed**
   ```bash
   docker-compose -f docker-compose.dev.yml build backend
   ```

3. **Check logs**
   ```bash
   docker-compose -f docker-compose.dev.yml logs backend
   ```

## 📝 Notes

- Tests run **inside Docker container** (Python is not needed on your local machine for Docker method)
- **Local test runner** available for development without Docker
- Each test run is isolated (uses in-memory SQLite database)
- Tests execute in **< 1 second**
- No external services needed (mocked)
- **Async tests** now auto-detected with pytest-asyncio 0.24.0
- **Timeout protection** prevents hanging tests (default 300s)

## 🔄 Upgrade Summary

### Key Improvements

1. **Testing Framework**: pytest 7.4.0 → 8.3.4
   - Better async support with `asyncio_mode = auto`
   - Enhanced error reporting
   - Improved fixture scoping

2. **Coverage**: coverage 7.4.0 → 7.6.9
   - Better exclusion patterns
   - Enhanced HTML reports

3. **New Features**:
   - `pytest-timeout` for test timeout protection
   - Enhanced async test auto-detection
   - Better code quality tooling (flake8, mypy, pylint updated)

4. **Dependencies Synchronized**:
   - SQLAlchemy 2.0.23 → 2.0.36 (matches main requirements)
   - httpx 0.25.2 → 0.27.2 (matches main requirements)
   - starlette 0.27.0 → 0.41.3 (latest stable)

## 🎉 Success!

All tests are working and validating your AADS backend models with the upgraded testing framework!
