import asyncio
import os
import httpx

async def debug_api_key():
    """Debug API key and environment setup"""
    
    # Check environment variables
    api_key = os.getenv("DESEARCH_API_KEY", "")
    base_url = os.getenv("DESEARCH_BASE_URL", "")
    
    print(f"DESEARCH_API_KEY: {api_key[:20]}... (length: {len(api_key)})")
    print(f"DESEARCH_BASE_URL: {base_url}")
    
    # Test direct API call with the exact same setup as the integration
    url = f"{base_url}/desearch/ai/search"
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    
    payload = {
        "date_filter": "PAST_24_HOURS",
        "model": "NOVA",
        "prompt": "bitcoin",
        "streaming": False,
        "tools": ["Twitter Search"]
    }
    
    print(f"\nTesting direct API call:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Found {len(data.get('tweets', []))} tweets")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(debug_api_key())
    print(f"\nAPI Key Test: {'✅ SUCCESS' if result else '❌ FAILED'}")