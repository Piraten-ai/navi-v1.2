**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# Docker Update Guide - AADS PRO
## Updated: 2026-01-23 (All Fixes Applied)

---

## ðŸš€ Quick Update (Recommended)

### Method 1: Rebuild with Latest Changes (Fastest)
```bash
# Stop all containers
docker-compose down

# Rebuild with no cache (ensures latest fixes)
docker-compose build --no-cache

# Start everything
docker-compose up -d

# Check logs
docker-compose logs -f backend frontend
```

**Time:** ~5-10 minutes
**Use when:** You've made code changes (like the React fixes we just applied)

---

## ðŸ“¦ Step-by-Step Update Process

### Step 1: Stop Running Containers
```bash
cd /path/to/navi-main

# Stop containers gracefully
docker-compose down

# Or force stop if needed
docker-compose down --timeout 30
```

### Step 2: Pull Latest Base Images (Optional but Recommended)
```bash
# Update base images to latest versions
docker-compose pull

# Or pull specific images
docker pull node:25-alpine
docker pull python:3.11-slim
docker pull nginx:1.29-alpine
docker pull postgres:15-alpine
docker pull influxdb:2.7-alpine
docker pull redis:7-alpine
docker pull ollama/ollama:latest
docker pull signalk/signalk-server:latest
```

### Step 3: Rebuild Application Images
```bash
# Rebuild with no cache (recommended after code changes)
docker-compose build --no-cache

# Or rebuild specific service
docker-compose build --no-cache frontend
docker-compose build --no-cache backend
```

**Why `--no-cache`?**
- Ensures all latest fixes are included
- Prevents using old cached layers
- Especially important after React Error #31 fixes

### Step 4: Start Updated Containers
```bash
# Start in detached mode
docker-compose up -d

# Or start with logs visible
docker-compose up

# Start specific services only
docker-compose up -d backend frontend
```

### Step 5: Verify Everything Works
```bash
# Check container status
docker-compose ps

# Should show all containers "Up"
# Example output:
# NAME                  STATUS
# aads-backend          Up 30 seconds (healthy)
# aads-frontend         Up 30 seconds (healthy)
# aads-postgres         Up 45 seconds
# aads-redis            Up 45 seconds
# ...

# Check logs for errors
docker-compose logs -f backend frontend

# Check frontend build includes latest fixes
docker-compose exec frontend ls -lh /usr/share/nginx/html/assets/

# Should show: index-B5pCMzj8.js or similar (new hash)
```

---

## ðŸ”§ Advanced Update Options

### Option A: Update Without Stopping (Zero Downtime)
```bash
# Build new images first
docker-compose build --no-cache

# Rolling update (one service at a time)
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend

# Verify each before proceeding
docker-compose ps
```

### Option B: Complete Clean Rebuild
```bash
# Warning: This removes volumes (data loss!)
docker-compose down -v

# Remove all AADS images
docker images | grep aads | awk '{print $3}' | xargs docker rmi -f

# Remove build cache
docker builder prune -af

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

**âš ï¸ USE WITH CAUTION:** This deletes all data (databases, logs, etc.)

### Option C: Update Production with Downtime Window
```bash
# 1. Export data first
docker-compose exec postgres pg_dump -U aads aads > backup_$(date +%Y%m%d).sql
docker-compose exec influxdb influx backup /tmp/backup
docker cp aads-influxdb:/tmp/backup ./influx_backup_$(date +%Y%m%d)

# 2. Stop everything
docker-compose down

# 3. Rebuild
docker-compose build --no-cache

# 4. Start and verify
docker-compose up -d
docker-compose logs -f

# 5. If issues occur, restore backup
# docker-compose exec postgres psql -U aads aads < backup_YYYYMMDD.sql
```

---

## ðŸ³ Docker Compose Commands Cheat Sheet

### Build Commands
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build frontend

# Build without cache
docker-compose build --no-cache

# Build with progress output
docker-compose build --progress=plain
```

