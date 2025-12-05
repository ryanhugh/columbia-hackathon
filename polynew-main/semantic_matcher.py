"""
PolySignal - Semantic Market Matcher
Enhanced matching using semantic similarity and vector embeddings
"""

from typing import Dict, List, Tuple
import re
from market_matcher import MarketMatcher


class SemanticMatcher:
    """Enhanced market matching with semantic similarity"""
    
    def __init__(self):
        """Initialize semantic matcher"""
        self.base_matcher = MarketMatcher()
        
        # Entity extraction patterns
        self.entity_patterns = {
            "BTC": [r"\b(bitcoin|btc)\b", r"bitcoin", r"btc"],
            "ETH": [r"\b(ethereum|eth)\b", r"ethereum", r"eth"],
            "SOL": [r"\b(solana|sol)\b", r"solana", r"sol"],
            "SPY": [r"\b(spy|s&p|s&p 500)\b", r"spy"],
            "QQQ": [r"\b(qqq|nasdaq)\b", r"qqq"],
            "NVDA": [r"\b(nvidia|nvda)\b", r"nvidia", r"nvda"],
            "TLT": [r"\b(tlt|treasury|bonds)\b", r"tlt"]
        }
        
        # Event type keywords
        self.event_keywords = {
            "regulatory": ["sec", "regulation", "approval", "ban", "lawsuit", "legal"],
            "macro": ["fed", "rate", "inflation", "cpi", "recession", "gdp"],
            "etf_approval": ["etf", "approval", "sec approval"],
            "upgrade": ["upgrade", "hardfork", "merge", "shanghai"],
            "earnings": ["earnings", "revenue", "profit"],
            "export_controls": ["export", "china", "restriction", "chip"],
            "election": ["election", "trump", "biden", "president"]
        }
    
    def semantic_match_score(self, holding_symbol: str, market_question: str,
                           market_category: str) -> Tuple[float, Dict]:
        """
        Calculate semantic match score between holding and market
        
        Returns:
            (score, details) where score is 0-1
        """
        question_lower = market_question.lower()
        category_lower = market_category.lower()
        
        score = 0.0
        details = {
            "entity_match": False,
            "category_match": False,
            "keyword_match": False,
            "event_type": None
        }
        
        # 1. Entity match (direct mention) - highest weight
        entity_patterns = self.entity_patterns.get(holding_symbol, [])
        for pattern in entity_patterns:
            if re.search(pattern, question_lower, re.IGNORECASE):
                score += 0.5
                details["entity_match"] = True
                break
        
        # 2. Category match
        asset_info = self.base_matcher.asset_to_markets.get(holding_symbol)
        if asset_info:
            for cat in asset_info["categories"]:
                if cat in category_lower:
                    score += 0.2
                    details["category_match"] = True
                    break
        
        # 3. Keyword match
        if asset_info:
            matched_keywords = 0
            for kw in asset_info["keywords"]:
                if kw in question_lower:
                    matched_keywords += 1
            
            if matched_keywords > 0:
                score += min(0.2, matched_keywords * 0.05)
                details["keyword_match"] = True
        
        # 4. Event type detection
        detected_event = None
        for event_type, keywords in self.event_keywords.items():
            if any(kw in question_lower for kw in keywords):
                detected_event = event_type
                details["event_type"] = event_type
                # Boost score if event type matches asset profile
                if asset_info and event_type in asset_info.get("event_types", []):
                    score += 0.1
                break
        
        # Normalize to 0-1
        score = min(1.0, score)
        
        return score, details
    
    async def find_markets_for_portfolio(self, holdings: Dict[str, float],
                                       min_edgescore: float = 50.0) -> List[Dict]:
        """
        Find and rank markets for a portfolio using semantic + correlation matching
        
        Args:
            holdings: {symbol: weight} portfolio
            min_edgescore: Minimum EdgeScore threshold
        
        Returns:
            Ranked list of markets with EdgeScore
        """
        from database import Database
        from edgescore import EdgeScoreCalculator
        
        db = Database()
        edgescore_calc = EdgeScoreCalculator(db)
        
        # Get all active markets
        all_markets = await self.base_matcher.pm_collector.get_active_markets(min_volume=50000)
        
        matched_markets = []
        
        for market in all_markets:
            market_id = market["id"]
            question = market.get("question", "")
            category = market.get("category", "")
            
            # Check each holding
            for symbol, weight in holdings.items():
                # Semantic match
                semantic_score, details = self.semantic_match_score(symbol, question, category)
                
                if semantic_score < 0.3:  # Too low semantic match
                    continue
                
                # Get correlation
                corr_data = db.get_correlation(category, symbol)
                
                # Calculate EdgeScore
                event_type = details.get("event_type")
                edgescore_data = edgescore_calc.calculate_edgescore(
                    category, symbol, event_type
                )
                
                edgescore = edgescore_data["edgescore"]
                
                # Composite match score
                correlation = abs(corr_data["correlation"]) if corr_data else 0.3
                
                # Final match = semantic (0.5) + correlation (0.3) + logical (0.2)
                composite_score = (
                    semantic_score * 0.5 +
                    min(correlation, 1.0) * 0.3 +
                    (1.0 if details["entity_match"] else 0.5) * 0.2
                )
                
                if composite_score >= 0.65 and edgescore >= min_edgescore:
                    # Calculate lead time
                    lead_time = edgescore_calc.calculate_lead_time(category, symbol)
                    
                    matched_markets.append({
                        "market_id": market_id,
                        "market_question": question,
                        "category": category,
                        "related_asset": symbol,
                        "portfolio_weight": f"{weight*100:.1f}%",
                        "edgescore": round(edgescore, 1),
                        "lead_time_hours": lead_time,
                        "semantic_score": round(semantic_score, 2),
                        "correlation": round(correlation, 3),
                        "composite_score": round(composite_score, 2),
                        "current_price": market.get("current_price", 0),
                        "volume_24h": market.get("volume_24h", 0),
                        "event_type": event_type,
                        "details": edgescore_data
                    })
        
        # Sort by EdgeScore (descending)
        matched_markets.sort(key=lambda x: x["edgescore"], reverse=True)
        
        return matched_markets
    
    async def close(self):
        """Clean up resources"""
        await self.base_matcher.close()

