# Quick Test Reference - AADS Backend

## 🚀 Quick Start

### Run All Tests:
```bash
cd backend
pytest tests/ -v
```

### Run Specific Module:
```bash
pytest tests/test_navi.py -v              # Conversational AI
pytest tests/test_psykologen.py -v        # Mental Health
pytest tests/test_ingenioren.py -v        # System Diagnostics
pytest tests/test_vakten.py -v            # Vision AI
pytest tests/test_navigator.py -v         # NAVTEX
pytest tests/test_nmea_gps.py -v          # GPS Parsing
pytest tests/test_legen.py -v             # Medical Triage
```

### Coverage Report:
```bash
pytest tests/ --cov=app/modules --cov-report=html
# Open htmlcov/index.html
```

---

## 📊 Test Suite Overview

| Module | Purpose | Tests | Coverage |
|--------|---------|-------|----------|
| **Navi** | Conversational AI (Ollama) | 60+ | 90% |
| **Psykologen** | Mental Health Support | 55+ | 95% |
| **Ingeniøren** | System Diagnostics | 60+ | 90% |
| **Vakten** | Vision AI Threats | 70+ | 95% |
| **Navigator** | NAVTEX Routing | 60+ | 90% |
| **NMEA GPS** | GPS Parsing | 40+ | 95% |
| **Legen** | Medical Triage | 50+ | 95% |
| **TOTAL** | All Modules | **370+** | **95%** |

---

## 🧪 Test Patterns

### Async Tests:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### Mocking External Services:
```python
@patch('httpx.AsyncClient')
async def test_with_http_mock(mock_client):
    mock_client.post.return_value = Mock(status_code=200)
    result = await function_that_uses_http()
    assert result is not None
```

### Temporary Files (Privacy Tests):
```python
with tempfile.TemporaryDirectory() as tmpdir:
    module = Module(data_dir=tmpdir)
    module.save_data("test")
    assert os.path.exists(tmpdir)
```

---

## 🔧 Common Commands

### Debug Single Test:
```bash
pytest tests/test_navi.py::TestChatFunctionality::test_chat_with_context -v
```

### Show Print Statements:
```bash
pytest tests/test_navi.py -v -s
```

### Stop on First Failure:
```bash
pytest tests/ -x
```

### Run Only Failed Tests:
```bash
pytest tests/ --lf
```

### Parallel Execution:
```bash
pytest tests/ -n auto  # Requires pytest-xdist
```

---

## 📝 Test File Structure

Each test file follows this pattern:

```python
"""
Module description
"""

import pytest
from unittest.mock import Mock, patch
from app.modules.module_name import ModuleClass

class TestFeature1:
    """Test feature 1"""
    
    def test_normal_case(self):
        """Test normal operation"""
        module = ModuleClass()
        result = module.method()
        assert result == expected
    
    def test_edge_case(self):
        """Test edge case"""
        module = ModuleClass()
        with pytest.raises(ValueError):
            module.method(invalid_input)

class TestFeature2:
    """Test feature 2"""
    # More tests...
```

---

## 🐛 Debugging Tips

### Test Fails Intermittently?
- Check for time-dependent logic
- Look for random number generation
- Verify async race conditions

### Import Errors?
- Ensure in backend/ directory
- Check PYTHONPATH is set
- Verify requirements installed

### Timeout Errors?
- Default timeout is 300s per test
- Adjust in pytest.ini if needed
- Check for infinite loops

---

## 📦 Dependencies

Install all test dependencies:
```bash
cd backend
pip install -r requirements-test.txt
```

Key packages:
- pytest 8.3.4
- pytest-asyncio 0.24.0
- pytest-timeout 2.3.1
- pytest-cov 6.0.0
- httpx 0.27.0
- psutil 6.1.0

---

## ✅ Verification Checklist

After making changes:

- [ ] Run affected test file: `pytest tests/test_module.py -v`
- [ ] Check coverage: `pytest tests/test_module.py --cov=app/modules/module`
- [ ] Run all tests: `pytest tests/ -v`
- [ ] Verify no warnings: `pytest tests/ -v --strict-warnings`
- [ ] Update documentation if needed

---

## 🎯 Coverage Goals

- **95%+**: Safety-critical (Vakten, Legen, Psykologen, NMEA GPS)
- **90%+**: Operational (Navigator, Navi, Ingeniøren)
- **Overall**: 95%+ combined coverage

Check coverage:
```bash
pytest tests/ --cov=app/modules --cov-report=term-missing
```

---

## 🔍 Finding Tests

### By Feature:
```bash
pytest tests/ -k "threat"        # All threat-related tests
pytest tests/ -k "mood"          # All mood-related tests
pytest tests/ -k "acoustic"      # All acoustic tests
```

### By Marker:
```bash
pytest tests/ -m asyncio         # Only async tests
pytest tests/ -m slow            # Only slow tests
```

### Count Tests:
```bash
pytest tests/ --collect-only -q
```

---

## 📚 Documentation

- Full summary: `TESTING_COMPLETE.md`
- Phase 2 details: `PHASE_2_TESTS_COMPLETE.md`
- Framework upgrade: `TESTING_UPGRADE_SUMMARY.md`
- Batch 1 modules: `CORE_MODULE_TESTS_SUMMARY.md`

---

## 🚨 Common Issues

### Issue: Tests fail with "No module named 'app'"
**Solution**: Run from backend/ directory or set PYTHONPATH

### Issue: Async tests hang
**Solution**: Check pytest-asyncio version (need 0.24.0+)

### Issue: Coverage seems low
**Solution**: Check exclude_lines in pytest.ini

### Issue: Tests pass locally but fail in CI
**Solution**: Check for hard-coded paths, time zones, or external dependencies

---

## 🎉 Success!

If you see this output, everything works:

```bash
$ pytest tests/ -v

=================== test session starts ===================
collected 370+ items

tests/test_vakten.py::TestThreatScore::test_basic PASSED
tests/test_navigator.py::TestParsing::test_gga PASSED
tests/test_navi.py::TestChat::test_response PASSED
...

=================== 370+ passed in 45.23s ===================
```

---

**Quick Reference**: Keep this file handy for daily testing tasks!
