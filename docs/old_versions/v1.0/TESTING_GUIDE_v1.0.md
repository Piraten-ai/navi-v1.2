# Testing Guide - Frontend Improvements

## Quick Start Testing

### Prerequisites
- Node.js 18+ installed
- Python 3.10+ installed
- Backend and Frontend code pulled

---

## Test 1: Signal K Integration

### Start Backend (Terminal 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

### Open Browser
```
http://localhost:3000
```

### Test Steps
1. Click **DASHBOARD** module (📊 icon at bottom)
2. **Verify:**
   - ✅ Connection status: "Connected" (green)
   - ✅ Position displays: e.g., "78.2232°N, 15.6267°E"
   - ✅ Timestamp updates every 1-2 seconds
   - ✅ Four gauges show data:
     - SPEED (0-30 KN)
     - HEADING (0-360°)
     - DEPTH (0-200 M)
     - TEMP (-40 to 20°C)

3. **Check Mock Data:**
   - Backend runs in mock mode by default
   - Position starts around 78.22°N, 15.62°E (Svalbard, Arctic)
   - Speed varies 8-12 knots
   - Depth around 150 meters
   - Temperature around -8°C

### Expected Console Output (Backend)
```
INFO:     Application startup complete
INFO:     WebSocket connection established
INFO:     Broadcasting Signal K data...
```

### Troubleshooting
**Problem:** "Not connected to Signal K"
- Check backend is running on port 8000
- Check browser console for WebSocket errors
- Verify `VITE_WS_URL=ws://localhost:8000/ws` in frontend/.env

**Problem:** No data updating
- Check backend logs for errors
- Ensure Signal K module is enabled
- Try refreshing browser (Ctrl+R)

---

## Test 2: AI Chat (Navi)

### Configure Backend AI
Choose ONE option:

**Option A: Claude API (Recommended)**
```bash
# In backend/.env
ANTHROPIC_API_KEY=your_claude_api_key_here
NAVI_LLM_PROVIDER=anthropic
NAVI_MODEL=claude-3-5-sonnet-20241022
```

**Option B: Ollama (Local)**
```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3.2

# In backend/.env
NAVI_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
NAVI_MODEL=llama3.2
```

### Restart Backend
```bash
# Ctrl+C to stop, then:
uvicorn app.main:app --reload
```

### Test Steps
1. Click **NAVI** module (💬 icon at bottom)
2. **Verify UI shows:**
   ```
   MODEL: AI Assistant (Claude/Ollama)
   STATUS: READY
   MESSAGES: 0
   CONTEXT: Arctic Navigation System
   ```

3. **Test normal message:**
   - Type: "What is the current weather in the Arctic?"
   - Press Enter or click SEND
   - Wait 2-5 seconds
   - **Verify:**
     - ✅ Your message appears with [USER] tag
     - ✅ AI response appears with [ASSISTANT] tag
     - ✅ "HEY! LISTEN!" prompt shows briefly (if enabled in settings)
     - ✅ Timestamp shows next to each message

4. **Test character limit:**
   - Type 900 characters
   - **Verify:** Counter shows "900/1000 CHARACTERS" in orange
   - Type 101+ more characters
   - **Verify:** Error message appears

5. **Test error handling:**
   - Stop backend (Ctrl+C)
   - Try sending message
   - **Verify error message:**
     ```
     ERROR: Cannot connect to backend server.
     Please ensure the backend is running on port 8000.
     ```

### Expected Console Output (Backend with Claude)
```
INFO: Navi chat request received
INFO: Using Anthropic Claude API
INFO: Response generated in 1.23s
```

### Troubleshooting
**Problem:** "AI service unavailable"
- Check API key is valid (Claude)
- Check Ollama is running: `ollama list`
- Check backend logs for specific errors

**Problem:** Slow responses
- Claude API: Normal (1-3 seconds)
- Ollama: Depends on hardware (3-10 seconds)
- Check backend isn't rate-limited

---

## Test 3: Module Icons & Navigation

### Test Steps
1. Look at bottom navigation bar
2. **Verify all 10 icons visible:**
   - 🤖 AUTONOMY
   - 📊 DASHBOARD
   - 🗺️ MAP
   - ⚙️ INSTRUMENTS
   - 👁️ VAKTEN
   - 💬 NAVI
   - 📡 NAVIGATOR
   - ⚕️ LEGEN
   - 🧠 PSYKOLOGEN
   - 🔧 INGENIOREN

