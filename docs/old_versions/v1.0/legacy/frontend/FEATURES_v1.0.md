**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# AADS Frontend Features

## ðŸŽ¨ Arctic HUD Theme
- **Toxic Green** (#00ff41) - Primary UI color
- **Arctic Blue** (#00d4ff) - Secondary accents
- **Titan Grey** (#2d3436) - Structural elements
- **Battle Mode** (#ff2020) - Press 'B' to toggle red theme
- Brutal, industrial, military aesthetic (Chuck Norris meets Guy Ritchie)
- Scanline CRT animation
- Grid background pattern
- Glowing text shadows
- Corner bracket decorations

## ðŸ› ï¸ Technology Stack
- **React 18** - Modern UI framework
- **TypeScript** - Type safety and better DX
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **WebSocket** - Real-time communication with backend
- **Axios** - HTTP client for API calls

## ðŸ“¡ Real-Time Features
- WebSocket connection with auto-reconnect
- NMEA data streaming (GPS, speed, heading)
- Real-time threat level monitoring
- System status indicators
- Connection status display

## ðŸ—ºï¸ Navigation Modules

### 1. Map
- Real-time GPS position display
- Latitude/Longitude coordinates
- Speed over ground
- True heading
- Last update timestamp

### 2. Instruments
- Speed gauge (knots)
- Heading gauge (degrees)
- Depth sounder (standby)
- System status terminal

### 3. Vakten (Vision Detection)
- 360Â° camera feed display
- AI detection log (YOLO v8)
- Manual scan trigger
- 80 detection classes
- Confidence threshold display

### 4. Navi (AI Assistant)
- Chat interface with Claude 3.5 Sonnet
- Message history
- Real-time responses
- System status display
- Error handling

### 5. Navigator (NAVTEX)
- Maritime safety messages
- Weather warnings
- Navigational warnings
- Priority-coded messages (urgent/important/routine)
- 518 kHz receiver status

### 6. Legen (Medical System)
- Medical records tracking
- Vital signs logging
- Injury documentation
- Medication records
- Emergency protocols

### 7. Psykologen (Mental Health)
- Crew wellness monitoring
- Mood tracking (good/neutral/poor)
- Stress level assessment (1-10)
- Wellness history
- Mental health resources

### 8. Ingenioren (Engineering)
- System diagnostics
- Component status monitoring
- Maintenance logging
- Warning indicators
- Critical alerts

## ðŸŽ® Interactive Features
- Battle mode toggle (press 'B' key)
- Module navigation system
- Threat level indicator
- Real-time status displays
- WebSocket connection indicator
- Responsive button states

## ðŸ³ Docker Support
- **Development**: Hot reload with Vite dev server
- **Production**: Optimized nginx-served static build
- Multi-stage builds for minimal image size
- nginx reverse proxy for API/WebSocket

## ðŸ“¦ Build & Deploy
- TypeScript compilation
- Vite bundling with code splitting
- CSS optimization with Tailwind
- Gzip compression
- Production-ready artifacts

## ðŸ”’ Type Safety
- Full TypeScript coverage
- Interface definitions for all data structures
- Type-safe WebSocket messages
- Type-safe API calls
- Strict mode enabled

## ðŸŽ¯ UX Features
- Keyboard shortcuts (B for battle mode)
- Hover effects on all interactive elements
- Active state indicators
- Loading states
- Error messages
- Responsive design
- Accessibility considerations

## ðŸš€ Performance
- Code splitting
- Lazy loading
- Optimized bundle size (~200KB JS, ~12KB CSS)
- Efficient re-renders with React hooks
- WebSocket connection pooling

