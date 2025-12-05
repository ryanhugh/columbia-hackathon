"""
PolySignal - Polymarket Data Collector
Monitors Polymarket for significant price movements
"""

import httpx
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import json

class PolymarketCollector:
    """Collects and monitors Polymarket market data"""
    
    BASE_URL = "https://clob.polymarket.com"
    GAMMA_URL = "https://gamma-api.polymarket.com"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.tracked_markets = {}
        
    async def get_active_markets(self, min_volume: float = 100000) -> List[Dict]:
        """Get active markets with significant volume"""
        try:
            response = await self.client.get(
                f"{self.GAMMA_URL}/markets",
                params={"limit": 100, "active": True, "closed": False}
            )
            response.raise_for_status()
            markets = response.json()
            
            filtered = []
            for market in markets:
                volume_24h = float(market.get("volume24hr", 0))
                if volume_24h >= min_volume:
                    category = market.get("groupItemTitle", "").lower()
                    relevant_categories = [
                        "politics", "elections", "crypto", "business", "finance",
                        "economics", "federal reserve", "inflation"
                    ]
                    
                    if any(cat in category for cat in relevant_categories):
                        filtered.append({
                            "id": market.get("condition_id"),
                            "question": market.get("question"),
                            "category": category,
                            "volume_24h": volume_24h,
                            "current_price": self._get_yes_price(market),
                            "tokens": market.get("tokens", [])
                        })
            
            return filtered
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def _get_yes_price(self, market: Dict) -> float:
        """Extract current YES price from market data"""
        try:
            tokens = market.get("tokens", [])
            for token in tokens:
                if token.get("outcome") == "Yes":
                    return float(token.get("price", 0))
            return 0.5
        except:
            return 0.5
    
    async def track_price_changes(self, market_id: str, interval: int = 60) -> Dict:
        """Track price changes for a specific market"""
        if market_id not in self.tracked_markets:
            self.tracked_markets[market_id] = {"prices": [], "timestamps": []}
        
        try:
            response = await self.client.get(f"{self.GAMMA_URL}/markets/{market_id}")
            response.raise_for_status()
            
            market = response.json()
            price = self._get_yes_price(market)
            now = datetime.now()
            
            self.tracked_markets[market_id]["prices"].append(price)
            self.tracked_markets[market_id]["timestamps"].append(now)
            
            # Keep last 24 hours
            cutoff = now - timedelta(hours=24)
            data = self.tracked_markets[market_id]
            valid_indices = [i for i, ts in enumerate(data["timestamps"]) if ts > cutoff]
            data["prices"] = [data["prices"][i] for i in valid_indices]
            data["timestamps"] = [data["timestamps"][i] for i in valid_indices]
            
            if len(data["prices"]) >= 2:
                return {
                    "market_id": market_id,
                    "current_price": price,
                    "change_1h": self._calculate_change(data, hours=1),
                    "change_4h": self._calculate_change(data, hours=4),
                    "change_24h": self._calculate_change(data, hours=24),
                    "timestamp": now.isoformat()
                }
            
            return {"market_id": market_id, "current_price": price, "timestamp": now.isoformat()}
        except Exception as e:
            print(f"Error tracking market {market_id}: {e}")
            return {}
    
    def _calculate_change(self, data: Dict, hours: int) -> float:
        """Calculate price change over time period"""
        try:
            now = datetime.now()
            cutoff = now - timedelta(hours=hours)
            for i, ts in enumerate(data["timestamps"]):
                if ts >= cutoff:
                    if i == 0:
                        return 0.0
                    old_price = data["prices"][i]
                    new_price = data["prices"][-1]
                    return ((new_price - old_price) / old_price) * 100
            return 0.0
        except:
            return 0.0
    
    async def close(self):
        await self.client.aclose()