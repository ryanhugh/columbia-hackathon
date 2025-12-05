"""
PolySignal - Market Matcher
Matches user holdings to relevant prediction markets
"""

from typing import Dict, List, Set
from data_collector import PolymarketCollector
import asyncio


class MarketMatcher:
    """Matches portfolio holdings to relevant prediction markets"""
    
    def __init__(self):
        """Initialize market matcher"""
        self.pm_collector = PolymarketCollector()
        
        # Mapping of assets to relevant market categories/keywords
        self.asset_to_markets = {
            # Crypto assets
            "BTC": {
                "categories": ["crypto", "bitcoin"],
                "keywords": ["bitcoin", "btc", "halving", "etf", "approval", "regulation", "sec"],
                "event_types": ["halving", "etf_approval", "regulation", "adoption"]
            },
            "ETH": {
                "categories": ["crypto", "ethereum"],
                "keywords": ["ethereum", "eth", "upgrade", "merge", "shanghai", "eip", "defi"],
                "event_types": ["upgrade", "protocol_change", "defi_event"]
            },
            "SOL": {
                "categories": ["crypto", "solana"],
                "keywords": ["solana", "sol", "outage", "upgrade", "breakpoint"],
                "event_types": ["network_event", "upgrade"]
            },
            "BNB": {
                "categories": ["crypto", "binance"],
                "keywords": ["binance", "bnb", "cz", "regulation", "lawsuit"],
                "event_types": ["regulation", "exchange_event"]
            },
            "XRP": {
                "categories": ["crypto", "ripple"],
                "keywords": ["ripple", "xrp", "sec", "lawsuit", "regulation"],
                "event_types": ["regulation", "lawsuit"]
            },
            # Stocks/ETFs
            "SPY": {
                "categories": ["politics", "elections", "economics", "federal reserve"],
                "keywords": ["fed", "rate", "inflation", "recession", "election", "trump", "biden"],
                "event_types": ["fed_decision", "election", "economic_data", "inflation"]
            },
            "QQQ": {
                "categories": ["politics", "elections", "economics", "federal reserve", "tech"],
                "keywords": ["fed", "rate", "tech", "nasdaq", "inflation"],
                "event_types": ["fed_decision", "tech_regulation"]
            },
            "TLT": {
                "categories": ["federal reserve", "economics", "inflation"],
                "keywords": ["fed", "rate", "inflation", "bonds", "treasury"],
                "event_types": ["fed_decision", "inflation_data"]
            },
            "GLD": {
                "categories": ["inflation", "economics", "geopolitics"],
                "keywords": ["inflation", "gold", "geopolitical", "war", "crisis"],
                "event_types": ["inflation_data", "geopolitical_event"]
            },
            "NVDA": {
                "categories": ["tech", "ai", "earnings"],
                "keywords": ["nvidia", "ai", "earnings", "gpu", "chip"],
                "event_types": ["earnings", "product_launch", "regulation"]
            }
        }
    
    def _calculate_semantic_match(self, asset_info: Dict, market: Dict) -> float:
        """
        Calculate semantic match score between asset and market
        
        Returns score 0-1
        """
        score = 0.0
        question_lower = market.get("question", "").lower()
        category_lower = market.get("category", "").lower()
        
        # Category match (weight: 0.4)
        category_matches = sum(1 for cat in asset_info["categories"] if cat in category_lower)
        if category_matches > 0:
            score += 0.4 * min(1.0, category_matches / len(asset_info["categories"]))
        
        # Keyword matches (weight: 0.3)
        keyword_matches = sum(1 for kw in asset_info["keywords"] if kw in question_lower)
        if keyword_matches > 0:
            score += 0.3 * min(1.0, keyword_matches / len(asset_info["keywords"]))
        
        # Event type match (weight: 0.3)
        # Check if market question suggests event types
        for event_type in asset_info.get("event_types", []):
            if event_type.replace("_", " ") in question_lower:
                score += 0.3 / len(asset_info.get("event_types", [1]))
        
        return min(1.0, score)
    
    async def find_relevant_markets(self, symbols: List[str], min_volume: float = 50000,
                                   min_match_score: float = 0.65) -> Dict[str, List[Dict]]:
        """
        Find relevant prediction markets for given asset symbols
        
        Args:
            symbols: List of asset symbols (BTC, ETH, SPY, etc.)
            min_volume: Minimum 24h volume for markets
        
        Returns:
            Dict mapping symbol to list of relevant markets
        """
        # Get all active markets
        all_markets = await self.pm_collector.get_active_markets(min_volume=min_volume)
        
        # Match markets to symbols
        matched_markets = {symbol: [] for symbol in symbols}
        
        for market in all_markets:
            question_lower = market.get("question", "").lower()
            category_lower = market.get("category", "").lower()
            
            for symbol in symbols:
                asset_info = self.asset_to_markets.get(symbol)
                if not asset_info:
                    continue
                
                # Calculate semantic match
                semantic_score = self._calculate_semantic_match(asset_info, market)
                
                # Calculate correlation component (if available)
                # This would come from database in real implementation
                correlation_score = 0.3  # Placeholder - would check DB
                
                # Logical rule match (explicit mention or category match)
                logical_score = 0.2
                if symbol.lower() in question_lower or any(cat in category_lower for cat in asset_info["categories"]):
                    logical_score = 0.2
                
                # Composite match score
                composite_score = (semantic_score * 0.5) + (correlation_score * 0.3) + (logical_score * 0.2)
                
                if composite_score >= min_match_score:
                    matched_markets[symbol].append({
                        "market_id": market["id"],
                        "question": market["question"],
                        "category": market["category"],
                        "current_price": market["current_price"],
                        "volume_24h": market["volume_24h"],
                        "relevance_score": self._calculate_relevance(market, asset_info),
                        "semantic_score": round(semantic_score, 2),
                        "composite_match": round(composite_score, 2)
                    })
        
        # Sort by relevance score
        for symbol in matched_markets:
            matched_markets[symbol].sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return matched_markets
    
    def _calculate_relevance(self, market: Dict, asset_info: Dict) -> float:
        """Calculate relevance score for a market"""
        score = 0.0
        question_lower = market.get("question", "").lower()
        category_lower = market.get("category", "").lower()
        
        # Category match (higher weight)
        for cat in asset_info["categories"]:
            if cat in category_lower:
                score += 2.0
        
        # Keyword matches
        for kw in asset_info["keywords"]:
            if kw in question_lower:
                score += 1.0
        
        # Volume boost (more volume = more relevant)
        volume = market.get("volume_24h", 0)
        if volume > 100000:
            score += 0.5
        if volume > 500000:
            score += 0.5
        
        return score
    
    def get_event_types_for_portfolio(self, symbols: List[str]) -> Set[str]:
        """Get all event types relevant to a portfolio"""
        event_types = set()
        for symbol in symbols:
            asset_info = self.asset_to_markets.get(symbol)
            if asset_info:
                event_types.update(asset_info.get("event_types", []))
        return event_types
    
    async def get_upcoming_events(self, symbols: List[str]) -> List[Dict]:
        """
        Get upcoming events relevant to portfolio (future: integrate with event calendars)
        
        Args:
            symbols: Portfolio symbols
        
        Returns:
            List of upcoming events
        """
        event_types = self.get_event_types_for_portfolio(symbols)
        
        # TODO: Integrate with event calendars (Fed meetings, earnings, etc.)
        # For now, return placeholder
        upcoming = []
        
        # Example: Fed meetings (would come from calendar API)
        if "fed_decision" in event_types:
            upcoming.append({
                "type": "fed_decision",
                "name": "Federal Reserve Meeting",
                "date": "2024-03-20",
                "relevance": "High",
                "affected_assets": [s for s in symbols if s in ["SPY", "QQQ", "TLT", "BTC"]]
            })
        
        return upcoming
    
    async def close(self):
        """Clean up resources"""
        await self.pm_collector.close()

