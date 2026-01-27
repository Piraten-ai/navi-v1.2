#!/bin/bash
# Fix Ollama URL in backend env files

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Fixing Backend Ollama Connection"
echo "================================"
echo ""

FILES=("config/backend.env.jetson" "config/backend.env.dev")
UPDATED=0

sed_in_place() {
    local expr="$1"
    local file="$2"
    if sed --version >/dev/null 2>&1; then
        sed -i "$expr" "$file"
    else
        sed -i '' "$expr" "$file"
    fi
}

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Updating $file..."
        cp "$file" "$file.backup.$(date +%s)"
        if grep -q "^OLLAMA_BASE_URL=" "$file"; then
            sed_in_place 's|^OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=http://navi:11434|g' "$file"
        else
            echo "OLLAMA_BASE_URL=http://navi:11434" >> "$file"
        fi
        UPDATED=1
    fi
done

if [ "$UPDATED" -eq 0 ]; then
    echo "No backend env files found under config/"
    exit 1
fi

echo ""
echo "Restarting backend..."
docker compose stop backend
docker compose up -d backend

echo ""
echo "Waiting for backend to start..."
sleep 10

echo ""
echo "Testing Ollama connection from backend..."
if docker exec aads-backend curl -f -s http://navi:11434/api/version > /dev/null 2>&1; then
    echo "OK: Backend can reach Ollama"
else
    echo "WARN: Backend still cannot reach Ollama"
    echo "      Checking backend logs..."
    docker compose logs --tail=20 backend | grep -i ollama || true
fi

echo ""
echo "Fix applied."
