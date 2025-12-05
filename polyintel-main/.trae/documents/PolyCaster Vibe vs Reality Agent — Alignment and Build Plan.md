## Scope and Defaults
- Category: crypto (hackathon demo focus)
- Sources: Polymarket Gamma, Desearch (twitter, reddit, web, +hackernews), optional Kalshi, optional Manus AI, ElevenLabs for audio
- Output: direction (YES/NO), confidence, reasoning, Trade Card, optional audio briefing

## Data Integrations
- Polymarket (Reality):
  - Use `events?search=<query>`; select the most liquid market from `markets`
  - Parse `outcomePrices` robustly; avoid 0.5 defaults unless truly unknown
  - Provide `yes_probability`, `no_probability`, `volume`, `liquidity`, `end_date`, `url`
- Kalshi (Optional Reality augmentation):
  - General trade API with resolver for common symbols; auth optional
  - Blend Reality by averaging Polymarket YES with Kalshi YES when available; fallback to Polymarket-only if not
- Desearch (Vibe):
  - Tools: `twitter`, `reddit`, `web` always; add `hackernews` for crypto
  - Model: `ORBIT`; `date_filter` selectable (default `PAST_24_HOURS`)
  - Return summaries, key content, metrics, and numeric `sentiment_score` (heuristic); Manus optional deep analysis

## Signal Logic
- Map `sentiment_score` [-1,1] → `sentiment_probability` [0,1]
- Reality probability = Polymarket YES (avg with Kalshi YES when available)
- Gap classification:
  - Aligned: gap < 0.15
  - Moderate Gap: 0.15 ≤ gap < 0.30
  - Major Divergence: gap ≥ 0.30
- Direction:
  - Long YES if `sentiment_probability > market_probability`
  - Long NO if `sentiment_probability < market_probability`
- Confidence:
  - `confidence = min(0.9, 0.6 + 0.5 * divergence)`

## Endpoints
- POST `/polycaster/search`: discover Polymarket markets with smart filtering and rich metadata
- POST `/polycaster/signal`: compute signal; toggles `use_manus`, `category`, `date_filter`; returns `audio_url`
- POST `/polycaster/sentiment`: sentiment-only analysis (heuristic or Manus)
- POST `/polycaster/analyze`: orchestrate search → signal in one call; return picked market, signal, card, audio, sentiment bundle

## Performance & Reliability
- Parallelize upstream requests with `asyncio.gather`
- TTL caches (60–120s) for Polymarket odds/search, Desearch, and Kalshi
- Tight timeouts (e.g., 5–12s) and safe fallbacks when sources stall
- Background audio generation with unique filenames per request; return stable `audio_url` immediately

## Audio Briefing
- ElevenLabs voice from `.env`; 15–30 second template: Market → Vibe → Reality → Recommendation → Confidence
- Serve via `GET /polyflow/audio/{filename}`

## Error Handling
- Continue with partial data when sources fail; annotate reasoning
- Clear `no_markets` response when discovery returns nothing; avoid irrelevant matches
- Deterministic heuristic sentiment when Manus unavailable or slow

## Validation
- Use `/docs` to run sample payloads for each endpoint
- Verify cache hits and latency; test heuristic vs Manus modes
- Confirm audio link appears immediately and file is generated shortly after

## Acceptance Criteria
- Search returns relevant, liquid crypto markets with correct probabilities and metadata
- Signal endpoint returns direction, confidence, reasoning within target latency
- Manus toggle respected end-to-end; heuristic fast, Manus deeper
- Audio briefing generated and served reliably

If this plan matches your approval, I will implement it end-to-end, verify with live calls, and provide example outputs for the demo.