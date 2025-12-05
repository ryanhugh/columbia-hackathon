# Test different ElevenLabs features for more dynamic audio
import os
from elevenlabs.client import ElevenLabs

def test_elevenlabs_features():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("No API key found")
        return
    
    client = ElevenLabs(api_key=api_key)
    
    # Test different voice settings
    text = "Welcome to the Crypto Sentiment Show! Here's what's moving prediction markets today."
    
    print("Testing different voice settings...")
    
    # Test 1: Different stability levels
    for stability in [0.2, 0.5, 0.8]:
        print(f"Testing stability: {stability}")
        audio = client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            voice_settings={
                "stability": stability,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True
            }
        )
        filename = f"test_stability_{stability}.mp3"
        with open(filename, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        print(f"Created: {filename}")
    
    # Test 2: Different models
    models = ["eleven_monolingual_v1", "eleven_multilingual_v1", "eleven_multilingual_v2"]
    for model in models:
        print(f"Testing model: {model}")
        try:
            audio = client.text_to_speech.convert(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id=model,
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            )
            filename = f"test_model_{model.replace('_', '-')}.mp3"
            with open(filename, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            print(f"Created: {filename}")
        except Exception as e:
            print(f"Model {model} failed: {e}")
    
    # Test 3: Different voices
    voices = [
        "JBFqnCBsd6RMkjVDRZzb",  # Default
        "21m00Tcm4TlvDq8ikWAM",  # Female
        "AZnzlk1XvdvUeBnXmlld"   # Alternative male
    ]
    
    for voice_id in voices:
        print(f"Testing voice: {voice_id}")
        try:
            audio = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            )
            filename = f"test_voice_{voice_id[:8]}.mp3"
            with open(filename, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            print(f"Created: {filename}")
        except Exception as e:
            print(f"Voice {voice_id} failed: {e}")

if __name__ == "__main__":
    test_elevenlabs_features()