### Start/Stop Commands
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Stop all services
docker-compose down

# Stop and remove volumes (âš ï¸ DATA LOSS)
docker-compose down -v

# Restart specific service
docker-compose restart backend
```

### Monitoring Commands
```bash
# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 frontend

# Check container status
docker-compose ps

# Check resource usage
docker stats aads-backend aads-frontend
```

### Maintenance Commands
```bash
# Execute command in container
docker-compose exec backend python -m app.main

# Open shell in container
docker-compose exec backend /bin/sh
docker-compose exec frontend /bin/sh

# View container details
docker-compose exec backend env
```

---

## ðŸ“‹ Post-Update Verification Checklist

### Frontend Checks
```bash
# 1. Check build hash changed (confirms new build)
curl -s http://localhost:3000 | grep "index-"
# Should show: index-B5pCMzj8.js (new hash)

# 2. Check CSS includes gauge styles
docker-compose exec frontend cat /usr/share/nginx/html/assets/*.css | grep "gauge-widget"
# Should return CSS for gauges

# 3. Test frontend loads
curl -s http://localhost:3000 | grep "AADS"
# Should return HTML with "AADS" title
```

### Backend Checks
```bash
# 1. Check health endpoint
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# 2. Check API docs load
curl -s http://localhost:8000/docs | head -20
# Should return Swagger UI HTML

# 3. Test NAVI endpoint
curl -X POST http://localhost:8000/api/v1/navi/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
# Should return JSON response (may be 503 if Ollama not ready)
```

### Database Checks
```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U aads
# Should return: accepting connections

# Check Redis
docker-compose exec redis redis-cli ping
# Should return: PONG

# Check InfluxDB
curl http://localhost:8086/health
# Should return: {"status":"pass"}
```

### Service Connectivity
```bash
# Check all services respond
docker-compose ps | grep "Up"
# All should show "Up (healthy)" or "Up"

# Check network connectivity
docker-compose exec backend ping -c 1 postgres
docker-compose exec backend ping -c 1 redis
docker-compose exec backend ping -c 1 influxdb
```

---

## ðŸ”¥ Troubleshooting

### Issue: Build Fails
**Symptoms:** `docker-compose build` exits with errors

**Solutions:**
```bash
# 1. Check Docker daemon running
docker ps

# 2. Free up disk space
docker system prune -a

# 3. Check Dockerfile syntax
docker-compose config

# 4. Build with verbose output
docker-compose build --progress=plain --no-cache 2>&1 | tee build.log
```

### Issue: Container Won't Start
**Symptoms:** Container exits immediately or keeps restarting

**Solutions:**
```bash
# 1. Check logs for errors
docker-compose logs backend

# 2. Check environment variables
docker-compose config

# 3. Verify dependencies are running
docker-compose ps postgres redis influxdb

# 4. Check port conflicts
netstat -tulpn | grep -E ':(8000|3000|5432|6379|8086)'

# 5. Start with manual command
docker-compose run --rm backend /bin/sh
# Then manually run: uvicorn app.main:app --host 0.0.0.0
```

### Issue: Frontend Shows Old Version
**Symptoms:** React Error #31 still occurring after rebuild

**Solutions:**
```bash
# 1. Hard refresh browser
# Ctrl+Shift+R (Windows/Linux)
# Cmd+Shift+R (Mac)

# 2. Clear browser cache completely

# 3. Verify new build
docker-compose exec frontend ls -l /usr/share/nginx/html/assets/
# Should show recent timestamp

# 4. Check nginx is serving new files
docker-compose exec frontend cat /usr/share/nginx/html/index.html | grep "index-"
# Should match latest build hash

# 5. Rebuild without cache
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Issue: Ollama Not Loading Models
**Symptoms:** NAVI returns 503 errors

**Solutions:**
```bash
# 1. Check Ollama is running
docker-compose exec navi ollama list

# 2. Pull llama model
docker-compose exec navi ollama pull llama3.2

# 3. Test Ollama directly
curl http://localhost:11434/api/tags

# 4. Check NVIDIA runtime (if using GPU)
docker run --rm --runtime=nvidia nvidia/cuda:11.0-base nvidia-smi
```

---

## ðŸŽ¯ Production Deployment Workflow

### Pre-Deployment
```bash
# 1. Backup current state
./scripts/backup.sh  # If you have one

# 2. Test build locally
docker-compose -f docker-compose.yml build --no-cache

# 3. Run tests (if any)
docker-compose run --rm backend pytest

# 4. Tag images
docker tag aads-backend:latest aads-backend:v4.2.0
docker tag aads-frontend:latest aads-frontend:v4.2.0
```

### Deployment
```bash
# 1. Pull latest code on server
cd /opt/aads
git pull origin main

# 2. Rebuild images
docker-compose build --no-cache

# 3. Start with health checks
docker-compose up -d
sleep 10

# 4. Verify health
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:3000

# 5. Check logs for errors
docker-compose logs --tail=100
```

### Post-Deployment
```bash
# 1. Monitor logs for 5 minutes
docker-compose logs -f --tail=50

# 2. Test critical paths
# - Frontend loads
# - NAVI responds
# - Gauges display
# - Signal K connects

# 3. Monitor resource usage
docker stats --no-stream

# 4. Document deployment
echo "$(date): Deployed v4.2.0 with React fixes" >> deployment.log
```

---

## ðŸ” Security Best Practices

### Update Secrets
```bash
# Generate new passwords
openssl rand -base64 32

# Update docker-compose.yml:
# - POSTGRES_PASSWORD
# - MINIO_ROOT_PASSWORD
# - INFLUXDB_INIT_PASSWORD
# - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN
```

### Scan Images for Vulnerabilities
```bash
# Install trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan images
trivy image aads-backend:latest
trivy image aads-frontend:latest

# Auto-fix with dependabot or renovate
```

### Limit Container Resources
Add to `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

---

## ðŸ“Š Monitoring After Update

### Check Container Health
```bash
# Every 30 seconds for 5 minutes
watch -n 30 'docker-compose ps'

# Check health endpoints
watch -n 10 'curl -s http://localhost:8000/health && curl -s http://localhost:3000'
```

### Monitor Logs
```bash
# Combined logs
docker-compose logs -f --tail=20

# Error logs only
docker-compose logs -f | grep -i error

# Specific service
docker-compose logs -f backend | grep -E "(ERROR|WARNING)"
```

### Resource Monitoring
```bash
# Real-time stats
docker stats

# Historical metrics (if using Prometheus/Grafana)
# Access: http://localhost:3001/grafana
```

---

## âœ… Update Complete Checklist

After running the update, verify:

- [ ] All containers show "Up (healthy)" or "Up"
- [ ] Frontend displays without React Error #31
- [ ] Gauges render with proper CSS styling
- [ ] NAVI chat works without crashes
- [ ] Dashboard position displays correctly
- [ ] Signal K connection established
- [ ] Backend health check returns 200
- [ ] Logs show no critical errors
- [ ] Resource usage is normal (<80% CPU/Memory)
- [ ] All API endpoints respond

---

## ðŸŽ‰ Success Criteria

Your update is successful when:

1. âœ… Build hash changed (e.g., `index-B5pCMzj8.js`)
2. âœ… CSS size increased (~39KB vs ~37KB) - gauge styles added
3. âœ… No React Error #31 in browser console
4. âœ… All 4 gauges render properly
5. âœ… NAVI chat works
6. âœ… All containers healthy
7. âœ… No errors in logs

---

**Last Updated:** 2026-01-23
**System Version:** AADS PRO v4.2.0-JETSON
**Docker Compose Version:** 3.8+
**Includes:** All React Error #31 fixes + UI scale improvements

