#!/bin/bash
# Update Jetson host for the Pi frontend (docker-compose.pi.yml)

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

JETSON_HOST_INPUT="$1"
JETSON_HOST="${JETSON_HOST_INPUT:-${JETSON_HOST:-192.168.39.196}}"

echo "Updating Pi frontend config"
echo "==========================="
echo ""
echo "JETSON_HOST: $JETSON_HOST"

sed_in_place() {
    local expr="$1"
    local file="$2"
    if sed --version >/dev/null 2>&1; then
        sed -i "$expr" "$file"
    else
        sed -i '' "$expr" "$file"
    fi
}

if [ -f ".env" ]; then
    if grep -q "^JETSON_HOST=" .env; then
        sed_in_place "s|^JETSON_HOST=.*|JETSON_HOST=${JETSON_HOST}|g" .env
    else
        echo "JETSON_HOST=${JETSON_HOST}" >> .env
    fi
else
    echo "JETSON_HOST=${JETSON_HOST}" > .env
fi

echo ""
echo "Rebuilding frontend..."
docker compose -f docker-compose.pi.yml build frontend

echo ""
echo "Starting frontend..."
docker compose -f docker-compose.pi.yml up -d frontend

echo ""
echo "Done."
echo "Frontend URL: http://localhost:3000"
