"""
PolySignal - TradFi & Crypto Data Collector
"""

import httpx
import asyncio
import os
from datetime import datetime
from typing import Dict, Optional

class CryptoCollector:
    """Collects cryptocurrency data"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize crypto collector
        
        Args:
            api_key: Optional CoinGecko API key for higher rate limits
                     Get one free at: https://www.coingecko.com/en/api
        """
        self.client = httpx.AsyncClient(timeout=30.0)
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY")
        self.assets = {
            "BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana",
            "BNB": "Binance Coin", "XRP": "Ripple"
        }
    
    async def get_prices(self) -> Dict[str, Dict]:
        """Get current crypto prices from CoinGecko"""
        try:
            ids = ",".join(["bitcoin", "ethereum", "solana", "binancecoin", "ripple"])
            params = {
                "ids": ids,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            
            # Add API key as query parameter if available
            if self.api_key:
                params["x_cg_demo_api_key"] = self.api_key
            
            response = await self.client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            mapping = {
                "bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL",
                "binancecoin": "BNB", "ripple": "XRP"
            }
            
            results = {}
            for gecko_id, symbol in mapping.items():
                if gecko_id in data:
                    results[symbol] = {
                        "name": self.assets[symbol],
                        "symbol": symbol,
                        "price": data[gecko_id]["usd"],
                        "change_24h": data[gecko_id].get("usd_24h_change", 0),
                        "timestamp": datetime.now().isoformat()
                    }
            return results
        except Exception as e:
            print(f"Error fetching crypto prices: {e}")
            return {}
    
    async def close(self):
        await self.client.aclose()

