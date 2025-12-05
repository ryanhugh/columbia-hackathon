import asyncio
import httpx
import json

async def get_reddit_data_structure():
    """Get detailed Reddit data structure from DeSearch API"""
    
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
                
                print("=== REDDIT DATA STRUCTURE ===")
                reddit_data = data.get('reddit_search', [])
                print(f"Reddit items found: {len(reddit_data)}")
                
                if reddit_data:
                    print(f"\nFirst Reddit item keys: {list(reddit_data[0].keys())}")
                    print(f"\nFirst Reddit item:")
                    print(json.dumps(reddit_data[0], indent=2))
                
                print("\n=== ALL RESPONSE KEYS ===")
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"{key}: list with {len(value)} items")
                        if value and key == 'reddit_search':
                            print(f"  Sample item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'Not a dict'}")
                    elif isinstance(value, dict):
                        print(f"{key}: dict with {len(value)} keys")
                    elif isinstance(value, str):
                        print(f"{key}: string (length {len(value)})")
                    else:
                        print(f"{key}: {type(value)}")
                
                return True
            else:
                print(f"Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(get_reddit_data_structure())