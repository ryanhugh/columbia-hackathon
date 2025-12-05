"""
PolySignal - Historical Data Collection Script
Collects and stores historical market data for correlation analysis
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from data_collector import PolymarketCollector
from market_data import CryptoCollector
from database import Database


class DataCollector:
    """Collects historical data from multiple sources"""
    
    def __init__(self):
        """Initialize collectors and database"""
        load_dotenv()
        self.pm_collector = PolymarketCollector()
        self.crypto_collector = CryptoCollector()
        self.db = Database()
    
    async def collect_polymarket_data(self, hours: int = 24):
        """
        Collect Polymarket data for specified hours
        
        Args:
            hours: How many hours of data to collect (default: 24)
        """
        print(f"🔍 Collecting Polymarket data for {hours} hours...")
        
        markets = await self.pm_collector.get_active_markets(min_volume=50000)
        print(f"✅ Found {len(markets)} active markets")
        
        collected = 0
        for market in markets:
            try:
                self.db.save_market_data(
                    market_id=market["id"],
                    price=market["current_price"],
                    market_question=market["question"],
                    category=market["category"],
                    volume_24h=market.get("volume_24h")
                )
                collected += 1
            except Exception as e:
                print(f"⚠️  Error saving market {market['id']}: {e}")
        
        print(f"✅ Collected {collected} market data points")
        return collected
    
    async def collect_crypto_data(self):
        """Collect current crypto prices"""
        print("🔍 Collecting crypto prices...")
        
        try:
            prices = await self.crypto_collector.get_prices()
            
            collected = 0
            for symbol, data in prices.items():
                try:
                    self.db.save_asset_data(
                        asset_symbol=symbol,
                        price=data["price"],
                        asset_name=data["name"],
                        change_24h=data.get("change_24h")
                    )
                    collected += 1
                except Exception as e:
                    print(f"⚠️  Error saving {symbol}: {e}")
            
            print(f"✅ Collected {collected} crypto price points")
            return collected
        except Exception as e:
            print(f"❌ Error collecting crypto data: {e}")
            return 0
    
    async def collect_continuous(self, interval_minutes: int = 5, duration_hours: int = 24):
        """
        Continuously collect data for specified duration
        
        Args:
            interval_minutes: Minutes between collections
            duration_hours: Total hours to collect
        """
        print(f"🚀 Starting continuous data collection")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Duration: {duration_hours} hours")
        print(f"   Total collections: ~{int((duration_hours * 60) / interval_minutes)}")
        print("-" * 60)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        iteration = 0
        
        try:
            while datetime.now() < end_time:
                iteration += 1
                print(f"\n📊 Collection #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Collect both data types
                pm_count = await self.collect_polymarket_data(hours=1)
                crypto_count = await self.collect_crypto_data()
                
                # Show stats
                stats = self.db.get_stats()
                print(f"📈 Database stats:")
                print(f"   Market data points: {stats.get('market_data_points', 0)}")
                print(f"   Asset data points: {stats.get('asset_data_points', 0)}")
                
                # Wait for next collection
                if datetime.now() < end_time:
                    wait_seconds = interval_minutes * 60
                    print(f"⏳ Waiting {interval_minutes} minutes until next collection...")
                    await asyncio.sleep(wait_seconds)
            
            print("\n✅ Data collection complete!")
            final_stats = self.db.get_stats()
            print(f"📊 Final stats:")
            print(f"   Market data points: {final_stats.get('market_data_points', 0)}")
            print(f"   Asset data points: {final_stats.get('asset_data_points', 0)}")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Collection stopped by user")
            final_stats = self.db.get_stats()
            print(f"📊 Collected so far:")
            print(f"   Market data points: {final_stats.get('market_data_points', 0)}")
            print(f"   Asset data points: {final_stats.get('asset_data_points', 0)}")
        except Exception as e:
            print(f"\n❌ Error during collection: {e}")
        finally:
            await self.cleanup()
    
    async def collect_single(self):
        """Collect data once"""
        print("📊 Single data collection run")
        print("-" * 60)
        
        await self.collect_polymarket_data()
        await self.collect_crypto_data()
        
        stats = self.db.get_stats()
        print("\n📈 Current database stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.pm_collector.close()
        await self.crypto_collector.close()


async def main():
    """Main entry point"""
    import sys
    
    collector = DataCollector()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "continuous":
            # Continuous collection
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            duration = int(sys.argv[3]) if len(sys.argv) > 3 else 24
            await collector.collect_continuous(interval_minutes=interval, duration_hours=duration)
        elif command == "single":
            # Single collection
            await collector.collect_single()
        else:
            print("Usage:")
            print("  python collect_data.py single              # Collect once")
            print("  python collect_data.py continuous [interval] [duration]")
            print("  python collect_data.py continuous 5 24    # Every 5 min for 24 hours")
    else:
        # Default: single collection
        await collector.collect_single()


if __name__ == "__main__":
    asyncio.run(main())

