"""
PolySignal - Relationship Explorer
Deep dive into prediction market - asset relationships
"""

import numpy as np
from typing import Dict, List, Tuple
from database import Database
from datetime import datetime, timedelta
from edgescore import EdgeScoreCalculator


class RelationshipExplorer:
    """Explores relationships between prediction markets and assets"""
    
    def __init__(self, db: Database):
        """
        Initialize relationship explorer
        
        Args:
            db: Database instance
        """
        self.db = db
        self.edgescore_calc = EdgeScoreCalculator(db)
    
    def explore_relationship(self, market_category: str, asset_symbol: str,
                           days: int = 30) -> Dict:
        """
        Explore relationship between market and asset
        
        Returns comprehensive relationship analysis
        """
        # Get historical data
        market_prices, asset_prices = self.db.get_data_for_correlation(
            market_category, asset_symbol, days=days
        )
        
        if len(market_prices) < 10:
            return {
                "error": "Insufficient data",
                "market_category": market_category,
                "asset_symbol": asset_symbol
            }
        
        # Calculate lead-lag analysis
        lead_lag = self._calculate_lead_lag(market_prices, asset_prices)
        
        # Calculate correlation heatmap (different lags)
        heatmap = self._calculate_correlation_heatmap(market_prices, asset_prices)
        
        # Historical performance
        performance = self._analyze_historical_performance(
            market_prices, asset_prices, lead_lag["optimal_lag_hours"]
        )
        
        # EdgeScore
        edgescore = self.edgescore_calc.calculate_edgescore(
            market_category, asset_symbol, lead_lag["optimal_lag_hours"]
        )
        
        # Get correlation data
        corr_data = self.db.get_correlation(market_category, asset_symbol)
        
        return {
            "market_category": market_category,
            "asset_symbol": asset_symbol,
            "edgescore": edgescore,
            "correlation": corr_data.get("correlation") if corr_data else None,
            "p_value": corr_data.get("p_value") if corr_data else None,
            "sample_size": len(market_prices),
            "lead_lag": lead_lag,
            "heatmap": heatmap,
            "performance": performance,
            "chart_data": self._prepare_chart_data(market_prices, asset_prices)
        }
    
    def _calculate_lead_lag(self, market_prices: List[float],
                           asset_prices: List[float]) -> Dict:
        """Calculate optimal lead-lag relationship"""
        if len(market_prices) != len(asset_prices) or len(market_prices) < 10:
            return {"optimal_lag_hours": 12, "correlation_at_lag": 0}
        
        # Calculate returns
        market_returns = np.diff(market_prices) / market_prices[:-1]
        asset_returns = np.diff(asset_prices) / asset_prices[:-1]
        
        # Test different lags (0 to 48 hours, assuming hourly data)
        max_lag = min(48, len(market_returns) - 5)
        best_lag = 0
        best_corr = 0
        
        for lag in range(0, max_lag, 1):
            if lag >= len(asset_returns):
                break
            
            # Shift asset returns by lag
            shifted_asset = asset_returns[lag:]
            market_aligned = market_returns[:len(shifted_asset)]
            
            if len(market_aligned) < 5:
                break
            
            corr, _ = stats.pearsonr(market_aligned, shifted_asset)
            
            if not np.isnan(corr) and abs(corr) > abs(best_corr):
                best_corr = corr
                best_lag = lag
        
        return {
            "optimal_lag_hours": best_lag,
            "correlation_at_lag": round(best_corr, 3),
            "lead_time": f"{best_lag} hours"
        }
    
    def _calculate_correlation_heatmap(self, market_prices: List[float],
                                      asset_prices: List[float]) -> List[Dict]:
        """Calculate correlations at different lag times"""
        if len(market_prices) != len(asset_prices):
            return []
        
        market_returns = np.diff(market_prices) / market_prices[:-1]
        asset_returns = np.diff(asset_prices) / asset_prices[:-1]
        
        heatmap = []
        lags = [0, 1, 3, 6, 12, 24, 48]
        
        for lag in lags:
            if lag >= len(asset_returns):
                continue
            
            shifted_asset = asset_returns[lag:]
            market_aligned = market_returns[:len(shifted_asset)]
            
            if len(market_aligned) < 5:
                continue
            
            corr, p_val = stats.pearsonr(market_aligned, shifted_asset)
            
            if not np.isnan(corr):
                heatmap.append({
                    "lag_hours": lag,
                    "correlation": round(corr, 3),
                    "p_value": round(p_val, 4),
                    "strength": "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
                })
        
        return heatmap
    
    def _analyze_historical_performance(self, market_prices: List[float],
                                       asset_prices: List[float],
                                       lag_hours: int) -> Dict:
        """Analyze historical performance of the relationship"""
        if len(market_prices) < 20:
            return {
                "significant_moves": 0,
                "followed_moves": 0,
                "success_rate": 0,
                "avg_follow_time_hours": lag_hours
            }
        
        # Find significant PM moves (>5% change)
        market_returns = np.diff(market_prices) / market_prices[:-1]
        significant_moves = []
        
        for i, ret in enumerate(market_returns):
            if abs(ret) > 0.05:  # 5% move
                significant_moves.append({
                    "index": i,
                    "change": ret,
                    "direction": "up" if ret > 0 else "down"
                })
        
        # Check if asset followed within lag window
        asset_returns = np.diff(asset_prices) / asset_prices[:-1]
        followed = 0
        
        for move in significant_moves:
            start_idx = move["index"]
            end_idx = min(start_idx + lag_hours, len(asset_returns))
            
            if end_idx > start_idx:
                window_returns = asset_returns[start_idx:end_idx]
                if len(window_returns) > 0:
                    total_return = np.sum(window_returns)
                    # Check if direction matches
                    if (move["direction"] == "up" and total_return > 0) or \
                       (move["direction"] == "down" and total_return < 0):
                        followed += 1
        
        success_rate = (followed / len(significant_moves) * 100) if significant_moves else 0
        
        return {
            "significant_moves": len(significant_moves),
            "followed_moves": followed,
            "success_rate": round(success_rate, 1),
            "avg_follow_time_hours": lag_hours
        }
    
    def _prepare_chart_data(self, market_prices: List[float],
                           asset_prices: List[float]) -> Dict:
        """Prepare data for charting"""
        # Normalize prices to 0-1 for comparison
        if not market_prices or not asset_prices:
            return {"market": [], "asset": [], "timestamps": []}
        
        market_norm = [(p - min(market_prices)) / (max(market_prices) - min(market_prices) + 1e-10) 
                      for p in market_prices]
        asset_norm = [(p - min(asset_prices)) / (max(asset_prices) - min(asset_prices) + 1e-10) 
                     for p in asset_prices]
        
        # Generate timestamps (simplified)
        timestamps = [(datetime.now() - timedelta(hours=len(market_prices)-i)).isoformat() 
                      for i in range(len(market_prices))]
        
        return {
            "market": [round(p, 3) for p in market_norm],
            "asset": [round(p, 3) for p in asset_norm],
            "timestamps": timestamps
        }
    
    def get_trading_strategies(self, market_category: str, asset_symbol: str) -> List[Dict]:
        """Get suggested trading strategies based on relationship"""
        relationship = self.explore_relationship(market_category, asset_symbol)
        
        if "error" in relationship:
            return []
        
        strategies = []
        edgescore = relationship.get("edgescore", {})
        score = edgescore.get("edgescore", 0)
        lag = relationship.get("lead_lag", {}).get("optimal_lag_hours", 12)
        performance = relationship.get("performance", {})
        
        if score >= 70:
            strategies.append({
                "name": "Buy on Probability Spike",
                "description": f"When PM probability rises sharply, buy {asset_symbol} within {lag} hours",
                "confidence": "High",
                "success_rate": performance.get("success_rate", 0)
            })
            
            strategies.append({
                "name": "Fade Extreme Moves",
                "description": f"When PM probability drops too fast, consider fading {asset_symbol}",
                "confidence": "Medium",
                "success_rate": performance.get("success_rate", 0) * 0.8
            })
        
        elif score >= 50:
            strategies.append({
                "name": "Watch and Confirm",
                "description": f"Monitor PM moves, confirm with {asset_symbol} price action before trading",
                "confidence": "Medium",
                "success_rate": performance.get("success_rate", 0)
            })
        
        return strategies

