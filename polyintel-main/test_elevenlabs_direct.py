import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(os.getcwd()) / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)

def test_elevenlabs_direct():
    """Test ElevenLabs API directly to debug the issue"""
    
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    print(f"Testing ElevenLabs API directly...")
    print(f"API Key present: {bool(api_key)}")
    
    try:
        from elevenlabs import ElevenLabs
        
        client = ElevenLabs(api_key=api_key)
        print("✅ ElevenLabs client created successfully")
        
        # Test getting available voices
        print("\nTesting voices endpoint...")
        voices = client.voices.get_all()
        print(f"Available voices: {len(voices.voices)}")
        if voices.voices:
            print(f"First voice: {voices.voices[0].name} (ID: {voices.voices[0].voice_id})")
        
        # Test text-to-speech with a simple request
        test_text = "Hello, this is a test of the ElevenLabs API."
        voice_id = "JBFqnCBsd6RMkjVDRZzb"  # Default voice
        model_id = "eleven_multilingual_v2"
        
        print(f"\nTesting text-to-speech...")
        print(f"Text: {test_text}")
        print(f"Voice ID: {voice_id}")
        print(f"Model ID: {model_id}")
        
        # Try the newer API format
        try:
            audio_data = client.text_to_speech.convert(
                text=test_text,
                voice_id=voice_id,
                model_id=model_id,
                output_format="mp3_44100_128"
            )
            print("✅ Text-to-speech successful!")
            print(f"Audio data type: {type(audio_data)}")
            print(f"Audio data length: {len(audio_data) if hasattr(audio_data, '__len__') else 'Unknown'}")
            
            # Save to file
            output_file = "test_direct.mp3"
            with open(output_file, "wb") as f:
                if isinstance(audio_data, bytes):
                    f.write(audio_data)
                else:
                    # Handle generator or other format
                    if hasattr(audio_data, 'read'):
                        f.write(audio_data.read())
                    else:
                        # Try to iterate if it's a generator
                        for chunk in audio_data:
                            f.write(chunk)
            
            print(f"✅ Audio saved to: {output_file}")
            return True
            
        except Exception as api_error:
            print(f"❌ Text-to-speech API error: {api_error}")
            
            # Try alternative API format
            try:
                print("\nTrying alternative API format...")
                audio_stream = client.generate(
                    text=test_text,
                    voice=voice_id,
                    model=model_id
                )
                
                output_file = "test_alternative.mp3"
                with open(output_file, "wb") as f:
                    if hasattr(audio_stream, 'read'):
                        f.write(audio_stream.read())
                    else:
                        for chunk in audio_stream:
                            f.write(chunk)
                
                print(f"✅ Alternative API successful! Saved to: {output_file}")
                return True
                
            except Exception as alt_error:
                print(f"❌ Alternative API also failed: {alt_error}")
                return False
                
    except ImportError as import_error:
        print(f"❌ Import error: {import_error}")
        print("ElevenLabs library might not be installed or might have changed")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_elevenlabs_direct()
    print(f"\nDirect API Test: {'✅ PASSED' if success else '❌ FAILED'}")