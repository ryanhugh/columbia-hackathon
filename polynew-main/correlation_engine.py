"""
PolySignal - Correlation Engine
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class CorrelationEngine:
    """Analyzes relationships between prediction markets and assets"""
    
    def __init__(self):
        self.expected_correlations = {
            "Trump wins": {"BTC": 0.7, "SPY": 0.3, "TLT": -0.4, "XLE": 0.5},
            "Fed cuts rates": {"SPY": 0.8, "TLT": 0.6, "BTC": 0.7, "VXX": -0.6},
            "Inflation rises": {"GLD": 0.8, "TLT": -0.7, "BTC": 0.5, "SPY": -0.3},
            "Recession": {"SPY": -0.8, "TLT": 0.7, "VXX": 0.9, "GLD": 0.6}
        }
    
    def identify_market_category(self, market_question: str) -> str:
        """Categorize market question"""
        question_lower = market_question.lower()
        categories = {
            "politics_republican": ["trump", "republican", "gop"],
            "politics_democrat": ["biden", "democrat", "harris"],
            "fed_rates": ["fed", "interest rate", "rate cut", "powell"],
            "inflation": ["inflation", "cpi", "pce"],
            "recession": ["recession", "gdp", "downturn"],
            "crypto": ["bitcoin", "ethereum", "crypto"],
            "war": ["russia", "ukraine", "iran", "israel", "war"]
        }
        
        for category, keywords in categories.items():
            if any(kw in question_lower for kw in keywords):
                return category
        return "general"
    
    def get_affected_assets(self, category: str) -> Dict[str, float]:
        """Get assets affected by category with correlations"""
        correlations = {
            "politics_republican": {"BTC": 0.6, "ETH": 0.5, "SPY": 0.3, "XLE": 0.5},
            "fed_rates": {"SPY": 0.8, "QQQ": 0.8, "BTC": 0.7, "TLT": 0.6},
            "inflation": {"GLD": 0.8, "TLT": -0.7, "BTC": 0.5},
            "recession": {"SPY": -0.8, "TLT": 0.7, "VXX": 0.9},
            "crypto": {"BTC": 0.9, "ETH": 0.9, "SOL": 0.8},
            "war": {"VXX": 0.8, "GLD": 0.7, "SPY": -0.6}
        }
        return correlations.get(category, {"SPY": 0.3, "BTC": 0.3})
    
    def calculate_price_impact(self, pm_change: float, correlation: float) -> Dict:
        """Estimate price impact"""
        expected_impact = correlation * pm_change * 0.02
        std_error = abs(expected_impact) * 0.3
        
        return {
            "expected_change": expected_impact,
            "low_estimate": expected_impact - std_error,
            "high_estimate": expected_impact + std_error,
            "confidence": abs(correlation)
        }
    
    def generate_signal(self, market_data: Dict, pm_change: float, timeframe: str = "4h") -> Dict:
        """Generate trading signal"""
        question = market_data.get("question", "")
        category = self.identify_market_category(question)
        affected_assets = self.get_affected_assets(category)
        
        impacts = {}
        for asset, correlation in affected_assets.items():
            impact = self.calculate_price_impact(pm_change / 100, correlation)
            if abs(impact["expected_change"]) > 0.01:
                impacts[asset] = {
                    "correlation": correlation,
                    "expected_change_pct": impact["expected_change"] * 100,
                    "range_low": impact["low_estimate"] * 100,
                    "range_high": impact["high_estimate"] * 100,
                    "confidence": impact["confidence"]
                }
        
        sorted_impacts = dict(sorted(impacts.items(), key=lambda x: abs(x[1]["expected_change_pct"]), reverse=True))
        
        suggestions = []
        for asset, impact in sorted_impacts.items():
            expected_change = impact["expected_change_pct"]
            if abs(expected_change) < 1:
                continue
            direction = "BUY" if expected_change > 0 else "SELL/SHORT"
            suggestions.append({
                "asset": asset,
                "direction": direction,
                "expected_move": f"{expected_change:+.1f}%",
                "confidence": f"{impact['confidence'] * 100:.0f}%",
                "timeframe": timeframe
            })
        
        signal_strength = self._calculate_signal_strength(pm_change, category, timeframe)
        
        return {
            "market_question": question,
            "category": category,
            "polymarket_change": f"{pm_change:+.1f}%",
            "timeframe": timeframe,
            "signal_strength": signal_strength,
            "affected_assets": sorted_impacts,
            "trade_suggestions": suggestions[:5],
            "timestamp": datetime.now().isoformat(),
            "risk_warning": "Past correlations don't guarantee future performance"
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
