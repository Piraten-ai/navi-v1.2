**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# AADS Frontend

React + TypeScript frontend for Arctic Autonomous Defense System.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Utility-first CSS
- **WebSocket** - Real-time communication

## Features

- Arctic HUD theme (toxic green, arctic blue, titan grey)
- Battle mode toggle (press 'B' key)
- 8 navigation modules
- Real-time WebSocket connection
- Responsive design
- Production-ready Docker builds

## Development

```bash
npm install
npm run dev
```

Access at http://localhost:3000

## Production

```bash
npm run build
npm run preview
```

## Docker

### Development
```bash
docker build -f Dockerfile.dev -t aads-frontend-dev .
docker run -p 3000:3000 aads-frontend-dev
```

### Production
```bash
docker build -t aads-frontend .
docker run -p 80:80 aads-frontend
```

## Environment Variables

Create `.env` file:
```
VITE_API_URL=http://localhost:8000
```

## Modules

1. **Map** - Position display (NMEA data)
2. **Instruments** - HUD gauges (speed, heading, depth)
3. **Vakten** - Vision detection interface
4. **Navi** - AI chat assistant (Claude)
5. **Navigator** - NAVTEX message display
6. **Legen** - Medical records system
7. **Psykologen** - Mental health tracking
8. **Ingenioren** - Engineering diagnostics

## Theme

- **Arctic Mode** (default): Green (#00ff41) + Blue (#00d4ff)
- **Battle Mode** (press 'B'): Red (#ff2020)
- Industrial military aesthetic
- Scanline animations
- Grid background
- Glowing effects

## WebSocket API

Connect to `ws://localhost:8000/ws`

Message format:
```json
{
  "type": "nmea|chat|alert",
  "data": {},
  "timestamp": "ISO8601"
}
```

