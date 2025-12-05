# PolyIntel Frontend - Trae Deployment Guide

## 📦 Quick Deployment

### Step 1: Extract the Frontend

```bash
# Navigate to your Trae project root (where alpha/ directory is)
cd /path/to/your/trae/project

# Extract the frontend
tar -xzf manus_frontend.tar.gz

# Move to alpha directory
mv manus_frontend alpha/
```

### Step 2: Verify Directory Structure

Your project should now look like this:

```
your-trae-project/
├── alpha/
│   ├── manus_frontend/          ← Frontend goes here
│   │   ├── index.html
│   │   └── assets/
│   │       ├── index-*.css
│   │       └── index-*.js
│   ├── app/
│   │   └── main.py
│   └── ...
```

### Step 3: Start/Restart Trae Backend

```bash
# If already running, restart
# The exact command depends on your setup, typically:
python -m uvicorn app.main:app --reload

# Or if using a different command:
./start_server.sh  # or whatever your startup script is
```

### Step 4: Access PolyIntel

Open your browser and navigate to:

```
http://localhost:8000/
```

You should see the PolyIntel dashboard!

---

## 🔌 Backend Integration

The frontend is pre-configured to connect to your Trae backend at `/polycaster`.

### Available Endpoints

The frontend expects these Trae endpoints to be available:

1. **Podcast Generation (Full + Short)**
   ```
   POST /polycaster/podcast/variants
   Body: {
     "query": "btc macro outlook",
     "category": "crypto",
     "duration": "PAST_24_HOURS"
   }
   ```

2. **Podcast Generation (Single)**
   ```
   POST /polycaster/podcast
   Body: {
     "query": "ethereum price outlook",
     "variant": 2,
     "target_duration_sec": 60
   }
   ```

3. **Sentiment Analysis**
   ```
   POST /polycaster/sentiment
   Body: {
     "query": "bitcoin bullish"
   }
   ```

4. **Health Check** (optional)
   ```
   GET /polycaster/health
   ```

---

## 🎨 Frontend Features

The deployed frontend includes:

### 1. **4-Agent Analysis System**
- **PolyCaster**: Sentiment analysis
- **PolyCop**: Manipulation detection
- **WhaleAuditor**: Trader verification with live feed
- **Arb Dashboard**: Cross-venue arbitrage

### 2. **Advanced Features**
- Featured markets for quick demos
- Live whale trade feed with smart polling
- Trader profile pages
- Whale alert configuration
- Clickable ticker strip

### 3. **Trae Integration**
- Podcast generation UI
- Sentiment analysis display
- Audio playback for briefings

---

## 🐛 Troubleshooting

### Issue: 404 Not Found

**Symptoms**: Visiting `http://localhost:8000/` shows 404

**Solutions**:
1. Verify `manus_frontend/` is in `alpha/` directory
2. Check that `index.html` exists in `manus_frontend/`
3. Restart the Trae backend
4. Check backend logs for static mount errors

### Issue: CORS Errors

**Symptoms**: Browser console shows CORS errors

**Solution**: Verify CORS is configured in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: API Calls Failing

**Symptoms**: Frontend loads but features don't work

**Solutions**:
1. Check that `/polycaster` endpoints are running
2. Open browser DevTools → Network tab to see failed requests
3. Verify backend is running on port 8000
4. Check backend logs for errors

### Issue: Assets Not Loading

**Symptoms**: Blank page or missing styles

**Solutions**:
1. Check browser console for 404 errors on `/assets/*` files
2. Verify `assets/` directory exists in `manus_frontend/`
3. Check file permissions: `chmod -R 755 alpha/manus_frontend`

---

## 🔧 Configuration

### Change API Base URL

If your backend runs on a different path or port, update the environment variable:

**Before building** (if you have source code):
```bash
# Edit .env.production
VITE_API_BASE_URL=/your-custom-path
```

**After deployment** (quick fix):
Edit `alpha/manus_frontend/assets/index-*.js` and find:
```javascript
const API_BASE = "/polycaster"
```
Change to your custom path.

### Change App Title

The app title is "PolyCaster Dashboard" by default.

To change it, edit `alpha/manus_frontend/index.html`:
```html
<title>Your Custom Title</title>
```

---

## 📊 Testing the Integration

### 1. Test Frontend Loads

```bash
curl http://localhost:8000/
# Should return HTML with "PolyCaster Dashboard"
```

### 2. Test API Connection

Open browser console and run:

```javascript
fetch('/polycaster/sentiment', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'bitcoin bullish' })
})
.then(r => r.json())
.then(console.log)
```

Should return sentiment analysis result.

### 3. Test Podcast Generation

In the PolyIntel UI:
1. Click on a featured market (e.g., "Trump 2024")
2. Navigate to PolyCaster tab
3. Click "Generate Podcast"
4. Should see audio player with briefing

---

## 🚀 Production Deployment

For production deployment:

### 1. Build Optimization

The frontend is already minified and optimized (342KB gzipped).

### 2. CDN/Static Hosting (Optional)

If you want to serve the frontend from a CDN:

1. Upload `manus_frontend/` contents to your CDN
2. Update CORS in Trae backend to allow CDN origin
3. Update `VITE_API_BASE_URL` to point to your backend domain

### 3. Environment Variables

For production, consider:

```bash
# In your deployment environment
VITE_API_BASE_URL=https://your-production-domain.com/polycaster
VITE_APP_TITLE=PolyIntel
```

---

## 📁 File Structure

```
manus_frontend/
├── index.html                    # Main HTML file
└── assets/
    ├── index-BqD-6QRe.css       # Styles (136KB)
    └── index-CcF1M2bG.js        # JavaScript bundle (864KB)
```

**Total Size**: ~1MB uncompressed, 342KB compressed

---

## 🔄 Updating the Frontend

To deploy a new version:

1. **Backup current version**:
   ```bash
   mv alpha/manus_frontend alpha/manus_frontend.backup
   ```

2. **Extract new version**:
   ```bash
   tar -xzf manus_frontend_new.tar.gz
   mv manus_frontend alpha/
   ```

3. **Restart backend**:
   ```bash
   # Your restart command
   ```

4. **Clear browser cache**:
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

---

## ✅ Verification Checklist

- [ ] `alpha/manus_frontend/` directory exists
- [ ] `index.html` is present in `manus_frontend/`
- [ ] `assets/` directory contains CSS and JS files
- [ ] Backend is running on port 8000
- [ ] Visiting `http://localhost:8000/` shows PolyIntel
- [ ] Browser console shows no errors
- [ ] API calls to `/polycaster/*` work
- [ ] Featured markets load correctly
- [ ] Podcast generation works

---

## 📞 Support

If you encounter issues:

1. Check browser console for errors (F12 → Console)
2. Check backend logs for API errors
3. Verify all endpoints are implemented in Trae
4. Test API endpoints directly with curl/Postman

---

## 🎯 Next Steps

After successful deployment:

1. **Test all features** with real Polymarket data
2. **Configure whale alerts** for your markets
3. **Customize branding** (logo, colors) if needed
4. **Set up monitoring** for API usage
5. **Enable analytics** (optional)

---

**Deployment Package**: `manus_frontend.tar.gz` (342KB)  
**Deployment Target**: `alpha/manus_frontend/`  
**Backend Requirements**: Trae with `/polycaster` endpoints  
**Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)
