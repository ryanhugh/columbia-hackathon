import asyncio
import httpx
import json

async def debug_reddit_data():
    """Debug Reddit data from DeSearch API"""
    
    api_key = "dt_$z88FMCYHlBu_Ep9aobf2IQtMmU4u-nD-DNpDIUDRZuA"
    url = "https://api.desearch.ai/desearch/ai/search"
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "date_filter": "PAST_24_HOURS",
        "model": "NOVA",
        "prompt": "bitcoin",
        "streaming": False,
        "tools": ["Twitter Search", "reddit", "Web Search"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                print("=== DEBUGGING REDDIT DATA ===")
                print(f"Response keys: {list(data.keys())}")
                
                reddit_data = data.get('reddit_search', [])
                print(f"Raw reddit_search data: {reddit_data}")
                print(f"Reddit data type: {type(reddit_data)}")
                print(f"Reddit data length: {len(reddit_data) if isinstance(reddit_data, list) else 'Not a list'}")
                
                if reddit_data and isinstance(reddit_data, list):
                    print(f"\nFirst Reddit item:")
                    print(json.dumps(reddit_data[0], indent=2))
                
                # Also check other data
                tweets = data.get('tweets', [])
                search = data.get('search', [])
                print(f"\nTweets: {len(tweets)}")
                print(f"Search items: {len(search)}")
                
                return True
            else:
                print(f"Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_reddit_data())