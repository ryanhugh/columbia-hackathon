# 🚀 Columbia Hackathon - Polymarket Intelligence Suite

A dual-project repository containing two complementary Polymarket intelligence platforms built for the Columbia Hackathon.

## 📦 Projects Overview

This repository contains two distinct but complementary projects:

### 1. **PolyIntel** - AI-Powered Market Intelligence Platform
**Location:** `polyintel-main/`

An advanced AI-powered platform that transforms Polymarket data into actionable trading signals and audio briefings.

**Key Features:**
- 🎙️ **AI Podcast Briefings** - Converts market sentiment into engaging audio content
- 🤖 **Multi-Agent Analysis** - Uses OpenAI, Anthropic, and DeepSeek for comprehensive market analysis
- 📊 **Social Sentiment Tracking** - Aggregates data from Twitter, Reddit, and news sources
- 🎯 **Trading Signal Generation** - Real-time alerts for prediction market opportunities
- 🌐 **Full-Stack Application** - FastAPI backend + React frontend

**Tech Stack:**
- Backend: Python 3.12+, FastAPI, Uvicorn
- Frontend: React 18.3, Vite, Tailwind CSS
- AI: OpenAI, Anthropic Claude, DeepSeek
- Audio: ElevenLabs TTS
- Data Sources: Polymarket API, DeSearch, Tavily

### 2. **PolySignal** - Cross-Asset Signal Monitor
**Location:** `polynew-main/`

A personalized portfolio tracking system that monitors Polymarket prediction markets and generates trading signals for correlated assets (crypto, stocks, commodities).

**Key Features:**
- 🎯 **Personalized Portfolio Tracking** - Connect your holdings to relevant prediction markets
- 📊 **EdgeScore System** - Predictive power scoring (0-100) for market-asset relationships
- 🔷 **Hybrid Correlation Engine** - Uses real correlations when available, estimates otherwise
- 📈 **Real-Time Monitoring** - Live signal generation with statistical validation
- 📅 **Event Calendar** - Upcoming events relevant to your portfolio

**Tech Stack:**
- Backend: Python 3.8+, Flask
- Database: SQLite
- Analysis: NumPy, SciPy, Pandas
- Data Sources: Polymarket, CoinGecko

---

## 🚀 Quick Start

### PolyIntel Setup

```bash
# Navigate to PolyIntel
cd polyintel-main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Run backend
python -m uvicorn app.main:app --reload --port 8000

# In a new terminal, setup frontend
cd polyintel-ui
npm install
npm run dev
```

**Access:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### PolySignal Setup

```bash
# Navigate to PolySignal
cd polynew-main

# Install dependencies
pip install -r requirements.txt

# Configure API keys (optional)
cp .env.example .env

# Run dashboard
python dashboard.py
```

**Access:**
- Dashboard: http://localhost:8080
- Personalized View: http://localhost:8080/personalized

---

## 📁 Repository Structure

```
columbia-hackathon/
├── polyintel-main/           # AI-Powered Market Intelligence
│   ├── app/                  # FastAPI backend
│   ├── agents/               # AI agent implementations
│   ├── integrations/         # External API integrations
│   ├── polycaster/           # Podcast generation system
│   ├── polyintel-ui/         # React frontend
│   ├── spoon/                # Custom modules
│   ├── requirements.txt
│   ├── SETUP_LOCAL.md        # Detailed setup guide
│   ├── PODCAST_USAGE.md      # Podcast feature documentation
│   └── README files...
│
├── polynew-main/             # Cross-Asset Signal Monitor
│   ├── dashboard.py          # Flask web dashboard
│   ├── monitor_hybrid.py     # Hybrid monitoring system
│   ├── portfolio.py          # Portfolio management
│   ├── edgescore.py          # EdgeScore calculator
│   ├── database.py           # SQLite database
│   ├── templates/            # HTML templates
│   ├── requirements.txt
│   ├── README.md             # Project documentation
│   ├── EXECUTIVE_SUMMARY.md  # Business analysis
│   └── Documentation files...
│
└── README.md                 # This file
```

---

## 🎯 Use Cases

