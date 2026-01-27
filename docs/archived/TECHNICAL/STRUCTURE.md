# Project Root - Clean Structure

## Essential Files (Root Level)

### Configuration
- `.env.development` - Development environment
- `.env.production` - Production environment
- `docker-compose.yml` - Main deployment config
- `docker-compose.dev.yml` - Development deployment

### Core Documentation
- `README.md` - Project overview
- `START_HERE.md` - Getting started guide
- `QUICK_REFERENCE.md` - Quick lookup guide
- `DOCUMENTATION_INDEX.md` - Documentation navigation

### Project Config
- `.github/` - GitHub Actions workflows
- `.vscode/` - IDE configuration
- `.gitignore` - Git ignore rules
- `aads-handover.code-workspace` - VSCode workspace

---

## Directories

### Source Code
- `backend/` - FastAPI backend
- `frontend/` - React frontend
- `navi/` - NAVI AI module

### Application Data
- `data/` - Application datasets
- `models/` - ML models (Ollama, Stable Diffusion, etc)
- `audio/` - Audio files

### Documentation
- `docs/` - Active documentation
- `docs/archived/` - Historical documentation (archived)

### Automation & Deployment
- `scripts/` - Shell and PowerShell scripts
- `deploy/` - Deployment tools

### System
- `.venv/` - Python virtual environment
- `.claude/` - Claude IDE cache
- `logs/` - Application logs

---

## Archive Contents

All historical documentation has been moved to `docs/archived/`:
- Completion reports and phase summaries
- Fix reports and updates
- Deployment guides and checklists
- Technical documentation and reports
- Testing guides and verification reports

See `docs/archived/INDEX.md` for full archive listing.
