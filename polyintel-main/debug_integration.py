import asyncio
import sys
import os
sys.path.append('/Users/amberkhan/Documents/trae_projects/alpha')

from integrations.de_search import DeSearchClient

async def debug_integration():
    """Debug the DeSearch integration step by step"""
    
    # Initialize the client
    client = DeSearchClient()
    
    print(f"Client API key: {client.api_key[:20]}... (length: {len(client.api_key)})")
    print(f"Client base URL: {client.base_url}")
    
    # Test the main API call directly
    import httpx
    
    api_key = client.api_key
    base = client.base_url or "https://api.desearch.ai"
    url = f"{base}/desearch/ai/search"
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    
    payload = {
        "date_filter": "PAST_24_HOURS",
        "model": "NOVA",
        "prompt": "bitcoin",
        "streaming": False,
        "tools": ["Twitter Search"]
    }
    
    print(f"\nTesting direct API call with integration settings:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"API key length: {len(api_key)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            response = await http_client.post(url, json=payload, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                tweets = data.get('tweets', [])
                print(f"✅ SUCCESS! Found {len(tweets)} real tweets")
                if tweets:
                    print(f"Sample: {tweets[0].get('text', '')[:100]}...")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(debug_integration())
    print(f"\nDirect API Test: {'✅ SUCCESS' if result else '❌ FAILED'}")