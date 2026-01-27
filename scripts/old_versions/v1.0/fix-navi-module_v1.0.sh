#!/bin/bash
# Fix Navi module to use OLLAMA_BASE_URL environment variable

echo "🔧 Fixing Navi Module to Read OLLAMA_BASE_URL"
echo "==============================================="
echo ""

NAVI_FILE="backend/app/modules/navi.py"

echo "Backing up original file..."
cp "$NAVI_FILE" "${NAVI_FILE}.backup"

echo "Updating navi.py..."

# Replace the last line that creates the global instance
cat > /tmp/fix_navi.py << 'PYTHON'
import sys

# Read the file
with open('backend/app/modules/navi.py', 'r') as f:
    lines = f.readlines()

# Find and replace the global instance creation
for i in range(len(lines) - 1, -1, -1):
    if 'navi = NaviModule(mock_mode=False)' in lines[i]:
        # Insert the OLLAMA_URL line before it
        lines.insert(i, 'OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")\n')
        # Update the navi instantiation
        lines[i+1] = 'navi = NaviModule(ollama_url=OLLAMA_URL, mock_mode=False)  # Use real Ollama connection\n'
        break

# Write back
with open('backend/app/modules/navi.py', 'w') as f:
    f.writelines(lines)

print("✅ Updated navi.py")
PYTHON

python3 /tmp/fix_navi.py
rm /tmp/fix_navi.py

echo ""
echo "Verifying change..."
tail -5 "$NAVI_FILE"

echo ""
echo "Restarting backend container..."
docker compose restart backend

echo ""
echo "Waiting for backend to start..."
sleep 10

echo ""
echo "Checking backend logs..."
docker compose logs --tail=20 backend | grep -i "navi initialized"

echo ""
echo "✅ Fix applied!"
echo ""
echo "Now try chatting with Navi at:"
echo "   http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "The Navi module should now connect to Ollama properly!"
