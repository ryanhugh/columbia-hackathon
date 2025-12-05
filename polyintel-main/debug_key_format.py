import os

# Check the exact API key from environment
api_key = os.getenv("DESEARCH_API_KEY", "")
print(f"Raw API key from env: '{api_key}'")
print(f"Length: {len(api_key)}")
print(f"First 10 chars: '{api_key[:10]}'")
print(f"Last 10 chars: '{api_key[-10:]}'")

# Check if there are any special characters
print(f"Contains '$': {'$' in api_key}")
print(f"Contains special chars: any(c for c in api_key if not c.isalnum() and c not in '_-$')")

# Try reading from .env file directly
import re
try:
    with open('/Users/amberkhan/Documents/trae_projects/alpha/.env', 'r') as f:
        content = f.read()
        # Find the DESEARCH_API_KEY line
        match = re.search(r'DESEARCH_API_KEY="([^"]*)"', content)
        if match:
            file_key = match.group(1)
            print(f"\nAPI key from file: '{file_key}'")
            print(f"File key length: {len(file_key)}")
            print(f"File key first 10: '{file_key[:10]}'")
            print(f"Match env key: {file_key == api_key}")
        else:
            print("\nCould not find DESEARCH_API_KEY in file")
except Exception as e:
    print(f"Error reading file: {e}")