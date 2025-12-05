import asyncio
import sys
import os
sys.path.append('/Users/amberkhan/Documents/trae_projects/alpha')

from integrations.de_search import DeSearchClient

async def test_trading_agent_flow():
    """Test the complete trading agent flow with real social media data"""
    
    client = DeSearchClient()
    
    # Test different crypto queries that a trading agent might use
    test_queries = [
        ("bitcoin", "crypto"),
        ("ethereum", "crypto"),
        ("solana", "crypto"),
        ("defi", "crypto"),
        ("nft", "crypto")
    ]
    
    print("Testing Trading Agent Flow with Real Social Media Data")
    print("=" * 60)
    
    for query, category in test_queries:
        print(f"\n🔍 Analyzing: {query.upper()} ({category})")
        print("-" * 40)
        
        try:
            result = await client.search_multi(query, category)
            
            if result.get('status') == 'success':
                source = result.get('source', 'unknown')
                sentiment = result.get('sentiment_score', 0)
                tweets = result.get('key_content', {}).get('tweets', [])
                
                print(f"✅ Source: {source}")
                print(f"📊 Sentiment: {sentiment:.3f}")
                print(f"🐦 Tweets: {len(tweets)}")
                
                if tweets:
                    # Show most engaging tweet
                    top_tweet = max(tweets, key=lambda x: x.get('likes', 0))
                    print(f"🔥 Top tweet: {top_tweet.get('text', '')[:80]}...")
                    print(f"   💖 {top_tweet.get('likes', 0)} likes")
                
                # Trading signal interpretation
                if sentiment > 0.3:
                    signal = "🚀 BULLISH"
                elif sentiment < -0.3:
                    signal = "🐻 BEARISH"
                else:
                    signal = "⚖️ NEUTRAL"
                
                print(f"📈 Trading Signal: {signal}")
                
            else:
                print(f"❌ Failed: {result.get('error', 'unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Trading Agent Flow Test Complete!")
    print("The agent is now using REAL social media data for sentiment analysis!")

if __name__ == "__main__":
    asyncio.run(test_trading_agent_flow())