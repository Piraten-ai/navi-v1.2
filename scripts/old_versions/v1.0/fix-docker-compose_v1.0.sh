#!/bin/bash
# Fix Docker Compose version issue on Jetson
# The error 'ContainerConfig' KeyError means docker-compose 1.29.2 is too old

set -e

echo "🔧 Docker Compose Version Fix"
echo "=============================="
echo ""

# Check current version
echo "Current docker-compose version:"
docker-compose --version || echo "Not found"
echo ""

echo "📦 Step 1: Removing old docker-compose..."
sudo rm -f /usr/bin/docker-compose /usr/local/bin/docker-compose

echo "📥 Step 2: Installing latest Docker Compose plugin..."
# Update package list
sudo apt-get update

# Install Docker Compose plugin (v2)
sudo apt-get install -y docker-compose-plugin

echo ""
echo "✅ Installation complete!"
echo ""

# Check new version
echo "New docker compose version:"
docker compose version

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "IMPORTANT: Docker Compose V2 Changes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "OLD command (v1):  docker-compose up -d"
echo "NEW command (v2):  docker compose up -d"
echo "                   ^^^ Note: NO HYPHEN"
echo ""
echo "All commands now use 'docker compose' instead of 'docker-compose'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create compatibility alias
echo "📝 Creating compatibility alias..."
cat >> ~/.bashrc <<'EOF'

# Docker Compose v2 compatibility alias
alias docker-compose='docker compose'
EOF

echo "✅ Alias added to ~/.bashrc"
echo "   Run: source ~/.bashrc  (or log out and back in)"
echo ""

# Clean up old containers/volumes that might be corrupted
echo "🧹 Cleaning up old Docker state..."
docker system prune -f

echo ""
echo "✅ All done! Now you can:"
echo ""
echo "   source ~/.bashrc              # Activate alias"
echo "   docker compose down           # Stop old containers"
echo "   docker compose build          # Rebuild images"
echo "   docker compose up -d          # Start services"
echo ""
echo "Or use the old syntax (via alias):"
echo "   docker-compose up -d"
echo ""
