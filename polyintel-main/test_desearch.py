import asyncio
import httpx
import json

async def test_desearch_api():
    """Test the DeSearch API directly to verify it works"""
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
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=12.0)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ SUCCESS! Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Response keys: {list(data.keys())}")
                    else:
                        print(f"Response: {str(data)[:200]}...")
                    return True
                except Exception as json_error:
                    print(f"❌ JSON parse error: {json_error}")
                    print(f"Raw response: {response.text[:300]}...")
                    return False
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_desearch_api())
    print(f"\nAPI Working: {result}")