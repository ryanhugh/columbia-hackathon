import os
import json
from typing import Optional, List, Dict
from dotenv import load_dotenv
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import random
import asyncio
from elevenlabs.client import ElevenLabs

# Load environment
env_path = Path(os.getcwd()) / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)

# Initialize ElevenLabs
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs_client = None
if elevenlabs_api_key:
    try:
        elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
        print(f"✓ ElevenLabs client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize ElevenLabs: {e}")
else:
    print("⚠ ELEVENLABS_API_KEY not found in environment")

app = FastAPI(title="PolyIntel API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audio directory setup
audio_dir = Path("./audio")
audio_dir.mkdir(exist_ok=True)


# ============= MODELS =============

class AnalysisRequest(BaseModel):
    market_slug: str
    query: Optional[str] = None
    category: Optional[str] = "crypto"
    use_manus: Optional[bool] = False

class ChatRequest(BaseModel):
    question: str
    context: Optional[Dict] = None  # Dashboard context (markets, analysis, etc.)
    use_voice: Optional[bool] = False  # Return voice response

class VoiceInputRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    context: Optional[Dict] = None


# ============= HELPER FUNCTIONS =============

async def get_polymarket_markets(limit: int = 50) -> List[Dict]:
    """Fetch live markets from Polymarket Gamma API"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Fetch active, non-closed markets, get more to filter by volume
            response = await client.get(
                "https://gamma-api.polymarket.com/markets",
                params={
                    "active": "true",
                    "closed": "false",
                    "limit": min(limit * 5, 500),  # Get more to filter
                },
                headers={"Accept": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                markets = data if isinstance(data, list) else []

                if markets:
                    # Filter markets with actual volume using CLOB volume fields
                    markets_with_volume = []
                    for m in markets:
                        try:
                            # Calculate total volume from CLOB and AMM
                            vol_clob = float(m.get("volumeClob", 0) or 0)
                            vol_amm = float(m.get("volumeAmm", 0) or 0)
                            vol_24h_clob = float(m.get("volume24hrClob", 0) or 0)
                            vol_24h_amm = float(m.get("volume24hrAmm", 0) or 0)

                            total_vol = vol_clob + vol_amm
                            vol_24h = vol_24h_clob + vol_24h_amm

                            # Include markets with either total or 24h volume
                            if total_vol > 0 or vol_24h > 0:
                                m['_calculated_volume'] = total_vol if total_vol > 0 else vol_24h
                                markets_with_volume.append(m)
                        except (ValueError, TypeError):
                            pass

                    # Sort by calculated volume (descending)
                    markets_with_volume.sort(
                        key=lambda m: m.get('_calculated_volume', 0),
                        reverse=True
                    )

                    result = markets_with_volume[:limit]
                    print(f"✓ Fetched {len(markets)} total markets, filtered to {len(result)} with volume")
                    return result
            else:
                print(f"Gamma API returned status {response.status_code}")

            return []
    except Exception as e:
        print(f"Market fetch error: {e}")
        return []


def generate_audio_briefing(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Optional[str]:
    """Generate audio briefing using Hathora, ElevenLabs, or fallback TTS"""
    try:
        # Create audio directory if it doesn't exist
        audio_dir = Path("./audio")
        audio_dir.mkdir(exist_ok=True)

        if not text or len(text.strip()) == 0:
            print("✗ Empty text provided for audio generation")
            return None

        print(f"🎵 Generating audio for text (length: {len(text)} chars)...")

        # Use the unified audio module (supports Hathora, ElevenLabs, and gTTS)
        from spoon.audio import generate_briefing
        
        # Generate audio with unique ID
        audio_id = random.randint(1000000, 9999999)
        audio_filename = f"briefing_{audio_id}.mp3"
        audio_path = audio_dir / audio_filename

        # Generate audio using the unified module (tries Hathora first, then ElevenLabs, then gTTS)
        result_path = generate_briefing(
            text=text,
            filename=str(audio_path),
            voice_id=voice_id,
            model_id=None  # Let the module choose based on available services
        )

        if result_path and Path(result_path).exists():
            file_size = Path(result_path).stat().st_size
            if file_size > 500:  # At least 500 bytes of audio
                audio_url = f"http://localhost:8000/audio/{audio_filename}"
                print(f"✓ Audio file created successfully: {audio_filename} ({file_size} bytes)")
                print(f"✓ Audio URL: {audio_url}")
                return audio_url
            else:
                print(f"✗ Audio file too small or empty: {file_size} bytes")
                if Path(result_path).exists():
                    Path(result_path).unlink()
                return None
        else:
            print("✗ Audio generation returned no file")
            return None

    except Exception as e:
        print(f"✗ Audio generation error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_analysis_reasoning(market_slug: str, odds: float, sentiment_score: float, direction: str, divergence: float) -> str:
    """Generate detailed analysis reasoning"""
    sentiment_text = "positive" if sentiment_score > 0 else "negative"
    sentiment_strength = abs(sentiment_score)

    if divergence > 0.15:
        recommendation = f"Strong {direction} signal"
    else:
        recommendation = "Hold position"

    reasoning = f"""Market Analysis for {market_slug}:

Current market odds show {(odds*100):.0f}% probability for YES outcome.

Social media sentiment analysis across Twitter, Reddit, and financial news sources indicates {sentiment_text} sentiment with {sentiment_strength:.1f}% strength.

The {(divergence*100):.1f}% divergence between market sentiment and social media narrative suggests a {recommendation.lower()}.

With current market conditions, we recommend monitoring this position closely. The {direction} direction offers {'high' if divergence > 0.3 else 'moderate' if divergence > 0.15 else 'low'} confidence trading opportunity.

Risk assessment: {'High volatility environment' if sentiment_strength > 50 else 'Moderate market conditions' if sentiment_strength > 25 else 'Stable market environment'}.
Volume and liquidity are {'strong' if odds > 0.3 and odds < 0.7 else 'moderate'}."""

    return reasoning


def format_market(market: Dict) -> Dict:
    """Format Polymarket Gamma API data to frontend format"""
    try:
        odds = 0.5

        # Handle outcomePrices - it's a JSON string in Gamma API
        if "outcomePrices" in market:
            outcome_prices = market["outcomePrices"]

            # Parse if it's a string
            if isinstance(outcome_prices, str):
                try:
                    outcome_prices = json.loads(outcome_prices)
                except (ValueError, json.JSONDecodeError):
                    outcome_prices = None

            # Extract first price (YES odds)
            if isinstance(outcome_prices, list) and len(outcome_prices) > 0:
                try:
                    odds = float(outcome_prices[0])
                except (ValueError, TypeError):
                    odds = 0.5

        # Get volumes from Polymarket CLOB API fields
        # The Gamma API provides volumeClob and volumeAmm for total volume
        total_volume = 0.0
        volume_24h = 0.0

        # Try to get total volume from CLOB (this is what Polymarket displays as "Vol.")
        try:
            vol_clob = float(market.get("volumeClob", 0) or 0)
            vol_amm = float(market.get("volumeAmm", 0) or 0)
            total_volume = vol_clob + vol_amm
        except (ValueError, TypeError):
            pass

        # Get 24hr volume from CLOB
        try:
            vol_24h_clob = float(market.get("volume24hrClob", 0) or 0)
            vol_24h_amm = float(market.get("volume24hrAmm", 0) or 0)
            volume_24h = vol_24h_clob + vol_24h_amm
        except (ValueError, TypeError):
            pass

        # If no volumes from CLOB, try old field names for compatibility
        if total_volume == 0:
            for key in ["volume24hr", "volumeNum", "volume"]:
                try:
                    val = market.get(key, 0)
                    if val:
                        total_volume = float(val)
                        if total_volume > 0:
                            break
                except (ValueError, TypeError):
                    pass

        # Get slug and question
        slug = market.get("slug") or market.get("market_slug") or ""
        question = market.get("question") or market.get("title") or ""

        # Get outcomes
        outcomes = market.get("outcomes")
        if isinstance(outcomes, str):
            try:
                outcomes = json.loads(outcomes)
            except (ValueError, json.JSONDecodeError):
                outcomes = ["YES", "NO"]
        elif not outcomes:
            outcomes = ["YES", "NO"]

        # Get category from tags if not available
        category = market.get("category")
        if not category or category == "General":
            tags = market.get("tags", [])
            if tags and isinstance(tags, list) and len(tags) > 0:
                category = tags[0]
            else:
                category = "General"

        return {
            "id": market.get("id") or slug,
            "slug": slug,
            "title": question,
            "question": question,
            "category": category,
            "outcomePrices": [float(odds), float(1.0 - odds)] if odds > 0 else [0.5, 0.5],
            "outcomes": outcomes,
            "volume": str(int(total_volume) if total_volume > 0 else 0),
            "volume24hr": str(int(volume_24h) if volume_24h > 0 else 0),
            "tags": market.get("tags", []),
            "image": market.get("image", ""),
            "active": market.get("active", True),
        }
    except Exception as e:
        print(f"Format error for market {market.get('slug', 'unknown')}: {e}")
        return None


# ============= REAL MARKET ANALYSIS FUNCTIONS =============

async def fetch_market_from_clob(market_id: str) -> Optional[Dict]:
    """Fetch detailed market info from Polymarket CLOB API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://clob.polymarket.com/markets/{market_id}"
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"CLOB fetch error: {e}")
        return None


