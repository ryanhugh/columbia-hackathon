"""
PolySignal - Real Correlation Engine
Uses calculated correlations from historical data instead of assumed values
"""

import numpy as np
from scipy import stats
from datetime import datetime
from typing import Dict, List, Optional
from database import Database


class RealCorrelationEngine:
    """Correlation engine that uses real calculated correlations from database"""
    
    def __init__(self, db: Database):
        """
        Initialize with database connection
        
        Args:
            db: Database instance for accessing stored correlations
        """
        self.db = db
        self.fallback_correlations = {
            "politics_republican": {"BTC": 0.6, "ETH": 0.5, "SPY": 0.3, "XLE": 0.5},
            "fed_rates": {"SPY": 0.8, "QQQ": 0.8, "BTC": 0.7, "TLT": 0.6},
            "inflation": {"GLD": 0.8, "TLT": -0.7, "BTC": 0.5},
            "recession": {"SPY": -0.8, "TLT": 0.7, "VXX": 0.9},
            "crypto": {"BTC": 0.9, "ETH": 0.9, "SOL": 0.8},
            "war": {"VXX": 0.8, "GLD": 0.7, "SPY": -0.6}
        }
    
    def identify_market_category(self, market_question: str) -> str:
        """Categorize market question"""
        question_lower = market_question.lower()
        categories = {
            "politics_republican": ["trump", "republican", "gop"],
            "politics_democrat": ["biden", "democrat", "harris"],
            "fed_rates": ["fed", "interest rate", "rate cut", "powell", "federal reserve"],
            "inflation": ["inflation", "cpi", "pce", "price index"],
            "recession": ["recession", "gdp", "downturn", "economic"],
            "crypto": ["bitcoin", "ethereum", "crypto", "btc", "eth"],
            "war": ["russia", "ukraine", "iran", "israel", "war", "conflict"]
        }
        
        for category, keywords in categories.items():
            if any(kw in question_lower for kw in keywords):
                return category
        return "general"
    
    def get_affected_assets(self, category: str) -> Dict[str, float]:
        """
        Get assets affected by category using real correlations from database
        
        Falls back to assumed correlations if no real data available
        """
        # Try to get real correlations from database
        correlations = self.db.get_all_correlations(market_category=category)
        
        if correlations:
            # Use real correlations
            result = {}
            for corr_data in correlations:
                asset = corr_data["asset_symbol"]
                corr_value = corr_data["correlation"]
                # Only include if statistically significant (p < 0.05) or high confidence
                p_value = corr_data.get("p_value")
                confidence = corr_data.get("confidence_level", 0)
                
                if p_value is None or p_value < 0.05 or confidence > 0.7:
                    result[asset] = corr_value
            
            if result:
                return result
        
        # Fallback to assumed correlations
        return self.fallback_correlations.get(category, {"SPY": 0.3, "BTC": 0.3})
    
    def calculate_price_impact(self, pm_change: float, correlation: float,
                              confidence: float = 0.5) -> Dict:
        """
        Estimate price impact using correlation
        
        Args:
            pm_change: Polymarket price change (as decimal, e.g., 0.1 for 10%)
            correlation: Correlation coefficient
            confidence: Confidence level (0-1)
        """
        # Scale impact based on correlation strength
        expected_impact = correlation * pm_change * 0.02
        
        # Adjust uncertainty based on confidence
        std_error = abs(expected_impact) * (1.0 - confidence) * 0.5
        
        return {
            "expected_change": expected_impact,
            "low_estimate": expected_impact - std_error,
            "high_estimate": expected_impact + std_error,
            "confidence": abs(correlation) * confidence
        }
    
    def generate_signal(self, market_data: Dict, pm_change: float,
                       timeframe: str = "4h") -> Dict:
        """
        Generate trading signal using real correlations
        
        Args:
            market_data: Market information dict
            pm_change: Price change percentage
            timeframe: Timeframe for the change
        """
        question = market_data.get("question", "")
        category = self.identify_market_category(question)
        affected_assets = self.get_affected_assets(category)
        
        impacts = {}
        for asset, correlation in affected_assets.items():
            # Get correlation metadata from database if available
            corr_data = self.db.get_correlation(category, asset)
            confidence = corr_data.get("confidence_level", 0.5) if corr_data else 0.5
            
            impact = self.calculate_price_impact(pm_change / 100, correlation, confidence)
            
            if abs(impact["expected_change"]) > 0.01:  # At least 1% expected change
                impacts[asset] = {
                    "correlation": correlation,
                    "expected_change_pct": impact["expected_change"] * 100,
                    "range_low": impact["low_estimate"] * 100,
                    "range_high": impact["high_estimate"] * 100,
                    "confidence": impact["confidence"],
                    "is_real_correlation": corr_data is not None,  # Flag if using real data
                    "sample_size": corr_data.get("sample_size") if corr_data else None,
                    "p_value": corr_data.get("p_value") if corr_data else None
                }
        
        # Sort by expected impact magnitude
        sorted_impacts = dict(sorted(
            impacts.items(),
            key=lambda x: abs(x[1]["expected_change_pct"]),
            reverse=True
        ))
        
        # Generate trade suggestions
        suggestions = []
        for asset, impact in sorted_impacts.items():
            expected_change = impact["expected_change_pct"]
            if abs(expected_change) < 1:  # Skip if less than 1% expected move
                continue
            
            direction = "BUY" if expected_change > 0 else "SELL/SHORT"
            data_source = "📊 Real Data" if impact["is_real_correlation"] else "📈 Estimated"
            
            suggestions.append({
                "asset": asset,
                "direction": direction,
                "expected_move": f"{expected_change:+.1f}%",
                "confidence": f"{impact['confidence'] * 100:.0f}%",
                "timeframe": timeframe,
                "data_source": data_source,
                "sample_size": impact.get("sample_size"),
                "p_value": impact.get("p_value")
            })
        
        signal_strength = self._calculate_signal_strength(pm_change, category, timeframe)
        
        return {
            "market_question": question,
            "category": category,
            "polymarket_change": f"{pm_change:+.1f}%",
            "timeframe": timeframe,
            "signal_strength": signal_strength,
            "affected_assets": sorted_impacts,
            "trade_suggestions": suggestions[:5],  # Top 5 suggestions
            "timestamp": datetime.now().isoformat(),
            "risk_warning": "Past correlations don't guarantee future performance. Use real correlations when available.",
            "using_real_data": any(imp.get("is_real_correlation") for imp in sorted_impacts.values())
        }
    
    def _calculate_signal_strength(self, pm_change: float, category: str, timeframe: str) -> str:
        """Determine signal strength"""
        abs_change = abs(pm_change)
        important_categories = ["fed_rates", "recession", "war"]
        category_multiplier = 1.5 if category in important_categories else 1.0
        timeframe_multiplier = {"1h": 2.0, "4h": 1.5, "24h": 1.0}.get(timeframe, 1.0)
        score = abs_change * category_multiplier * timeframe_multiplier
        
        if score >= 20:
            return "STRONG"
        elif score >= 10:
            return "MEDIUM"
        else:
            return "WEAK"

