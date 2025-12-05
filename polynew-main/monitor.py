"""
PolySignal - Main Monitoring Script
Monitors Polymarket for significant price movements and generates trading signals
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from data_collector import PolymarketCollector
from market_data import CryptoCollector
from correlation_engine import CorrelationEngine

# Load environment variables from .env file
load_dotenv()


class PolySignalMonitor:
    """Main monitoring system that watches Polymarket and generates signals"""
    
    def __init__(self, min_price_change: float = 5.0, check_interval: int = 60):
        """
        Initialize the monitor
        
        Args:
            min_price_change: Minimum price change percentage to trigger signal (default: 5%)
            check_interval: Seconds between checks (default: 60)
        """
        self.pm_collector = PolymarketCollector()
        # Pass API key from environment if available
        coingecko_key = os.getenv("COINGECKO_API_KEY")
        self.crypto_collector = CryptoCollector(api_key=coingecko_key)
        self.correlation_engine = CorrelationEngine()
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
                # Generate signal
                market_data = {
                    "id": market_id,
                    "question": market_info["question"],
                    "category": market_info["category"],
                    "current_price": result["current_price"]
                }
                
                signal = self.correlation_engine.generate_signal(
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
        
        print("\n" + "=" * 60)
        print("🚨 NEW SIGNAL DETECTED")
        print("=" * 60)
        print(f"📋 Market: {signal['market_question']}")
        print(f"🏷️  Category: {signal['category']}")
        print(f"📊 Polymarket Change: {signal['polymarket_change']} ({signal['timeframe']})")
        print(f"💪 Signal Strength: {signal['signal_strength']}")
        print(f"⏰ Time: {signal['timestamp']}")
        print("\n💡 Trade Suggestions:")
        
        for i, suggestion in enumerate(signal['trade_suggestions'], 1):
            print(f"  {i}. {suggestion['direction']} {suggestion['asset']}")
            print(f"     Expected Move: {suggestion['expected_move']}")
            print(f"     Confidence: {suggestion['confidence']}")
            print(f"     Timeframe: {suggestion['timeframe']}")
        
        print(f"\n⚠️  {signal['risk_warning']}")
        print("=" * 60 + "\n")
        
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
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Error in monitoring loop: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        await self.pm_collector.close()
        await self.crypto_collector.close()
        print(f"📊 Total signals generated this session: {len(self.signals_generated)}")
        print("✅ Cleanup complete")


async def main():
    """Entry point"""
    print("=" * 60)
    print("🚀 PolySignal - Polymarket Cross-Market Signal Monitor")
    print("=" * 60)
    print()
    
    # Create and run monitor
    monitor = PolySignalMonitor(
        min_price_change=5.0,  # 5% minimum change to trigger signal
        check_interval=60      # Check every 60 seconds
    )
    
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())

