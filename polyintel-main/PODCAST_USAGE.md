# 🎙️ Crypto Sentiment Podcast Briefings

## What This Is
Your AI-powered podcast companion that scours social media (Twitter, Reddit, news) and turns market sentiment into engaging audio briefings for prediction market traders.

## 🚀 Quick Start

### Generate a Podcast Briefing
```bash
curl -X POST "http://localhost:8000/polycaster/podcast" \
  -H "Content-Type: application/json" \
  -d '{"query": "Bitcoin ETF approval", "category": "crypto"}'
```

### Listen to the Audio
```bash
afplay podcast_briefing_Bitcoin_ETF_approval_*.mp3
```

## 🎯 What Makes This Different

**For Prediction Market Degens:**
- Uses trader language ("apes are bullish", "degen mode", "fade the crowd")
- Focuses on what moves prediction markets, not just prices
- Identifies contrarian opportunities
- Timeline analysis (days vs weeks vs months)

**Conversational Style:**
- "What's up degens!" instead of "Welcome to your market briefing"
- "The real tea" instead of "comprehensive analysis"
- "YOLO your rent money" instead of "investment advice"

## 📊 Endpoints

### `/polycaster/podcast` - Generate Podcast Briefing
**Request:**
```json
{
  "query": "Ethereum staking",
  "category": "crypto",
  "duration": "PAST_24_HOURS"
}
```

**Response:**
```json
{
  "status": "success",
  "query": "Ethereum staking",
  "audio_file": "podcast_briefing_Ethereum_staking_123456.mp3",
  "audio_url": "/polyflow/audio/podcast_briefing_Ethereum_staking_123456.mp3",
  "sentiment_score": 0.75,
  "data_sources": {
    "total_items": 12,
    "tweet_count": 5,
    "post_count": 4,
    "news_count": 3
  }
}
```

## 🎛️ Customization

### Voice Settings
Add to `.env`:
```bash
# Make it sound more energetic for trading
ELEVENLABS_STABILITY="0.4"          # More variation
ELEVENLABS_SIMILARITY_BOOST="0.8"   # Clear voice
ELEVENLABS_STYLE="0.2"               # Slight personality
```

### AI Analysis Source
The system tries in order:
1. **OpenAI** (if `OPENAI_API_KEY` is set)
2. **Sudo** (if `SUDO_API_KEY` is set) 
3. **Fallback** (basic analysis)

## 🎧 Example Topics to Try

**High-Engagement Topics:**
```bash
# Bitcoin narratives
"Bitcoin halving 2024"
"Bitcoin institutional adoption"
"Bitcoin price prediction 2024"

# Ethereum ecosystem
"Ethereum Layer 2 solutions"
"Ethereum staking rewards"
"Ethereum vs Solana"

# DeFi Trends
"DeFi total value locked"
"Yield farming strategies"
"DeFi regulation news"

# Market Events
"Crypto market manipulation"
"Altcoin season 2024"
"Crypto bear market over"
```

## 🔥 What You'll Hear

Instead of: *"Market sentiment analysis indicates moderately bullish conditions..."*

You'll get: *"What's up degens! The crowd is leaning bullish right now, which means apes are feeling good about this play..."*

Instead of: *"Technical analysis suggests potential upside..."*

You'll get: *"Here's where it gets interesting for all you prediction market degens - this sentiment isn't just noise..."

## 📈 How to Use This

1. **Before Making Trades** - Get the crowd sentiment
2. **Finding Contrarian Plays** - Look for overhyped sentiment
3. **Timing Entries/Exits** - Sentiment often precedes price moves
4. **Research Supplement** - Combine with your own analysis

## ⚠️ Not Financial Advice
This is sentiment analysis, not trading advice. Always:
- Do your own research
- Consider multiple factors
- Never risk more than you can afford to lose
- Use sentiment as one tool among many

## 🛠️ Technical Details

**Data Sources:**
- Twitter (real-time tweets)
- Reddit (crypto subreddits)
- News (crypto publications)

**Processing:**
- Real-time sentiment scoring
- AI-powered analysis (OpenAI/Sudo)
- ElevenLabs text-to-speech
- ~2-3 minute audio briefings

**File Sizes:**
- Regular briefings: ~50KB (30 seconds)
- Podcast briefings: ~500KB-2MB (2-4 minutes)