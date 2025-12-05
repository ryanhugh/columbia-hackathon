import os
import httpx

class AproOracleClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("APRO_BASE_URL", "")
        self.api_key = os.getenv("APRO_API_KEY", "")
        # APRO v1 API base URL (public, no API key required)
        self.v1_base_url = "https://api-ai-oracle.apro.com/v1"

    async def fetch_market_baseline(self, market_id: str) -> dict:
        if not self.base_url or not self.api_key:
            return {"direction": "YES", "confidence": 0.5, "proof_link": ""}
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{self.base_url}/baseline",
                    params={"market_id": market_id},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                if res.status_code != 200:
                    return {"direction": "YES", "confidence": 0.5, "proof_link": ""}
                return res.json()
        except Exception:
            return {"direction": "YES", "confidence": 0.5, "proof_link": ""}
    
    async def fetch_real_price_data(self, symbol: str, quotation: str = "usd") -> dict:
        """
        Fetch real price data from APRO v1 API (public, no API key required)
        This provides verified oracle data for prediction markets
        """
        try:
            print(f"⚖️ [APRO Oracle v1] Fetching real price for: {symbol}/{quotation}")
            
            # Map common symbols to APRO format
            symbol_mapping = {
                "BTC": "BTC",
                "ETH": "ETH", 
                "USD0": "USD0",
                "AAVE": "AAVE",
                "LINK": "LINK",
                "UNI": "UNI",
                "COMP": "COMP",
                "MKR": "MKR",
                "SNX": "SNX",
                "YFI": "YFI"
            }
            
            # Get the standardized symbol
            apro_symbol = symbol_mapping.get(symbol.upper(), symbol.upper())
            
            url = f"{self.v1_base_url}/ticker/currency/price"
            params = {
                "name": apro_symbol,
                "quotation": quotation,
                "type": "median"  # Get median price from multiple sources
            }
            
            async with httpx.AsyncClient() as client:
                # No headers needed for v1 API - it's public!
                res = await client.get(url, params=params, timeout=15.0)
                
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status", {}).get("code") == 200:
                        price_data = data.get("data", {})
                        price = price_data.get("price")
                        timestamp = price_data.get("timestamp")
                        
                        print(f"✅ [APRO Oracle v1] Got live price: ${price} at {timestamp}")
                        
                        return {
                            "source": "APRO Oracle v1 (Live)",
                            "symbol": symbol,
                            "price": price,
                            "timestamp": timestamp,
                            "status": "STABLE" if 0.98 <= price <= 1.02 else "VOLATILE" if price > 0 else "ERROR",
                            "providers": price_data.get("providers", []),
                            "proof_link": f"https://api-ai-oracle.apro.com/v1/ticker/currency/price?name={apro_symbol}&quotation={quotation}"
                        }
                    else:
                        print(f"⚠️ [APRO Oracle v1] API returned error: {data.get('status', {})}")
                        return self._create_fallback_price(symbol)
                else:
                    print(f"⚠️ [APRO Oracle v1] HTTP {res.status_code}: {res.text}")
                    return self._create_fallback_price(symbol)
                    
        except Exception as e:
            print(f"❌ [APRO Oracle v1] Error fetching price: {e}")
            return self._create_fallback_price(symbol)
    
    def _create_fallback_price(self, symbol: str) -> dict:
        """Create fallback price data when APRO v1 fails"""
        print(f"📊 [APRO Oracle] Using fallback for {symbol}")
        
        # Basic fallback prices for common symbols
        fallback_prices = {
            "BTC": 45000,
            "ETH": 2500,
            "USD0": 1.0,
            "AAVE": 120,
            "LINK": 15,
            "UNI": 8,
            "COMP": 65,
            "MKR": 1500,
            "SNX": 4,
            "YFI": 9000
        }
        
        price = fallback_prices.get(symbol.upper(), 100)
        
        return {
            "source": "APRO Oracle (Fallback)",
            "symbol": symbol,
            "price": price,
            "timestamp": int(time.time()),
            "status": "FALLBACK",
            "providers": ["fallback"],
            "proof_link": "#"
        }
    
    async def get_supported_currencies(self) -> list:
        """Get list of supported currencies from APRO v1"""
        try:
            url = f"{self.v1_base_url}/ticker/currencies/list"
            
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=10.0)
                
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status", {}).get("code") == 200:
                        currencies = data.get("data", {}).get("currencies", [])
                        print(f"✅ [APRO Oracle v1] Found {len(currencies)} supported currencies")
                        return currencies
                
                print(f"⚠️ [APRO Oracle v1] Failed to get currencies: {res.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ [APRO Oracle v1] Error fetching currencies: {e}")
            return []