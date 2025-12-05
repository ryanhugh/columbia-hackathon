#!/usr/bin/env bash

BASE="http://localhost:8000"

echo "--- health ---"
curl -s "$BASE/health" ; echo

echo "--- keys ---"
curl -s "$BASE/health/keys" ; echo

echo "--- sentiment ---"
curl -s -X POST "$BASE/polycaster/sentiment" -H 'Content-Type: application/json' -d '{"query":"ethereum price november 2025","category":"crypto","date_filter":"PAST_24_HOURS"}' | head -n 1 ; echo

echo "--- analyze/slug ---"
curl -s -X POST "$BASE/polycaster/analyze/slug" -H 'Content-Type: application/json' -d '{"slug":"what-price-will-ethereum-hit-in-november-2025","category":"crypto","date_filter":"PAST_24_HOURS"}' | head -n 1 ; echo

echo "--- polycop inspect ---"
curl -s -X POST "$BASE/polycop/inspect" -H 'Content-Type: application/json' -d '{"slug":"what-price-will-ethereum-hit-in-november-2025","category":"crypto","date_filter":"PAST_24_HOURS","sensitivity":0.25}' | head -n 1 ; echo

echo "--- polycop monitor ---"
curl -s -X POST "$BASE/polycop/monitor" -H 'Content-Type: application/json' -d '{"limit":5,"category":"crypto","sensitivity":0.25}' | head -n 1 ; echo

echo "--- podcast (long) ---"
curl -s -X POST "$BASE/polycaster/podcast" -H 'Content-Type: application/json' -d '{"query":"submission demo long","category":"crypto","duration":"PAST_24_HOURS"}' | head -n 1 ; echo

echo "--- podcast (variants) ---"
curl -s -X POST "$BASE/polycaster/podcast/variants" -H 'Content-Type: application/json' -d '{"query":"submission demo variants","category":"crypto","duration":"PAST_24_HOURS"}' | head -n 1 ; echo

echo "--- whale summary ---"
curl -s "$BASE/whale/polywhaler/summary" | head -n 1 ; echo

echo "--- whale crossref ---"
curl -s "$BASE/whale/crossref?slug=what-price-will-ethereum-hit-in-november-2025" | head -n 1 ; echo

echo "--- trending (crypto) ---"
curl -s "$BASE/polymarket/trending?limit=5&category=crypto" | head -n 1 ; echo

echo "--- dashboard ---"
curl -s "$BASE/dashboard?market_id=what-price-will-ethereum-hit-in-november-2025&category=crypto&sensitivity=0.25" | head -n 1 ; echo

echo "--- chat ---"
curl -s -X POST "$BASE/chat" -H 'Content-Type: application/json' -d '{"query":"ethereum price november 2025","category":"crypto","sensitivity":0.25}' | head -n 1 ; echo

echo "--- audio status check ---"
LONG_URL=$(curl -s -X POST "$BASE/polycaster/podcast" -H 'Content-Type: application/json' -d '{"query":"audio status check","category":"crypto","duration":"PAST_24_HOURS"}' | sed -n 's/.*"audio_url":"\([^"]*\)".*/\1/p')
SHORT_URL=$(curl -s -X POST "$BASE/polycaster/podcast/variants" -H 'Content-Type: application/json' -d '{"query":"audio status check variants","category":"crypto","duration":"PAST_24_HOURS"}' | sed -n 's/.*"audio_url":"\([^"]*\)".*/\1/p')
[ -n "$LONG_URL" ] && echo "long: $LONG_URL -> $(curl -s -o /dev/null -w '%{http_code}' "$BASE$LONG_URL")" || echo "long: unavailable"
[ -n "$SHORT_URL" ] && echo "short: $SHORT_URL -> $(curl -s -o /dev/null -w '%{http_code}' "$BASE$SHORT_URL")" || echo "short: unavailable"