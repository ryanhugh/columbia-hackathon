import asyncio
import sys
import os
sys.path.append('/Users/amberkhan/Documents/trae_projects/alpha')

from integrations.de_search import DeSearchClient

async def test_reddit_integration():
    """Test the DeSearch integration with Reddit data"""
    
    client = DeSearchClient()
    
    print("Testing DeSearch Integration with Reddit Data")
    print("=" * 50)
    
    try:
        result = await client.search_multi("bitcoin", "crypto")
        
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Source: {result.get('source', 'unknown')}")
        print(f"Sentiment Score: {result.get('sentiment_score', 'unknown')}")
        
        # Check all content types
        key_content = result.get('key_content', {})
        tweets = key_content.get('tweets', [])
        posts = key_content.get('posts', [])
        news = key_content.get('news', [])
        sources = key_content.get('sources', [])
        
        print(f"\n📊 Content Breakdown:")
        print(f"🐦 Twitter: {len(tweets)} tweets")
        print(f"🤖 Reddit: {len(posts)} posts")
        print(f"🌐 Web/News: {len(news)} articles")
        print(f"📡 Sources: {sources}")
        
        # Show Reddit data
        if posts:
            print(f"\n🔥 Top Reddit Posts:")
            for i, post in enumerate(posts[:3]):
                print(f"{i+1}. {post.get('text', 'No title')[:80]}...")
                print(f"   🔗 {post.get('url', 'No link')[:50]}...")
                if post.get('snippet'):
                    print(f"   📝 {post.get('snippet', '')[:100]}...")
                print()
        
        # Show Twitter data
        if tweets:
            print(f"🐦 Top Tweets:")
            for i, tweet in enumerate(tweets[:2]):
                print(f"{i+1}. @{tweet.get('user', 'unknown')}:")
                print(f"   {tweet.get('text', 'No text')[:80]}...")
                print(f"   💖 {tweet.get('likes', 0)} likes")
                print()
        
        # Show web data
        if news:
            print(f"🌐 Web Articles:")
            for i, article in enumerate(news[:2]):
                print(f"{i+1}. {article.get('title', 'No title')[:80]}...")
                print(f"   📝 {article.get('text', 'No snippet')[:100]}...")
                print(f"   🔗 {article.get('url', 'No link')[:50]}...")
                print()
        
        # Metrics
        metrics = result.get('metrics', {})
        print(f"📈 Metrics:")
        print(f"  Total items: {metrics.get('total_items', 0)}")
        print(f"  Source diversity: {metrics.get('source_diversity', 0)}")
        
        # Summary
        summary = result.get('summary', {})
        print(f"\n📝 Summary:")
        print(f"  Overall: {summary.get('overall', 'no summary')}")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_reddit_integration())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Reddit integration working!")