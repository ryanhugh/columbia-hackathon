# 🔷 PolyEdge Personalized Dashboard

The "holy sh*t I get it" moment for users.

## 🎯 What This Is

A complete redesign that transforms PolyEdge from a generic correlation tool into a **personalized portfolio edge map**.

**Before:** "Here are some correlations"
**After:** "Here's YOUR edge map - these markets lead YOUR holdings"

## 🚀 Access

**New Personalized Dashboard:**
```
http://localhost:8080/personalized
```

**Classic Dashboard (still available):**
```
http://localhost:8080/classic
```

**Default (redirects to personalized):**
```
http://localhost:8080
```

## 📊 Features

### Section 1: Portfolio Overview

- **Holding Cards**: Each asset with weight percentage
- **Edge Intensity Bars**: Visual indicator (High/Medium/Low)
  - Shows how much event-risk is currently active
  - Color-coded: Red (High) → Yellow (Medium) → Green (Low)

### Section 2: Markets That Matter Most

Ranked table showing:
- **Rank**: Priority order
- **Market**: Prediction market question
- **Related Asset**: Which holding it affects
- **EdgeScore**: Predictive power (0-100)
- **Lead Time**: Hours before asset typically moves
- **Alert Status**: 🔥 Live / ⚠️ Spike / 🔍 Elevated
- **Explore Button**: Opens Relationship Explorer

### Section 3: Relationship Explorer

Click "Explore" on any market to see:
- **Chart**: PM probability vs asset price
- **Lead-lag zones**: Highlighted correlation periods
- **Historical Performance**: "12 significant PM moves → 10 times asset followed"
- **Strategies**: Toggle between trading approaches

### Section 4: Event Calendar

Calendar view showing:
- **Upcoming Events**: Fed meetings, ETF decisions, upgrades, etc.
- **Relevant Markets**: Which PMs track each event
- **Impact Likelihood**: High/Medium/Low

## 🧮 EdgeScore Formula

```
EdgeScore = (|Correlation| × Stability × Significance × ImpactWeight) × 100
```

**Components:**
- **Correlation**: Pearson correlation (PM probability ↔ asset return)
- **Stability**: Rolling-window consistency (0-1)
- **Significance**: P-value mapped to 0-1 scale
- **ImpactWeight**: Asset/event type weighting

**Score Interpretation:**
- **86+**: Strong predictive relationship
- **60-85**: Moderate but tradable
- **<60**: Lower confidence

## 🔍 Semantic Matching

Enhanced matching algorithm:

1. **Entity Match** (50% weight): Direct mention of asset
2. **Category Match** (20% weight): Market category matches asset profile
3. **Keyword Match** (20% weight): Relevant keywords in question
4. **Event Type** (10% weight): Event type matches asset sensitivity

**Final Match Score:**
```
Composite = (Semantic × 0.5) + (Correlation × 0.3) + (Logical × 0.2)
```

Only markets with composite score ≥ 0.65 appear in dashboard.

## 📁 Files Created

- `edgescore.py` - EdgeScore calculator
- `semantic_matcher.py` - Enhanced semantic matching
- `templates/dashboard_personalized.html` - New UI
- Updated `dashboard.py` - New routes and logic

## 🎨 UI Design

- **Dark theme**: Professional, Bloomberg-terminal inspired
- **Gradient accents**: Purple/blue theme
- **Card-based layout**: Clean, modern
- **Interactive modals**: Relationship explorer
- **Responsive**: Works on all screen sizes

## 🔧 API Endpoints

### Get Markets That Matter
```bash
curl http://localhost:8080/api/markets-that-matter
```

### Get Relationship Data
```bash
curl http://localhost:8080/api/relationship/<market_id>/<asset>
```

### Get Edge Intensity
```bash
curl http://localhost:8080/api/portfolio/<portfolio_id>/edge-intensity
```

## 💡 The Value Proposition

**Investor Pitch:**

> "Prediction markets move before the world does — but today, traders don't know which events actually matter for their portfolio. PolyEdge is the first engine that connects your holdings to the prediction markets that statistically lead them. Plug in your portfolio, and PolyEdge instantly identifies which event markets historically predict moves in BTC, ETH, SPY, NVDA and more — including lead times, correlation strength, and real-time alerts.
>
> Instead of sifting through hundreds of markets, users get a personalized event map: 'ETH ETF approval odds just spiked; historically ETH follows within ~8 hours.' We use historical correlation, semantic matching, and statistical lag analysis to surface only the markets with proven predictive power for the user's specific holdings.
>
> PolyEdge becomes a personalized macro radar — a Bloomberg terminal powered by prediction markets."

## 🚀 Next Steps

1. **View the dashboard**: http://localhost:8080
2. **Create a portfolio**: `python manage_portfolio.py create`
3. **Watch it personalize**: Dashboard updates automatically
4. **Explore relationships**: Click "Explore" on any market

---

**This is the "holy sh*t I get it" moment.** 🔥

