# Test APRO Oracle v1 integration
import asyncio
import os
from integrations.apro_oracle import AproOracleClient

async def test_apro_v1():
    client = AproOracleClient()
    
    # Test supported currencies
    print("📋 Testing APRO v1 supported currencies...")
    currencies = await client.get_supported_currencies()
    print(f"Supported currencies: {currencies[:10]}...")  # First 10
    
    # Test real price data
    test_symbols = ["BTC", "ETH", "USD0", "AAVE", "LINK"]
    
    for symbol in test_symbols:
        print(f"\n💰 Testing price for {symbol}...")
        result = await client.fetch_real_price_data(symbol)
        print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_apro_v1())