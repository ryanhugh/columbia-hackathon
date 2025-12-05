"""
PolySignal - Correlation Calculator
Calculates real correlations from historical data stored in database
"""

import numpy as np
from scipy import stats
from database import Database
from typing import Dict, List, Tuple


class CorrelationCalculator:
    """Calculates correlations between Polymarket categories and assets"""
    
    def __init__(self, db: Database):
        """
        Initialize calculator
        
        Args:
            db: Database instance
        """
        self.db = db
        
        # Categories to analyze
        self.categories = [
            "politics_republican",
            "politics_democrat",
            "fed_rates",
            "inflation",
            "recession",
            "crypto",
            "war"
        ]
        
        # Assets to correlate
        self.assets = ["BTC", "ETH", "SOL", "BNB", "XRP", "SPY", "QQQ", "TLT", "GLD", "VXX", "XLE"]
    
    def calculate_correlation(self, market_prices: List[float], asset_prices: List[float]) -> Dict:
        """
        Calculate correlation between two price series
        
        Returns:
            Dict with correlation, p-value, and statistics
        """
        if len(market_prices) < 10 or len(asset_prices) < 10:
            return None
        
        if len(market_prices) != len(asset_prices):
            # Align lengths
            min_len = min(len(market_prices), len(asset_prices))
            market_prices = market_prices[:min_len]
            asset_prices = asset_prices[:min_len]
        
        if len(market_prices) < 10:
            return None
        
        # Calculate price changes (returns)
        market_returns = np.diff(market_prices) / market_prices[:-1]
        asset_returns = np.diff(asset_prices) / asset_prices[:-1]
        
        # Ensure same length
        min_len = min(len(market_returns), len(asset_returns))
        market_returns = market_returns[:min_len]
        asset_returns = asset_returns[:min_len]
        
        if len(market_returns) < 5:
            return None
        
        # Calculate Pearson correlation
        correlation, p_value = stats.pearsonr(market_returns, asset_returns)
        
        # Calculate confidence level (inverse of p-value, capped at 1.0)
        confidence = max(0.0, min(1.0, 1.0 - p_value))
        
        return {
            "correlation": float(correlation),
            "p_value": float(p_value),
            "sample_size": len(market_returns),
            "confidence_level": confidence,
            "is_significant": p_value < 0.05
        }
    
    def calculate_all_correlations(self, days: int = 30, min_sample_size: int = 20) -> Dict:
        """
        Calculate correlations for all category-asset pairs
        
        Args:
            days: Number of days of historical data to use
            min_sample_size: Minimum number of data points required
        
        Returns:
            Dict with results summary
        """
        print(f"🔍 Calculating correlations using {days} days of data...")
        print(f"   Minimum sample size: {min_sample_size} data points")
        print("-" * 60)
        
        results = {
            "calculated": 0,
            "significant": 0,
            "failed": 0,
            "correlations": []
        }
        
        for category in self.categories:
            print(f"\n📊 Category: {category}")
            
            for asset in self.assets:
                try:
                    # Get paired data
                    market_prices, asset_prices = self.db.get_data_for_correlation(
                        market_category=category,
                        asset_symbol=asset,
                        days=days
                    )
                    
                    if len(market_prices) < min_sample_size:
                        print(f"   ⚠️  {asset}: Insufficient data ({len(market_prices)} points)")
                        results["failed"] += 1
                        continue
                    
                    # Calculate correlation
                    corr_result = self.calculate_correlation(market_prices, asset_prices)
                    
                    if corr_result is None:
                        print(f"   ❌ {asset}: Calculation failed")
                        results["failed"] += 1
                        continue
                    
                    # Save to database
                    self.db.save_correlation(
                        market_category=category,
                        asset_symbol=asset,
                        correlation=corr_result["correlation"],
                        p_value=corr_result["p_value"],
                        sample_size=corr_result["sample_size"],
                        confidence_level=corr_result["confidence_level"]
                    )
                    
                    # Track results
                    results["calculated"] += 1
                    if corr_result["is_significant"]:
                        results["significant"] += 1
                    
                    significance = "✅" if corr_result["is_significant"] else "⚠️"
                    print(f"   {significance} {asset}: {corr_result['correlation']:.3f} "
                          f"(p={corr_result['p_value']:.3f}, n={corr_result['sample_size']})")
                    
                    results["correlations"].append({
                        "category": category,
                        "asset": asset,
                        **corr_result
                    })
                    
                except Exception as e:
                    print(f"   ❌ {asset}: Error - {e}")
                    results["failed"] += 1
        
        return results
    
    def print_summary(self, results: Dict):
        """Print summary of correlation calculations"""
        print("\n" + "=" * 60)
        print("📊 CORRELATION CALCULATION SUMMARY")
        print("=" * 60)
        print(f"✅ Calculated: {results['calculated']}")
        print(f"📈 Significant (p < 0.05): {results['significant']}")
        print(f"❌ Failed/Insufficient data: {results['failed']}")
        
        if results["correlations"]:
            print("\n🔝 Top Correlations (by absolute value):")
            sorted_corrs = sorted(
                results["correlations"],
                key=lambda x: abs(x["correlation"]),
                reverse=True
            )[:10]
            
            for corr in sorted_corrs:
                sig = "✅" if corr["is_significant"] else "⚠️"
                print(f"   {sig} {corr['category']} → {corr['asset']}: "
                      f"{corr['correlation']:.3f} (p={corr['p_value']:.3f})")
    
    def show_stored_correlations(self, category: str = None):
        """Display stored correlations from database"""
        correlations = self.db.get_all_correlations(market_category=category)
        
        if not correlations:
            print("No correlations found in database.")
            print("Run calculate_correlations.py first to calculate them.")
            return
        
        print(f"\n📊 Stored Correlations{' (' + category + ')' if category else ''}:")
        print("-" * 60)
        
        for corr in correlations:
            sig = "✅" if (corr.get("p_value") or 1.0) < 0.05 else "⚠️"
            print(f"{sig} {corr['market_category']} → {corr['asset_symbol']}: "
                  f"{corr['correlation']:.3f}")
            print(f"   p-value: {corr.get('p_value', 'N/A'):.4f}, "
                  f"sample: {corr.get('sample_size', 'N/A')}, "
                  f"confidence: {corr.get('confidence_level', 0):.2f}")


def main():
    """Main entry point"""
    import sys
    
    db = Database()
    calculator = CorrelationCalculator(db)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "calculate":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            results = calculator.calculate_all_correlations(days=days)
            calculator.print_summary(results)
        elif command == "show":
            category = sys.argv[2] if len(sys.argv) > 2 else None
            calculator.show_stored_correlations(category=category)
        else:
            print("Usage:")
            print("  python calculate_correlations.py calculate [days]  # Calculate correlations")
            print("  python calculate_correlations.py show [category]  # Show stored correlations")
    else:
        # Default: show stored correlations
        calculator.show_stored_correlations()


if __name__ == "__main__":
    main()

