#!/bin/bash
# Quick fix and rebuild script for the Raspberry Pi frontend

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Fixing TypeScript configuration..."

if [ ! -d "frontend" ]; then
    echo "frontend/ not found. Run from the repo root."
    exit 1
fi

cd frontend
cat > tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"],
  "exclude": ["src/test/**/*", "**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF
cd ..

echo "TypeScript config updated"
echo ""
echo "Rebuilding frontend image..."

docker compose -f docker-compose.pi.yml down
docker compose -f docker-compose.pi.yml build --no-cache frontend
docker compose -f docker-compose.pi.yml up -d frontend

echo ""
echo "Rebuild complete."
echo "Frontend: http://localhost:3000"
