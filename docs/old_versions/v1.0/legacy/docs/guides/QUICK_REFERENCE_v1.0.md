**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# NAVI Settings & Dashboard - Quick Reference

## ðŸš€ Deploy New Features

On your Jetson, run:
```bash
cd ~/navi-main
chmod +x update-frontend.sh
./update-frontend.sh
```

Wait for "UPDATE COMPLETE!" message, then open:
**http://192.168.39.196:3000**

---

## âš™ï¸ Settings Panel

**Access:** Click âš™ï¸ button (top-right corner)

**What you can configure:**
- âœ… Hey Listen! prompts (on/off)
- ðŸ–¥ï¸ Screensaver settings
- ðŸŽ¨ Theme (Arctic Cyan / Battle Red)
- âš”ï¸ Battle mode activation key
- ðŸ”„ Reset to defaults

**Settings persist automatically** - no save button needed!

---

## ðŸ“Š Dashboard Module

**Access:** Click "DASHBOARD" in bottom module bar

**What you get:**
- ðŸš¤ **Speed gauge** - Vessel speed in knots
- ðŸ§­ **Heading gauge** - Compass bearing in degrees
- ðŸŒŠ **Depth gauge** - Water depth in meters
- ðŸŒ¡ï¸ **Temperature gauge** - External temp in Â°C

All gauges are color-coded:
- ðŸ”´ Red = >80% of max (warning)
- ðŸŸ  Orange = >60% of max (caution)
- ðŸ”µ Cyan = Normal range

---

## ðŸ’¬ Hey Listen! System

**The Soul of the Project** âœ¨

When NAVI has something important to say, a floating alert appears:
- âš ï¸ Shows random prompts like "HEY! LISTEN!" or "WATCH OUT!"
- ðŸŽ¯ Bounces and glows to grab your attention
- â±ï¸ Auto-dismisses after 3 seconds
- ðŸ‘† Click to dismiss immediately
- âš™ï¸ Can be disabled in settings if you prefer quiet operation

---

## âš”ï¸ Battle Mode

**Quick Toggle:** Press **B** key (or your configured key)

Instantly switches between:
- ðŸ”µ **Arctic Cyan** - Default operating mode
- ðŸ”´ **Battle Red** - High-intensity alert mode

---

## ðŸ§­ All 8 Modules

Your NAVI system includes:
1. **DASHBOARD** - Customizable gauges (NEW!)
2. **MAP** - GPS and navigation
3. **INSTRUMENTS** - Sensor displays
4. **VAKTEN** - Watch system
5. **NAVI** - AI Assistant with Hey Listen!
6. **NAVIGATOR** - Route planning
7. **LEGEN** - Health monitoring
8. **PSYKOLOGEN** - Psychological support

---

## ðŸ”§ If Something Breaks

**Frontend not loading?**
```bash
docker-compose restart frontend
```

**Need to see logs?**
```bash
docker-compose logs -f frontend
```

**Nuclear option (rebuild everything)?**
```bash
docker-compose down
docker-compose up -d --build
```

**Settings acting weird?**
- Open browser console (F12)
- Go to Application â†’ Local Storage
- Delete `aads-settings` key
- Refresh page

---

## ðŸ“ Quick Tests

### Test Settings
1. Click âš™ï¸ button
2. Toggle "Hey Listen!" off
3. Close settings
4. Refresh page
5. Open settings again - should still be off âœ…

### Test Hey Listen
1. Enable "Hey Listen!" in settings
2. Go to NAVI module
3. Send a message: "hello"
4. When NAVI responds â†’ floating alert appears âœ…

### Test Dashboard
1. Click "DASHBOARD" module
2. Should see 4 gauges with values âœ…
3. Each gauge should have:
   - Label at top
   - Big number in center
   - Unit (KN, Â°, M, Â°C)
   - Min/max at bottom

### Test Battle Mode
1. Press **B** key
2. Theme should flip to red âœ…
3. Press **B** again
4. Back to cyan âœ…

---

## ðŸŽ¯ What's Working

âœ… Settings system with localStorage
âœ… Hey Listen! prompts (toggleable)
âœ… Dashboard with 4 gauges
âœ… All original 8 modules
âœ… Battle mode toggle
âœ… Theme switching
âœ… Settings persistence

## ðŸ”® What's Next

â³ Connect gauges to real sensor data
â³ Add drag-and-drop widget repositioning
â³ Add more widget types (graphs, charts)
â³ Create dashboard layout presets
â³ Widget configuration (custom min/max, colors)

---

## ðŸ’¾ Current Status

**Deployment:** Code pushed to GitHub âœ…
**Jetson Status:** Awaiting `update-frontend.sh` run
**Testing:** Local testing complete, Jetson deployment pending

**When you deploy, test these 4 things:**
1. âš™ï¸ Settings button works
2. ðŸ“Š Dashboard shows gauges
3. ðŸ’¬ Hey Listen appears (if enabled)
4. âš”ï¸ Battle mode toggles with B key

---

**Need help?** Check [SETTINGS_DASHBOARD_SUMMARY.md](SETTINGS_DASHBOARD_SUMMARY.md) for full details.

**Happy navigating! ðŸš¢â„ï¸**

