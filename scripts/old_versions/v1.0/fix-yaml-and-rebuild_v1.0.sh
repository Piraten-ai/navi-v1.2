#!/bin/bash
# Quick fix for docker-compose.yml YAML syntax error

echo "🔧 Fixing docker-compose.yml"
echo ""

# Show the error area
echo "Checking line 50..."
sed -n '48,52p' docker-compose.yml

echo ""
echo "Restoring from backup if available..."

if [ -f "docker-compose.yml.backup" ]; then
    cp docker-compose.yml.backup docker-compose.yml
    echo "✅ Restored from backup"
else
    echo "⚠️  No backup found"
    echo ""
    echo "Creating fresh docker-compose.yml with correct WebSocket URL..."
    
    # Get Jetson IP
    JETSON_IP=$(hostname -I | awk '{print $1}')
    
    cat > docker-compose.yml << EOF
services:
  # Backend FastAPI server
  backend:
    build: ./backend
    container_name: aads-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://aads:aads_secure_pass@postgres:5432/aads
      - INFLUXDB_URL=http://influxdb:8086
      - INFLUXDB_TOKEN=aads_influx_token
      - INFLUXDB_ORG=aads
      - INFLUXDB_BUCKET=aads_metrics
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
      - OLLAMA_BASE_URL=http://navi:11434
      - LOG_LEVEL=INFO
      - ENVIRONMENT=production
      - VOICE_ENABLED=true
      - PIPER_VOICE_MODEL=/app/models/piper/en_US-lessac-medium.onnx
      - WHISPER_MODEL_SIZE=tiny.en
    volumes:
      - ./backend/app:/app/app
      - ./logs:/app/logs
      - ./models/piper:/app/models/piper:ro
      - ./audio:/app/audio:ro
    depends_on:
      - postgres
      - influxdb
      - redis
      - minio
      - navi
    restart: unless-stopped
    networks:
      - aads-network

  # Frontend React dashboard
  frontend:
    build: ./frontend
    container_name: aads-frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://${JETSON_IP}:8000
      - VITE_WS_URL=ws://${JETSON_IP}:8000/ws
      - VITE_SIGNALK_HOST=http://${JETSON_IP}:3001
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - aads-network

  # PostgreSQL database for persistent data
  postgres:
    image: postgres:15-alpine
    container_name: aads-postgres
    environment:
      - POSTGRES_DB=aads
      - POSTGRES_USER=aads
      - POSTGRES_PASSWORD=aads_secure_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - aads-network

  # InfluxDB for time-series data (NMEA, IMU, metrics)
  influxdb:
    image: influxdb:2.7-alpine
    container_name: aads-influxdb
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=aads
      - DOCKER_INFLUXDB_INIT_PASSWORD=aads_influx_pass
      - DOCKER_INFLUXDB_INIT_ORG=aads
      - DOCKER_INFLUXDB_INIT_BUCKET=aads_metrics
      - DOCKER_INFLUXDB_INIT_RETENTION=30d
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=aads_influx_token
    volumes:
      - influxdb_data:/var/lib/influxdb2
    restart: unless-stopped
    networks:
      - aads-network

  # Redis for pub/sub messaging and caching
  redis:
    image: redis:7-alpine
    container_name: aads-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - aads-network

  # MinIO for S3-compatible object storage (video clips, images)
  minio:
    image: minio/minio:latest
    container_name: aads-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    restart: unless-stopped
    networks:
      - aads-network

  # Ollama LLM server for Navi AI assistant
  navi:
    image: ollama/ollama:latest
    container_name: aads-navi-ollama
    runtime: nvidia
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    restart: unless-stopped
    networks:
      - aads-network

  # Signal K server for maritime navigation data (compass, depth, wind, etc.)
  signalk:
    image: signalk/signalk-server:latest
    container_name: aads-signalk
    ports:
      - "3001:3000"
      - "10332:10332/udp"
    environment:
      - NODE_ENV=production
    volumes:
      - signalk_data:/root/.signalk
    restart: unless-stopped
    networks:
      - aads-network

volumes:
  postgres_data:
    driver: local
  influxdb_data:
    driver: local
  redis_data:
    driver: local
  minio_data:
    driver: local
  ollama_data:
    driver: local
  signalk_data:
    driver: local

networks:
  aads-network:
    driver: bridge
EOF
    
    echo "✅ Created fresh docker-compose.yml with IP: $JETSON_IP"
fi

echo ""
echo "Validating YAML syntax..."
if docker compose config > /dev/null 2>&1; then
    echo "✅ YAML is valid!"
    
    echo ""
    echo "Rebuilding frontend..."
    docker compose build --no-cache frontend
    
    echo ""
    echo "Starting frontend..."
    docker compose up -d frontend
    
    echo ""
    echo "✅ Done! WebSocket URL is now configured correctly"
    echo "   Frontend: http://$(hostname -I | awk '{print $1}'):3000"
else
    echo "❌ YAML validation failed"
    docker compose config
fi
