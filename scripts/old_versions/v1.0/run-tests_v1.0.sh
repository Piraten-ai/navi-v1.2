#!/bin/bash
# AADS Test Runner - Run tests inside Docker container

echo "🧪 Running AADS Backend Tests..."
echo "================================"
echo ""

if ! command -v docker-compose >/dev/null 2>&1; then
  echo "docker-compose not found, running tests locally..."
  cd backend
  python -m pip install -q -r requirements.txt
  python -m pip install -q -r tests/requirements-test.txt
  python -m pytest tests/test_models_quick.py -v --tb=short
else
  docker-compose -f docker-compose.dev.yml run --rm backend bash -c "
      pip install -q pytest sqlalchemy httpx &&
      pytest tests/test_models_quick.py -v --tb=short
  "
fi

echo ""
echo "✅ Tests complete!"