3. Click each icon
4. **Verify:**
   - ✅ Icon highlights when active
   - ✅ Module content loads
   - ✅ No console errors

### Troubleshooting
**Problem:** Icons show as boxes/question marks
- Browser emoji support issue
- Fallback to first letter should work
- Try different browser (Chrome, Firefox, Edge)

---

## Test 4: Settings & Configuration

### Test Steps
1. Click **⚙️ SETTINGS** button (top right)
2. **Verify settings panel opens:**
   - Battle Mode Key
   - Idle Timeout
   - Theme selection
   - Navi Prompts toggle
   - Widget configuration

3. **Test Navi Prompts toggle:**
   - Turn OFF "Enable Navi Prompts"
   - Go to NAVI module
   - Send a message
   - **Verify:** NO "HEY! LISTEN!" popup shows

4. **Test Battle Mode:**
   - Press **B** key
   - **Verify:**
     - Colors change from cyan to red
     - "⚠ BATTLE MODE ACTIVE ⚠" banner shows
     - All modules render correctly

---

## Test 5: Real Signal K Server (Optional)

If you have a real Signal K server:

### Configure Backend
```bash
# In backend/.env
SIGNALK_WS_URL=ws://YOUR_SIGNALK_IP:3001/signalk/v1/stream
SIGNALK_HTTP_URL=http://YOUR_SIGNALK_IP:3001
SIGNALK_MOCK_MODE=false
```

### Test Steps
1. Restart backend
2. Check backend logs: "Connected to Signal K server"
3. Go to DASHBOARD
4. **Verify:** Real vessel data appears (not mock data)

### Verify Real Data
- Position changes as vessel moves
- Speed matches vessel's actual SOG
- Heading matches compass
- Depth matches depth sounder

---

## Performance Testing

### Check Bundle Size
```bash
cd frontend
npm run build
```

**Expected output:**
```
dist/assets/index-abc123.js    216 KB │ gzip: 69.6 KB
dist/assets/index-def456.css    13 KB │ gzip: 3.3 KB
```

### Check Load Time
1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh page (Ctrl+R)
4. **Verify:**
   - Total load < 1 second on good connection
   - All resources load successfully
   - No 404 errors

### Check WebSocket
1. Open browser DevTools (F12)
2. Go to Network tab → WS filter
3. Click on `ws://localhost:8000/ws`
4. **Verify:**
   - Connection status: 101 Switching Protocols
   - Messages tab shows Signal K data flowing
   - ~1-2 messages per second

---

## Automated Testing (Future)

### Unit Tests (Not yet implemented)
```bash
cd frontend
npm test
```

### E2E Tests (Not yet implemented)
```bash
cd frontend
npm run test:e2e
```

---

## Troubleshooting Common Issues

### Issue: Frontend won't start
```
Error: Cannot find module 'vite'
```
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: Backend won't start
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: WebSocket disconnects constantly
**Possible causes:**
- Firewall blocking port 8000
- Backend crashed (check logs)
- Proxy/VPN interfering

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check WebSocket endpoint
curl http://localhost:8000/ws
# Should return "426 Upgrade Required"
```

### Issue: AI responses are errors
**Check backend logs for:**
```
ERROR: Anthropic API key not configured
```
**Solution:** Add `ANTHROPIC_API_KEY` to backend/.env

```
ERROR: Ollama service not available
```
**Solution:** Start Ollama: `ollama serve`

---

## Success Criteria

✅ **Signal K Integration:**
- Dashboard shows real-time position
- Gauges update every 1-2 seconds
- No console errors

✅ **AI Chat:**
- Messages send and receive successfully
- Errors show specific guidance
- Character counter works

✅ **GUI:**
- All 10 module icons visible
- Navigation smooth
- No visual glitches

✅ **Performance:**
- Page loads < 1 second
- WebSocket stable
- No memory leaks

---

## Next: Production Deployment

See `SIGNALK_INTEGRATION.md` for production setup including:
- Docker deployment
- Nginx configuration
- SSL/TLS setup
- Monitoring and logging

---

**Questions?** Check `FRONTEND_IMPROVEMENTS_2026-01-23.md` for detailed documentation.
