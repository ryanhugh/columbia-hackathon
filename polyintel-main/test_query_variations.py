import asyncio
import httpx

async def test_different_queries():
    """Test different queries to see if Reddit data is available"""
    
    api_key = "dt_$z88FMCYHlBu_Ep9aobf2IQtMmU4u-nD-DNpDIUDRZuA"
    url = "https://api.desearch.ai/desearch/ai/search"
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    base_payload = {
        "date_filter": "PAST_24_HOURS",
        "model": "NOVA",
        "streaming": False,
        "tools": ["Twitter Search", "reddit", "Web Search"]
    }
    
    # Test different queries that might have more Reddit activity
    test_queries = [
        "bitcoin",
        "crypto",
        "cryptocurrency", 
        "ethereum",
        "defi",
        "wallstreetbets",
        "gamestop",
        "reddit crypto"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing query: '{query}' ---")
        
        payload = {**base_payload, "prompt": query}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    tweets = data.get('tweets', [])
                    reddit = data.get('reddit_search', [])
                    search = data.get('search', [])
                    
                    print(f"✅ Tweets: {len(tweets)}")
                    print(f"✅ Reddit: {len(reddit)}")
                    print(f"✅ Search: {len(search)}")
                    
                    if reddit:
                        print(f"🎉 REDDIT DATA FOUND for '{query}'!")
                        print(f"Sample: {reddit[0].get('title', 'No title')[:80]}...")
                        return True
                    
                    if search:
                        print(f"🎉 SEARCH DATA FOUND for '{query}'!")
                        print(f"Sample: {search[0].get('title', 'No title')[:80]}...")
                        
                else:
                    print(f"❌ Failed: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n--- Summary ---")
    print("Reddit data availability may depend on the specific query and current activity.")
    print("The API supports Reddit, but may not always return data for all queries.")
    return False

if __name__ == "__main__":
    asyncio.run(test_different_queries())