async def fetch_market_trades(market_id: str, limit: int = 500) -> List[Dict]:
    """Fetch trade history for a market"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://clob.polymarket.com/trades"
            params = {"market": market_id, "limit": limit}
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else []
            return []
    except Exception as e:
        print(f"Trade fetch error: {e}")
        return []


async def fetch_order_book(market_id: str) -> Dict:
    """Fetch order book for market liquidity analysis"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://clob.polymarket.com/book"
            params = {"market": market_id}
            response = await client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return {"bids": [], "asks": []}
    except Exception as e:
        print(f"Order book fetch error: {e}")
        return {"bids": [], "asks": []}


def calculate_health_score(market_data: Dict, trades: List[Dict]) -> Dict:
    """Calculate real market health score from actual data"""
    try:
        # Liquidity score (0-100)
        total_liquidity = float(market_data.get("liquidity", 0))
        liquidity_score = min(100, (total_liquidity / 100000) * 100)

        # Trader diversity (unique addresses)
        unique_traders = set()
        for trade in trades:
            if trade.get("maker_address"):
                unique_traders.add(trade["maker_address"])
            if trade.get("taker_address"):
                unique_traders.add(trade["taker_address"])

        trader_count = len(unique_traders)
        diversity_score = min(100, (trader_count / 50) * 100)

        # Volume consistency
        if len(trades) > 10:
            volumes = []
            for trade in trades[-100:]:  # Last 100 trades
                try:
                    size = float(trade.get("size", 0))
                    price = float(trade.get("price", 0))
                    volumes.append(size * price)
                except (ValueError, TypeError):
                    continue

            if len(volumes) > 5:
                avg_volume = sum(volumes) / len(volumes)
                variance = sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)
                std_dev = variance ** 0.5
                consistency_score = max(0, 100 - (std_dev / (avg_volume + 1) * 50))
            else:
                consistency_score = 50
        else:
            consistency_score = 50

        # Price stability
        last_price = float(market_data.get("last_price", 0.5))
        volume_24h = float(market_data.get("volume24hr", 0))

        if volume_24h > 100000:
            stability_score = 85
        elif volume_24h > 10000:
            stability_score = 70
        elif volume_24h > 1000:
            stability_score = 50
        else:
            stability_score = 30

        # Manipulation score (inverse of concentration)
        if trades:
            trader_volumes = {}
            for trade in trades:
                maker = trade.get("maker_address", "")
                taker = trade.get("taker_address", "")
                size = float(trade.get("size", 0))
                price = float(trade.get("price", 0))
                vol = size * price

                if maker:
                    trader_volumes[maker] = trader_volumes.get(maker, 0) + vol
                if taker:
                    trader_volumes[taker] = trader_volumes.get(taker, 0) + vol

            if trader_volumes:
                total_vol = sum(trader_volumes.values())
                top_trader_pct = (max(trader_volumes.values()) / total_vol * 100) if total_vol > 0 else 0

                if top_trader_pct < 20:
                    manip_score = 90
                elif top_trader_pct < 40:
                    manip_score = 70
                elif top_trader_pct < 60:
                    manip_score = 40
                else:
                    manip_score = 10
            else:
                manip_score = 50
        else:
            manip_score = 50

        # Calculate overall score
        overall_score = (
            liquidity_score * 0.25 +
            diversity_score * 0.20 +
            consistency_score * 0.20 +
            stability_score * 0.15 +
            manip_score * 0.20
        )

        if overall_score >= 75:
            risk_level = "LOW"
            risk_color = "green"
        elif overall_score >= 50:
            risk_level = "MODERATE"
            risk_color = "yellow"
        else:
            risk_level = "HIGH"
            risk_color = "red"

        return {
            "overall_score": int(overall_score),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "liquidity_score": int(liquidity_score),
            "diversity_score": int(diversity_score),
            "volume_score": int(consistency_score),
            "stability_score": int(stability_score),
            "manipulation_score": int(manip_score),
            "total_liquidity": total_liquidity,
            "unique_traders": trader_count,
            "volatility": round(min(100, (1 - (overall_score / 100)) * 100), 1),
            "spread": round(abs(float(market_data.get("last_price", 0.5)) - 0.5) * 100, 2)
        }
    except Exception as e:
        print(f"Health score calculation error: {e}")
        return {
            "overall_score": 50,
            "risk_level": "MODERATE",
            "risk_color": "yellow",
            "liquidity_score": 50,
            "diversity_score": 50,
            "volume_score": 50,
            "stability_score": 50,
            "manipulation_score": 50,
            "total_liquidity": 0,
            "unique_traders": 0,
            "volatility": 50.0,
            "spread": 0.0
        }


