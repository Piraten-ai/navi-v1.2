# Deploy NAVI to Jetson - Automated Script
# Run this on Windows PowerShell

$JETSON_IP = "192.168.39.196"
$JETSON_USER = "navi"
$JETSON_PATH = "~/navi-main"

Write-Host "Deploying NAVI to Jetson at $JETSON_IP..." -ForegroundColor Cyan

# Step 1: Copy all files
Write-Host "Copying files to Jetson..." -ForegroundColor Yellow
scp docker-compose.yml "${JETSON_USER}@${JETSON_IP}:${JETSON_PATH}/"
scp -r backend "${JETSON_USER}@${JETSON_IP}:${JETSON_PATH}/"
scp -r frontend "${JETSON_USER}@${JETSON_IP}:${JETSON_PATH}/"
scp -r data "${JETSON_USER}@${JETSON_IP}:${JETSON_PATH}/"
scp .env.example "${JETSON_USER}@${JETSON_IP}:${JETSON_PATH}/"

# Step 2: Stop old containers, build and start new ones
Write-Host "Rebuilding and restarting containers on Jetson..." -ForegroundColor Yellow
ssh "${JETSON_USER}@${JETSON_IP}" "cd ${JETSON_PATH}; docker-compose down; docker-compose build; docker-compose up -d"

# Step 3: Wait and check status
Write-Host "Waiting 10 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Step 4: Check health
Write-Host "Checking deployment status..." -ForegroundColor Green
ssh "${JETSON_USER}@${JETSON_IP}" "cd ${JETSON_PATH}; docker-compose ps"

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Frontend: http://${JETSON_IP}:3000" -ForegroundColor Cyan
Write-Host "Backend: http://${JETSON_IP}:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://${JETSON_IP}:8000/docs" -ForegroundColor Cyan
