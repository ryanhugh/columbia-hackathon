import asyncio
import httpx

async def test_reddit_support():
    """Test if DeSearch API supports Reddit data"""
    
    api_key = "dt_$z88FMCYHlBu_Ep9aobf2IQtMmU4u-nD-DNpDIUDRZuA"
    url = "https://api.desearch.ai/desearch/ai/search"
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    # Test different tool combinations
    tool_combinations = [
        ["Twitter Search"],
        ["Reddit Search"],
        ["Twitter Search", "Reddit Search"],
        ["Social Media Search"],
        ["Reddit"],
        ["reddit"],
        ["social"],
        ["Social"],
        ["Twitter Search", "Reddit Search", "Web Search"],
        ["Twitter", "Reddit"],
    ]
    
    base_payload = {
        "date_filter": "PAST_24_HOURS",
        "model": "NOVA",
        "prompt": "bitcoin",
        "streaming": False,
    }
    
    for tools in tool_combinations:
        print(f"\n--- Testing tools: {tools} ---")
        payload = {**base_payload, "tools": tools}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check what data we got back
                    tweets = data.get('tweets', [])
                    posts = data.get('posts', [])
                    reddit_data = data.get('reddit', [])
                    
                    print(f"✅ SUCCESS!")
                    print(f"Tweets: {len(tweets)}")
                    print(f"Posts: {len(posts)}")
                    print(f"Reddit data: {len(reddit_data)}")
                    
                    # Check response keys
                    response_keys = list(data.keys())
                    print(f"Response keys: {response_keys}")
                    
                    # If we have Reddit data, show a sample
                    if reddit_data:
                        print(f"Sample Reddit post: {reddit_data[0] if reddit_data else 'None'}")
                    elif posts:
                        print(f"Sample post: {posts[0] if posts else 'None'}")
                    
                    # Check if there are any other social media indicators
                    for key, value in data.items():
                        if isinstance(value, list) and key not in ['tweets', 'posts', 'reddit']:
                            print(f"{key}: {len(value)} items")
                            
                else:
                    print(f"Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_reddit_support())