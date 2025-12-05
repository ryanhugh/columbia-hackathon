# PolyIntel - Local Setup Guide

Complete guide to run PolyIntel backend and frontend locally.

## System Requirements

- **Python 3.12+**
- **Node.js 18+**
- **macOS/Linux/Windows** (with git bash or WSL for Windows)

## Part 1: Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd /Users/raahulvignesh/Desktop/Projects/polyintel
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# On Windows, use:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your editor
```

**Required API Keys to Add:**

```bash
# LLM Provider (pick at least one)
OPENAI_API_KEY=your_openai_key
# OR
ANTHROPIC_API_KEY=your_claude_key
# OR
DEEPSEEK_API_KEY=your_deepseek_key

# Market Data (required)
POLYMARKET_API_KEY=your_polymarket_key
DESEARCH_API_KEY=your_desearch_key

# Audio Generation (optional)
ELEVENLABS_API_KEY=your_elevenlabs_key

# Web3 (optional, for trading)
PRIVATE_KEY=your_wallet_private_key
RPC_URL=https://base-rpc.publicnode.com

# Optional Integrations
TAVILY_API_KEY=your_tavily_key
OKX_API_KEY=your_okx_key
```

### Step 5: Run Backend Server

```bash
# Make sure venv is activated
python -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Access Points:**
- API: `http://localhost:8000`
- API Docs (Swagger UI): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Part 2: Frontend Setup

### Step 1: Open New Terminal Window

Keep the backend running in the first terminal.

### Step 2: Navigate to Frontend Directory

```bash
cd /Users/raahulvignesh/Desktop/Projects/polyintel-ui
```

### Step 3: Install Dependencies

```bash
npm install
```

This installs all required packages:
- React 18.3.1
- Vite (build tool)
- React Router (navigation)
- Zustand (state management)
- Axios (HTTP client)
- Tailwind CSS (styling)
- Lucide React (icons)

### Step 4: Create Environment File

```bash
cp .env.example .env
```

The default `.env` should work:
```bash
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

### Step 5: Start Frontend Development Server

```bash
npm run dev
```

**Expected Output:**
```
  VITE v5.0.8  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

---

## Part 3: Verify Integration

### Check Backend

Open in browser: `http://localhost:8000/docs`

You should see the interactive API documentation showing all available endpoints.

### Check Frontend

Open in browser: `http://localhost:5173`

You should see the PolyIntel dashboard with:
- Header with logo and navigation
- Market analysis input field
- Empty state message

### Test Connection

1. Go to Dashboard (`http://localhost:5173`)
2. Enter a market slug (e.g., `btc-100k`)
3. Click "Analyze"
4. You should see results within seconds

---

## Complete Local Setup Checklist

```bash
# Terminal 1 - Backend
✓ cd polyintel
✓ python3 -m venv venv
✓ source venv/bin/activate
✓ pip install -r requirements.txt
✓ cp .env.example .env (edit with your keys)
✓ python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
✓ cd polyintel-ui
✓ npm install
✓ cp .env.example .env
✓ npm run dev
```

---

## Quick Command Reference

### Backend Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Run with auto-reload (development)
python -m uvicorn app.main:app --reload --port 8000

# Run without auto-reload (production-like)
python -m uvicorn app.main:app --port 8000

# View API docs
# Open: http://localhost:8000/docs
```

### Frontend Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Project Structure

```
Projects/
├── polyintel/                 # Backend (FastAPI)
│   ├── venv/                  # Virtual environment
│   ├── app/
│   │   └── main.py            # API server
│   ├── integrations/          # External APIs
│   ├── agents/                # AI agents
│   ├── spoon/                 # Custom modules
│   ├── .env                   # Your API keys (not in git)
│   ├── requirements.txt
│   └── SETUP_LOCAL.md         # This file
│
└── polyintel-ui/              # Frontend (React/Vite)
    ├── node_modules/          # Dependencies
    ├── src/
    │   ├── components/        # React components
    │   ├── pages/             # Page components
    │   ├── services/          # API client
    │   ├── store/             # State management
    │   └── styles/            # CSS/Tailwind
    ├── .env                   # Frontend config
    ├── vite.config.js
    ├── package.json
    └── README.md
```

---

## Troubleshooting

### Backend Issues

#### "ModuleNotFoundError: No module named 'fastapi'"

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

#### "Port 8000 already in use"

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python -m uvicorn app.main:app --port 8001
```

#### API keys not loading from .env

```bash
# Verify .env file exists and has correct format
cat .env

# Make sure it's in the root directory
# /Users/raahulvignesh/Desktop/Projects/polyintel/.env
```

### Frontend Issues

#### "Cannot connect to backend"

Check:
1. Backend is running: `http://localhost:8000/docs`
2. `VITE_API_URL` in `.env` is correct
3. Check browser console (F12) for CORS errors

#### "npm: command not found"

Install Node.js from: https://nodejs.org (18+ LTS recommended)

#### "Port 5173 already in use"

```bash
# Kill process on port 5173
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or specify different port in vite.config.js
```

#### Dependencies installation fails

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Development Workflow

### Making Changes

**Backend:**
- Edit files in `app/` or `integrations/`
- Server auto-reloads when you save (if using `--reload`)
- Test via `http://localhost:8000/docs`

**Frontend:**
- Edit files in `src/`
- Browser auto-updates when you save
- Hot Module Replacement (HMR) enabled by default

### Testing API Endpoints

Use the Swagger UI at `http://localhost:8000/docs` to test endpoints directly.

Example workflow:
1. Click on `/polycaster/signal` endpoint
2. Click "Try it out"
3. Enter test data (e.g., `market_slug: "btc-100k"`)
4. Click "Execute"
5. See the response

---

## Next Steps

1. **Add API Keys**: Get keys from services and add to `.env`
2. **Explore API**: Visit `http://localhost:8000/docs` to see all endpoints
3. **Test Signals**: Try analyzing different markets
4. **Customize UI**: Modify components in `src/` as needed
5. **Extend Features**: Add new pages or API integrations

---

## Environment Variables Reference

### Backend (.env in /polyintel/)

```bash
# Core LLM (choose one or more)
OPENAI_API_KEY              # For OpenAI API access
ANTHROPIC_API_KEY           # For Claude API access
DEEPSEEK_API_KEY            # For DeepSeek API access

# Market Data
POLYMARKET_API_KEY          # Polymarket data access
DESEARCH_API_KEY            # Social media/research data

# Audio Generation
ELEVENLABS_API_KEY          # Text-to-speech for podcasts

# Blockchain
PRIVATE_KEY                 # Wallet private key (for trading)
RPC_URL                     # Blockchain RPC endpoint

# Optional Integrations
TAVILY_API_KEY              # Web search API
OKX_API_KEY                 # Crypto exchange data
```

### Frontend (.env in /polyintel-ui/)

```bash
VITE_API_URL                # Backend API URL (http://localhost:8000)
VITE_API_TIMEOUT            # Request timeout in ms (30000)
```

---

## Getting Help

1. **Backend Errors**: Check `app/main.py` and check the console output
2. **Frontend Errors**: Open browser DevTools (F12) and check Console tab
3. **API Issues**: Visit `http://localhost:8000/docs` to verify endpoints
4. **Connection Issues**: Verify both servers are running on correct ports

---

## Files Created

- ✅ Frontend project structure
- ✅ React components (Dashboard, History, WhaleTracker, Settings)
- ✅ API client service (`src/services/api.ts`)
- ✅ State management with Zustand
- ✅ Tailwind CSS styling
- ✅ React Router navigation
- ✅ Environment configuration

You're now ready to run PolyIntel locally! 🚀
