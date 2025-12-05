import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(os.getcwd()) / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)

def test_elevenlabs_api_versions():
    """Test different ElevenLabs API versions and methods"""
    
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    print(f"Testing different ElevenLabs API methods...")
    print(f"API Key present: {bool(api_key)}")
    
    try:
        from elevenlabs import ElevenLabs
        
        client = ElevenLabs(api_key=api_key)
        print("✅ ElevenLabs client created successfully")
        
        # Check available methods
        print(f"\nClient attributes: {[attr for attr in dir(client) if not attr.startswith('_')]}")
        
        # Check text_to_speech methods
        if hasattr(client, 'text_to_speech'):
            print(f"Text-to-speech attributes: {[attr for attr in dir(client.text_to_speech) if not attr.startswith('_')]}")
        
        # Test different API approaches
        test_text = "Hello, this is a test of the ElevenLabs API for crypto trading briefings."
        voice_id = "JBFqnCBsd6RMkjVDRZzb"
        
        # Approach 1: Direct text_to_speech.convert
        if hasattr(client.text_to_speech, 'convert'):
            try:
                print("\n--- Testing text_to_speech.convert ---")
                audio_data = client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=test_text,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
                print(f"✅ text_to_speech.convert successful!")
                print(f"Audio data type: {type(audio_data)}")
                
                # Save audio
                output_file = "test_convert.mp3"
                if isinstance(audio_data, bytes):
                    with open(output_file, "wb") as f:
                        f.write(audio_data)
                else:
                    # Handle generator
                    with open(output_file, "wb") as f:
                        for chunk in audio_data:
                            f.write(chunk)
                print(f"✅ Audio saved to: {output_file}")
                return True
                
            except Exception as e1:
                print(f"❌ text_to_speech.convert failed: {e1}")
        
        # Approach 2: Using generate method if available
        if hasattr(client, 'generate'):
            try:
                print("\n--- Testing client.generate ---")
                audio_stream = client.generate(
                    text=test_text,
                    voice=voice_id,
                    model="eleven_multilingual_v2"
                )
                print(f"✅ client.generate successful!")
                
                output_file = "test_generate.mp3"
                with open(output_file, "wb") as f:
                    for chunk in audio_stream:
                        f.write(chunk)
                print(f"✅ Audio saved to: {output_file}")
                return True
                
            except Exception as e2:
                print(f"❌ client.generate failed: {e2}")
        
        # Approach 3: Try the old API format
        try:
            print("\n--- Testing legacy API format ---")
            from elevenlabs import generate, save
            
            audio = generate(
                text=test_text,
                voice=voice_id,
                model="eleven_multilingual_v2",
                api_key=api_key
            )
            
            output_file = "test_legacy.mp3"
            save(audio, output_file)
            print(f"✅ Legacy API successful! Saved to: {output_file}")
            return True
            
        except Exception as e3:
            print(f"❌ Legacy API failed: {e3}")
            
    except ImportError as import_error:
        print(f"❌ Import error: {import_error}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return False

if __name__ == "__main__":
    success = test_elevenlabs_api_versions()
    print(f"\nAPI Test: {'✅ PASSED' if success else '❌ FAILED'}")