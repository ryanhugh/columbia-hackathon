import asyncio
import sys
import os
sys.path.append('/Users/amberkhan/Documents/trae_projects/alpha')

from integrations.de_search import DeSearchClient

async def test_full_multi_source():
    """Test the DeSearch integration with full multi-source data (Twitter + Reddit + Web)"""
    
    client = DeSearchClient()
    
    print("Testing Full Multi-Source Integration (Twitter + Reddit + Web)")
    print("=" * 65)
    
    # Use "crypto" query since it returns Reddit data
    query = "crypto"
    category = "crypto"
    
    try:
        result = await client.search_multi(query, category)
        
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Source: {result.get('source', 'unknown')}")
        print(f"Query: {result.get('query', 'unknown')}")
        print(f"Sentiment Score: {result.get('sentiment_score', 'unknown')}")
        
        # Check all content types
        key_content = result.get('key_content', {})
        tweets = key_content.get('tweets', [])
        posts = key_content.get('posts', [])
        news = key_content.get('news', [])
        sources = key_content.get('sources', [])
        
        print(f"\n📊 CONTENT BREAKDOWN:")
        print(f"🐦 Twitter: {len(tweets)} tweets")
        print(f"🤖 Reddit: {len(posts)} posts")
        print(f"🌐 Web/News: {len(news)} articles")
        print(f"📡 Active Sources: {sources}")
        
        # Show Reddit data
        if posts:
            print(f"\n🔥 TOP REDDIT POSTS:")
            for i, post in enumerate(posts[:3]):
                print(f"{i+1}. 📰 {post.get('text', 'No title')[:80]}...")
                print(f"   🔗 {post.get('url', 'No link')[:60]}...")
                if post.get('snippet'):
                    print(f"   📝 {post.get('snippet', '')[:100]}...")
                print()
        
        # Show Twitter data
        if tweets:
            print(f"🐦 TOP TWEETS:")
            for i, tweet in enumerate(tweets[:2]):
                print(f"{i+1}. @{tweet.get('user', 'unknown')}:")
                print(f"   {tweet.get('text', 'No text')[:80]}...")
                print(f"   💖 {tweet.get('likes', 0)} likes | 🔄 {tweet.get('retweets', 0)} retweets")
                print()
        
        # Show web data
        if news:
            print(f"🌐 WEB ARTICLES:")
            for i, article in enumerate(news[:2]):
                print(f"{i+1}. 📄 {article.get('title', 'No title')[:80]}...")
                print(f"   📝 {article.get('text', 'No snippet')[:100]}...")
                print(f"   🔗 {article.get('url', 'No link')[:60]}...")
                print()
        
        # Metrics
        metrics = result.get('metrics', {})
        print(f"📈 METRICS:")
        print(f"  Total items analyzed: {metrics.get('total_items', 0)}")
        print(f"  Source diversity: {metrics.get('source_diversity', 0)} (1.0 = maximum diversity)")
        print(f"  Twitter count: {metrics.get('tweet_count', 0)}")
        print(f"  Reddit count: {metrics.get('post_count', 0)}")
        print(f"  Web count: {metrics.get('news_count', 0)}")
        
        # Summary
        summary = result.get('summary', {})
        print(f"\n📝 AI SUMMARY:")
        print(f"  Overall: {summary.get('overall', 'no summary')}")
        if summary.get('completion'):
            print(f"  Analysis: {summary.get('completion', '')[:300]}...")
        
        # Trading signal
        sentiment = result.get('sentiment_score', 0)
        if sentiment > 0.3:
            signal = "🚀 BULLISH - Strong positive sentiment"
        elif sentiment < -0.3:
            signal = "🐻 BEARISH - Strong negative sentiment"
        elif sentiment > 0.1:
            signal = "📈 SLIGHTLY BULLISH - Moderate positive sentiment"
        elif sentiment < -0.1:
            signal = "📉 SLIGHTLY BEARISH - Moderate negative sentiment"
        else:
            signal = "⚖️ NEUTRAL - Mixed or balanced sentiment"
        
        print(f"\n💰 TRADING SIGNAL: {signal}")
        print(f"📊 Sentiment Score: {sentiment:.3f}")
        
        return result.get('status') == 'success' and len(sources) > 1
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_multi_source())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Multi-source integration working!")
    if success:
        print("🎉 Your trading agent now has access to REAL data from Twitter, Reddit, AND the web!")
    else:
        print("⚠️  Only single source working - check API response for more data sources.")