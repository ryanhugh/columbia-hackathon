import asyncio
import httpx

async def test_different_auth_methods():
    """Test different authentication methods for DeSearch API"""
    
    api_key = "dt_$z88FMCYHlBu_Ep9aobf2IQtMmU4u-nD-DNpDIUDRZuA"
    url = "https://api.desearch.ai/desearch/ai/search"
    
    payload = {
        "date_filter": "PAST_24_HOURS",
        "model": "NOVA",
        "prompt": "bitcoin",
        "streaming": False,
        "tools": ["Twitter Search"]
    }
    
    # Test different authentication methods
    auth_methods = [
        {"name": "Direct Auth (current)", "headers": {"Authorization": api_key, "Content-Type": "application/json"}},
        {"name": "Bearer Token", "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}},
        {"name": "X-API-Key Header", "headers": {"X-API-Key": api_key, "Content-Type": "application/json"}},
        {"name": "API Key in URL", "headers": {"Content-Type": "application/json"}, "params": {"api_key": api_key}},
    ]
    
    for i, auth_method in enumerate(auth_methods):
        print(f"\n--- Testing {auth_method['name']} ---")
        print(f"Headers: {auth_method['headers']}")
        if 'params' in auth_method:
            print(f"Params: {auth_method['params']}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if 'params' in auth_method:
                    response = await client.post(url, json=payload, headers=auth_method['headers'], params=auth_method['params'])
                else:
                    response = await client.post(url, json=payload, headers=auth_method['headers'])
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    tweets = data.get('tweets', [])
                    print(f"✅ SUCCESS! Found {len(tweets)} tweets")
                    if tweets:
                        print(f"Sample tweet: {tweets[0].get('text', '')[:100]}...")
                    return True
                else:
                    print(f"Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return False

if __name__ == "__main__":
    result = asyncio.run(test_different_auth_methods())
    print(f"\n{'✅ SUCCESS' if result else '❌ FAILED'}: Found working auth method!")