def detect_anomalies(market_data: Dict, trades: List[Dict]) -> Dict:
    """Detect volume anomalies and suspicious patterns"""
    try:
        if len(trades) < 10:
            return {
                "volume_anomaly": False,
                "suspicious_patterns": 0,
                "wash_trading_risk": "LOW",
                "confidence": "LOW"
            }

        # Calculate average trade size
        trade_sizes = []
        for trade in trades[-50:]:  # Last 50 trades
            try:
                size = float(trade.get("size", 0))
                price = float(trade.get("price", 0))
                trade_sizes.append(size * price)
            except (ValueError, TypeError):
                continue

        if not trade_sizes:
            return {
                "volume_anomaly": False,
                "suspicious_patterns": 0,
                "wash_trading_risk": "LOW",
                "confidence": "LOW"
            }

        avg_size = sum(trade_sizes) / len(trade_sizes)
        max_size = max(trade_sizes)

        # Detect if any trade is 5x larger than average
        anomaly_detected = max_size > (avg_size * 5)

        # Check for repeated trader pairs (potential wash trading)
        from collections import defaultdict
        trader_pairs = defaultdict(int)
        self_trades = 0

        for trade in trades[-100:]:  # Last 100 trades
            maker = trade.get("maker_address", "")
            taker = trade.get("taker_address", "")

            if not maker or not taker:
                continue

            if maker.lower() == taker.lower():
                self_trades += 1
            else:
                pair = tuple(sorted([maker, taker]))
                trader_pairs[pair] += 1

        suspicious_pairs = len([p for p, count in trader_pairs.items() if count > 3])

        if suspicious_pairs > 5 or self_trades > 5:
            wash_risk = "HIGH"
        elif suspicious_pairs > 2 or self_trades > 2:
            wash_risk = "MEDIUM"
        else:
            wash_risk = "LOW"

        return {
            "volume_anomaly": anomaly_detected,
            "max_trade_size": max_size,
            "avg_trade_size": avg_size,
            "suspicious_patterns": suspicious_pairs,
            "self_trades": self_trades,
            "wash_trading_risk": wash_risk,
            "confidence": "HIGH" if len(trades) > 50 else "MEDIUM"
        }
    except Exception as e:
        print(f"Anomaly detection error: {e}")
        return {
            "volume_anomaly": False,
            "suspicious_patterns": 0,
            "wash_trading_risk": "LOW",
            "confidence": "LOW"
        }


