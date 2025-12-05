"""
PolySignal - EdgeScore Calculator
Calculates predictive edge scores for prediction market → asset relationships
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple
from database import Database
from datetime import datetime, timedelta


class EdgeScoreCalculator:
    """Calculates EdgeScore for prediction market → asset relationships"""
    
    def __init__(self, db: Database):
        """
        Initialize calculator
        
        Args:
            db: Database instance
        """
        self.db = db
        
        # Impact weights by asset type and event category
        self.impact_weights = {
            # Crypto assets
            "BTC": {
                "macro": 0.6,
                "regulatory": 0.9,
                "etf_approval": 1.0,
                "halving": 1.0,
                "adoption": 0.7
            },
            "ETH": {
                "macro": 0.6,
                "regulatory": 0.9,
                "etf_approval": 1.0,
                "upgrade": 0.9,
                "defi": 0.8
            },
            "SOL": {
                "macro": 0.5,
                "regulatory": 0.8,
                "network_event": 0.9,
                "upgrade": 0.8
            },
            # Stocks/ETFs
            "SPY": {
                "macro": 1.0,
                "fed_decision": 1.0,
                "election": 0.8,
                "inflation": 0.9,
                "recession": 1.0
            },
            "QQQ": {
                "macro": 0.9,
                "fed_decision": 0.9,
                "tech_regulation": 0.8,
                "inflation": 0.7
            },
            "NVDA": {
                "tech_regulation": 0.9,
                "export_controls": 1.0,
                "earnings": 0.8,
                "product_launch": 0.7,
                "ai_regulation": 0.9
            },
            "TLT": {
                "fed_decision": 1.0,
                "inflation": 0.9,
                "macro": 0.8
            }
        }
    
    def calculate_edgescore(self, market_category: str, asset_symbol: str,
                           event_type: str = None, lag_hours: int = 12) -> Dict:
        """
        Calculate EdgeScore for a market-asset pair
        
        Args:
            market_category: Prediction market category
            asset_symbol: Asset symbol
            event_type: Type of event (regulatory, macro, etc.)
            lag_hours: Lead time in hours
        
        Returns:
            Dict with edgescore and components
        """
        # Get correlation data
        corr_data = self.db.get_correlation(market_category, asset_symbol)
        
        if not corr_data:
            return {
                "edgescore": 0,
                "correlation": 0,
                "stability": 0,
                "significance": 0,
                "impact_weight": 0,
                "lead_time_hours": lag_hours,
                "confidence": "low"
            }
        
        correlation = abs(corr_data.get("correlation", 0))
        p_value = corr_data.get("p_value", 1.0)
        sample_size = corr_data.get("sample_size", 0)
        
        # Calculate stability (rolling correlation consistency)
        stability = self._calculate_stability(market_category, asset_symbol)
        
        # Calculate significance (p-value mapped to 0-1)
        significance = self._calculate_significance(p_value, sample_size)
        
        # Get impact weight
        impact_weight = self._get_impact_weight(asset_symbol, event_type or market_category)
        
        # Calculate EdgeScore
        edgescore = (correlation * stability * significance * impact_weight) * 100
        
        # Determine confidence level
        if edgescore >= 70:
            confidence = "high"
        elif edgescore >= 50:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "edgescore": round(edgescore, 1),
            "correlation": round(correlation, 3),
            "stability": round(stability, 2),
            "significance": round(significance, 2),
            "impact_weight": round(impact_weight, 2),
            "lead_time_hours": lag_hours,
            "p_value": round(p_value, 4),
            "sample_size": sample_size,
            "confidence": confidence
        }
    
    def _calculate_stability(self, market_category: str, asset_symbol: str,
                            window_days: int = 7) -> float:
        """
        Calculate correlation stability over rolling windows
        
        Returns:
            Stability score (0-1)
        """
        # Get historical data
        market_prices, asset_prices = self.db.get_data_for_correlation(
            market_category, asset_symbol, days=30
        )
        
        if len(market_prices) < window_days * 2:
            return 0.5  # Default moderate stability
        
        # Calculate rolling correlations
        window_size = min(len(market_prices) // 3, 20)  # Adaptive window
        if window_size < 5:
            return 0.5
        
        rolling_corrs = []
        for i in range(len(market_prices) - window_size):
            window_market = market_prices[i:i+window_size]
            window_asset = asset_prices[i:i+window_size]
            
            if len(window_market) >= 5:
                try:
                    corr, _ = stats.pearsonr(
                        np.diff(window_market) / window_market[:-1],
                        np.diff(window_asset) / window_asset[:-1]
                    )
                    if not np.isnan(corr):
                        rolling_corrs.append(abs(corr))
                except:
                    pass
        
        if not rolling_corrs:
            return 0.5
        
        # Stability = 1 - coefficient of variation
        mean_corr = np.mean(rolling_corrs)
        std_corr = np.std(rolling_corrs)
        
        if mean_corr == 0:
            return 0.5
        
        cv = std_corr / mean_corr
        stability = max(0, min(1, 1 - cv))
        
        return stability
    
    def _calculate_significance(self, p_value: float, sample_size: int) -> float:
        """
        Map p-value and sample size to significance score (0-1)
        """
        if p_value is None:
            return 0.3  # Unknown significance
        
        # P-value component (lower is better)
        if p_value < 0.01:
            p_score = 1.0
        elif p_value < 0.05:
            p_score = 0.8
        elif p_value < 0.10:
            p_score = 0.6
        else:
            p_score = 0.3
        
        # Sample size component (more is better)
        if sample_size >= 100:
            n_score = 1.0
        elif sample_size >= 50:
            n_score = 0.8
        elif sample_size >= 20:
            n_score = 0.6
        else:
            n_score = 0.4
        
        # Combined significance
        significance = (p_score * 0.7) + (n_score * 0.3)
        
        return significance
    
    def _get_impact_weight(self, asset_symbol: str, event_category: str) -> float:
        """
        Get impact weight based on asset type and event category
        """
        asset_weights = self.impact_weights.get(asset_symbol, {})
        
        # Try exact match first
        if event_category in asset_weights:
            return asset_weights[event_category]
        
        # Try partial matches
        for key, weight in asset_weights.items():
            if key in event_category.lower() or event_category.lower() in key:
                return weight
        
        # Default based on asset type
        if asset_symbol in ["BTC", "ETH", "SOL"]:
            return 0.6  # Crypto default
        elif asset_symbol in ["SPY", "QQQ", "TLT"]:
            return 0.7  # Macro default
        else:
            return 0.5  # Generic default
    
    def calculate_lead_time(self, market_category: str, asset_symbol: str) -> int:
        """
        Calculate optimal lead time (hours) for this relationship
        
        Returns:
            Lead time in hours
        """
        # Get historical data
        market_prices, asset_prices = self.db.get_data_for_correlation(
            market_category, asset_symbol, days=30
        )
        
        if len(market_prices) < 20:
            return 12  # Default
        
        # Test different lag windows
        best_lag = 12
        best_corr = 0
        
        for lag_hours in [1, 4, 8, 12, 24, 48]:
            # Shift asset prices by lag
            if len(asset_prices) > lag_hours:
                shifted_asset = asset_prices[lag_hours:]
                matched_market = market_prices[:-lag_hours] if len(market_prices) > lag_hours else market_prices
                
                if len(shifted_asset) >= 10 and len(matched_market) >= 10:
                    try:
                        corr, _ = stats.pearsonr(
                            np.diff(matched_market) / matched_market[:-1],
                            np.diff(shifted_asset) / shifted_asset[:-1]
                        )
                        if not np.isnan(corr) and abs(corr) > abs(best_corr):
                            best_corr = corr
                            best_lag = lag_hours
                    except:
                        pass
        
        return best_lag
    
    def get_edge_intensity(self, asset_symbol: str, portfolio_holdings: Dict) -> str:
        """
        Calculate edge intensity for an asset in a portfolio
        
        Returns:
            "high", "medium", or "low"
        """
        # Count relevant markets with high edgescore
        high_edge_count = 0
        total_markets = 0
        
        # Get all correlations for this asset
        correlations = self.db.get_all_correlations()
        asset_corrs = [c for c in correlations if c["asset_symbol"] == asset_symbol]
        
        for corr in asset_corrs:
            edgescore_data = self.calculate_edgescore(
                corr["market_category"],
                asset_symbol
            )
            total_markets += 1
            if edgescore_data["edgescore"] >= 60:
                high_edge_count += 1
        
        if total_markets == 0:
            return "low"
        
        high_edge_ratio = high_edge_count / total_markets
        
        if high_edge_ratio >= 0.5:
            return "high"
        elif high_edge_ratio >= 0.3:
            return "medium"
        else:
            return "low"
