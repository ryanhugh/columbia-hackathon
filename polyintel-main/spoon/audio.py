import os
from typing import Optional, Dict
import httpx

def _get_elevenlabs_key() -> str:
    """Get ElevenLabs API key from environment"""
    for k in ["ELEVENLABS_API_KEY", "ELEVEN_LABS_API_KEY", "ELEVEN_API_KEY", "ELEVENLABS_KEY"]:
        v = os.getenv(k, "")
        if v:
            return v
    return ""

def _get_hathora_key() -> str:
    """Get Hathora API key from environment"""
    return os.getenv("HATHORA_API_KEY", "")

def _generate_with_hathora(text: str, filename: str, model: Optional[str] = None, voice: Optional[str] = None) -> Optional[str]:
    """Generate audio using Hathora TTS API"""
    try:
        api_key = _get_hathora_key()
        if not api_key:
            print("⚠ Hathora API key not found")
            return None
        
        # Hathora API endpoints (adjust based on actual API documentation)
        base_url = os.getenv("HATHORA_API_URL", "https://api.hathora.dev")
        endpoint = f"{base_url}/v1/tts"  # Common pattern, may need adjustment
        
        # Try different authentication formats
        # Hathora keys often start with "hathora_org_st_" suggesting they might use different auth
        headers = {
            "Content-Type": "application/json"
        }
        
        # Try Bearer token first
        if api_key.startswith("Bearer ") or "bearer" in api_key.lower():
            headers["Authorization"] = api_key
        elif api_key.startswith("hathora_"):
            # Hathora org key format - try as Bearer or as X-API-Key
            headers["Authorization"] = f"Bearer {api_key}"
            # Also try as API key header
            headers_alt = headers.copy()
            headers_alt["X-API-Key"] = api_key
            headers_alt.pop("Authorization", None)
        else:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Try different possible request formats
        payload = {
            "text": text,
        }
        
        # Add optional parameters if provided
        if model:
            payload["model"] = model
        if voice:
            payload["voice"] = voice
        
        print(f"🎙️ Generating audio with Hathora TTS...")
        
        # Make the API request - try different auth methods
        with httpx.Client(timeout=30.0) as client:
            # Try with Bearer token first
            response = client.post(endpoint, json=payload, headers=headers)
            
            # If that fails and we have a Hathora org key, try with X-API-Key header
            if response.status_code == 401 and api_key.startswith("hathora_"):
                headers_alt = {
                    "Content-Type": "application/json",
                    "X-API-Key": api_key
                }
                response = client.post(endpoint, json=payload, headers=headers_alt)
            
            if response.status_code == 200:
                # Check if response is audio data or a URL
                content_type = response.headers.get("content-type", "")
                
                if "audio" in content_type or response.content.startswith(b'\xff\xfb') or response.content.startswith(b'ID3'):
                    # Direct audio data
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    print(f"✓ Hathora audio generated successfully")
                    return filename
                else:
                    # Might be JSON with audio_url
                    try:
                        data = response.json()
                        audio_url = data.get("audio_url") or data.get("url") or data.get("audioUrl")
                        if audio_url:
                            # Download the audio file
                            audio_response = client.get(audio_url, timeout=30.0)
                            if audio_response.status_code == 200:
                                with open(filename, "wb") as f:
                                    f.write(audio_response.content)
                                print(f"✓ Hathora audio downloaded successfully")
                                return filename
                    except:
                        pass
                    
                    # Try to save raw response as audio
                    if len(response.content) > 100:  # Reasonable audio file size
                        with open(filename, "wb") as f:
                            f.write(response.content)
                        print(f"✓ Hathora audio saved (assuming binary format)")
                        return filename
                        
            else:
                print(f"⚠ Hathora API error: {response.status_code} - {response.text[:200]}")
                # Try alternative endpoint formats
                alternative_endpoints = [
                    f"{base_url}/tts",
                    f"{base_url}/api/tts",
                    f"{base_url}/v1/text-to-speech",
                ]
                
                for alt_endpoint in alternative_endpoints:
                    try:
                        alt_response = client.post(alt_endpoint, json=payload, headers=headers, timeout=30.0)
                        if alt_response.status_code == 200:
                            with open(filename, "wb") as f:
                                f.write(alt_response.content)
                            print(f"✓ Hathora audio generated via alternative endpoint")
                            return filename
                    except Exception as e:
                        continue
                        
        return None
        
    except Exception as e:
        print(f"⚠ Hathora TTS error: {e}")
        import traceback
        traceback.print_exc()
        return None

def _generate_with_elevenlabs(text: str, filename: str, settings: Optional[Dict] = None, output_format: Optional[str] = None, voice_id: Optional[str] = None, model_id: Optional[str] = None) -> Optional[str]:
    """Generate audio using ElevenLabs"""
    try:
        from elevenlabs.client import ElevenLabs
        api_key = _get_elevenlabs_key()
        if not api_key:
            return None
        
        client = ElevenLabs(api_key=api_key)
        voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
        model_id = model_id or os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5")
        stability = float(os.getenv("ELEVENLABS_STABILITY", "0.5"))
        similarity_boost = float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75"))
        style = float(os.getenv("ELEVENLABS_STYLE", "0.0"))
        use_speaker_boost = os.getenv("ELEVENLABS_SPEAKER_BOOST", "true").lower() == "true"
        
        voice_settings = settings or {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        }
        kwargs = {
            "text": text,
            "voice_id": voice_id,
            "model_id": model_id
        }
        fmt = output_format or os.getenv("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")
        if fmt:
            kwargs["output_format"] = fmt
        if voice_settings:
            kwargs["voice_settings"] = voice_settings
        
        audio_stream = client.text_to_speech.convert(**kwargs)
        
        with open(filename, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
        return filename
    except ImportError:
        print("ElevenLabs library not installed")
        return None
    except Exception as e:
        print(f"ElevenLabs error: {e}")
        return None

def _generate_with_gtts(text: str, filename: str) -> Optional[str]:
    """Generate audio using Google Text-to-Speech (free fallback)"""
    try:
        from gtts import gTTS
        import io
        
        # Use gTTS to generate audio
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to file
        tts.save(filename)
        return filename
    except ImportError:
        print("gTTS library not installed. Install with: pip install gtts")
        return None
    except Exception as e:
        print(f"gTTS error: {e}")
        return None

def generate_briefing(text: str, filename: Optional[str] = None, settings: Optional[Dict] = None, output_format: Optional[str] = None, voice_id: Optional[str] = None, model_id: Optional[str] = None) -> Optional[str]:
    """Generate audio briefing with fallback options"""
    path = filename or "polyflow_briefing.mp3"
    
    # Try Hathora first (if API key is available) - primary TTS provider
    if _get_hathora_key():
        print("🎙️ Attempting Hathora TTS...")
        result = _generate_with_hathora(text, path, model=model_id, voice=voice_id)
        if result:
            return result
        print("⚠ Hathora failed, trying fallback...")
    
    # Try ElevenLabs (if API key is available)
    if _get_elevenlabs_key():
        result = _generate_with_elevenlabs(text, path, settings, output_format, voice_id, model_id)
        if result:
            return result
        print("⚠ ElevenLabs failed, trying fallback...")
    
    # Fallback to gTTS (free, no API key needed)
    print("🆓 Using free TTS fallback (gTTS)...")
    result = _generate_with_gtts(text, path)
    if result:
        return result
    
    print("❌ All audio generation methods failed")
    return None