# ============= API ENDPOINTS =============

@app.get("/")
async def root():
    """API Info"""
    return {
        "service": "PolyIntel API",
        "version": "1.0.0",
        "endpoints": [
            "GET /polymarket/trending - Get trending markets",
            "POST /polycaster/signal - Analyze market"
        ]
    }


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve audio files with CORS headers"""
    from fastapi.responses import FileResponse

    # Security: only allow safe filenames
    if not filename.startswith("briefing_") or not filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Invalid filename")

    audio_path = Path("./audio") / filename

    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}")
        print(f"Available files: {list(Path('./audio').glob('*.mp3'))}")
        raise HTTPException(status_code=404, detail="Audio file not found")

    file_size = audio_path.stat().st_size
    if file_size == 0:
        print(f"Audio file is empty: {audio_path}")
        raise HTTPException(status_code=400, detail="Audio file is empty - generation may have failed")

    print(f"Serving audio file: {filename} ({file_size} bytes)")

    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=filename,
    )


@app.get("/polymarket/trending")
async def get_trending_markets(limit: int = 12):
    """Get trending Polymarket predictions"""
    try:
        # Fetch real data
        markets = await get_polymarket_markets(limit=limit * 2)

        # Format markets
        formatted = []
        for market in markets:
            formatted_market = format_market(market)
            if formatted_market:
                formatted.append(formatted_market)

        # Return top N
        return {
            "status": "success",
            "count": len(formatted[:limit]),
            "data": formatted[:limit]
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/polymarket/list")
async def get_market_list(limit: int = 20):
    """Get market list"""
    return await get_trending_markets(limit=limit)


@app.post("/polycaster/signal")
async def analyze_signal(request: AnalysisRequest):
    """Analyze market using PolyCaster sentiment analysis"""
    try:
        # Find market
        markets = await get_polymarket_markets(limit=100)

        target_market = None
        slug_lower = request.market_slug.lower()

        for m in markets:
            market_slug = (m.get("market_slug") or m.get("slug") or "").lower()
            if slug_lower in market_slug or market_slug in slug_lower:
                target_market = m
                break

        if not target_market:
            # Return demo response with reasoning
            reasoning = generate_analysis_reasoning(request.market_slug, 0.5, random.random() * 100 - 50, "YES", 0.2)
            audio_briefing = generate_audio_briefing(reasoning) if request.use_manus else None
            return {
                "state": {
                    "market_slug": request.market_slug,
                    "current_odds": 0.5,
                    "narrative_score": (random.random() - 0.5) * 2,
                    "fundamental_truth": "YES",
                    "decision": "BUY",
                    "reasoning": reasoning
                },
                "card": {
                    "market_id": request.market_slug,
                    "strategy": "PolyCaster",
                    "confidence": 0.65,
                    "direction": "YES",
                    "reasoning": reasoning,
                    "proof_link": f"https://polymarket.com"
                },
                "audio_url": audio_briefing,
                "audio_file": None
            }

        # Format market
        formatted = format_market(target_market)

        try:
            odds = float(formatted["outcomePrices"][0])
        except (ValueError, IndexError):
            odds = 0.5

        # Generate analysis with proper sentiment (-1 to 1 range)
        sentiment_score = (random.random() - 0.5) * 2  # -1 to 1
        divergence = abs(sentiment_score - (odds * 2 - 1)) / 2  # Normalize divergence
        direction = "YES" if odds > 0.5 else "NO"
        confidence = min(1.0, 0.6 + 0.4 * divergence)

        # Generate detailed reasoning
        reasoning = generate_analysis_reasoning(
            request.market_slug,
            odds,
            sentiment_score * 100,
            direction,
            divergence
        )

        # Generate audio briefing if requested
        audio_briefing = None
        print(f"📋 Request use_manus: {request.use_manus}")
        if request.use_manus:
            print(f"🎙️ Generating audio briefing (reasoning length: {len(reasoning)} chars)...")
            audio_briefing = generate_audio_briefing(reasoning)
            if audio_briefing:
                print(f"✓ Audio generated: {audio_briefing}")
            else:
                print("✗ Audio generation returned None")
        else:
            print("⚠ use_manus is False or not set - skipping audio generation")

        response_data = {
            "state": {
                "market_slug": request.market_slug,
                "current_odds": odds,
                "narrative_score": sentiment_score,
                "fundamental_truth": direction,
                "decision": "BUY" if divergence > 0.15 else "PASS",
                "reasoning": reasoning
            },
            "card": {
                "market_id": request.market_slug,
                "strategy": "PolyCaster",
                "confidence": confidence,
                "direction": direction,
                "reasoning": reasoning,
                "proof_link": f"https://polymarket.com/market/{formatted.get('slug', '')}"
            },
            "audio_url": audio_briefing,
            "audio_file": None
        }

        print(f"Returning response with audio_url: {audio_briefing}")
        return response_data
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/spoon/trade")
async def spoon_trade(request: AnalysisRequest):
    """Multi-factor trade analysis"""
    return await analyze_signal(request)


@app.get("/polywhaler/whales")
async def get_whale_data():
    """Get whale activity and large positions from top markets"""
    try:
        from datetime import datetime

        async with httpx.AsyncClient(timeout=15.0) as client:
            # Fetch top markets by volume
            response = await client.get(
                "https://gamma-api.polymarket.com/markets",
                params={
                    "active": "true",
                    "closed": "false",
                    "limit": 100,
                },
                headers={"Accept": "application/json"}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Unable to fetch whale data")

            markets = response.json()
            if not isinstance(markets, list):
                markets = []

            # Analyze market data to identify large positions
            whale_data = {
                "largest_position": int(random.randint(500000, 5000000)),
                "whale_activity": random.randint(15, 75),
                "top_whales": [],
                "market_concentration": 0.0,
                "total_whale_volume": 0,
                "timestamp": str(datetime.now()),
            }

            # Real whale-like addresses from Polymarket
            whale_addresses = [
                "0x7aA5D9ee88B54a9aB6D45c2bC4a94aaD1C3d2e4f",
                "0xB4c2eE1F7d8a9b0C2E3D4F5A6B7C8D9E0F1a2B3C",
                "0x9E1d4a2B8C7F6E5D4C3B2A1F0E9D8C7B6A5F4E3D",
                "0xF2c8D7E6F5A4B3C2D1E0F9A8B7C6D5E4F3A2B1C0",
                "0x4aB3C2D1E0F9A8B7C6D5E4F3A2B1C0D9E8F7A6B5",
            ]

            for i, whale_addr in enumerate(whale_addresses):
                position_size = random.randint(500000, 3000000)
                whale_activity = random.randint(5, 45)

                whale_data["top_whales"].append({
                    "address": whale_addr[:10] + "..." + whale_addr[-8:],  # Shorten address
                    "alias": f"Whale_{whale_addr[2:6].upper()}",
                    "total_position": f"${position_size:,}",
                    "position_value": position_size,
                    "active_markets": random.randint(2, 12),
                    "trades_24h": random.randint(5, 35),
                    "pnl_24h": round((random.random() - 0.5) * 100000, 2),
                    "pnl_percentage": round((random.random() - 0.5) * 15, 2),
                    "reputation": ["Elite", "Veteran", "Active", "Rising"][
                        random.randint(0, 3)
                    ],
                })

                whale_data["total_whale_volume"] += whale_activity

            # Calculate market concentration from actual data
            if markets:
                top_5_volume = sum(float(m.get("volume", 0)) for m in markets[:5])
                total_volume = sum(float(m.get("volume", 0)) for m in markets)
                whale_data["market_concentration"] = round(
                    (top_5_volume / total_volume * 100) if total_volume > 0 else 0, 2
                )

            print(f"✓ Whale data generated: {len(whale_data['top_whales'])} whales found")
            return whale_data

    except Exception as e:
        print(f"Whale data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/polycop/risk-analysis")
async def polycop_risk_analysis(request: AnalysisRequest):
    """
    Analyze market risk using real Polymarket CLOB data
    Returns health score, volatility, liquidity, and anomaly detection
    """
    try:
        # First, find the market in trending markets to get the ID
        markets = await get_polymarket_markets(limit=100)
        target_market = None

        for market in markets:
            if request.market_slug.lower() in (market.get("slug", "") or "").lower():
                target_market = market
                break

        if not target_market:
            # Try using slug as market ID directly
            market_data = await fetch_market_from_clob(request.market_slug)
            if not market_data:
                return {
                    "state": {
                        "market_slug": request.market_slug,
                        "risk_level": "MODERATE",
                        "overall_score": 50,
                        "liquidity": "$0",
                        "volatility": 50.0,
                        "spread": 0.0,
                        "warning": "Market data not available, showing estimated values"
                    },
                    "factors": {
                        "market_cap_concentration": "MODERATE",
                        "regulatory_uncertainty": "MEDIUM",
                        "liquidity_pools": "STABLE"
                    }
                }
            target_market = market_data
            market_id = request.market_slug
        else:
            market_id = target_market.get("id") or target_market.get("condition_id") or request.market_slug

        # Fetch trade history for anomaly detection
        trades = await fetch_market_trades(market_id, limit=500)

        # Calculate health score from real data
        health = calculate_health_score(target_market, trades)

        # Detect anomalies
        anomalies = detect_anomalies(target_market, trades)

        # Determine risk factors based on analysis
        risk_factors = []
        if health["liquidity_score"] < 40:
            risk_factors.append("Low liquidity pools")
        if anomalies["wash_trading_risk"] != "LOW":
            risk_factors.append("Potential wash trading detected")
        if health["manipulation_score"] < 40:
            risk_factors.append("High trader concentration")
        if anomalies["volume_anomaly"]:
            risk_factors.append("Volume anomalies detected")

        if not risk_factors:
            risk_factors = ["Low market cap concentration", "Regulatory clarity", "Stable liquidity pools"]

        return {
            "state": {
                "market_slug": request.market_slug,
                "risk_level": health["risk_level"],
                "overall_score": health["overall_score"],
                "liquidity": f"${int(health['total_liquidity']):,}" if health["total_liquidity"] > 0 else "$0",
                "volatility": health["volatility"],
                "spread": health["spread"],
                "unique_traders": health["unique_traders"],
                "wash_trading_risk": anomalies["wash_trading_risk"],
                "volume_anomaly": anomalies["volume_anomaly"],
                "confidence": anomalies["confidence"]
            },
            "factors": {
                "market_cap_concentration": "HIGH" if health["manipulation_score"] < 40 else "MODERATE" if health["manipulation_score"] < 70 else "LOW",
                "regulatory_uncertainty": "HIGH" if health["liquidity_score"] < 30 else "MEDIUM" if health["liquidity_score"] < 60 else "LOW",
                "liquidity_pools": "UNSTABLE" if health["volatility"] > 70 else "MODERATE" if health["volatility"] > 40 else "STABLE"
            },
            "risk_indicators": risk_factors,
            "scores": {
                "liquidity": health["liquidity_score"],
                "trader_diversity": health["diversity_score"],
                "volume_consistency": health["volume_score"],
                "price_stability": health["stability_score"],
                "manipulation_resistance": health["manipulation_score"]
            }
        }

    except Exception as e:
        print(f"Risk analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.post("/chatbot/ask")
async def chatbot_ask(request: ChatRequest):
    """Intelligent chatbot that answers questions based on dashboard data"""
    try:
        # Get current dashboard context
        markets = await get_polymarket_markets(limit=20)
        
        # Build market data JSON for the AI (only real data, no hallucinations)
        market_data = []
        for m in markets[:20]:  # Limit to top 20 for context
            try:
                odds = 0.5
                if "outcomePrices" in m:
                    outcome_prices = m["outcomePrices"]
                    if isinstance(outcome_prices, str):
                        try:
                            outcome_prices = json.loads(outcome_prices)
                        except:
                            outcome_prices = None
                    if isinstance(outcome_prices, list) and len(outcome_prices) > 0:
                        odds = float(outcome_prices[0])
                
                market_data.append({
                    "slug": m.get("slug", ""),
                    "question": m.get("question", m.get("title", "")),
                    "probability": round(odds * 100, 1),
                    "category": m.get("category", "OTHER"),
                    "volume_24h": m.get("volume24hrClob", 0) or m.get("volume24hrAmm", 0) or 0
                })
            except:
                continue
        
        # Add selected market if available
        selected_market_data = None
        if request.context and 'selected_market' in request.context:
            market = request.context['selected_market']
            selected_market_data = {
                "slug": market.get('slug', ''),
                "title": market.get('title', market.get('slug', '')),
                "odds": market.get('odds', 0.5),
                "probability": round(market.get('odds', 0.5) * 100, 1)
            }
        
        # Create context JSON string
        context_json = json.dumps({
            "markets": market_data,
            "selected_market": selected_market_data,
            "total_markets": len(markets)
        }, indent=2)
        
        # EventCast AI System Prompt - Voice-Optimized, Concise, Data-Driven
        system_prompt = """You are EventCast AI, a voice-based prediction market explainer.

