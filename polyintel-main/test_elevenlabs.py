import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(os.getcwd()) / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)

# Test ElevenLabs integration
from spoon.audio import generate_briefing

def test_elevenlabs():
    """Test ElevenLabs audio generation"""
    
    # Test the API key
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    print(f"ELEVENLABS_API_KEY present: {bool(api_key)}")
    print(f"ELEVENLABS_API_KEY length: {len(api_key)}")
    
    # Test voice and model settings
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    print(f"Voice ID: {voice_id}")
    print(f"Model ID: {model_id}")
    
    # Test briefing generation
    test_text = "This is a test of the ElevenLabs audio briefing system for crypto trading signals."
    
    print(f"\nTesting audio generation with text: '{test_text}'")
    
    try:
        result = generate_briefing(test_text, "test_briefing.mp3")
        print(f"Audio generation result: {result}")
        
        if result and os.path.exists(result):
            print(f"✅ SUCCESS! Audio file created: {result}")
            print(f"File size: {os.path.getsize(result)} bytes")
            return True
        else:
            print("❌ FAILED: No audio file created")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_elevenlabs()
    print(f"\nElevenLabs Test: {'✅ PASSED' if success else '❌ FAILED'}")