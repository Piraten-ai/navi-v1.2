#!/bin/bash
# Run module-specific tests

echo "============================================"
echo "Running AADS Module Tests"
echo "============================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests by module with coverage
echo "Testing Vakten (Vision AI) Module..."
python -m pytest tests/test_vakten.py -v --cov=app.modules.vakten --cov-report=term-missing

echo ""
echo "Testing Navigator (NAVTEX) Module..."
python -m pytest tests/test_navigator.py -v --cov=app.modules.navigator --cov-report=term-missing

echo ""
echo "Testing NMEA GPS Module..."
python -m pytest tests/test_nmea_gps.py -v --cov=app.modules.nmea_gps --cov-report=term-missing

echo ""
echo "Testing Legen (Medical Triage) Module..."
python -m pytest tests/test_legen.py -v --cov=app.modules.legen --cov-report=term-missing

echo ""
echo "Testing Navi (Conversational AI) Module..."
python -m pytest tests/test_navi.py -v --cov=app.modules.navi --cov-report=term-missing

echo ""
echo "Testing Psykologen (Mental Health) Module..."
python -m pytest tests/test_psykologen.py -v --cov=app.modules.psykologen --cov-report=term-missing

echo ""
echo "Testing Ingeniøren (System Diagnostics) Module..."
python -m pytest tests/test_ingenioren.py -v --cov=app.modules.ingenioren --cov-report=term-missing

echo ""
echo "============================================"
echo "Running ALL Tests with Full Coverage..."
echo "============================================"
python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo "Coverage report generated in htmlcov/index.html"
echo "Done!"
