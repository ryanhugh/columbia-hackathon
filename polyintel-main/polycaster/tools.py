import os
import requests
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()

class AlphaTools:
    def __init__(self):
        self.eleven = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.desearch_key = os.getenv("DESEARCH_API_KEY")
        # Polymarket Public Endpoint (No Auth needed for reading)
        self.poly_url = "https://clob.polymarket.com"

    # --- 1. LIVE MARKET DATA (Polymarket) ---
    def get_polymarket_data(self, ticker_slug):
        """Fetches REAL-TIME odds from Polymarket."""
        print(f"🔍 [Live] Fetching Polymarket: {ticker_slug}...")
        try:
            # We use the Gamma API for easier public access
            url = f"https://gamma-api.polymarket.com/events?slug={ticker_slug}"
            response = requests.get(url)
            
            if response.status_code != 200:
                return {"error": "Market not found"}
                
            data = response.json()
            if not data:
                return {"error": "No data returned"}

            market = data[0]['markets'][0]
            
            # Parse the outcomePrices JSON string
            import json
            outcome_prices = json.loads(market['outcomePrices'])
            outcome_yes = float(outcome_prices[0])
            outcome_no = float(outcome_prices[1])
            
            return {
                "title": data[0]['title'],
                "yes_price": outcome_yes,
                "no_price": outcome_no,
                "volume": float(market['volume']),
                "liquidity": float(market['liquidity'])
            }
        except Exception as e:
            return {"error": str(e)}

    # --- 2. LIVE SOCIAL SENTIMENT (DeSearch) ---
    def get_social_signals(self, query):
        """Fetches REAL-TIME social posts via DeSearch."""
        print(f"📡 [Live] Scanning DeSearch: {query}...")
        url = "https://api.desearch.ai/v1/search"
        headers = {"Authorization": f"Bearer {self.desearch_key}"}
        
        # 'social' filter targets Twitter/Farcaster/Reddit via DeSearch
        payload = {"query": query, "filter": "social", "limit": 5}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                results = response.json().get('results', [])
                # extract just the snippets for the LLM
                return [r['content'] for r in results if 'content' in r]
            return []
        except:
            return ["Error fetching live socials."]

    # --- 3. LIVE GROUND TRUTH (APRO Oracle v1 - Real Verified Data) ---
    def get_real_world_price(self, symbol):
        """Fetches REAL-TIME verified asset price from APRO Oracle v1 API."""
        print(f"⚖️ [Live] Verifying Ground Truth via APRO Oracle for: {symbol}...")
        
        # Map symbols to APRO Oracle format
        apro_map = {
            "USD0": "usd0", 
            "USDC": "usd-coin", 
            "BTC": "bitcoin", 
            "ETH": "ethereum", 
            "SOL": "solana",
            "BNB": "binancecoin",
            "ADA": "cardano",
            "XRP": "ripple",
            "DOGE": "dogecoin",
            "MATIC": "polygon"
        }
        
        try:
            # Try APRO Oracle v1 API first (no API key required)
            apro_symbol = apro_map.get(symbol.upper(), symbol.lower())
            url = f"https://api-ai-oracle.apro.com/v1/ticker/currency/price"
            params = {
                "name": apro_symbol,
                "quotation": "usd",
                "type": "median"  # Get median price from multiple sources
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status", {}).get("code") == 200 and "data" in data:
                    price_data = data["data"]
                    price = float(price_data["price"])
                    timestamp = price_data.get("timestamp", "")
                    return {
                        "price": price, 
                        "source": f"APRO Oracle v1 (Verified) - {timestamp}",
                        "providers": price_data.get("prices", [])
                    }
            
            # Fallback to CoinGecko if APRO doesn't have the asset
            print(f"⚖️ APRO Oracle unavailable, falling back to CoinGecko for {symbol}")
            return self._get_coingecko_price(symbol)
            
        except Exception as e:
            print(f"⚖️ APRO Oracle error: {e}, falling back to CoinGecko")
            return self._get_coingecko_price(symbol)
    
    def _get_coingecko_price(self, symbol):
        """Fallback method using CoinGecko for price data."""
        # Map symbols to CoinGecko IDs
        cg_map = {
            "USD0": "usd0", 
            "USDC": "usd-coin", 
            "BTC": "bitcoin", 
            "ETH": "ethereum", 
            "SOL": "solana"
        }
        cg_id = cg_map.get(symbol.upper(), "bitcoin")
        
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
            data = requests.get(url).json()
            price = data[cg_id]['usd']
            return {"price": price, "source": "CoinGecko (Live)"}
        except:
            return {"price": None, "source": "CoinGecko (Error)"}

    # --- 4. LIVE AUDIO (ElevenLabs) ---
    def generate_audio(self, text):
        """Generates audio from the script."""
        try:
            print("🎙️ [Live] Synthesizing Audio...")
            audio_stream = self.eleven.text_to_speech.convert(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb", # 'George'
                model_id="eleven_turbo_v2_5",
                output_format="mp3_44100_128"
            )
            return b"".join(chunk for chunk in audio_stream)
        except Exception as e:
            print(f"Audio Error: {e}")
            return None