### PolyIntel - For Active Traders
- **Sentiment Analysis**: Get AI-powered sentiment briefings on market events
- **Audio Briefings**: Listen to market analysis while commuting
- **Multi-Source Intelligence**: Aggregate Twitter, Reddit, and news sentiment
- **Trading Signals**: Real-time alerts for prediction market opportunities

### PolySignal - For Portfolio Managers
- **Portfolio Correlation**: Track which prediction markets affect your holdings
- **Risk Monitoring**: Edge Intensity bars showing event-risk per asset
- **Lead Time Analysis**: Know when assets typically move after PM changes
- **Event Calendar**: Upcoming events relevant to your portfolio

---

## 🔑 Required API Keys

### PolyIntel
- **LLM Provider** (choose one): OpenAI, Anthropic, or DeepSeek
- **Market Data**: Polymarket API, DeSearch API
- **Audio** (optional): ElevenLabs API
- **Web3** (optional): Private key for trading
- **Additional** (optional): Tavily, OKX

### PolySignal
- **Market Data** (optional): CoinGecko API

---

## 📊 Key Features Comparison

| Feature | PolyIntel | PolySignal |
|---------|-----------|------------|
| **AI Analysis** | ✅ Multi-agent | ❌ |
| **Audio Briefings** | ✅ Podcast generation | ❌ |
| **Portfolio Tracking** | ❌ | ✅ EdgeScore system |
| **Real Correlations** | ❌ | ✅ Statistical validation |
| **Social Sentiment** | ✅ Twitter/Reddit/News | ❌ |
| **Trading Signals** | ✅ AI-powered | ✅ Correlation-based |
| **Web Interface** | ✅ React SPA | ✅ Flask dashboard |
| **Target Users** | Active traders | Portfolio managers |

---

## 📚 Documentation

### PolyIntel Documentation
- [SETUP_LOCAL.md](polyintel-main/SETUP_LOCAL.md) - Complete local setup guide
- [PODCAST_USAGE.md](polyintel-main/PODCAST_USAGE.md) - Podcast feature guide
- [ELEVENLABS_CUSTOMIZATION.md](polyintel-main/ELEVENLABS_CUSTOMIZATION.md) - Audio customization

### PolySignal Documentation
- [README.md](polynew-main/README.md) - Project overview
- [EXECUTIVE_SUMMARY.md](polynew-main/EXECUTIVE_SUMMARY.md) - Business context
- [HYBRID_SETUP.md](polynew-main/HYBRID_SETUP.md) - Hybrid system setup
- [PORTFOLIO_FEATURE.md](polynew-main/PORTFOLIO_FEATURE.md) - Portfolio tracking
- [PERSONALIZED_DASHBOARD.md](polynew-main/PERSONALIZED_DASHBOARD.md) - Dashboard features

---

## 🛠️ Development

### PolyIntel Development
```bash
# Backend with auto-reload
python -m uvicorn app.main:app --reload

# Frontend with HMR
npm run dev

# Run tests
python -m pytest
```

### PolySignal Development
```bash
# Run dashboard
python dashboard.py

# Collect historical data
python collect_data.py continuous 5 24

# Calculate correlations
python calculate_correlations.py calculate 7

# Manage portfolios
python manage_portfolio.py create
```

---

## ⚠️ Important Notes

- **Not Financial Advice**: These are monitoring and analysis tools, not investment advice
- **Risk Warning**: Trading and prediction markets involve risk of loss
- **API Costs**: Some features require paid API subscriptions
- **Data Privacy**: Keep your API keys and private keys secure
- **Educational Purpose**: Built for hackathon demonstration and learning

---

## 🤝 Contributing

Both projects welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is provided as-is for educational and research purposes.

---

## 🏆 Hackathon Context

Built for the Columbia Hackathon to demonstrate innovative applications of:
- Prediction market data analysis
- AI-powered market intelligence
- Cross-asset correlation tracking
- Real-time sentiment analysis
- Portfolio risk monitoring

---

## 📞 Support

For issues, questions, or feature requests:
- Check the documentation in each project folder
- Review the setup guides
- Open an issue on GitHub

---

**Transform prediction markets into actionable intelligence.** 🚀

**Built with ❤️ for the Columbia Hackathon**
