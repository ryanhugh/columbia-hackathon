from typing import Any, Optional, Dict
import os
import time
import httpx
import json
from integrations.de_search import DeSearchClient
from integrations.apro_oracle import AproOracleClient
from integrations.aioz import AiozClient

class MCPTools:
    def __init__(self) -> None:
        self.desearch = DeSearchClient()
        self.apro = AproOracleClient()
        self.aioz = AiozClient()
        self._cache: Dict[str, Any] = {}

    def _cache_get(self, key: str, ttl: float) -> Any:
        item = self._cache.get(key)
        if not item:
            return None
        value, ts = item
        if time.time() - ts > ttl:
            return None
        return value

    def _cache_set(self, key: str, value: Any) -> None:
        self._cache[key] = (value, time.time())

    async def market_odds(self, market_slug: str) -> float:
        base = os.getenv("POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com")
        url = f"{base}/events?slug={market_slug}"
        try:
            cached = self._cache_get(f"odds:{market_slug}", ttl=120.0)
            if cached is not None:
                return float(cached)
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=6.0)
                if res.status_code != 200:
                    ev = await client.get(f"{base}/events?search={market_slug}", timeout=6.0)
                    if ev.status_code != 200:
                        return 0.5
                    events = ev.json()
                    if not isinstance(events, list) or not events:
                        return 0.5
                    event = events[0]
                    markets = event.get("markets", [])
                    if not markets:
                        return 0.5
                    prices = markets[0].get("outcomePrices", [0.5])
                    yes_price = float(prices[0]) if prices else 0.5
                    self._cache_set(f"odds:{market_slug}", yes_price)
                    return yes_price
                data = res.json()
                markets = data[0].get("markets", [])
                if not markets:
                    return 0.5
                prices = markets[0].get("outcomePrices", [0.5])
                yes_price = float(prices[0]) if prices else 0.5
                self._cache_set(f"odds:{market_slug}", yes_price)
                return yes_price
        except Exception:
            return 0.5

    async def narrative(self, market_slug: str) -> float:
        data = await self.desearch.query_sentiment(market_slug)
        return float(data.get("score", 0.0))

    async def narrative_raw(self, query: str) -> dict:
        try:
            return await self.desearch.query_sentiment(query)
        except Exception:
            return {"score": 0.0}

    async def desearch_multi(self, query: str, category: str, date_filter: str = "PAST_24_HOURS") -> dict:
        key = f"desearch:{query}:{category}:{date_filter}"
        cached = self._cache_get(key, ttl=120.0)
        if cached is not None:
            return cached
        try:
            res = await self.desearch.search_multi(query, category, date_filter)
            self._cache_set(key, res)
            return res
        except Exception:
            return {"status": "error", "query": query}

    async def fundamental(self, market_slug: str) -> str:
        data = await self.apro.fetch_market_baseline(market_slug)
        d = data.get("direction", "YES")
        return d

    async def reasoning(self, strategy: str, context: dict) -> str:
        text = await self.aioz.generate_reasoning(strategy, context)
        if text:
            return text
        return (
            f"strategy={strategy} slug={context.get('market_slug','')} "
            f"odds={context.get('current_odds','')} narrative={context.get('narrative_score','')} "
            f"fundamental={context.get('fundamental_truth','')} decision={context.get('decision','')}"
        )

    async def kalshi_odds(self, market_slug: str) -> Optional[float]:
        base = os.getenv("KALSHI_BASE_URL", "https://api.kalshi.com/trade-api/v2")
        try:
            cached = self._cache_get(f"kalshi:{market_slug}", ttl=120.0)
            if cached is not None:
                return float(cached)
            async with httpx.AsyncClient() as client:
                url = f"{base}/markets"
                res = await client.get(url, params={"slug": market_slug}, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, dict):
                        odds = data.get("odds")
                        if odds is not None:
                            self._cache_set(f"kalshi:{market_slug}", float(odds))
                            return float(odds)
                res2 = await client.get(url, params={"text": market_slug}, timeout=5.0)
                if res2.status_code == 200:
                    data2 = res2.json()
                    if isinstance(data2, dict):
                        odds2 = data2.get("odds")
                        if odds2 is not None:
                            self._cache_set(f"kalshi:{market_slug}", float(odds2))
                            return float(odds2)
                return None
        except Exception:
            return None

    async def polymarket_search(self, query: str) -> dict:
        base = os.getenv("POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com")
        try:
            cached = self._cache_get(f"pm_search:{query}", ttl=120.0)
            if cached is not None:
                return cached
            async with httpx.AsyncClient() as client:
                # First try exact search, then broader search
                ev_res = await client.get(f"{base}/events", params={"search": query}, timeout=12.0)
                if ev_res.status_code != 200:
                    return {"status": "error", "query": query}
                events = ev_res.json()
        except Exception:
            return {"status": "error", "query": query}

        filtered = []
        crypto_keywords = [
            "bitcoin", "btc", "ethereum", "eth", "cryptocurrency", 
            "blockchain", "altcoin", "defi", "nft", "token", "coin", "wallet", 
            "mining", "solana", "cardano", "ada", "dogecoin", "doge",
            "binance", "coinbase", "kraken", "uniswap", "compound", "aave"
        ]
        
        # Check if user is searching for crypto-related terms (be more specific)
        query_lower = query.lower()
        user_wants_crypto = any(keyword in query_lower for keyword in crypto_keywords)
        
        # Special handling for "etf" - only consider it crypto-related if combined with crypto terms
        if "etf" in query_lower and not user_wants_crypto:
            user_wants_crypto = False
        
        for event in events if isinstance(events, list) else []:
            markets = event.get("markets", [])
            event_title = str(event.get("title", "")).lower()
            event_desc = str(event.get("description", "")).lower()
            category = str(event.get("category", "")).lower()
            
            # Check if this is crypto-related (be more specific with matching)
            is_crypto_related = False
            for keyword in crypto_keywords:
                # Use word boundaries to avoid false positives
                if f" {keyword} " in f" {event_title} " or f" {keyword} " in f" {event_desc} " or keyword in category:
                    is_crypto_related = True
                    break
            
            # Special handling for "etf" in event content
            if not is_crypto_related and "etf" in event_title and user_wants_crypto:
                is_crypto_related = True
            
            # If user searched for crypto terms but this isn't crypto-related, skip
            if user_wants_crypto and not is_crypto_related:
                continue
                
            for m in markets:
                prices = m.get("outcomePrices", [])
                if isinstance(prices, str):
                    try:
                        prices = json.loads(prices) if prices else []
                    except Exception:
                        prices = []
                yes_prob = float(prices[0]) if prices else 0.5
                volume = float(m.get("volume", 0) or 0)
                liquidity = float(m.get("liquidity", 0) or 0)
                
                # Boost crypto-related markets in ranking
                crypto_boost = 1.5 if is_crypto_related else 1.0
                
                filtered.append({
                    "id": m.get("id"),
                    "question": m.get("question", event.get("title", "")),
                    "slug": event.get("slug"),
                    "category": event.get("category"),
                    "yes_probability": round(yes_prob, 4),
                    "no_probability": round(1 - yes_prob, 4),
                    "volume": volume,
                    "volume_24hr": m.get("volume24hr", 0),
                    "liquidity": liquidity,
                    "active": m.get("active", False),
                    "closed": m.get("closed", False),
                    "end_date": m.get("endDate"),
                    "description": str(event.get("description", ""))[:200],
                    "url": f"https://polymarket.com/event/{event.get('slug')}",
                    "is_crypto_related": is_crypto_related
                })

        def _rank(m: dict) -> float:
            base_score = 0.6 * float(m.get("volume", 0) or 0) + 0.2 * float(m.get("volume_24hr", 0) or 0) + 0.2 * float(m.get("liquidity", 0) or 0)
            crypto_boost = 1.5 if m.get("is_crypto_related", False) else 1.0
            return base_score * crypto_boost
            
        filtered.sort(key=_rank, reverse=True)
        result = {
            "status": "success",
            "query": query,
            "total_found": len(filtered),
            "returned": min(len(filtered), 5),
            "markets": filtered[:5],
            "filtered_non_crypto": len(events) - len(filtered) if isinstance(events, list) else 0
        }
        self._cache_set(f"pm_search:{query}", result)
        return result