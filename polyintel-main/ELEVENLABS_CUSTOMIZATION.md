# ElevenLabs Customization Guide

## Quick Start
Add these to your `.env` file:

```bash
# Voice Settings
ELEVENLABS_VOICE_ID="JBFqnCBsd6RMkjVDRZzb"  # Default voice
ELEVENLABS_MODEL_ID="eleven_multilingual_v2"  # For multiple languages

# Advanced Voice Settings
ELEVENLABS_STABILITY="0.5"          # 0.0 to 1.0 (lower = more emotional variation)
ELEVENLABS_SIMILARITY_BOOST="0.75" # 0.0 to 1.0 (higher = closer to original voice)
ELEVENLABS_STYLE="0.0"             # 0.0 to 1.0 (higher = more style exaggeration)
ELEVENLABS_SPEAKER_BOOST="true"    # true/false (enhances speaker clarity)
```

## Voice Options

### Pre-made Voices (no API key needed)
- `JBFqnCBsd6RMkjVDRZzb` - Default male voice
- `21m00Tcm4TlvDq8ikWAM` - Female voice
- `AZnzlk1XvdvUeBnXmlld` - Another male voice

### Your Custom Voices
1. Go to https://beta.elevenlabs.io/voice-library
2. Create or clone a voice
3. Copy the Voice ID from your voice settings
4. Add to `.env`: `ELEVENLABS_VOICE_ID="your_voice_id"`

## Model Options

```bash
# For English only (faster, better quality)
ELEVENLABS_MODEL_ID="eleven_monolingual_v1"

# For multiple languages
ELEVENLABS_MODEL_ID="eleven_multilingual_v1"
ELEVENLABS_MODEL_ID="eleven_multilingual_v2"  # Latest
```

## Voice Settings Explained

### Stability (0.0 to 1.0)
- **0.0-0.3**: More emotional variation, less stable
- **0.4-0.6**: Balanced (recommended for trading briefings)
- **0.7-1.0**: Very stable, consistent tone

### Similarity Boost (0.0 to 1.0)
- **0.0-0.5**: Less similar to original voice
- **0.6-0.8**: Good balance (recommended)
- **0.9-1.0**: Very close to original voice

### Style (0.0 to 1.0)
- **0.0**: Natural reading
- **0.3-0.5**: Slight style enhancement
- **0.6-1.0**: Strong style exaggeration

## Testing Your Settings

```bash
# Test with custom settings
curl -X POST "http://localhost:8000/polycaster/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "Bitcoin price analysis"}'

# Listen to the generated audio
afplay briefing_*.mp3
```

## Troubleshooting

### Audio not playing?
- Check file size: `ls -la *.mp3` (should be > 10KB)
- Test direct generation: `python -c "from spoon.audio import generate_briefing; generate_briefing('Test')"`

### Voice not found?
- Verify your Voice ID in ElevenLabs dashboard
- Try a pre-made voice first

### Want different languages?
- Use `eleven_multilingual_v2` model
- Set stability to 0.5-0.7 for better pronunciation