#!/bin/bash
# Fix WebSocket URL for frontend to connect properly

echo "🔧 Fixing Frontend WebSocket Configuration"
echo "==========================================="
echo ""

# Get Jetson IP address
JETSON_IP=$(hostname -I | awk '{print $1}')

echo "Detected Jetson IP: $JETSON_IP"
echo ""

# Update docker-compose.yml
echo "Updating docker-compose.yml..."

# Backup original
cp docker-compose.yml docker-compose.yml.backup

# Update the frontend environment variables
cat > /tmp/update_compose.py << 'PYTHON_SCRIPT'
import yaml
import sys

# Read docker-compose.yml
with open('docker-compose.yml', 'r') as f:
    compose = yaml.safe_load(f)

# Get IP from command line
jetson_ip = sys.argv[1]

# Update frontend environment
if 'services' in compose and 'frontend' in compose['services']:
    if 'environment' not in compose['services']['frontend']:
        compose['services']['frontend']['environment'] = []
    
    env = compose['services']['frontend']['environment']
    
    # Update or add environment variables
    updated_env = []
    api_found = ws_found = signalk_found = False
    
    for item in env:
        if isinstance(item, str):
            if item.startswith('VITE_API_URL='):
                updated_env.append(f'VITE_API_URL=http://{jetson_ip}:8000')
                api_found = True
            elif item.startswith('VITE_WS_URL='):
                updated_env.append(f'VITE_WS_URL=ws://{jetson_ip}:8000/ws')
                ws_found = True
            elif item.startswith('VITE_SIGNALK_HOST='):
                updated_env.append(f'VITE_SIGNALK_HOST=http://{jetson_ip}:3001')
                signalk_found = True
            else:
                updated_env.append(item)
    
    # Add missing variables
    if not api_found:
        updated_env.append(f'VITE_API_URL=http://{jetson_ip}:8000')
    if not ws_found:
        updated_env.append(f'VITE_WS_URL=ws://{jetson_ip}:8000/ws')
    if not signalk_found:
        updated_env.append(f'VITE_SIGNALK_HOST=http://{jetson_ip}:3001')
    
    compose['services']['frontend']['environment'] = updated_env

# Write updated docker-compose.yml
with open('docker-compose.yml', 'w') as f:
    yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

print(f"✅ Updated frontend environment variables to use {jetson_ip}")
PYTHON_SCRIPT

# Check if PyYAML is installed
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "PyYAML not installed. Using sed fallback..."
    
    # Use sed to update the environment variables
    sed -i "s|VITE_API_URL=http://.*:8000|VITE_API_URL=http://${JETSON_IP}:8000|g" docker-compose.yml
    sed -i "s|VITE_WS_URL=ws://.*:8000/ws|VITE_WS_URL=ws://${JETSON_IP}:8000/ws|g" docker-compose.yml
    sed -i "s|VITE_SIGNALK_HOST=http://.*:3001|VITE_SIGNALK_HOST=http://${JETSON_IP}:3001|g" docker-compose.yml
    
    echo "✅ Updated using sed"
else
    python3 /tmp/update_compose.py "$JETSON_IP"
    rm /tmp/update_compose.py
fi

echo ""
echo "Updated configuration:"
grep -A 5 "frontend:" docker-compose.yml | grep "VITE_"

echo ""
echo "Stopping frontend..."
docker compose stop frontend

echo ""
echo "Rebuilding frontend with new configuration..."
docker compose build frontend

echo ""
echo "Starting frontend..."
docker compose up -d frontend

echo ""
echo "Waiting 10 seconds for frontend to start..."
sleep 10

echo ""
echo "✅ Frontend updated and restarted!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend:  http://${JETSON_IP}:3000"
echo "   Backend:   http://${JETSON_IP}:8000"
echo "   API Docs:  http://${JETSON_IP}:8000/docs"
echo ""
echo "Testing frontend..."
if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding!"
    echo ""
    echo "🎉 WebSocket should now connect properly!"
    echo "   Open http://${JETSON_IP}:3000 in your browser"
else
    echo "⚠️  Frontend not responding yet - check logs:"
    echo "   docker compose logs -f frontend"
fi

echo ""
echo "Backup saved as: docker-compose.yml.backup"
