# 💼 Portfolio Tracking Feature

Personalized portfolio monitoring that shows which prediction markets matter for YOUR holdings.

## 🎯 What This Does

Transforms PolySignal from:
- **Generic**: "Here are global correlations"
- **To Personalized**: "Here's what matters for YOUR portfolio"

## 🚀 Quick Start

### 1. Create a Portfolio

```bash
python manage_portfolio.py create
```

Follow the prompts to:
- Name your portfolio
- Add holdings (e.g., BTC 0.4, ETH 0.3, SPY 0.3)
- Save to database

### 2. Analyze Your Portfolio

```bash
python manage_portfolio.py analyze <portfolio_id>
```

This will:
- Find relevant prediction markets for your holdings
- Show correlations (if calculated)
- Display portfolio insights

### 3. View in Dashboard

The dashboard automatically shows your portfolio if you have one created.

Open: http://localhost:8080

## 📊 Features

### Portfolio Management
- **Create portfolios** with multiple holdings
- **Weight-based** or **amount-based** entry
- **Multiple portfolios** per user
- **Database persistence**

### Market Matching
Automatically finds relevant prediction markets for each holding:

**Crypto Holdings:**
- BTC → Bitcoin halving, ETF approvals, regulation
- ETH → Protocol upgrades, DeFi events, network changes
- SOL → Network events, outages, upgrades

**Stock Holdings:**
- SPY → Fed decisions, elections, economic data
- NVDA → Earnings, product launches, AI regulation
- TLT → Fed decisions, inflation data

### Personalized Correlations
- Tracks correlations between YOUR holdings and relevant markets
- Shows which markets have the strongest impact on your portfolio
- Identifies high-impact markets that affect multiple holdings

### Portfolio Alerts
- Alerts when relevant markets move
- Shows expected impact on your holdings
- Prioritizes by portfolio weight

## 🔧 API Usage

### Create Portfolio
```bash
curl -X POST http://localhost:8080/api/portfolios \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Crypto Portfolio",
    "holdings": [
      {"symbol": "BTC", "weight": 0.5},
      {"symbol": "ETH", "weight": 0.3},
      {"symbol": "SOL", "weight": 0.2}
    ]
  }'
```

### List Portfolios
```bash
curl http://localhost:8080/api/portfolios
```

### Analyze Portfolio
```bash
curl http://localhost:8080/api/portfolio/<portfolio_id>/analyze
```

## 📈 Example Output

### Portfolio Analysis
```
📊 Analyzing Portfolio: My Crypto Portfolio

Holdings:
  BTC: 50.0%
  ETH: 30.0%
  SOL: 20.0%

🔍 Finding relevant prediction markets...

📈 Relevant Markets by Holding:

BTC:
  1. ✅ Will Bitcoin ETF be approved in Q1 2024?
     Correlation: 0.731 | Relevance: 8.5
  2. ✅ Will Bitcoin halving occur before May 2024?
     Correlation: 0.612 | Relevance: 7.2

ETH:
  1. ✅ Will Ethereum upgrade complete in Q2 2024?
     Correlation: 0.689 | Relevance: 6.8

💡 Portfolio Insights:

🎯 High Impact Market:
   Will Bitcoin ETF be approved in Q1 2024?
   Affects: BTC
   Portfolio weight: 50.0%
   Priority: HIGH

🔗 Strongest Correlation:
   BTC ↔ Will Bitcoin ETF be approved in Q1 2024?
   Correlation: 0.731 (p=0.0023)
```

## 🎯 Use Cases

### 1. Crypto Trader
- Hold BTC, ETH, SOL
- Wants to know which events to watch
- Gets alerts when relevant markets move

### 2. Stock Investor
- Hold SPY, QQQ, individual stocks
- Wants macro event radar
- Sees which Fed decisions/elections matter

### 3. Mixed Portfolio
- Hold both crypto and stocks
- Wants unified view
- Sees cross-asset correlations

## 🔮 Future Enhancements

### On-Chain Integration
```python
# Connect wallet addresses
portfolio.add_holdings_from_addresses(["0x123...", "0x456..."])
```

### Broker API Integration
```python
# Connect to broker (Coinbase, Binance, etc.)
portfolio.sync_from_broker(api_key)
```

### Event Calendar
- Upcoming Fed meetings
- Earnings dates
- Protocol upgrades
- Regulatory deadlines

### Backtesting
- "How would my portfolio have performed if I followed these signals?"
- Historical correlation analysis

## 📁 Files

- `portfolio.py` - Portfolio management
- `market_matcher.py` - Matches holdings to markets
- `portfolio_correlations.py` - Personalized correlation tracking
- `portfolio_alerts.py` - Portfolio-specific alerts
- `manage_portfolio.py` - CLI for portfolio management
- `database.py` - Portfolio storage (updated)

## 🎯 The Value Proposition

**Before:** "Here are some correlations that might be useful"

**After:** "Here's exactly what matters for YOUR portfolio, ranked by impact"

This is the difference between a research tool and a personal assistant.

---

**Start tracking your portfolio today!**

```bash
python manage_portfolio.py create
```

