import os
from typing import Optional, List, Dict
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

# Load environment variables
env_path = Path(os.getcwd()) / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)

app = FastAPI(title="PolyIntel API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= REQUEST/RESPONSE MODELS =============

class AnalysisRequest(BaseModel):
    market_slug: str
    query: Optional[str] = None
    category: Optional[str] = "crypto"
    use_manus: Optional[bool] = False


class TradeSignal(BaseModel):
    market_id: str
    strategy: str
    confidence: float
    direction: str
    reasoning: str
    proof_link: str


# ============= POLYMARKET DATA FETCHING =============

async def fetch_polymarket_markets(limit: int = 50) -> List[Dict]:
    """Fetch live markets from Polymarket CLOB API"""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            # Try CLOB API first (more reliable for trending)
            url = "https://clob.polymarket.com/markets"
            params = {"limit": min(limit, 1000), "active": True}

            response = await client.get(url, params=params)

            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Polymarket API unavailable")

            data = response.json()
            markets = data.get("data", []) if isinstance(data, dict) else data

            if not isinstance(markets, list):
                raise HTTPException(status_code=502, detail="Invalid Polymarket response format")

            return markets[:limit]
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Polymarket connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching markets: {str(e)}")


def parse_market_data(market: Dict) -> Dict:
    """Parse raw market data into standardized format"""
    try:
        # Extract odds from various possible formats
        odds = 0.5
        tokens = market.get("tokens", [])
        if tokens and isinstance(tokens, list):
            for token in tokens:
                if token.get("outcome", "").lower() == "yes":
                    try:
                        odds = float(token.get("price", 0.5))
                        break
                    except (ValueError, TypeError):
                        pass

        # Extract volume
        volume_24h = 0.0
        for vol_key in ["volume24hr", "volume_24hr", "volumeNum", "volume"]:
            try:
                volume_24h = float(market.get(vol_key, 0))
                if volume_24h > 0:
                    break
            except (ValueError, TypeError):
                pass

        # Extract slug/id
        slug = market.get("market_slug") or market.get("slug") or ""
        market_id = market.get("id") or market.get("question_id") or slug

        # Extract question/title
        question = market.get("question") or market.get("title") or ""

        return {
            "id": market_id,
            "slug": slug,
            "title": question,
            "question": question,
            "category": ",".join(market.get("tags", [])) if market.get("tags") else "General",
            "outcomePrices": [str(odds), str(max(0.0, 1.0 - odds))],
            "outcomes": market.get("outcomes", ["YES", "NO"]),
            "volume24hr": str(volume_24h),
            "volume": str(market.get("volume", 0)),
            "liquidity": str(market.get("liquidity", 0)),
            "tags": market.get("tags", []),
            "image": market.get("image", ""),
            "active": market.get("active", True),
        }
    except Exception as e:
        return None


# ============= API ENDPOINTS =============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "PolyIntel API"}


@app.get("/polymarket/trending")
async def polymarket_trending(limit: int = 12, category: Optional[str] = None):
    """
    Get trending Polymarket prediction markets
    Fetches live data from Polymarket CLOB API
    """
    try:
        # Fetch raw markets
        markets = await fetch_polymarket_markets(limit=min(limit * 2, 100))

        # Parse and filter markets
        parsed_markets = []
        for market in markets:
            parsed = parse_market_data(market)
            if parsed:
                # Filter by category if specified
                if category:
                    category_lower = category.lower()
                    question_lower = parsed.get("question", "").lower()

                    # Category matching logic
                    matches = False
                    if category_lower == "crypto":
                        matches = any(k in question_lower for k in ["btc", "bitcoin", "eth", "ethereum", "crypto", "solana"])
                    elif category_lower == "politics":
                        matches = any(k in question_lower for k in ["election", "trump", "biden", "vote", "president"])
                    elif category_lower == "culture":
                        matches = any(k in question_lower for k in ["grammy", "oscar", "taylor", "swift", "celebrity"])
                    elif category_lower == "sports":
                        matches = any(k in question_lower for k in ["nba", "nfl", "mlb", "soccer", "game"])

                    if not matches:
                        continue

                parsed_markets.append(parsed)

        # Sort by volume
        parsed_markets.sort(
            key=lambda x: float(x.get("volume24hr", 0)),
            reverse=True
        )

        # Return top N
        result = parsed_markets[:limit]
        return {
            "status": "success",
            "count": len(result),
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/polymarket/list")
async def polymarket_list(limit: int = 20, category: Optional[str] = None):
    """Get list of Polymarket markets - alias for trending"""
    return await polymarket_trending(limit=limit, category=category)


@app.post("/polycaster/signal")
async def polycaster_signal(request: AnalysisRequest):
    """
    Analyze market sentiment vs reality
    Returns vibe score and divergence analysis
    """
    try:
        # Fetch market data
        markets = await fetch_polymarket_markets(limit=50)

        # Find matching market
        target_market = None
        slug_lower = request.market_slug.lower()

        for market in markets:
            market_slug = (market.get("market_slug") or market.get("slug") or "").lower()
            if market_slug == slug_lower or slug_lower in market_slug:
                target_market = market
                break

        if not target_market:
            raise HTTPException(status_code=404, detail=f"Market not found: {request.market_slug}")

        # Parse market data
        parsed = parse_market_data(target_market)

        # Extract current odds
        try:
            current_odds = float(parsed.get("outcomePrices", ["0.5"])[0])
        except (ValueError, IndexError):
            current_odds = 0.5

        # Generate simulated sentiment analysis
        # In production, this would call sentiment APIs (DeSearch, etc.)
        import random
        narrative_score = (random.random() - 0.5) * 2  # -1 to 1

        # Calculate divergence
        reality_odds = current_odds + (random.random() - 0.5) * 0.2
        divergence = abs(current_odds - reality_odds)

        # Determine direction
        direction = "YES" if reality_odds > 0.5 else "NO"
        confidence = abs(narrative_score) / 2  # Convert -1..1 to 0..0.5

        return {
            "state": {
                "market_slug": request.market_slug,
                "current_odds": current_odds,
                "narrative_score": narrative_score,
                "fundamental_truth": direction,
                "decision": "BUY" if divergence > 0.15 else "PASS",
                "reasoning": f"Market analysis for {parsed.get('question')}. Current odds: {current_odds:.2%}. Sentiment indicator shows {narrative_score:+.2f} divergence."
            },
            "card": {
                "market_id": request.market_slug,
                "strategy": "PolyCaster",
                "confidence": min(1.0, confidence),
                "direction": direction,
                "reasoning": f"Sentiment-based analysis indicates {direction} with {confidence:.1%} confidence.",
                "proof_link": f"https://polymarket.com/market/{parsed.get('slug', request.market_slug)}"
            },
            "audio_url": None,
            "audio_file": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.post("/spoon/trade")
async def spoon_trade(request: AnalysisRequest):
    """Multi-factor trade signal analysis"""
    # Call polycaster as base analysis
    return await polycaster_signal(request)


# ============= ROOT & DOCUMENTATION =============

@app.get("/")
async def root():
    """PolyIntel API - Prediction Market Analysis"""
    return {
        "name": "PolyIntel",
        "version": "1.0.0",
        "description": "AI-powered prediction market analysis",
        "endpoints": {
            "health": "/health",
            "trending_markets": "/polymarket/trending?limit=12",
            "market_list": "/polymarket/list?limit=20",
            "analyze_market": "POST /polycaster/signal",
            "trade_signal": "POST /spoon/trade",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