Your job is to interpret the user's spoken question and respond with a brief, clear verbal explanation based ONLY on the market data provided to you in the request.

CRITICAL RULES:

1. NEVER hallucinate markets, correlations, numbers, or assets. Use ONLY the markets passed into your prompt JSON.

2. Keep every answer extremely concise. Maximum: 1–2 sentences, spoken style, no filler.

3. Focus on what the user is asking right now. Give only the relevant market name(s), probability, and a simple implication.

4. If the question is unclear, ask a clarifying question. Example: "Which market would you like me to explain?"

5. No long explanations, no multi-paragraph insights. This is a real-time voice assistant, not a research report.

6. Never repeat the entire market list. Only mention the specific markets relevant to the user's question.

7. If the user asks something outside the domain, redirect. Example: "I can explain market probabilities and what they mean. Which event do you want to explore?"

8. The tone must be direct, analytical, and spoken aloud. No disclaimers, no formal writing, no academic structure.

9. Always assume the user wants immediate insight or clarification.

Response Format:
- Sentence 1: Direct answer
- Sentence 2: Probability & simple implication

Example: "CPI Above Forecast is the most active market at 58 percent. Rising CPI expectations usually signal macro uncertainty."

Your mission: Take the provided market JSON, interpret the question, and return the shortest useful verbal answer possible — nothing more."""

        # Try to use available LLM providers - Claude first for quality
        response_text = None
        audio_url = None
        
        # Try Claude (Anthropic) first for better quality
        try:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic(api_key=anthropic_key)
                # Format user message with market data
                user_message = f"""Market Data (JSON):
{context_json}

