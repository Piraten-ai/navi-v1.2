**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# Testing Quick Start Guide - AADS

Get started with the AADS test suite in 5 minutes.

---

## Backend Tests (Python/FastAPI)

### Prerequisites
```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### Run Tests

**Quick smoke test (5 tests, <1 second):**
```bash
python -m pytest tests/test_models_quick.py -v
```

**Module tests (recommended):**
```bash
# Vision AI
python -m pytest tests/test_vakten.py -v

# NAVTEX Parsing
python -m pytest tests/test_navigator.py -v

# GPS Module
python -m pytest tests/test_nmea_gps.py -v

# Medical Triage
python -m pytest tests/test_legen.py -v
```

**All tests with coverage:**
```bash
python -m pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report
```

**Run module tests script:**
```bash
bash run_module_tests.sh
```

---

## Frontend Tests (React/TypeScript)

### Prerequisites
```bash
cd frontend
npm install
```

### Run Tests

**Interactive watch mode:**
```bash
npm test
```

**With UI:**
```bash
npm run test:ui
```

**With coverage:**
```bash
npm run test:coverage
```

---

## CI/CD Integration

Tests automatically run on:
- Push to main/develop branches
- Pull requests
- Nightly schedule (integration tests)

**GitHub Actions Workflows:**
- `.github/workflows/ci-cd.yml` - Main CI/CD pipeline
- `.github/workflows/integration-tests.yml` - Integration testing

---

## Test Structure

```
backend/tests/
â”œâ”€â”€ test_vakten.py           # Vision AI (20KB, 560 lines)
â”œâ”€â”€ test_navigator.py        # NAVTEX (23KB, 719 lines)
â”œâ”€â”€ test_nmea_gps.py         # GPS (22KB, 700+ lines)
â”œâ”€â”€ test_legen.py            # Medical (19KB, 600+ lines)
â”œâ”€â”€ test_navi.py             # Conversational AI (18KB, 550+ lines)
â”œâ”€â”€ test_psykologen.py       # Mental Health (22KB, 680+ lines)
â”œâ”€â”€ test_ingenioren.py       # Diagnostics (19KB, 600+ lines)
â”œâ”€â”€ test_api.py              # API endpoints (existing)
â”œâ”€â”€ test_database.py         # Database operations (existing)
â”œâ”€â”€ test_error_handling.py   # Error handling (existing)
â”œâ”€â”€ test_models.py           # Database models (existing)
â”œâ”€â”€ test_signalk.py          # Signal K integration (existing)
â””â”€â”€ conftest.py              # Shared fixtures

frontend/
â”œâ”€â”€ vitest.config.ts         # Vitest configuration
â””â”€â”€ src/
    â””â”€â”€ test/
        â””â”€â”€ setup.ts         # Test setup & mocks
```

---

## Common Commands

### Backend

```bash
# Run specific test
pytest tests/test_vakten.py::TestThreatScoreCalculation::test_threat_score_ice_floe_close_range -v

# Run tests by marker
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Skip slow tests

# Run with verbose output
pytest tests/ -vv

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s

# Parallel execution
pytest tests/ -n 4
```

### Frontend

```bash
# Run specific test file
npm test -- src/components/__tests__/Dashboard.test.tsx

# Run tests matching pattern
npm test -- --run --reporter=verbose
```

---

## Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Vakten Module | 95% | âœ… ~95% |
| Navigator Module | 95% | âœ… ~95% |
| NMEA GPS Module | 90% | âœ… ~90% |
| Legen Module | 95% | âœ… ~95% |
| Navi Module | 85% | âœ… ~85% |
| Psykologen Module | 90% | âœ… ~90% |
| IngeniÃ¸ren Module | 90% | âœ… ~90% |
| **Overall Backend** | **85-90%** | âœ… **~85-90%** |
| Frontend | 80% | ðŸ”„ Infrastructure Ready |

---

## Debugging Tests

### Backend

**Enable verbose logging:**
```python
# In conftest.py or specific test
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Use pytest debugger:**
```bash
pytest tests/test_vakten.py --pdb  # Drop into debugger on failure
```

**Print fixture values:**
```python
def test_something(sample_detection):
    print(f"Detection: {sample_detection}")  # Use -s flag to see prints
    assert sample_detection.confidence > 0.8
```

### Frontend

**Use Vitest UI for debugging:**
```bash
npm run test:ui
```

**Console.log in tests:**
```typescript
it('should render', () => {
  console.log('Debugging...')
  // test code
})
```

---

## Troubleshooting

### Backend

**Issue:** Import errors for app modules
```bash
# Solution: Run from backend directory
cd backend
python -m pytest tests/
```

**Issue:** Database connection errors
```bash
# Solution: Tests use in-memory SQLite, no DB needed
# If errors persist, check conftest.py fixture setup
```

**Issue:** Async test failures
```bash
# Solution: Ensure pytest-asyncio is installed
pip install pytest-asyncio
```

### Frontend

**Issue:** Cannot find module errors
```bash
# Solution: Install dependencies
npm install
```

**Issue:** jsdom errors
```bash
# Solution: Ensure jsdom is installed
npm install --save-dev jsdom
```

---

## Next Steps

1. **Run backend tests:** `cd backend && python -m pytest tests/ -v`
2. **View coverage:** `python -m pytest tests/ --cov=app --cov-report=html`
3. **Open report:** `open htmlcov/index.html`
4. **Install frontend deps:** `cd frontend && npm install`
5. **Run frontend tests:** `npm test`

---

## Documentation

- **Full Test Plan:** `C:\Users\artic\.claude\plans\warm-moseying-harp.md`
- **Test Summary:** `TEST_IMPROVEMENTS_SUMMARY.md`
- **Test Suite Docs:** `backend/tests/README.md`
- **Testing Guide:** `TESTING.md`

---

## Support

If tests fail or you encounter issues:
1. Check test output for error messages
2. Review fixture setup in `conftest.py`
3. Verify all dependencies are installed
4. Check module imports are correct
5. Ensure you're running from the correct directory

**Happy Testing! ðŸ§ªâœ…**

