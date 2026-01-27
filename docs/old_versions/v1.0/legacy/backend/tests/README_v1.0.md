**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# AADS Backend Test Suite

Comprehensive test suite for the AADS (Arctic Autonomous Detection System) backend.

## Overview

This test suite provides 165+ tests covering:
- âœ… Database models (40+ tests)
- âœ… Database operations (35+ tests)
- âœ… Error handling system (40+ tests)
- âœ… API endpoints (50+ tests)

**Expected coverage:** 85-90%

## Quick Start

### 1. Install Dependencies

```bash
pip install -r tests/requirements-test.txt
```

### 2. Run All Tests

```bash
cd backend
pytest tests/ -v
```

### 3. Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### 4. View Coverage Report

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

## Test Organization

### Test Files

```
tests/
â”œâ”€â”€ conftest.py              # Shared fixtures and configuration
â”œâ”€â”€ pytest.ini               # Pytest settings
â”œâ”€â”€ requirements-test.txt    # Testing dependencies
â”œâ”€â”€ test_models.py          # Database model tests (40+ tests)
â”œâ”€â”€ test_database.py        # Database operation tests (35+ tests)
â”œâ”€â”€ test_error_handling.py  # Error handling tests (40+ tests)
â””â”€â”€ test_api.py             # API endpoint tests (50+ tests)
```

### Test Categories (Markers)

Run specific test categories using markers:

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# API tests only
pytest -m api

# Database tests only
pytest -m database

# Skip slow tests
pytest -m "not slow"
```

## Test Examples

### Database Model Tests

```python
def test_create_vision_detection(test_db_session):
    """Test creating a VisionDetection record."""
    detection = VisionDetection(
        threat_type="ice",
        confidence=0.92,
        distance_meters=500.0
    )

    test_db_session.add(detection)
    test_db_session.commit()

    assert detection.id is not None
    assert detection.created_at is not None
```

### API Endpoint Tests

```python
def test_create_detection(client):
    """Test creating a detection via API."""
    response = client.post("/api/v1/detections", json={
        "threat_type": "ice",
        "confidence": 0.92
    })

    assert response.status_code == 201
    assert response.json()["threat_type"] == "ice"
```

### Error Handling Tests

```python
def test_retry_decorator():
    """Test retry decorator with failures."""
    @retry(max_attempts=3, delay=0.1)
    def failing_function():
        raise ValueError("Temporary error")

    with pytest.raises(ValueError):
        failing_function()
```

## Fixtures

### Database Fixtures

- `test_db_engine` - In-memory SQLite database
- `test_db_session` - Database session for tests
- `client` - FastAPI TestClient

### Sample Data Fixtures

- `sample_vision_detection` - Sample detection record
- `sample_navtex_message` - Sample NAVTEX message
- `sample_audio_anomaly` - Sample audio anomaly
- `sample_sensor_reading` - Sample sensor reading
- `sample_voyage` - Sample voyage record
- `sample_alert` - Sample alert record

### Mock Fixtures

- `mock_ollama_response` - Mock Ollama API response
- `mock_gemini_response` - Mock Gemini API response
- `mock_claude_response` - Mock Claude API response

## Running Specific Tests

### Run Single Test File

```bash
pytest tests/test_models.py -v
```

### Run Single Test Class

```bash
pytest tests/test_models.py::TestVisionDetection -v
```

### Run Single Test Function

```bash
pytest tests/test_models.py::TestVisionDetection::test_create_vision_detection -v
```

### Run Tests Matching Pattern

```bash
# Run all tests with "detection" in the name
pytest tests/ -k detection -v
```

## Coverage Reports

### Generate HTML Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
```

### Generate Terminal Coverage Report

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Generate XML Coverage Report (for CI/CD)

```bash
pytest tests/ --cov=app --cov-report=xml
```

## Performance Testing

### Run Only Fast Tests

```bash
pytest -m "not slow"
```

### Run Slow Tests Separately

```bash
pytest -m slow
```

### Parallel Test Execution

```bash
# Run tests in parallel (4 workers)
pytest tests/ -n 4
```

## Debugging

### Run with Verbose Output

```bash
pytest tests/ -vv
```

### Show Print Statements

```bash
pytest tests/ -s
```

### Drop into Debugger on Failure

```bash
pytest tests/ --pdb
```

### Show Locals on Failure

```bash
pytest tests/ -l
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r tests/requirements-test.txt

      - name: Run tests
        run: pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

### 1. Test Isolation

Each test should be independent:

```python
def test_example(test_db_session):
    # Create fresh data
    record = Model(...)
    test_db_session.add(record)
    test_db_session.commit()

    # Test logic
    assert record.id is not None

    # Cleanup happens automatically
```

### 2. Use Fixtures

Reuse common setup with fixtures:

```python
def test_with_fixture(sample_vision_detection):
    # sample_vision_detection is already created
    assert sample_vision_detection.threat_type == "ice"
```

### 3. Descriptive Test Names

```python
# Good
def test_create_detection_with_valid_data():
    pass

# Bad
def test_detection():
    pass
```

### 4. Arrange-Act-Assert Pattern

```python
def test_example():
    # Arrange
    data = {"key": "value"}

    # Act
    result = function(data)

    # Assert
    assert result == expected
```

## Troubleshooting

### Import Errors

```bash
# Ensure app is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Database Errors

Tests use in-memory SQLite, so no database setup needed. If you see database errors:

```bash
# Clear pytest cache
pytest --cache-clear
```

### Fixture Not Found

Ensure `conftest.py` is in the tests directory:

```bash
ls tests/conftest.py
```

## Test Statistics

| Category | Tests | Coverage Goal |
|----------|-------|---------------|
| Models | 40+ | 95% |
| Database | 35+ | 90% |
| Error Handling | 40+ | 95% |
| API | 50+ | 85% |
| **TOTAL** | **165+** | **85-90%** |

## Next Steps

After running the test suite:

1. âœ… Review coverage report
2. âœ… Add tests for uncovered code
3. âœ… Integrate with CI/CD
4. âœ… Add performance benchmarks
5. âœ… Add security tests

## Support

For issues or questions about the test suite, see:

- Test documentation in each test file
- Fixture definitions in `conftest.py`
- Pytest documentation: https://docs.pytest.org

