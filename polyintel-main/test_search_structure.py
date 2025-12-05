import asyncio
import httpx
import json

async def get_search_data_structure():
    """Get detailed search data structure from DeSearch API"""
    
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
        "tools": ["Twitter Search", "reddit", "Web Search"]  # Get all data
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                print("=== SEARCH DATA STRUCTURE ===")
                search_data = data.get('search', [])
                print(f"Search items found: {len(search_data)}")
                
                if search_data:
                    print(f"\nFirst search item keys: {list(search_data[0].keys())}")
                    print(f"\nFirst search item:")
                    print(json.dumps(search_data[0], indent=2))
                
                print("\n=== REDDIT DATA SAMPLE ===")
                reddit_data = data.get('reddit_search', [])
                if reddit_data:
                    print(f"First Reddit item:")
                    print(json.dumps(reddit_data[0], indent=2))
                
                return True
            else:
                print(f"Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(get_search_data_structure())