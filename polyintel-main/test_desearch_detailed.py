import asyncio
import httpx
import json

async def test_desearch_api_detailed():
    """Test the DeSearch API and get detailed response structure"""
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
        "tools": ["Twitter Search"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"Making request to {url}...")
            response = await client.post(url, json=payload, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ SUCCESS! Response type: {type(data)}")
                    
                    # Print detailed structure
                    print("\n=== RESPONSE STRUCTURE ===")
                    for key, value in data.items():
                        print(f"\n{key}:")
                        if isinstance(value, list):
                            print(f"  Type: list with {len(value)} items")
                            if value and len(value) > 0:
                                print(f"  First item type: {type(value[0])}")
                                if isinstance(value[0], dict):
                                    print(f"  First item keys: {list(value[0].keys())}")
                                    # Show first item content
                                    print(f"  Sample first item: {json.dumps(value[0], indent=2)[:300]}...")
                        elif isinstance(value, dict):
                            print(f"  Type: dict with keys: {list(value.keys())}")
                        elif isinstance(value, str):
                            print(f"  Type: string (length {len(value)})")
                            if len(value) > 0:
                                print(f"  Content preview: {value[:200]}...")
                        else:
                            print(f"  Type: {type(value)}")
                            print(f"  Value: {value}")
                    
                    return True
                except Exception as json_error:
                    print(f"❌ JSON parse error: {json_error}")
                    print(f"Raw response: {response.text[:300]}...")
                    return False
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_desearch_api_detailed())
    print(f"\nAPI Working: {result}")