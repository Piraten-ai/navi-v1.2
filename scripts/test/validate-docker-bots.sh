#!/bin/bash
# Docker bots validation script
# Validates Docker and CI/CD configurations

set -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Validating Docker and GitHub Actions configurations..."
echo "======================================================"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

have_cmd() { command -v "$1" >/dev/null 2>&1; }

yaml_check() {
  local file="$1"
  if ! have_cmd python3; then
    return 2
  fi
  python3 - "$file" <<'PY'
import sys
try:
    import yaml
except Exception:
    sys.exit(2)

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    yaml.safe_load(f)
PY
}

echo "Checking Docker Compose files..."
if have_cmd docker; then
    for file in docker-compose.yml docker-compose.dev.yml docker-compose.pi.yml; do
        if docker compose -f "$file" config >/dev/null 2>&1; then
            echo -e "${GREEN}OK${NC} $file is valid"
            ((PASS++))
        else
            echo -e "${RED}FAIL${NC} $file has errors"
            ((FAIL++))
        fi
    done
else
    echo -e "${YELLOW}WARN${NC} docker not found, skipping compose checks"
    ((WARN++))
fi
echo ""

echo "Checking Dockerfiles (hadolint via Docker)..."
if have_cmd docker; then
    for dockerfile in backend/Dockerfile backend/Dockerfile.dev frontend/Dockerfile frontend/Dockerfile.dev; do
        if [ -f "$dockerfile" ]; then
            if docker run --rm -i hadolint/hadolint < "$dockerfile" >/dev/null 2>&1; then
                echo -e "${GREEN}OK${NC} $dockerfile passes hadolint"
                ((PASS++))
            else
                echo -e "${YELLOW}WARN${NC} $dockerfile has hadolint warnings"
                ((WARN++))
            fi
        else
            echo -e "${RED}FAIL${NC} $dockerfile not found"
            ((FAIL++))
        fi
    done
else
    echo -e "${YELLOW}WARN${NC} docker not found, skipping hadolint checks"
    ((WARN++))
fi
echo ""

echo "Checking GitHub Actions workflows..."
for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        yaml_check "$workflow"
        case $? in
            0)
                echo -e "${GREEN}OK${NC} $workflow has valid YAML syntax"
                ((PASS++))
                ;;
            2)
                echo -e "${YELLOW}WARN${NC} PyYAML not available; skipping YAML check for $workflow"
                ((WARN++))
                ;;
            *)
                echo -e "${RED}FAIL${NC} $workflow has YAML syntax errors"
                ((FAIL++))
                ;;
        esac
    fi
done
echo ""

echo "Checking Dependabot configuration..."
if [ -f ".github/dependabot.yml" ]; then
    yaml_check ".github/dependabot.yml"
    case $? in
        0)
            echo -e "${GREEN}OK${NC} dependabot.yml has valid YAML syntax"
            ((PASS++))
            ;;
        2)
            echo -e "${YELLOW}WARN${NC} PyYAML not available; skipping dependabot.yml check"
            ((WARN++))
            ;;
        *)
            echo -e "${RED}FAIL${NC} dependabot.yml has YAML syntax errors"
            ((FAIL++))
            ;;
    esac
else
    echo -e "${RED}FAIL${NC} dependabot.yml not found"
    ((FAIL++))
fi
echo ""

echo "Checking for obsolete version fields..."
if ! grep -q "^version:" docker-compose.yml 2>/dev/null \
   && ! grep -q "^version:" docker-compose.dev.yml 2>/dev/null \
   && ! grep -q "^version:" docker-compose.pi.yml 2>/dev/null; then
    echo -e "${GREEN}OK${NC} No obsolete version fields in compose files"
    ((PASS++))
else
    echo -e "${YELLOW}WARN${NC} Found obsolete version fields in compose files"
    ((WARN++))
fi
echo ""

echo "======================================================"
echo "Validation Summary:"
echo -e "${GREEN}Passed${NC}: $PASS"
echo -e "${YELLOW}Warnings${NC}: $WARN"
echo -e "${RED}Failed${NC}: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}All critical checks passed.${NC}"
    exit 0
else
    echo -e "${RED}Some critical checks failed. Review the errors above.${NC}"
    exit 1
fi
