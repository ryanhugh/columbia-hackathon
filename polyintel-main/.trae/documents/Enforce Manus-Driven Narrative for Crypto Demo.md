## Clarification
- Narrative source without Manus: currently from Desearch multi-source results using a heuristic score (twitter, reddit, web, hackernews for crypto).
- Manus role: deep LLM sentiment analysis that converts Desearch content into a numeric score, distribution, and key drivers. If your vision requires richer, reliable narrative, we will make Manus the default and required path.

## Decision
- Make Manus required for sentiment/narrative in the crypto demo.
- Keep Desearch as content collector; Manus transforms that content into the score we use in Vibe vs Reality.

## Keys & Config
- Required: `DESEARCH_API_KEY`, `MANUS_API_KEY`, `ELEVENLABS_API_KEY` (voice optional via `ELEVENLABS_VOICE_ID`).
- Add a diagnostics endpoint to confirm keys loaded from `.env` and test a minimal Manus call.

## Implementation Changes
1. Remove `use_manus` toggle from signal/analyze; always run Manus sentiment.
2. Pipeline:
   - Desearch → Collect tweets/posts/news (twitter, reddit, web, hackernews for crypto)
   - Manus → Analyze combined text and return `{overall_score, distribution, drivers}`
   - Compute `sentiment_probability = (overall_score + 1) / 2`
3. Signal logic (unchanged thresholds):
   - Gap classification: Aligned < 0.15, Moderate 0.15–0.30, Major ≥ 0.30
   - Direction: Long YES if sentiment_probability > market_probability, else Long NO
   - Confidence: `min(0.9, 0.6 + 0.5 * divergence)`
4. Error handling:
   - If Manus fails or key missing, return clear error and do not proceed; optional fallback to heuristic only when explicitly allowed (not in demo).
5. Performance:
   - Keep parallel fetch (Polymarket, Kalshi, Desearch) and caches; Manus analysis runs once per request.
6. Audio:
   - Generate briefing in background, unique filenames per request.

## Verification
- Add `/health/keys` to show which keys are loaded.
- Add `/health/manus` to run a small test prompt and return status.
- Validate `/polycaster/signal` and `/polycaster/analyze` with Manus-only flow.

## Next Steps
- You can provide or rotate `MANUS_API_KEY` in `.env`. I will wire Manus as required and add the diagnostics endpoints, then verify end-to-end responses in `/docs`. 