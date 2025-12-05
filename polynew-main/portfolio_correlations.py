"""
PolySignal - Portfolio Correlations
Tracks personalized correlations between user's holdings and prediction markets
"""

from typing import Dict, List, Optional
from database import Database
from portfolio import Portfolio
from market_matcher import MarketMatcher
import asyncio


class PortfolioCorrelationTracker:
    """Tracks correlations between portfolio holdings and prediction markets"""
    
    def __init__(self, db: Database):
        """
        Initialize tracker
        
        Args:
            db: Database instance
        """
        self.db = db
        self.market_matcher = MarketMatcher()
    
    async def analyze_portfolio(self, portfolio: Portfolio) -> Dict:
        """
        Analyze portfolio and find relevant markets + correlations
        
        Args:
            portfolio: Portfolio instance
        
        Returns:
            Analysis results
        """
        symbols = portfolio.get_symbols()
        
        # Find relevant markets
        relevant_markets = await self.market_matcher.find_relevant_markets(symbols)
        
        # Get correlations for each symbol-market pair
        correlations = {}
        for symbol in symbols:
            correlations[symbol] = []
            
            for market in relevant_markets.get(symbol, [])[:10]:  # Top 10 per asset
                market_id = market["market_id"]
                category = market["category"]
                
                # Get correlation from database
                corr_data = self.db.get_correlation(category, symbol)
                
                if corr_data:
                    correlations[symbol].append({
                        "market_id": market_id,
                        "market_question": market["question"],
                        "category": category,
                        "correlation": corr_data["correlation"],
                        "p_value": corr_data.get("p_value"),
                        "sample_size": corr_data.get("sample_size"),
                        "is_significant": (corr_data.get("p_value") or 1.0) < 0.05,
                        "relevance_score": market["relevance_score"]
                    })
                else:
                    # No real correlation yet, but still show market
                    correlations[symbol].append({
                        "market_id": market_id,
                        "market_question": market["question"],
                        "category": category,
                        "correlation": None,
                        "relevance_score": market["relevance_score"],
                        "note": "No correlation data yet - collecting..."
                    })
        
        # Calculate portfolio-level insights
        insights = self._generate_insights(portfolio, correlations)
        
        return {
            "portfolio": portfolio.to_dict(),
            "relevant_markets": relevant_markets,
            "correlations": correlations,
            "insights": insights
        }
    
    def _generate_insights(self, portfolio: Portfolio, correlations: Dict) -> List[Dict]:
        """Generate insights about which markets matter most for portfolio"""
        insights = []
        holdings = portfolio.get_holdings()
        
        # Find markets that affect multiple holdings
        market_impact = {}  # {market_id: {symbols: [], total_weight: float}}
        
        for symbol, markets in correlations.items():
            weight = holdings.get(symbol, 0)
            for market in markets:
                market_id = market["market_id"]
                if market_id not in market_impact:
                    market_impact[market_id] = {
                        "symbols": [],
                        "total_weight": 0,
                        "market_question": market["market_question"],
                        "avg_correlation": 0,
                        "correlation_count": 0
                    }
                
                market_impact[market_id]["symbols"].append(symbol)
                market_impact[market_id]["total_weight"] += weight
                
                if market.get("correlation"):
                    market_impact[market_id]["avg_correlation"] += abs(market["correlation"])
                    market_impact[market_id]["correlation_count"] += 1
        
        # Calculate average correlations
        for market_id, data in market_impact.items():
            if data["correlation_count"] > 0:
                data["avg_correlation"] /= data["correlation_count"]
        
        # Sort by total portfolio weight affected
        sorted_markets = sorted(
            market_impact.items(),
            key=lambda x: x[1]["total_weight"] * (x[1]["avg_correlation"] or 0.5),
            reverse=True
        )
        
        # Generate insights
        for market_id, data in sorted_markets[:5]:  # Top 5
            if data["total_weight"] > 0.1:  # At least 10% of portfolio
                insights.append({
                    "type": "high_impact_market",
                    "market_id": market_id,
                    "market_question": data["market_question"],
                    "affected_holdings": data["symbols"],
                    "portfolio_weight": f"{data['total_weight']*100:.1f}%",
                    "avg_correlation": data["avg_correlation"],
                    "priority": "HIGH" if data["total_weight"] > 0.3 else "MEDIUM"
                })
        
        # Find strongest correlations
        strongest = []
        for symbol, markets in correlations.items():
            for market in markets:
                if market.get("correlation") and market.get("is_significant"):
                    strongest.append({
                        "symbol": symbol,
                        "market_question": market["market_question"],
                        "correlation": market["correlation"],
                        "p_value": market["p_value"]
                    })
        
        strongest.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        if strongest:
            insights.append({
                "type": "strongest_correlation",
                "data": strongest[0]
            })
        
        return insights
    
    def get_portfolio_alerts(self, portfolio: Portfolio, recent_signals: List[Dict]) -> List[Dict]:
        """
        Get alerts relevant to portfolio from recent signals
        
        Args:
            portfolio: Portfolio instance
            signals: Recent signals from monitor
        
        Returns:
            List of relevant alerts
        """
        alerts = []
        symbols = portfolio.get_symbols()
        holdings = portfolio.get_holdings()
        
        for signal in recent_signals:
            # Check if signal affects any holdings
            affected_assets = signal.get("affected_assets", {})
            
            for symbol in symbols:
                if symbol in affected_assets:
                    weight = holdings.get(symbol, 0)
                    impact = affected_assets[symbol]
                    
                    alerts.append({
                        "type": "portfolio_impact",
                        "symbol": symbol,
                        "portfolio_weight": f"{weight*100:.1f}%",
                        "market_question": signal.get("market_question"),
                        "expected_impact": impact.get("expected_change_pct"),
                        "confidence": impact.get("confidence"),
                        "signal_strength": signal.get("signal_strength"),
                        "timestamp": signal.get("timestamp")
                    })
        
        return alerts
    
    async def close(self):
        """Clean up resources"""
        await self.market_matcher.close()

