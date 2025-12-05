# PolyIntel UI - Frontend

A modern React dashboard for AI-powered prediction market analysis.

## Quick Start (Local Development)

### Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org)
- **npm** or **yarn**
- **Backend running** at `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd /Users/raahulvignesh/Desktop/Projects/polyintel-ui

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

**Frontend runs at:** `http://localhost:5173`

---

## Features

### Dashboard
- **Market Analysis**: Analyze any prediction market by slug
- **Strategy Selection**: Choose between SPOON (multi-factor) or PolyCaster (sentiment) analysis
- **Real-time Signals**: Get AI-generated trade signals with confidence scores
- **Market Links**: Quick access to market pages on Polymarket

### History Page
- **Signal Archive**: View all past signals and analysis
- **Performance Stats**: Win rate, total signals, date range
- **Searchable**: Filter signals by market or date

### Whale Tracker
- **Activity Monitoring**: Track large holder transactions
- **Volume Analysis**: See total buy/sell volume by whale traders
- **Impact Analysis**: Monitor how large orders affect market odds

### Settings
- **API Configuration**: Set custom backend URL
- **Auto-Refresh**: Enable periodic signal refresh
- **Theme Support**: Dark/light mode (foundation ready)
- **Notifications**: Control desktop alerts

---

## Project Structure

```
polyintel-ui/
├── src/
│   ├── components/          # React components
│   │   ├── Header.tsx       # Navigation header
│   │   ├── SignalCard.tsx   # Signal display card
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorAlert.tsx
│   ├── pages/               # Page components
│   │   ├── Dashboard.tsx    # Main analysis page
│   │   ├── History.tsx      # Signal history
│   │   ├── WhaleTracker.tsx # Whale activity
│   │   └── Settings.tsx     # User settings
│   ├── services/
│   │   └── api.ts           # Backend API client
│   ├── store/
│   │   └── signals.ts       # Zustand state management
│   ├── styles/
│   │   └── index.css        # Tailwind CSS
│   ├── App.tsx              # Router setup
│   └── main.tsx             # Entry point
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind configuration
├── postcss.config.js        # PostCSS configuration
├── package.json
└── .env.example
```

---

## API Service Methods

The `src/services/api.ts` file provides these methods:

```typescript
// Trade Analysis
APIService.analyzeWithSPOON(marketSlug)
APIService.analyzeWithPolycaster(marketSlug, query, category, useManus)

// Market Data
APIService.getMarkets(params)
APIService.getMarketDetails(marketSlug)

// Sentiment
APIService.analyzeSentiment(marketSlug)

// Advanced Features
APIService.inspectManipulation(marketData)
APIService.generatePodcast(marketSlug, analysis)
APIService.chatWithAI(query, context)
APIService.getWhaleActivity(limit)
```

---

## State Management (Zustand)

The signal store manages:
- **signals**: Current trading signals
- **favorites**: Bookmarked markets
- **history**: All past signals (persisted to localStorage)

```typescript
const { signals, addSignal, toggleFavorite, history } = useSignalStore();
```

---

## Environment Variables

Create a `.env` file:

```bash
# Backend API URL (must match backend port)
VITE_API_URL=http://localhost:8000

# Request timeout in milliseconds
VITE_API_TIMEOUT=30000
```

---

## Development Commands

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm preview
```

---

## API Integration

The frontend communicates with these backend endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/spoon/trade` | Multi-factor analysis |
| POST | `/polycaster/signal` | Sentiment analysis |
| GET | `/polymarket/list` | Market listings |
| GET | `/polycaster/sentiment` | Sentiment score |
| POST | `/polycop/inspect` | Manipulation detection |
| GET | `/polywhaler/feeds` | Whale activity |
| POST | `/sudo/chat` | AI chat |

---

## Customization

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/Header.tsx`

### Adding New API Methods

1. Add method to `src/services/api.ts`
2. Use in components via `APIService.methodName()`

### Styling

- **Tailwind CSS** - Utility classes in JSX
- **Custom styles** - `src/styles/index.css`
- **Component classes** - Defined in `tailwind.config.js`

---

## Troubleshooting

### "Cannot connect to backend"
- Ensure backend is running: `python -m uvicorn app.main:app --reload`
- Check `VITE_API_URL` in `.env` matches backend port
- Frontend runs on `5173`, backend on `8000`

### "npm install fails"
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Ensure Node.js 18+ is installed

### "Port 5173 already in use"
- Kill the process: `lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9`
- Or change port in `vite.config.js`

---

## Next Steps

- [ ] Connect to real backend endpoints
- [ ] Add WebSocket for real-time updates
- [ ] Implement dark/light theme toggle
- [ ] Add advanced charting (TradingView integration)
- [ ] Create signal alerts/notifications
- [ ] Build performance analytics dashboard
- [ ] Add market watchlist functionality
- [ ] Implement backtesting view

---

## License

Same as PolyIntel main project
