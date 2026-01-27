# 🚀 AADS Jetson Quick Fix

## One-Command Solution

SSH into your Jetson and run:

```bash
bash deploy/fix-everything.sh
```

That's it! This script will:

✅ Stop all containers cleanly
✅ Create `.env` configuration file
✅ Download Piper TTS model for voice
✅ Start all Docker services
✅ Verify everything is working

---

## What It Fixes

- ❌ Backend API not responding → **FIXED**
- ❌ Missing `.env` file → **CREATED**
- ❌ Piper TTS model missing → **DOWNLOADED**
- ❌ High CPU usage → **OPTIMIZED**
- ❌ Service connection issues → **RESOLVED**

---

## Access After Fix

Once complete, access via:

- 🖥️ **Frontend**: http://192.168.39.196:3000
- ⚙️ **Backend API**: http://192.168.39.196:8000
- 📖 **API Docs**: http://192.168.39.196:8000/docs

---

## If You Need Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service
docker-compose logs -f aads-backend
docker-compose logs -f aads-frontend

# Clear logs
docker-compose logs --tail 0
```

---

## Run Diagnostic After

```bash
bash diagnose-jetson.sh
```

Should show all ✓ green checkmarks!

---

## Need Help?

**Service won't start?**
```bash
docker-compose logs -f aads-backend
```

**Need to restart?**
```bash
docker-compose restart
```

**Full rebuild (if needed)?**
```bash
docker-compose down
docker-compose up -d --build
```

---

**Made with ❤️ for AADS**
