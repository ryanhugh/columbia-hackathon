"""
PolySignal - Hybrid Monitor
Uses real correlations when available, falls back to estimated correlations
Combines the best of both approaches
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from data_collector import PolymarketCollector
from market_data import CryptoCollector
from database import Database
from real_correlation_engine import RealCorrelationEngine
from correlation_engine import CorrelationEngine


class HybridMonitor:
    """Hybrid monitoring system using both real and estimated correlations"""
    
    def __init__(self, min_price_change: float = 5.0, check_interval: int = 60):
        """
        Initialize the hybrid monitor
        
        Args:
            min_price_change: Minimum price change percentage to trigger signal (default: 5%)
            check_interval: Seconds between checks (default: 60)
        """
        load_dotenv()
        
        self.pm_collector = PolymarketCollector()
        self.crypto_collector = CryptoCollector()
        self.db = Database()
        
        # Use real correlation engine (will fall back to estimated if no data)
        self.real_engine = RealCorrelationEngine(self.db)
        # Keep original engine as pure fallback
        self.estimated_engine = CorrelationEngine()
        
        self.min_price_change = min_price_change
        self.check_interval = check_interval
        self.tracked_markets = {}
        self.signals_generated = []
        
    async def initialize(self):
        """Initialize and discover active markets"""
        print("🔍 Discovering active Polymarket markets...")
        markets = await self.pm_collector.get_active_markets(min_volume=100000)
        
        if not markets:
            print("⚠️  No active markets found. Retrying...")
            return
            
        print(f"✅ Found {len(markets)} active markets")
        
        # Check database stats
        stats = self.db.get_stats()
        real_correlations = stats.get("correlations", 0)
        
        if real_correlations > 0:
            print(f"📊 Using {real_correlations} real correlations from database")
        else:
            print("⚠️  No real correlations found - using estimated correlations")
            print("   Run 'python calculate_correlations.py calculate' to calculate real correlations")
        
        # Initialize tracking for each market
        for market in markets:
            market_id = market["id"]
            self.tracked_markets[market_id] = {
                "question": market["question"],
                "category": market["category"],
                "initial_price": market["current_price"],
                "last_price": market["current_price"],
                "last_check": datetime.now()
            }
            
        print(f"📊 Tracking {len(self.tracked_markets)} markets")
        print(f"⚙️  Monitoring every {self.check_interval} seconds")
        print(f"📈 Minimum price change threshold: {self.min_price_change}%")
        print("-" * 60)
        
    async def check_markets(self):
        """Check all tracked markets for significant changes"""
        tasks = []
        for market_id in self.tracked_markets.keys():
            tasks.append(self.pm_collector.track_price_changes(market_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        signals = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
                
            if not result or "change_4h" not in result:
                continue
                
            market_id = result["market_id"]
            market_info = self.tracked_markets.get(market_id)
            
            if not market_info:
                continue
            
            # Check for significant changes
            change_1h = result.get("change_1h", 0)
            change_4h = result.get("change_4h", 0)
            change_24h = result.get("change_24h", 0)
            
            # Use 4h change as primary signal (most reliable)
            significant_change = abs(change_4h) >= self.min_price_change
            
            if significant_change:
                # Save data to database for future correlation calculations
                try:
                    self.db.save_market_data(
                        market_id=market_id,
                        price=result["current_price"],
                        market_question=market_info["question"],
                        category=market_info["category"]
                    )
                except:
                    pass  # Don't fail if database save fails
                
                # Generate signal using real correlation engine (with fallback)
                market_data = {
                    "id": market_id,
                    "question": market_info["question"],
                    "category": market_info["category"],
                    "current_price": result["current_price"]
                }
                
                signal = self.real_engine.generate_signal(
                    market_data, 
                    change_4h, 
                    timeframe="4h"
                )
                
                # Only generate if we have trade suggestions
                if signal.get("trade_suggestions"):
                    signals.append({
                        "signal": signal,
                        "raw_data": result
                    })
                    
                # Update tracked price
                market_info["last_price"] = result["current_price"]
                market_info["last_check"] = datetime.now()
        
        return signals
    
    def display_signal(self, signal_data: Dict):
        """Display a generated signal in a formatted way"""
        signal = signal_data["signal"]
        raw = signal_data["raw_data"]
        
        using_real = signal.get("using_real_data", False)
        data_indicator = "📊 REAL DATA" if using_real else "📈 ESTIMATED"
        
        print("\n" + "=" * 60)
        print(f"🚨 NEW SIGNAL DETECTED - {data_indicator}")
        print("=" * 60)
        print(f"📋 Market: {signal['market_question']}")
        print(f"🏷️  Category: {signal['category']}")
        print(f"📊 Polymarket Change: {signal['polymarket_change']} ({signal['timeframe']})")
        print(f"💪 Signal Strength: {signal['signal_strength']}")
        print(f"⏰ Time: {signal['timestamp']}")
        print("\n💡 Trade Suggestions:")
        
        for i, suggestion in enumerate(signal['trade_suggestions'], 1):
            data_source = suggestion.get('data_source', '📈 Estimated')
            sample_info = ""
            if suggestion.get('sample_size'):
                sample_info = f" (n={suggestion['sample_size']})"
            if suggestion.get('p_value'):
                p_val = suggestion['p_value']
                sig = "✅" if p_val < 0.05 else "⚠️"
                sample_info += f" {sig}p={p_val:.3f}"
            
            print(f"  {i}. {suggestion['direction']} {suggestion['asset']} {data_source}{sample_info}")
            print(f"     Expected Move: {suggestion['expected_move']}")
            print(f"     Confidence: {suggestion['confidence']}")
            print(f"     Timeframe: {suggestion['timeframe']}")
        
        print(f"\n⚠️  {signal['risk_warning']}")
        print("=" * 60 + "\n")
        
        # Save signal to database
        try:
            signal_to_save = signal.copy()
            signal_to_save["market_id"] = raw.get("market_id")
            self.db.save_signal(signal_to_save)
        except:
            pass  # Don't fail if database save fails
        
        # Store signal
        self.signals_generated.append(signal_data)
    
    async def run(self):
        """Main monitoring loop"""
        try:
            await self.initialize()
            
            iteration = 0
            while True:
                iteration += 1
                print(f"\n🔄 Check #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                signals = await self.check_markets()
                
                if signals:
                    print(f"✅ Found {len(signals)} significant signal(s)")
                    for signal_data in signals:
                        self.display_signal(signal_data)
                else:
                    print("⏳ No significant changes detected")
                
                # Also collect current asset prices for database
                try:
                    crypto_prices = await self.crypto_collector.get_prices()
                    for symbol, data in crypto_prices.items():
                        self.db.save_asset_data(
                            asset_symbol=symbol,
                            price=data["price"],
                            asset_name=data["name"],
                            change_24h=data.get("change_24h")
                        )
                except:
                    pass  # Don't fail monitoring if price collection fails
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Error in monitoring loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        await self.pm_collector.close()
        await self.crypto_collector.close()
        
        stats = self.db.get_stats()
        print(f"📊 Session summary:")
        print(f"   Signals generated: {len(self.signals_generated)}")
        print(f"   Total signals in DB: {stats.get('signals_generated', 0)}")
        print(f"   Market data points: {stats.get('market_data_points', 0)}")
        print(f"   Asset data points: {stats.get('asset_data_points', 0)}")
        print("✅ Cleanup complete")


async def main():
    """Entry point"""
    print("=" * 60)
    print("🚀 PolySignal - Hybrid Monitor (Real + Estimated Correlations)")
    print("=" * 60)
    print()
    
    # Create and run monitor
    monitor = HybridMonitor(
        min_price_change=5.0,  # 5% minimum change to trigger signal
        check_interval=60      # Check every 60 seconds
    )
    
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())

