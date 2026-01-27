#!/bin/bash
# Fix Navi module to use OLLAMA_BASE_URL environment variable

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Fixing Navi module to read OLLAMA_BASE_URL"
echo "========================================="
echo ""

NAVI_FILE="backend/app/modules/navi.py"

echo "Backing up original file..."
cp "$NAVI_FILE" "${NAVI_FILE}.backup"

cat > /tmp/fix_navi.py << 'PYTHON'
import os

path = "backend/app/modules/navi.py"
with open(path, "r") as f:
    content = f.read()

if "OLLAMA_URL = os.getenv" in content and "NaviModule(ollama_url=OLLAMA_URL" in content:
    print("navi.py already uses OLLAMA_BASE_URL")
    raise SystemExit(0)

lines = content.splitlines(True)
updated = False
for i in range(len(lines) - 1, -1, -1):
    if "navi = NaviModule(mock_mode=False)" in lines[i]:
        lines.insert(i, 'OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://navi:11434")\n')
        lines[i + 1] = "navi = NaviModule(ollama_url=OLLAMA_URL, mock_mode=False)  # Use real Ollama connection\n"
        updated = True
        break

if not updated:
    raise SystemExit("Could not find NaviModule initialization to update")

with open(path, "w") as f:
    f.writelines(lines)

print("Updated navi.py")
PYTHON

python3 /tmp/fix_navi.py
rm /tmp/fix_navi.py

echo ""
echo "Restarting backend container..."
docker compose restart backend

echo ""
echo "Checking backend logs..."
docker compose logs --tail=20 backend | grep -i "navi initialized" || true

echo ""
echo "Fix applied."
echo "Frontend runs on the Raspberry Pi (docker-compose.pi.yml)."
