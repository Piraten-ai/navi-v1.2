#!/bin/bash
# Fix Docker Compose version issue on Jetson
# The error "ContainerConfig" KeyError means docker-compose 1.29.2 is too old.

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Docker Compose Version Fix"
echo "=========================="
echo ""

echo "Current docker-compose version:"
docker-compose --version || echo "Not found"
echo ""

echo "Step 1: Removing old docker-compose..."
sudo rm -f /usr/bin/docker-compose /usr/local/bin/docker-compose

echo "Step 2: Installing latest Docker Compose plugin..."
sudo apt-get update
sudo apt-get install -y docker-compose-plugin

echo ""
echo "Installation complete."
echo ""

echo "New docker compose version:"
docker compose version

echo ""
echo "=========================="
echo "IMPORTANT: Docker Compose v2"
echo "=========================="
echo ""
echo "OLD command (v1):  docker-compose up -d"
echo "NEW command (v2):  docker compose up -d"
echo "                   (no hyphen)"
echo ""
echo "All commands now use 'docker compose' instead of 'docker-compose'."
echo ""

echo "Creating compatibility alias if missing..."
if ! grep -q "alias docker-compose='docker compose'" ~/.bashrc 2>/dev/null; then
    cat >> ~/.bashrc <<'EOF'

# Docker Compose v2 compatibility alias
alias docker-compose='docker compose'
EOF
    echo "Alias added to ~/.bashrc"
else
    echo "Alias already present in ~/.bashrc"
fi
echo "Run: source ~/.bashrc  (or log out and back in)"
echo ""

echo "Cleaning up old Docker state..."
docker system prune -f

echo ""
echo "All done. Next steps:"
echo "  source ~/.bashrc"
echo "  docker compose down"
echo "  docker compose build"
echo "  docker compose up -d"
