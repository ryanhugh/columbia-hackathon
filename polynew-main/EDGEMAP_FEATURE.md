# 🗺️ PolyEdge Personalized Dashboard - Edge Map Feature

**The "holy sh*t I get it" moment for users.**

## 🎯 What This Is

Transforms PolySignal from a generic correlation tool into a **personalized portfolio edge map** that shows:
- Which prediction markets matter for YOUR holdings
- How strong the predictive relationship is (EdgeScore)
- When to expect moves (lead time)
- Real-time alerts when relevant markets move

## 🚀 Features Implemented

### 1. Portfolio Edge Map
**Main screen showing your portfolio's event risk**

- **Portfolio Overview**: Each holding with Edge Intensity bar
  - High/Medium/Low intensity based on active event-risk
  - Visual bars showing risk level
  
- **Markets That Matter Most**: Ranked list personalized to your portfolio
  - Rank, Market, Related Asset, EdgeScore, Lead Time, Alert status
  - Sorted by EdgeScore (predictive power)
  - Live alerts (🔥 Live, ⚠️ Spike, 🔍 Elevated)

### 2. EdgeScore Algorithm
**Quantifies predictive edge for each market-asset pair**

Formula: `EdgeScore = (|Correlation| × Stability × Significance × ImpactWeight) × 100`

Components:
- **Correlation**: Pearson correlation between PM probability changes and asset returns
- **Stability**: Rolling-window correlation consistency (0-1)
- **Significance**: P-value mapped to 0-1 scale
- **ImpactWeight**: Hand-tuned based on asset/event type

Score Interpretation:
- **86+**: Strong predictive relationship
- **60-85**: Moderate but tradable
- **40-59**: Weak but watchable
- **<40**: Noise

### 3. Relationship Explorer
**Deep dive into any market-asset relationship**

Click any market in "Markets That Matter" to see:
- Chart of PM probability vs asset price
- Lead-lag analysis (optimal lag time)
- Correlation heatmap (different lag times)
- Historical performance:
  - "X significant PM moves → Y times asset followed within Z hours"
- Trading strategies:
  - "Buy dips when prob rises sharply"
  - "Fade markets when prob drops too fast"

### 4. Enhanced Market Matching
**Semantic matching algorithm**

Three-component matching:
- **Semantic (50%)**: Category/keyword/event type matching
- **Correlation (30%)**: Historical correlation strength
- **Logical (20%)**: Explicit mentions or category rules

Only markets with composite match > 0.65 appear in dashboard.

### 5. Event Calendar
**Upcoming events relevant to your holdings**

Shows:
- Fed meetings
- CPI releases
- ETF decisions
- Protocol upgrades
- Earnings reports
- Regulatory hearings

Each event shows:
- Date
- Relevant prediction markets
- Impact likelihood (Low/Med/High)
- Affected holdings

## 📊 Dashboard Sections

### Section 1: Portfolio Overview
```
BTC — 40%  [High Edge Intensity Bar]
ETH — 25%  [Medium Edge Intensity Bar]
SOL — 15%  [Low Edge Intensity Bar]
```

### Section 2: Markets That Matter Most
```
Rank | Market              | Asset | EdgeScore | Lead Time | Alert
1    | ETH ETF Approval    | ETH   | 86        | 8 hrs     | 🔥 Live
2    | Fed Cut September   | SPY   | 78        | 4 hrs     | ⚠️ Spike
3    | BTC to hit $100k    | BTC   | 65        | 6 hrs     | —
```

### Section 3: Relationship Explorer
Click any market to explore:
- Price correlation charts
- Lead-lag zones
- Historical success rate
- Trading strategies

### Section 4: Event Calendar
Monthly view showing:
- Upcoming events
- Relevant markets
- Impact on holdings

## 🔧 API Endpoints

### Get Markets That Matter
```bash
GET /api/portfolio/<portfolio_id>/markets-that-matter
```

Returns ranked list with EdgeScores.

### Get Edge Intensity
```bash
GET /api/portfolio/<portfolio_id>/edge-intensity
```

Returns High/Medium/Low for each holding.

### Explore Relationship
```bash
GET /api/relationship/<market_category>/<asset_symbol>
```

Returns comprehensive relationship analysis.

### Get Events
```bash
GET /api/portfolio/<portfolio_id>/events
```

Returns upcoming events calendar.

## 🎨 UI Features

### Edge Intensity Bars
- **High** (Red-Orange gradient): Multiple high-EdgeScore markets active
- **Medium** (Orange-Yellow gradient): Some relevant markets
- **Low** (Green gradient): Few or weak relationships

### Market Rows
- Clickable to open Relationship Explorer
- Color-coded EdgeScore (red=high, orange=medium, green=low)
- Alert indicators for active movements

### Responsive Design
- Works on desktop, tablet, mobile
- Grid layouts adapt to screen size

## 📈 Example Use Case

**User Portfolio:**
- BTC: 50%
- ETH: 30%
- SPY: 20%

**Dashboard Shows:**

1. **Edge Intensity:**
   - BTC: High (ETF approval market active, EdgeScore 86)
   - ETH: Medium (Upgrade market, EdgeScore 65)
   - SPY: Low (No strong markets currently)

2. **Markets That Matter:**
   - #1: ETH ETF Approval → ETH (EdgeScore 86, 8hrs lead)
   - #2: Fed Cut September → SPY (EdgeScore 78, 4hrs lead)
   - #3: BTC to $100k → BTC (EdgeScore 65, 6hrs lead)

3. **User Action:**
   - Clicks "ETH ETF Approval"
   - Sees: "12 significant PM moves → 10 times ETH followed within 12 hours"
   - Strategy: "Buy on probability spike"
   - Sets alert for when PM probability rises >5%

## 🔮 Future Enhancements

### Real-time Alerts
- WebSocket connections for live updates
- Push notifications
- Email/SMS alerts

### Advanced Analytics
- Backtesting interface
- Strategy performance tracking
- Portfolio optimization suggestions

### Integration
- Connect broker APIs (auto-sync holdings)
- On-chain wallet scanning
- Trading bot integration

## 💡 The Value Proposition

**Before:** "Here are some correlations that might be useful"

**After:** "Here's exactly what matters for YOUR portfolio, ranked by predictive power, with lead times and alerts"

This transforms prediction markets from research data into actionable, personalized trading signals.

---

**View your Edge Map at: http://localhost:8080**

The dashboard automatically shows your portfolio's Edge Map when you have a portfolio created!

