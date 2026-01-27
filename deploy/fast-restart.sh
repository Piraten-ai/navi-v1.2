#!/bin/bash
# AADS PRO - Aggressive Fast Restart
# Fixes 'ContainerConfig' errors and "zombie" networks automatically

echo "🧊 Initializing Hard Reset for AADS PRO..."

# 1. Force stop and remove core containers
echo "🧹 Removing stuck containers..."
docker rm -f aads-backend aads-frontend 2>/dev/null || true

# 2. Cleanup orphaned networks that block restarts
echo "🌐 Cleaning up networks..."
docker network prune -f

# 3. Pull latest code (if in git repo)
if [ -d .git ]; then
    echo "📥 Pulling latest updates..."
    git pull
fi

# 4. Rebuild and launch with force-recreate
echo "🔨 Building and launching services..."
docker-compose up -d --build --force-recreate backend frontend

echo ""
echo "✅ SUCCESS: System is restarting."
echo "Dashboard: http://192.168.39.196:3000"
echo "Backend:   http://192.168.39.196:8000"
echo ""
echo "🔧 If you see 'No such image', Docker is just cleaning up. Wait 30 seconds and refresh."
