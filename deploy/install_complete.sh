#!/bin/bash
# NAVI Complete Standalone Deployment
# Single command to deploy on any Jetson device
# Usage: curl -sSL https://raw.githubusercontent.com/Piraten-ai/navi-main/main/deploy/install_complete.sh | sudo bash

set -e

echo "=== NAVI Arctic Decision Support System ==="
echo "Installing to /opt/navi-main..."

# Create directory
mkdir -p /opt/navi-main
cd /opt/navi-main

# Clone or pull latest
if [ -d .git ]; then
  git pull origin main
else
  git clone https://github.com/Piraten-ai/navi-main.git . || curl -sSL https://github.com/Piraten-ai/navi-main/archive/refs/heads/main.tar.gz | tar xz --strip-components=1
fi

# Ensure Docker is installed and running
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo bash get-docker.sh
  rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
  echo "Installing Docker Compose..."
  sudo apt-get update
  sudo apt-get install -y docker-compose
fi

# Add current user to docker group
sudo usermod -aG docker $(whoami)

# Stop any existing services
echo "Stopping existing services..."
docker-compose down 2>/dev/null || true

# Build and start everything
echo "Building containers (this may take 10-15 minutes)..."
docker-compose build

echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check health
echo "Checking health..."
for i in {1..30}; do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is healthy!"
    break
  fi
  echo "  Waiting for backend... ($i/30)"
  sleep 1
done

# Show status
echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "Access the system:"
echo "  Web Dashboard: http://$(hostname -I | awk '{print $1}'):3000"
echo "  Backend API:   http://$(hostname -I | awk '{print $1}'):8000"
echo "  API Docs:      http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "Manage services:"
echo "  View logs:     docker-compose logs -f"
echo "  Stop:          docker-compose down"
echo "  Restart:       docker-compose restart"
echo ""
echo "Access via SSH:"
ssh_user=$(whoami)
if [ "$ssh_user" = "root" ]; then
  ssh_user="navi"
fi
echo "  ssh $ssh_user@$(hostname -I | awk '{print $1}')"
echo ""
