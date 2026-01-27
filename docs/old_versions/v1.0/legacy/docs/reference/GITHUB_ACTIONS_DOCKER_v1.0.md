**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# GitHub Actions CI/CD Documentation

This document describes the GitHub Actions workflows configured for the AADS project, with a focus on Docker-based builds and deployments.

## Workflows Overview

### 1. **ci-cd.yml** - Main CI/CD Pipeline
**Triggers:** Push to main/develop, PRs, version tags

**Jobs:**
- **test**: Runs Python (pytest) and Node.js tests with coverage reporting
- **build-backend**: Builds and pushes backend Docker image to GHCR
- **build-frontend**: Builds and pushes frontend Docker image to GHCR
- **security-scan**: Runs Trivy vulnerability scanner on built images
- **deploy-staging**: Deploys to staging environment (develop branch only)
- **deploy-production**: Deploys to production (version tags only)

**Key Features:**
- Multi-platform builds (amd64, arm64)
- GitHub Actions cache for faster builds
- Automatic semantic versioning based on tags
- CodeCov integration for test coverage

### 2. **docker-build.yml** - Docker-Specific CI
**Triggers:** Push/PR to main/develop affecting Docker files

**Jobs:**
- **docker-lint**: Runs Hadolint on all Dockerfiles
- **build-test**: Builds images locally and runs basic tests
- **build-multiarch**: Builds multi-architecture images
- **compose-test**: Validates docker-compose configurations
- **image-size**: Analyzes and reports image sizes

**Key Features:**
- Hadolint for Dockerfile best practices
- Local build testing before push
- Security scanning with Trivy
- Image size analysis

### 3. **integration-tests.yml** - Full Stack Testing
**Triggers:** Push/PR to main/develop, nightly schedule

**Jobs:**
- **integration-tests**: Runs full stack with docker-compose
- **docker-compose-prod-test**: Validates production compose file
- **smoke-test**: Quick sanity checks on PRs

**Key Features:**
- Full service orchestration testing
- Health check validation
- WebSocket connection testing
- Automatic cleanup

## Docker Build Strategy

### Multi-Stage Builds
Both backend and frontend use optimized multi-stage builds:

**Backend:**
```dockerfile
# Build stage: Compile dependencies
# Runtime stage: Minimal production image
```

**Frontend:**
```dockerfile
# Builder stage: npm build with Vite
# Runtime stage: nginx serving static files
```

### Build Caching
We use multiple caching strategies:

1. **GitHub Actions Cache** (`type=gha`)
   - Caches Docker layers between workflow runs
   - Significantly speeds up rebuilds

2. **BuildKit Cache Mounts**
   - Caches pip/npm downloads
   - Prevents re-downloading dependencies

3. **Layer Optimization**
   - Dependencies installed before application code
   - Maximizes cache hit rate

### Security Best Practices

1. **Non-Root Users**
   - Backend runs as `appuser` (UID 1000)
   - Frontend runs as `nginx` user

2. **Vulnerability Scanning**
   - Trivy scans on every build
   - SARIF reports uploaded to GitHub Security

3. **Minimal Base Images**
   - Alpine Linux where possible
   - Slim variants for Python

4. **Dependency Updates**
   - Dependabot configured for Docker, pip, npm, and GitHub Actions
   - Weekly automated updates

## Environment Configuration

### Secrets Required

For full deployment, configure these secrets:

- `GITHUB_TOKEN`: Auto-provided for GHCR
- `KUBECONFIG_STAGING`: Kubernetes config for staging
- `KUBECONFIG_PRODUCTION`: Kubernetes config for production

### Environment Variables

**Development (docker-compose.dev.yml):**
- `DEV_MODE=true`
- `MOCK_CAMERA=true`
- SQLite database (no external DB needed)

**Production (docker-compose.yml):**
- PostgreSQL, InfluxDB, Redis, MinIO, Ollama
- Full GPU support for AI models
- Persistent volumes for data

## Image Registry

Images are pushed to GitHub Container Registry (GHCR):

```
ghcr.io/<OWNER>/<REPO>/backend:latest
ghcr.io/<OWNER>/<REPO>/frontend:latest
```

**Tag Strategy:**
- `latest`: Latest build from main branch
- `develop`: Latest build from develop branch
- `v1.2.3`: Semantic version tags
- `main-abc123`: Branch + commit SHA

## Running Locally

### Pull Pre-Built Images
```bash
docker pull ghcr.io/<OWNER>/<REPO>/backend:latest
docker pull ghcr.io/<OWNER>/<REPO>/frontend:latest
```

### Build Locally
```bash
# Development build
docker compose -f docker-compose.dev.yml build

# Production build
docker compose -f docker-compose.yml build
```

### Run Integration Tests
```bash
# Start services
docker compose -f docker-compose.dev.yml up -d

# Wait for health checks
until curl -f http://localhost:8000/health; do sleep 2; done

# Run tests
docker compose exec backend pytest tests/ -v

# Cleanup
docker compose down -v
```

## Optimization Tips

### Reduce Build Time
1. Use `.dockerignore` files (already configured)
2. Order Dockerfile layers from least to most frequently changed
3. Use build cache mounts for package managers
4. Leverage multi-stage builds

### Reduce Image Size
1. Use Alpine base images where possible
2. Remove build dependencies in production stage
3. Use `.dockerignore` to exclude unnecessary files
4. Combine RUN commands to reduce layers

### Improve Security
1. Run as non-root user (already implemented)
2. Scan images regularly (automated with Trivy)
3. Keep base images updated (Dependabot configured)
4. Use specific version tags, not `latest`

## Monitoring and Debugging

### View Workflow Logs
1. Go to **Actions** tab in GitHub
2. Select the workflow run
3. Click on individual jobs to see logs

### Debug Failed Builds
```bash
# Reproduce locally
docker build -t test-build ./backend

# Check image layers
docker history test-build

# Inspect running container
docker run -it test-build sh
```

### Common Issues

**Problem:** Build timeout
**Solution:** Increase timeout in workflow or optimize Dockerfile

**Problem:** Cache not working
**Solution:** Check if file changes invalidate cache layers

**Problem:** Multi-arch build fails
**Solution:** Ensure QEMU is set up with `docker/setup-qemu-action`

## Deployment

### Staging Deployment
Automatically deploys when pushing to `develop` branch:
```bash
git push origin develop
```

### Production Deployment
Create and push a version tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers:
1. Full test suite
2. Multi-platform image builds
3. Security scanning
4. Kubernetes deployment to production
5. GitHub Release creation

## Best Practices

1. **Always test locally** before pushing
2. **Review Dependabot PRs** regularly
3. **Monitor security scan results** in GitHub Security tab
4. **Use semantic versioning** for releases
5. **Keep workflows updated** with latest action versions

## References

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [BuildKit Documentation](https://github.com/moby/buildkit)
- [Hadolint](https://github.com/hadolint/hadolint)
- [Trivy Scanner](https://github.com/aquasecurity/trivy)

