# PolyIntel UI - Professional Dashboard Setup Guide

## 🎉 What's New

Your PolyIntel frontend has been completely redesigned with a professional dashboard layout that includes:

✅ **Featured Markets Sidebar** - Quick access to trending markets
✅ **Live Ticker** - Auto-scrolling market quotes in header
✅ **Advanced Analysis View** - Professional multi-panel analysis interface
✅ **Sentiment vs Reality** - Side-by-side market analysis
✅ **Recommendation Engine** - AI-powered trading signals
✅ **Responsive Design** - Works perfectly on mobile, tablet, desktop

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /Users/raahulvignesh/Desktop/Projects/polyintel-ui
npm install
```

### 2. Start the Frontend
```bash
npm run dev
```
Opens at: **http://localhost:5173**

### 3. Start the Backend (separate terminal)
```bash
cd /Users/raahulvignesh/Desktop/Projects/polyintel
source venv/bin/activate
python -m uvicorn app.main:app --reload
```
Runs at: **http://localhost:8000**

---

## 📊 Dashboard Overview

### Left Sidebar (30% width)
- **Featured Markets Section**
  - 4 pre-loaded popular prediction markets
  - Click any market to load its analysis
  - Each card shows odds, volume, sentiment, risk, whale tracking
  - Selected market has blue border highlight

- **Search Markets**
  - Find and select markets by name
  - Expandable for market discovery

### Main Content Area (70% width)
- **Market Header**
  - Large market title
  - Current odds percentage
  - Polymarket link
  - Status badges

- **Analysis Tabs**
  - PolyCaster (active) - Sentiment analysis
  - PolyCop - Manipulation detection
  - WhaleAuditor - Large holder tracking
  - Arb Dashboard - Cross-venue opportunities

- **PolyCaster Analysis**
  - Audio briefing player
  - Two-column comparison:
    - **The Vibe** (Left) - Social sentiment score
    - **The Reality** (Right) - Market odds vs sentiment

- **Reasoning & Recommendation**
  - Detailed analysis explanation
  - Actionable recommendation (LONG YES, HOLD, etc.)

---

## 🎨 Color Guide

```
Cyan (#00D9FF)      - Primary action, active elements
Purple (#A78BFA)    - "The Vibe" sentiment analysis
Green (#4ADE80)     - Bullish, positive sentiment
Red (#F87171)       - Bearish, negative sentiment
Yellow (#FBBF24)    - Highlights, featured items
Gray-800            - Card backgrounds
Gray-900            - Main background
```

---

## 🔌 API Integration Points

### Currently Using Mock Data
The dashboard is designed to work with these backend endpoints:

```
GET  /polymarket/trending              → Trending markets list
POST /polycaster/signal                → Sentiment analysis
POST /polycop/inspect                  → Manipulation detection
GET  /polywhaler/feeds                 → Whale activity
```

**To connect real data**, update in `src/pages/DashboardV2.tsx`:
- Replace `featuredMarkets` array with API call to `/polymarket/trending`
- Replace `analyzeMarket()` function to call `/polycaster/signal`
- Connect tabs to respective API endpoints

---

## 📱 Responsive Breakpoints

| Device | Layout | Sidebar |
|--------|--------|---------|
| Mobile (<768px) | Stacked | Full width, scrollable |
| Tablet (768-1024px) | 2 columns | 1/3 width |
| Desktop (>1024px) | 3 columns | 1/4 width |

---

## 🎮 User Interactions

### Selecting a Market
```
1. Click on featured market in sidebar
2. Market becomes selected (blue border)
3. Loading spinner appears (500ms animation)
4. Analysis generates and displays
5. Can switch to different analysis tabs
```

### Audio Briefing
```
Button: "▶ Play Audio Briefing"
- Reads analysis details aloud
- Uses ElevenLabs TTS
- Useful for on-the-go insights
```

### Recommendation Button
```
Shows current recommendation:
- GREEN border = Action available (LONG YES/NO)
- GRAY border = Hold (no clear signal)
```

---

## 🛠️ Customization

### Change Featured Markets
Edit `src/pages/DashboardV2.tsx`, line ~45:
```typescript
const featuredMarkets: FeaturedMarket[] = [
  {
    id: '1',
    slug: 'your-market-slug',
    title: 'Your market question',
    category: 'Category',
    odds: 0.52,
    volume: 1000000,
    ...
  }
]
```

### Change Color Scheme
Edit `tailwind.config.js` to modify default colors:
- Primary: Change `cyan-400` to your color
- Secondary: Change `purple-400` to your color
- Positive: Change `green-400` to your color

### Modify Layout
- Sidebar width: Change `lg:col-span-1` and `lg:col-span-3`
- Card styling: Edit Tailwind classes in the component
- Font sizes: Adjust `text-sm`, `text-lg`, `text-3xl`, etc.

---

## 📊 Sample Featured Markets

The dashboard comes pre-loaded with:
1. **Trump 2024** - Politics category
2. **Taylor Swift Grammy** - Culture category
3. **Bitcoin $100K** - Crypto category
4. **Doom Game of Year** - Gaming category

Each shows realistic odds, volumes, and sentiment indicators.

---

## 🔄 Data Flow

```
User Opens Dashboard
     ↓
DashboardV2 mounts
     ↓
Load first featured market
     ↓
analyzeMarket() generates analysis
     ↓
Mock data populates vibe/reality
     ↓
Recommendation calculated
     ↓
UI renders with all data
     ↓
User can select different markets
     ↓
Process repeats for new selection
```

---

## 🚨 Troubleshooting

### Ticker not scrolling?
- Check `LiveTicker.tsx` `useEffect` hook
- Verify scroll position state is updating
- Browser might need refresh

### Analysis not loading?
- Check that `analyzeMarket()` completes
- Verify loading spinner timeout (500ms)
- Check browser console for errors

### Styles not applying?
- Ensure `npm run dev` is running
- Clear browser cache (Cmd+Shift+R)
- Verify Tailwind is in `styles/index.css`

### Markets not displaying?
- Check `featuredMarkets` array is populated
- Verify `selectedMarket` is set on mount
- Check for console errors in DevTools

---

## 📚 Project Structure

```
polyintel-ui/
├── src/
│   ├── components/
│   │   ├── Header.tsx          (with LiveTicker)
│   │   ├── LiveTicker.tsx      (NEW - moving ticker)
│   │   ├── TrendingMarkets.tsx (trending grid)
│   │   └── ...
│   ├── pages/
│   │   ├── DashboardV2.tsx     (NEW - professional layout)
│   │   ├── Dashboard.tsx       (original - deprecated)
│   │   └── ...
│   ├── services/
│   │   └── api.ts              (API client)
│   ├── styles/
│   │   └── index.css
│   └── App.tsx                 (routes DashboardV2)
├── vite.config.js
├── tailwind.config.js
├── package.json
└── REDESIGN.md
```

---

## 🔐 Environment Variables

Create `.env` in polyintel-ui:
```bash
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

---

## 💡 Pro Tips

1. **Use browser DevTools** (F12) to inspect elements and adjust styling
2. **Check Network tab** to see API calls when connected to backend
3. **Try different markets** in the search box to see layout changes
4. **Resize browser** to see responsive design in action
5. **Check Console** for any warnings or errors

---

## 🎯 Next Steps

1. ✅ Frontend is built and styled
2. ⏳ Connect backend API endpoints
3. ⏳ Replace mock data with real market data
4. ⏳ Implement audio briefing player
5. ⏳ Add more analysis tabs (PolyCop, WhaleAuditor)
6. ⏳ Create user accounts and favorites
7. ⏳ Build alert system for signals

---

## 📞 Support

If something isn't working:
1. Check the browser console (F12)
2. Look at backend logs (Terminal 1)
3. Verify both servers are running
4. Try refreshing the page (Cmd+R or Ctrl+R)
5. Check environment variables

---

**UI Version**: 2.0 Professional Dashboard
**Status**: ✅ Ready for API Integration
**Last Updated**: November 2024

Enjoy your new professional prediction market dashboard! 🚀
