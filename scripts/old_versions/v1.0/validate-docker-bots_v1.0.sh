#!/bin/bash

# Docker Bots Validation Script
# Validates all Docker and CI/CD configurations

set -euo pipefail

echo "🔍 Validating Docker and GitHub Actions Configurations..."
echo "=========================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation results
PASS=0
FAIL=0
WARN=0

# Check 1: Docker Compose Files
echo "📦 Checking Docker Compose Files..."
if docker compose -f docker-compose.yml config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ docker-compose.yml is valid${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ docker-compose.yml has errors${NC}"
    ((FAIL++))
fi

if docker compose -f docker-compose.dev.yml config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ docker-compose.dev.yml is valid${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ docker-compose.dev.yml has errors${NC}"
    ((FAIL++))
fi
echo ""

# Check 2: Dockerfile Syntax
echo "🐳 Checking Dockerfiles..."
for dockerfile in backend/Dockerfile backend/Dockerfile.dev frontend/Dockerfile frontend/Dockerfile.dev; do
    if [ -f "$dockerfile" ]; then
        if docker run --rm -i hadolint/hadolint < "$dockerfile" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $dockerfile passes hadolint${NC}"
            ((PASS++))
        else
            echo -e "${YELLOW}⚠️  $dockerfile has warnings (non-critical)${NC}"
            ((WARN++))
        fi
    else
        echo -e "${RED}❌ $dockerfile not found${NC}"
        ((FAIL++))
    fi
done
echo ""

# Check 3: GitHub Actions Workflows
echo "⚙️  Checking GitHub Actions Workflows..."
for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        # Basic YAML syntax check
        if python3 -c "import yaml; f = open(\"$workflow\"); yaml.safe_load(f); f.close()" 2>/dev/null; then
            echo -e "${GREEN}✅ $workflow has valid YAML syntax${NC}"
            ((PASS++))
        else
            echo -e "${RED}❌ $workflow has YAML syntax errors${NC}"
            ((FAIL++))
        fi
    fi
done
echo ""

# Check 4: Dependabot Configuration
echo "🤖 Checking Dependabot Configuration..."
if [ -f ".github/dependabot.yml" ]; then
    if python3 -c "import yaml; f = open(\".github/dependabot.yml\"); yaml.safe_load(f); f.close()" 2>/dev/null; then
        echo -e "${GREEN}✅ dependabot.yml has valid YAML syntax${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ dependabot.yml has YAML syntax errors${NC}"
        ((FAIL++))
    fi
else
    echo -e "${RED}❌ dependabot.yml not found${NC}"
    ((FAIL++))
fi
echo ""

# Check 5: Version Field Removed
echo "🔄 Checking for obsolete version fields..."
if ! grep -q "^version:" docker-compose.yml && ! grep -q "^version:" docker-compose.dev.yml; then
    echo -e "${GREEN}✅ Obsolete version fields removed from docker-compose files${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  Found obsolete version fields in docker-compose files${NC}"
    ((WARN++))
fi
echo ""

# Summary
echo "=========================================================="
echo "📊 Validation Summary:"
echo -e "${GREEN}✅ Passed: $PASS${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARN${NC}"
echo -e "${RED}❌ Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some critical checks failed. Please review the errors above.${NC}"
    exit 1
fi
