import asyncio
import sys
import os
sys.path.append('/Users/amberkhan/Documents/trae_projects/alpha')

from integrations.de_search import DeSearchClient

async def test_integration():
    """Test the DeSearch integration with real data"""
    
    # Initialize the client
    client = DeSearchClient()
    
    # Test with a crypto query
    query = "bitcoin"
    category = "crypto"
    
    print(f"Testing DeSearch integration with query: '{query}'")
    print("=" * 50)
    
    try:
        result = await client.search_multi(query, category)
        
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Source: {result.get('source', 'unknown')}")
        print(f"Query: {result.get('query', 'unknown')}")
        print(f"Category: {result.get('category', 'unknown')}")
        print(f"Sentiment Score: {result.get('sentiment_score', 'unknown')}")
        
        # Check if we got real data
        key_content = result.get('key_content', {})
        tweets = key_content.get('tweets', [])
        
        print(f"\nReal Twitter Data Found: {len(tweets)} tweets")
        
        if tweets:
            print("\nSample tweets:")
            for i, tweet in enumerate(tweets[:3]):
                print(f"{i+1}. @{tweet.get('user', 'unknown')}:")
                print(f"   {tweet.get('text', 'no text')[:100]}...")
                print(f"   Likes: {tweet.get('likes', 0)}, Retweets: {tweet.get('retweets', 0)}")
                print()
        
        # Check metrics
        metrics = result.get('metrics', {})
        print(f"Metrics:")
        print(f"  Total items: {metrics.get('total_items', 0)}")
        print(f"  Tweet count: {metrics.get('tweet_count', 0)}")
        print(f"  Source diversity: {metrics.get('source_diversity', 0)}")
        
        # Check summary
        summary = result.get('summary', {})
        print(f"\nSummary:")
        print(f"  Overall: {summary.get('overall', 'no summary')}")
        
        return result.get('status') == 'success' and len(tweets) > 0
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Integration working with real data!")