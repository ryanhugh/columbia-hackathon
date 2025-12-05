import os
from typing import Optional, Dict
from elevenlabs.client import ElevenLabs

def _get_key() -> str:
    for k in ["ELEVENLABS_API_KEY", "ELEVEN_LABS_API_KEY", "ELEVEN_API_KEY", "ELEVENLABS_KEY"]:
        v = os.getenv(k, "")
        if v:
            return v
    return ""

def generate_briefing(text: str, filename: Optional[str] = None, settings: Optional[Dict] = None, output_format: Optional[str] = None, voice_id: Optional[str] = None, model_id: Optional[str] = None) -> Optional[str]:
    api_key = _get_key()
    if not api_key:
        return None
    client = ElevenLabs(api_key=api_key)
    voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
    model_id = model_id or os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5")
    stability = float(os.getenv("ELEVENLABS_STABILITY", "0.5"))
    similarity_boost = float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75"))
    style = float(os.getenv("ELEVENLABS_STYLE", "0.0"))
    use_speaker_boost = os.getenv("ELEVENLABS_SPEAKER_BOOST", "true").lower() == "true"
    
    try:
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
        
        path = filename or "polyflow_briefing.mp3"
        with open(path, "wb") as f:
            # Write the audio stream to file
            for chunk in audio_stream:
                f.write(chunk)
        return path
    except Exception as e:
        print(f"ElevenLabs error: {e}")
        return None