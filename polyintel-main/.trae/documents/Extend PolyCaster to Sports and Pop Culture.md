## Scope
- Keep crypto as primary demo category; add support for sports and pop_culture.
- Manus remains required for narrative; Desearch collects content per category.
- Outputs unchanged: direction (YES/NO), confidence, reasoning, Trade Card, audio.

## Category Support
- Categories: crypto (existing), sports, pop_culture.
- Desearch tool selection:
  - crypto: twitter, reddit, web, hackernews
  - sports: twitter, reddit, web (sports subreddits and X trends)
  - pop_culture: twitter, reddit, web (entertainment subreddits and X trends)
- Model: ORBIT; date_filter default PAST_24_HOURS; configurable per request.

## Signal Logic (unchanged)
- sentiment_probability = (overall_score + 1)/2 from Manus.
- reality_probability = Polymarket YES (avg with Kalshi YES when available).
- Gap thresholds:
  - Aligned: < 0.15
  - Moderate: 0.15–0.30
  - Major: ≥ 0.30
- Direction: Long YES if sentiment_probability > market_probability; Long NO otherwise.
- Confidence: min(0.9, 0.6 + 0.5 × divergence).

## API Changes
- Extend existing endpoints to accept `category: "crypto" | "sports" | "pop_culture"`:
  - POST `/polycaster/search` (uses events-first Polymarket discovery)
  - POST `/polycaster/signal` (Manus mandatory; audio optional)
  - POST `/polycaster/sentiment` (Manus mandatory mode)
  - POST `/polycaster/analyze` (orchestrates search → signal)

## Integration Details
- Polymarket: continue events-first search; pick most-liquid market.
- Kalshi: optional augmentation; fallback to Polymarket-only when unavailable.
- Desearch: category-mapped tools; ensure multi-source inputs for sports/pop_culture.
- Manus: analyze Desearch combined text into structured sentiment JSON; required.
- ElevenLabs: background audio generation with unique filenames.

## Performance & Reliability
- Parallelize upstream fetches; TTL caches (120s) for Polymarket/Desearch/Kalshi.
- Tight timeouts and safe fallbacks; deterministic responses even when a source fails.
- Non-blocking audio; stable URL returned immediately.

## Validation
- `/docs` sample requests for sports and pop_culture.
- Verify search relevance and signal quality; confirm Manus processing and audio links.

## Acceptance Criteria
- Sports and pop_culture queries return relevant Polymarket markets with rich metadata.
- Signals computed with Manus-driven sentiment and gap thresholds; confidence scaling applied.
- Optional Kalshi blending used when available; otherwise Polymarket-only.
- Audio briefing generated reliably; endpoints return within target latency.

If approved, I will implement category mapping, remove Manus optionality across endpoints, and verify the new categories end-to-end with examples.