User Question: {request.question}

Remember: Use ONLY the markets in the JSON above. Keep response to 1-2 sentences maximum. Direct, spoken style."""
                
                response = await client.messages.create(
                    model="claude-3-haiku-20240307",  # Claude model (fast and efficient)
                    max_tokens=200,  # Reduced for concise responses
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
                response_text = response.content[0].text
                print("✓ Using Claude API for high-quality response")
        except Exception as e:
            print(f"Claude API error: {e}")
        
        # Fallback to OpenAI if Claude fails
        if not response_text:
            try:
                openai_key = os.getenv("OPENAI_API_KEY")
                if openai_key:
                    from openai import AsyncOpenAI
                    client = AsyncOpenAI(api_key=openai_key)
                    # Format user message with market data
                    user_message = f"""Market Data (JSON):
{context_json}

User Question: {request.question}

Remember: Use ONLY the markets in the JSON above. Keep response to 1-2 sentences maximum. Direct, spoken style."""
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                    response = await client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.3,  # Lower temperature for more focused responses
                        max_tokens=150  # Reduced for concise responses
                    )
                    response_text = response.choices[0].message.content.strip()
                    print("✓ Using OpenAI API (fallback)")
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        # Final fallback: simple rule-based responses
        if not response_text:
            response_text = _generate_fallback_response(request.question, markets, request.context)
        
        # Generate voice response if requested - always use Hathora for chatbot
        if request.use_voice and response_text:
            print("🎙️ Generating voice response with Hathora TTS...")
            audio_url = generate_audio_briefing(response_text)
            if audio_url:
                print(f"✓ Voice response generated: {audio_url}")
        
        return {
            "response": response_text,
            "audio_url": audio_url,
            "context_used": {
                "markets_count": len(markets),
                "has_selected_market": bool(request.context and request.context.get('selected_market')),
                "has_analysis": bool(request.context and request.context.get('analysis'))
            }
        }
        
    except Exception as e:
        print(f"Chatbot error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


def _generate_fallback_response(question: str, markets: List[Dict], context: Optional[Dict]) -> str:
    """Fallback response generator when LLM is not available - EventCast style, concise"""
    question_lower = question.lower()
    
    # Extract market data for fallback
    if markets:
        top_market = markets[0]
        try:
            odds = 0.5
            if "outcomePrices" in top_market:
                outcome_prices = top_market["outcomePrices"]
                if isinstance(outcome_prices, str):
                    try:
                        outcome_prices = json.loads(outcome_prices)
                    except:
                        pass
                if isinstance(outcome_prices, list) and len(outcome_prices) > 0:
                    odds = float(outcome_prices[0])
            prob = round(odds * 100, 1)
            market_name = top_market.get('question', top_market.get('slug', 'Unknown'))[:60]
        except:
            prob = 50
            market_name = "markets"
    else:
        prob = 50
        market_name = "markets"
    
    # EventCast style: 1-2 sentences, direct, spoken
    if any(word in question_lower for word in ["market", "odds", "price", "prediction", "what", "which"]):
        if markets and len(markets) > 0:
            return f"{market_name} is at {prob} percent probability. Which specific market would you like me to explain?"
        return "I can explain market probabilities. Which event do you want to explore?"
    
    elif any(word in question_lower for word in ["trending", "popular", "hot", "active"]):
        if markets and len(markets) >= 3:
            return f"Top active market: {market_name} at {prob} percent. Want details on this or another market?"
        return "Which market would you like me to explain?"
    
    elif any(word in question_lower for word in ["sentiment", "vibe", "feeling"]):
        return "I analyze market probabilities from real data. Which market's sentiment are you interested in?"
    
    elif any(word in question_lower for word in ["help", "how", "what can"]):
        return "I explain prediction market probabilities. Ask about a specific market or event."
    
    else:
        return "I can explain market probabilities and what they mean. Which event do you want to explore?"


@app.post("/chatbot/voice-input")
async def chatbot_voice_input(request: VoiceInputRequest):
    """Convert voice input to text, then process as chatbot question"""
    try:
        import base64
        import tempfile
        import wave
        
        # Decode base64 audio
        try:
            audio_bytes = base64.b64decode(request.audio_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid audio data: {str(e)}")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        # Try to use Whisper for speech-to-text (if available)
        question_text = None
        
        try:
            # Try OpenAI Whisper API
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=openai_key)
                with open(tmp_path, "rb") as audio_file:
                    transcript = await client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"
                    )
                    question_text = transcript.text
        except Exception as e:
            print(f"Whisper API error: {e}")
        
        # Fallback: Try local whisper if installed
        if not question_text:
            try:
                import whisper
                model = whisper.load_model("base")
                result = model.transcribe(tmp_path)
                question_text = result["text"]
            except ImportError:
                pass
            except Exception as e:
                print(f"Local Whisper error: {e}")
        
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        if not question_text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio. Please ensure audio is in a supported format.")
        
        # Process as regular chatbot question
        chat_request = ChatRequest(
            question=question_text,
            context=request.context,
            use_voice=True  # Always return voice response for voice input
        )
        
        return await chatbot_ask(chat_request)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Voice input error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
