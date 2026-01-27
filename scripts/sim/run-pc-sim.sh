#!/bin/bash
# One-button PC simulation (Signal K + bridge + full stack)

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export BACKEND_ENV_FILE="config/backend.env.sim"

echo "Starting dev stack with simulation env..."
docker compose -f docker-compose.dev.yml up -d

echo ""
echo "Stack started."
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8001"
echo "Signal K: http://localhost:3001"
