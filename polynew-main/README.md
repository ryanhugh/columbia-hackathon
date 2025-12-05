# 🚀 PolySignal - Prediction Market Cross-Asset Signal Monitor

**Transform prediction markets into personalized trading signals for your portfolio.**

PolySignal monitors Polymarket prediction markets and generates trading signals for correlated assets (crypto, stocks, commodities) based on real-time market movements and historical correlations.

## ✨ Features

### 🎯 Personalized Portfolio Tracking
- **Connect your holdings** - Track which prediction markets matter for YOUR portfolio
- **Edge Intensity Bars** - Visual indicators showing event-risk per asset
- **EdgeScore** - Predictive power score (0-100) for each market-asset relationship
- **Lead Time Analysis** - Know when assets typically move after PM changes

### 📊 Real-Time Monitoring
- **Live Signal Generation** - Alerts when significant PM movements occur
- **Hybrid Correlation Engine** - Uses real correlations when available, falls back to estimates
- **Statistical Validation** - P-values, confidence intervals, sample sizes

### 🔷 Personalized Dashboard
- **Portfolio Edge Map** - See which markets matter most for your holdings
- **Markets That Matter** - Ranked list with EdgeScores and lead times
- **Relationship Explorer** - Deep dive into PM-asset correlations
- **Event Calendar** - Upcoming events relevant to your portfolio

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys (Optional)

Create a `.env` file:
```bash
COINGECKO_API_KEY=your_key_here
```

Get a free CoinGecko API key at: https://www.coingecko.com/en/api

### 3. Run the Dashboard

```bash
python dashboard.py
```

Then open: **http://localhost:8080**

### 4. Create a Portfolio

```bash
python manage_portfolio.py create
```

## 📁 Project Structure

```
.
├── dashboard.py              # Web dashboard (Flask)
├── monitor.py               # Original monitor
├── monitor_hybrid.py        # Hybrid monitor (real + estimated)
├── portfolio.py              # Portfolio management
├── edgescore.py             # EdgeScore calculator
├── semantic_matcher.py      # Enhanced market matching
├── database.py              # SQLite database
├── data_collector.py        # Polymarket data collection
├── market_data.py           # Crypto/asset data
├── correlation_engine.py    # Original correlation engine
├── real_correlation_engine.py  # Real correlation engine
├── collect_data.py          # Historical data collection
├── calculate_correlations.py # Correlation calculator
├── manage_portfolio.py      # Portfolio CLI
└── templates/
    ├── dashboard.html       # Classic dashboard
    └── dashboard_personalized.html  # Personalized dashboard
```

## 🎯 Use Cases

### For Crypto Traders
- Track BTC, ETH, SOL holdings
- Get alerts for ETF approvals, halvings, upgrades
- See which events historically move your assets

### For Stock Investors
- Monitor SPY, QQQ, individual stocks
- Track Fed decisions, elections, economic data
- Personalized macro event radar

### For Mixed Portfolios
- Unified view of crypto + stocks
- Cross-asset correlation insights
- Event calendar for all holdings

## 📊 How It Works

1. **Data Collection**: Continuously collects Polymarket and asset prices
2. **Correlation Calculation**: Calculates real correlations from historical data
3. **Semantic Matching**: Matches your holdings to relevant prediction markets
4. **EdgeScore Calculation**: Scores predictive power of each relationship
5. **Signal Generation**: Alerts when relevant markets move significantly

## 🔧 Configuration

### Monitor Settings
Edit `monitor_hybrid.py`:
```python
monitor = HybridMonitor(
    min_price_change=5.0,  # Minimum % change to trigger
    check_interval=60      # Seconds between checks
)
```

### Data Collection
```bash
# Single collection
python collect_data.py single

# Continuous (every 5 min for 24 hours)
python collect_data.py continuous 5 24
```

### Calculate Correlations
```bash
# After collecting 1-2 weeks of data
python calculate_correlations.py calculate 7
```

## 📚 Documentation

- **[START_HERE.md](START_HERE.md)** - Project overview and strategy
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Business context
- **[HYBRID_SETUP.md](HYBRID_SETUP.md)** - Hybrid system setup guide
- **[PORTFOLIO_FEATURE.md](PORTFOLIO_FEATURE.md)** - Portfolio tracking guide
- **[PERSONALIZED_DASHBOARD.md](PERSONALIZED_DASHBOARD.md)** - Dashboard features
- **[DASHBOARD_README.md](DASHBOARD_README.md)** - Dashboard usage

## 🎨 Dashboard Views

### Personalized Dashboard (Default)
**http://localhost:8080/personalized**

- Portfolio overview with Edge Intensity
- Markets That Matter ranked table
- Relationship Explorer
- Event Calendar

### Classic Dashboard
**http://localhost:8080/classic**

- Recent signals
- Statistics
- Correlations
- Activity feed

## 🔌 API Endpoints

```bash
# Statistics
GET /api/stats

# Signals
GET /api/signals

# Correlations
GET /api/correlations

# Portfolios
GET /api/portfolios
POST /api/portfolios

# Markets That Matter
GET /api/markets-that-matter

# Relationship Data
GET /api/relationship/<market_id>/<asset>
```

## 🧮 EdgeScore Formula

```
EdgeScore = (|Correlation| × Stability × Significance × ImpactWeight) × 100
```

- **Correlation**: Pearson correlation (PM probability ↔ asset return)
- **Stability**: Rolling-window consistency (0-1)
- **Significance**: P-value mapped to 0-1 scale
- **ImpactWeight**: Asset/event type weighting

## ⚠️ Important Notes

- **Not Financial Advice**: This is a monitoring tool, not investment advice
- **Correlations are Estimates**: Based on historical patterns, not guarantees
- **Past Performance ≠ Future Results**: Always do your own research
- **Risk Warning**: Trading involves risk of loss

## 🛠️ Requirements

- Python 3.8+
- Flask 3.0+
- httpx
- numpy
- scipy
- python-dotenv

## 📄 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built for cross-market signal detection using prediction market intelligence.**

**Transform prediction markets into your personalized trading edge.** 🚀
