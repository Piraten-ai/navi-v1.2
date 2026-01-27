# NAVI Settings & Dashboard - Quick Reference

## 🚀 Deploy New Features

On your Jetson, run:
```bash
cd ~/navi-main
chmod +x update-frontend.sh
./update-frontend.sh
```

Wait for "UPDATE COMPLETE!" message, then open:
**http://192.168.39.196:3000**

---

## ⚙️ Settings Panel

**Access:** Click ⚙️ button (top-right corner)

**What you can configure:**
- ✅ Hey Listen! prompts (on/off)
- 🖥️ Screensaver settings
- 🎨 Theme (Arctic Cyan / Battle Red)
- ⚔️ Battle mode activation key
- 🔄 Reset to defaults

**Settings persist automatically** - no save button needed!

---

## 📊 Dashboard Module

**Access:** Click "DASHBOARD" in bottom module bar

**What you get:**
- 🚤 **Speed gauge** - Vessel speed in knots
- 🧭 **Heading gauge** - Compass bearing in degrees
- 🌊 **Depth gauge** - Water depth in meters
- 🌡️ **Temperature gauge** - External temp in °C

All gauges are color-coded:
- 🔴 Red = >80% of max (warning)
- 🟠 Orange = >60% of max (caution)
- 🔵 Cyan = Normal range

---

## 💬 Hey Listen! System

**The Soul of the Project** ✨

When NAVI has something important to say, a floating alert appears:
- ⚠️ Shows random prompts like "HEY! LISTEN!" or "WATCH OUT!"
- 🎯 Bounces and glows to grab your attention
- ⏱️ Auto-dismisses after 3 seconds
- 👆 Click to dismiss immediately
- ⚙️ Can be disabled in settings if you prefer quiet operation

---

## ⚔️ Battle Mode

**Quick Toggle:** Press **B** key (or your configured key)

Instantly switches between:
- 🔵 **Arctic Cyan** - Default operating mode
- 🔴 **Battle Red** - High-intensity alert mode

---

## 🧭 All 8 Modules

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

## 🔧 If Something Breaks

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
- Go to Application → Local Storage
- Delete `aads-settings` key
- Refresh page

---

## 📝 Quick Tests

### Test Settings
1. Click ⚙️ button
2. Toggle "Hey Listen!" off
3. Close settings
4. Refresh page
5. Open settings again - should still be off ✅

### Test Hey Listen
1. Enable "Hey Listen!" in settings
2. Go to NAVI module
3. Send a message: "hello"
4. When NAVI responds → floating alert appears ✅

### Test Dashboard
1. Click "DASHBOARD" module
2. Should see 4 gauges with values ✅
3. Each gauge should have:
   - Label at top
   - Big number in center
   - Unit (KN, °, M, °C)
   - Min/max at bottom

### Test Battle Mode
1. Press **B** key
2. Theme should flip to red ✅
3. Press **B** again
4. Back to cyan ✅

---

## 🎯 What's Working

✅ Settings system with localStorage
✅ Hey Listen! prompts (toggleable)
✅ Dashboard with 4 gauges
✅ All original 8 modules
✅ Battle mode toggle
✅ Theme switching
✅ Settings persistence

## 🔮 What's Next

⏳ Connect gauges to real sensor data
⏳ Add drag-and-drop widget repositioning
⏳ Add more widget types (graphs, charts)
⏳ Create dashboard layout presets
⏳ Widget configuration (custom min/max, colors)

---

## 💾 Current Status

**Deployment:** Code pushed to GitHub ✅
**Jetson Status:** Awaiting `update-frontend.sh` run
**Testing:** Local testing complete, Jetson deployment pending

**When you deploy, test these 4 things:**
1. ⚙️ Settings button works
2. 📊 Dashboard shows gauges
3. 💬 Hey Listen appears (if enabled)
4. ⚔️ Battle mode toggles with B key

---

**Need help?** Check [SETTINGS_DASHBOARD_SUMMARY.md](SETTINGS_DASHBOARD_SUMMARY.md) for full details.

**Happy navigating! 🚢❄️**
