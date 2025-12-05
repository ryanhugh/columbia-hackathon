import os
from dotenv import load_dotenv
from pathlib import Path
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time
import asyncio
import json
from fastapi.responses import FileResponse, StreamingResponse
import httpx
from pydantic import BaseModel
from typing import Optional, List, Dict
from spoon.graph import Graph, AgentState
from spoon.mcp_tools import MCPTools
from integrations.sudoapp import SudoClient
from integrations.foreverland import ForeverlandClient
from spoon.vibe_reality_agent import run_vibe_reality
from spoon.audio import generate_briefing
from spoon.mcp_tools import MCPTools
from spoon.podcast_briefing import PodcastBriefingGenerator
from polycaster.tools.sentiment_tool import SentimentAnalyzerTool
from agents.whale import WhaleAgent
from integrations.polywhaler import PolywhalerClient
from integrations.polymarket_data import PolymarketDataAPI
from agents.whale import update_learned_whales, get_learned_whales
try:
    from openai import AsyncOpenAI as _AsyncOpenAI
    OPENAI_OK = True
except Exception:
    OPENAI_OK = False

env_path = Path(os.getcwd()) / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TradeRequest(BaseModel):
    market_slug: str

@app.post("/spoon/trade")
async def spoon_trade(req: TradeRequest):
    tools = MCPTools()

    async def node_odds(state: AgentState) -> AgentState:
        odds = await tools.market_odds(state["market_slug"])
        state["current_odds"] = float(odds)
        return state

    async def node_narrative(state: AgentState) -> AgentState:
        score = await tools.narrative(state["market_slug"])
        state["narrative_score"] = float(score)
        return state

    async def node_fundamental(state: AgentState) -> AgentState:
        truth = await tools.fundamental(state["market_slug"])
        state["fundamental_truth"] = str(truth)
        return state

    async def node_decide(state: AgentState) -> AgentState:
        buy = state["narrative_score"] >= 0 and state["fundamental_truth"] == "YES" and state["current_odds"] <= 0.6
        state["decision"] = "BUY" if buy else "PASS"
        return state

    g = Graph()
    g.add_node("odds", node_odds)
    g.add_node("narrative", node_narrative)
    g.add_node("fundamental", node_fundamental)
    g.add_node("decision", node_decide)
    g.add_edge("odds", "narrative")
    g.add_edge("narrative", "fundamental")
    g.add_edge("fundamental", "decision")

    initial: AgentState = {
        "market_slug": req.market_slug,
        "current_odds": 0.0,
        "narrative_score": 0.0,
        "fundamental_truth": "",
        "decision": "PASS",
    }
    final = await g.run("odds", initial)

    reasoning = await tools.reasoning("SPOON_GRAPH", {
        "market_slug": final["market_slug"],
        "current_odds": final["current_odds"],
        "narrative_score": final["narrative_score"],
        "fundamental_truth": final["fundamental_truth"],
        "decision": final["decision"],
    })

    card = {
        "market_id": final["market_slug"],
        "strategy": "SPOON",
        "confidence": 1.0 if final["decision"] == "BUY" else 0.0,
        "direction": "YES" if final["decision"] == "BUY" else "NO",
        "reasoning": reasoning,
        "proof_link": f"https://polymarket.com/event/{final['market_slug']}",
    }
    uploader = ForeverlandClient()
    upload_res = await uploader.upload_trade_card(card)
    return {"state": final, "card": card, "upload": upload_res}

class PolySignalRequest(BaseModel):
    market_slug: str
    query: Optional[str] = None
    category: Optional[str] = "crypto"
    date_filter: Optional[str] = "PAST_24_HOURS"
    use_manus: Optional[bool] = False

@app.post("/polycaster/signal")
async def polycaster_signal(req: PolySignalRequest, background_tasks: BackgroundTasks):
    final = await run_vibe_reality(req.market_slug, use_manus=req.use_manus or False)
    if req.query:
        tools = MCPTools()
        raw = await tools.desearch_multi(req.query, req.category or "crypto", req.date_filter or "PAST_24_HOURS")
        analyzer = SentimentAnalyzerTool()
        manu_res_str = await analyzer.execute(json.dumps(raw))
        try:
            manu_res = json.loads(manu_res_str)
            score = float(manu_res.get("overall_score", raw.get("sentiment_score", 0.0)))
        except Exception:
            raise HTTPException(status_code=500, detail="Manus sentiment failed")
        final["narrative_score"] = score
        signed = final["reality_odds"] * 2.0 - 1.0
        final["gap"] = score - signed
    briefing = (
        f"Briefing: Market {final['market_slug']} is priced at {final['reality_odds']:.2f}. "
        f"Sentiment score is {final['narrative_score']:.2f}, gap {final['gap']:.2f}. "
        f"Recommendation: {final['decision']} {final['direction']} with confidence {final['confidence']:.2f}."
    )
    audio_file = f"briefing_{final['market_slug']}_{int(time.time())}.mp3"
    background_tasks.add_task(generate_briefing, briefing, audio_file)
    audio_url = f"/polyflow/audio/{audio_file}"
    card = {
        "market_id": final["market_slug"],
        "strategy": "VIBE_REALITY",
        "confidence": final["confidence"],
        "direction": final["direction"],
        "reasoning": final["analysis"],
        "proof_link": f"https://polymarket.com/event/{final['market_slug']}",
    }
    uploader = ForeverlandClient()
    upload_res = await uploader.upload_trade_card(card)
    return {"state": final, "card": card, "upload": upload_res, "audio_file": audio_file, "audio_url": audio_url}

@app.get("/polyflow/audio/{filename}")
async def polyflow_audio(filename: str):
    path = os.path.join(os.getcwd(), filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(path, media_type="audio/mpeg", filename=filename)

 

class SudoChatMessage(BaseModel):
    role: str
    content: str

class SudoChatRequest(BaseModel):
    model: str
    messages: List[SudoChatMessage]
    store: bool = True
    api_key: Optional[str] = None

@app.post("/sudo/chat")
async def sudo_chat(req: SudoChatRequest):
    client = SudoClient()
    data = await client.chat_completions(req.model, [m.model_dump() for m in req.messages], req.store, req.api_key)
    return data

@app.get("/sudo/status")
async def sudo_status():
    return {"has_key": bool(os.getenv("SUDO_API_KEY"))}

@app.get("/sudo/env")
async def sudo_env():
    p = Path(os.getcwd()) / ".env"
    parsed = dotenv_values(str(p)) if p.exists() else {}
    return {"env_path": str(p), "exists": p.exists(), "has_sudo_in_file": bool(parsed.get("SUDO_API_KEY"))}
class PolySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

@app.post("/polycaster/search")
async def polycaster_search(req: PolySearchRequest):
    tools = MCPTools()
    data = await tools.polymarket_search(req.query)
    if req.limit and isinstance(data, dict) and "markets" in data:
        data["returned"] = min(len(data["markets"]), req.limit)
        data["markets"] = data["markets"][:req.limit]
    return data

@app.get("/polymarket/list")
async def polymarket_list(limit: int = 10, category: Optional[str] = None, active_only: bool = True):
    try:
        async with httpx.AsyncClient() as client:
            url = "https://gamma-api.polymarket.com/markets?active=true&limit=100"
            res = await client.get(url, timeout=15.0)
            if res.status_code != 200:
                raise HTTPException(status_code=502, detail="Polymarket markets feed error")
            markets = res.json() if isinstance(res.json(), list) else res.json().get("markets", [])
            out = []
            for m in markets:
                if not isinstance(m, dict):
                    continue
                if active_only and (m.get("closed", False) or not m.get("active", True)):
                    continue
                # Parse outcomePrices robustly (array of strings/numbers or JSON string)
                prices = m.get("outcomePrices")
                if isinstance(prices, str):
                    try:
                        import json as _json
                        prices = _json.loads(prices)
                    except Exception:
                        prices = []
                prices = prices or []
                try:
                    yes = float(prices[0]) if len(prices) > 0 else float(m.get("yesProbability", 0) or m.get("yes_probability", 0) or 0)
                except Exception:
                    yes = 0.0
                try:
                    no = float(prices[1]) if len(prices) > 1 else max(0.0, 1.0 - yes)
                except Exception:
                    no = max(0.0, 1.0 - yes)
                # Filter out degenerate odds and very low volume to avoid zeros in UI
                vol24 = float(m.get("volume24hr") or m.get("volume_24hr") or 0)
                if yes <= 0.0 and vol24 <= 0.0:
                    continue
                cat = (m.get("category") or "").lower()
                if category and category.lower() not in cat:
                    continue
                out.append({
                    "id": m.get("id") or m.get("slug") or m.get("questionID") or "",
                    "question": m.get("question") or m.get("title") or "",
                    "description": m.get("description") or "",
                    "outcomes": m.get("outcomes") or ["YES", "NO"],
                    "outcomePrices": [str(yes), str(no)],
                    "volume": str(m.get("volume") or 0),
                    "volume24hr": str(vol24),
                    "liquidity": str(m.get("liquidity") or 0),
                    "endDate": m.get("endDate") or m.get("end_date") or None,
                    "active": bool(m.get("active", True)),
                    "closed": bool(m.get("closed", False)),
                    "marketType": m.get("marketType") or "binary",
                    "tags": [m.get("category") or ""],
                    "slug": m.get("slug") or "",
                })
            # Prefer non-sports categories to match ticker short-forms
            out = [o for o in out if (o.get("tags") or [""])[0].lower() not in ("sports", "nba", "nfl")]
            if limit and isinstance(out, list):
                out = out[:limit]
            return {"status": "success", "count": len(out), "data": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class SentimentRequest(BaseModel):
    query: str
    category: Optional[str] = "crypto"
    date_filter: Optional[str] = "PAST_24_HOURS"

@app.post("/polycaster/sentiment")
async def polycaster_sentiment(req: SentimentRequest):
    tools = MCPTools()
    raw = await tools.desearch_multi(req.query, req.category or "crypto", req.date_filter or "PAST_24_HOURS")
    analyzer = SentimentAnalyzerTool()
    manu_res = await analyzer.execute(json.dumps(raw))
    try:
        parsed = json.loads(manu_res)
    except Exception:
        raise HTTPException(status_code=500, detail="Manus sentiment failed")
    return {"mode": "manus", "result": parsed, "raw": raw}

class PolyCopInspectRequest(BaseModel):
    slug: str
    category: Optional[str] = "crypto"
    date_filter: Optional[str] = "PAST_24_HOURS"
    sensitivity: Optional[float] = 0.25

@app.post("/polycop/inspect")
async def polycop_inspect(req: PolyCopInspectRequest):
    tools = MCPTools()
    try:
        odds = await tools.market_odds(req.slug)
        raw = await tools.desearch_multi(req.slug, req.category or "crypto", req.date_filter or "PAST_24_HOURS")
        narrative = float(raw.get("sentiment_score", 0.0))
        signed = odds * 2.0 - 1.0
        gap = narrative - signed
        whale = await tools.desearch.query_whale_activity(req.slug)
        fundamental_dir = await tools.fundamental(req.slug)
        kalshi = await tools.kalshi_odds(req.slug)
        search = await tools.polymarket_search(req.slug)
        markets = search.get("markets", []) if isinstance(search, dict) else []
        liquidity = 0.0
        volume24hr = 0.0
        if markets:
            try:
                liquidity = float(markets[0].get("liquidity", 0) or 0)
            except Exception:
                liquidity = 0.0
            try:
                volume24hr = float(markets[0].get("volume24hr", 0) or markets[0].get("volume_24hr", 0) or 0)
            except Exception:
                volume24hr = 0.0
        alerts = []
        if abs(gap) >= float(req.sensitivity or 0.25):
            alerts.append({"type": "narrative_odds_divergence", "value": gap, "severity": min(1.0, abs(gap))})
        market_dir = "YES" if odds >= 0.5 else "NO"
        whale_dir = str(whale.get("direction", ""))
        whale_conf = float(whale.get("confidence", 0.0) or 0.0)
        if whale_dir and whale_dir != market_dir and whale_conf >= 0.6:
            alerts.append({"type": "whale_opposition", "direction": whale_dir, "confidence": whale_conf, "severity": 0.6})
        if fundamental_dir and fundamental_dir != market_dir:
            alerts.append({"type": "fundamental_opposition", "direction": fundamental_dir, "severity": 0.5})
        if liquidity and liquidity < 1000:
            alerts.append({"type": "low_liquidity", "value": liquidity, "severity": 0.4})
        if volume24hr and volume24hr < 100:
            alerts.append({"type": "low_volume_24h", "value": volume24hr, "severity": 0.3})
        rec = "PASS"
        direction = market_dir
        if gap > float(req.sensitivity or 0.25):
            rec = "FADE_MARKET"
            direction = "YES" if narrative > signed else "NO"
        elif gap < -float(req.sensitivity or 0.25):
            rec = "FOLLOW_MARKET"
            direction = market_dir
        return {
            "status": "success",
            "slug": req.slug,
            "metrics": {
                "polymarket_odds": odds,
                "kalshi_odds": kalshi,
                "narrative_score": narrative,
                "signed_odds": signed,
                "gap": gap,
                "liquidity": liquidity,
                "volume24hr": volume24hr
            },
            "signals": {
                "whale": whale,
                "fundamental": fundamental_dir
            },
            "alerts": alerts,
            "recommendation": {"action": rec, "direction": direction}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PolyCopMonitorRequest(BaseModel):
    limit: Optional[int] = 10
    category: Optional[str] = None
    sensitivity: Optional[float] = 0.25
    webhook_url: Optional[str] = None

@app.post("/polycop/monitor")
async def polycop_monitor(req: PolyCopMonitorRequest):
    try:
        trending = await polymarket_trending(limit=req.limit or 10, category=req.category)
        data = trending.get("data", []) if isinstance(trending, dict) else []
        out = []
        for item in data:
            slug = item.get("slug") or ""
            if not slug:
                continue
            res = await polycop_inspect(PolyCopInspectRequest(slug=slug, category=req.category or "crypto", date_filter="PAST_24_HOURS", sensitivity=req.sensitivity or 0.25))
            alerts = res.get("alerts", []) if isinstance(res, dict) else []
            max_sev = 0.0
            if alerts:
                try:
                    max_sev = max(float(a.get("severity", 0.0) or 0.0) for a in alerts)
                except Exception:
                    max_sev = 0.0
            out.append({
                "slug": slug,
                "question": item.get("question") or "",
                "odds": item.get("outcomePrices", ["0.5"])[:1],
                "alerts": alerts,
                "max_severity": max_sev,
                "recommendation": res.get("recommendation")
            })
        out.sort(key=lambda x: float(x.get("max_severity", 0.0) or 0.0), reverse=True)
        result = {"status": "success", "count": len(out), "data": out}
        # Optional webhook delivery
        if req.webhook_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(req.webhook_url, json=result, timeout=5.0)
            except Exception:
                pass
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Streaming alerts (SSE-like via StreamingResponse) ---
@app.get("/polycop/stream")
async def polycop_stream(category: Optional[str] = None, interval_sec: int = 6, sensitivity: float = 0.25):
    async def event_generator():
        while True:
            try:
                res = await polycop_monitor(PolyCopMonitorRequest(limit=10, category=category, sensitivity=sensitivity))
                yield (json.dumps({"type": "snapshot", "ts": int(time.time()), "payload": res}) + "\n")
            except Exception as e:
                yield (json.dumps({"type": "error", "detail": str(e)}) + "\n")
            await asyncio.sleep(max(2, min(30, int(interval_sec))))
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Risk heuristics tools and dashboard ---
async def _compute_risk_tools(slug: str, category: str = "crypto", sensitivity: float = 0.25) -> dict:
    tools = MCPTools()
    odds = await tools.market_odds(slug)
    signed = odds * 2.0 - 1.0
    raw = await tools.desearch_multi(slug, category, "PAST_24_HOURS")
    sentiment = float(raw.get("sentiment_score", 0.0))
    news_count = int(raw.get("metrics", {}).get("news_count", 0) or 0)
    posts_count = int(raw.get("metrics", {}).get("post_count", 0) or 0)
    tweets_count = int(raw.get("metrics", {}).get("tweet_count", 0) or 0)
    gap = sentiment - signed
    trending = await polymarket_trending(limit=20, category=category)
    avg_vol24 = 0.0
    vols = []
    for d in (trending.get("data", []) if isinstance(trending, dict) else []):
        try:
            vols.append(float(d.get("volume24hr") or 0))
        except Exception:
            pass
    if vols:
        avg_vol24 = sum(vols) / float(len(vols))
    # fetch market liquidity/volume via search
    search = await tools.polymarket_search(slug)
    markets = search.get("markets", []) if isinstance(search, dict) else []
    liquidity = float(markets[0].get("liquidity", 0) or 0) if markets else 0.0
    vol24 = float(markets[0].get("volume24hr", markets[0].get("volume_24hr", 0)) or 0) if markets else 0.0
    # Heuristics
    wash_score = 0.0
    if liquidity > 0:
        wash_score = max(0.0, min(1.0, (vol24 / liquidity) * (1.0 - min(1.0, abs(gap)))))
    volume_anomaly_score = 0.0
    if avg_vol24 > 0:
        volume_anomaly_score = max(0.0, min(1.0, vol24 / avg_vol24))
    pump_dump_risk = 0.0
    if sentiment > 0.6 and liquidity < 1000:
        pump_dump_risk = min(1.0, 0.5 + (sentiment - 0.6) + (1000 - liquidity) / 2000.0)
    news_price_discrepancy = 0.0
    if abs(gap) > sensitivity and news_count <= 1:
        news_price_discrepancy = min(1.0, abs(gap))
    # Health score (lower risk → higher health)
    risks = [wash_score, volume_anomaly_score, pump_dump_risk, news_price_discrepancy]
    health = max(0.0, 1.0 - (sum(risks) / max(1, len(risks))))
    return {
        "inputs": {
            "odds": odds,
            "signed_odds": signed,
            "sentiment": sentiment,
            "gap": gap,
            "liquidity": liquidity,
            "volume24hr": vol24,
            "avg_volume24hr": avg_vol24,
            "news_count": news_count,
            "tweets_count": tweets_count,
            "posts_count": posts_count
        },
        "tools": {
            "wash_trading_score": round(wash_score, 3),
            "volume_anomaly_score": round(volume_anomaly_score, 3),
            "pump_dump_risk": round(pump_dump_risk, 3),
            "news_price_discrepancy": round(news_price_discrepancy, 3),
            "health_score": round(health, 3)
        }
    }

@app.get("/dashboard")
async def dashboard(market_id: str, category: Optional[str] = "crypto", sensitivity: float = 0.25):
    try:
        res = await _compute_risk_tools(market_id, category or "crypto", sensitivity)
        inspect = await polycop_inspect(PolyCopInspectRequest(slug=market_id, category=category or "crypto", date_filter="PAST_24_HOURS", sensitivity=sensitivity))
        return {"status": "success", "market_id": market_id, "risk": res, "inspect": inspect}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    query: str
    category: Optional[str] = "crypto"
    sensitivity: Optional[float] = 0.25

@app.post("/chat")
async def chat(req: ChatRequest):
    tools = MCPTools()
    try:
        search = await tools.polymarket_search(req.query)
        markets = search.get("markets", []) if isinstance(search, dict) else []
        if not markets:
            return {"status": "no_markets", "query": req.query}
        slug = markets[0].get("slug") or markets[0].get("id") or req.query
        dashboard_res = await dashboard(slug, req.category or "crypto", float(req.sensitivity or 0.25))
        summary = ""
        if OPENAI_OK and os.getenv("OPENAI_API_KEY"):
            try:
                client = _AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                prompt = json.dumps({
                    "role": "user",
                    "content": (
                        f"Brief trader summary for slug '{slug}'. "
                        f"Key risks: {dashboard_res['risk']['tools']}. "
                        f"Core metrics: {dashboard_res['risk']['inputs']}. "
                        "Give clear, professional positioning guidance."
                    )
                })
                resp = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional market risk analyst. Be concise and actionable."},
                        json.loads(prompt)
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                summary = resp.choices[0].message.content.strip()
            except Exception:
                summary = ""
        return {"status": "success", "slug": slug, "dashboard": dashboard_res, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SynthPodcastRequest(BaseModel):
    slug: str
    query: Optional[str] = None
    category: Optional[str] = "crypto"
    date_filter: Optional[str] = "PAST_24_HOURS"
    variant: Optional[int] = 1
    target_duration_sec: Optional[int] = None

@app.post("/polycaster/podcast/synth")
async def polycaster_podcast_synth(req: SynthPodcastRequest):
    try:
        risk = await polycop_inspect(PolyCopInspectRequest(slug=req.slug, category=req.category or "crypto", date_filter=req.date_filter or "PAST_24_HOURS", sensitivity=0.25))
        analysis = await polycaster_analyze_slug(PolyAnalyzeSlugRequest(slug=req.slug, category=req.category or "crypto", date_filter=req.date_filter or "PAST_24_HOURS"), BackgroundTasks())
        whale_agent = WhaleAgent()
        whale_sig = await whale_agent.generate(req.slug, {})
        r_metrics = risk.get("metrics", {})
        r_tools = await _compute_risk_tools(req.slug, req.category or "crypto", 0.25)
        a_state = analysis.get("state", {}) if isinstance(analysis, dict) else {}
        sentiment_score = float(r_metrics.get("narrative_score", 0.0))
        odds = float(r_metrics.get("polymarket_odds", 0.0))
        gap = float(r_metrics.get("gap", 0.0))
        liquidity = float(r_metrics.get("liquidity", 0.0))
        rec = risk.get("recommendation", {})
        action = rec.get("action", "PASS")
        direction = rec.get("direction", "NO")
        title = req.query or req.slug.replace("-", " ")
        sections = []
        sections.append(f"Briefing on {title}. This briefing synthesizes market analysis, risk signals and whale activity for positioning.")
        sections.append(f"Core metrics: odds {odds:.2f}, sentiment {sentiment_score:.2f}, gap {gap:.2f}, liquidity {liquidity:.2f}.")
        sections.append(f"Risk tools: wash={r_tools['tools']['wash_trading_score']}, volume_anom={r_tools['tools']['volume_anomaly_score']}, pump_dump={r_tools['tools']['pump_dump_risk']}, news_gap={r_tools['tools']['news_price_discrepancy']}, health={r_tools['tools']['health_score']}.")
        a_dec = a_state.get("decision", "PASS")
        a_dir = a_state.get("direction", "NO")
        a_conf = float(a_state.get("confidence", 0.0) or 0.0)
        a_text = str(a_state.get("analysis", "")).strip()
        if a_text:
            sections.append(f"Analysis: {a_text}")
        sections.append(f"PolyCaster decision: {a_dec} {a_dir} (confidence {a_conf:.2f}).")
        sections.append(f"Whale auditor: {whale_sig.direction} (confidence {whale_sig.confidence:.2f}).")
        sections.append(f"PolyCop recommendation: {action} {direction}.")
        sections.append("Summary: Use the recommendation with risk limits; reassess if sentiment or liquidity changes.")
        script = "\n\n".join(sections)
        audio_file = f"podcast_synth_{req.slug}_{int(time.time())}.mp3"
        audio_path = generate_briefing(script, audio_file)
        return {
            "status": "success",
            "slug": req.slug,
            "query": title,
            "audio_file": audio_file,
            "audio_url": f"/polyflow/audio/{audio_file}",
            "briefing": script,
            "risk": risk,
            "analysis": analysis,
            "whale": whale_sig.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/whale/polywhaler/summary")
async def whale_polywhaler_summary():
    client = PolywhalerClient()
    data = await client.fetch_summary()
    return data

@app.get("/whale/crossref")
async def whale_crossref(slug: str):
    data_api = PolymarketDataAPI()
    info = await data_api.event_info(slug)
    whales = [a.strip().lower() for a in (os.getenv("POLYMARKET_WHALE_WALLETS", "").split(",")) if a.strip()]
    trades = []
    buys = 0
    sells = 0
    if info.get("event_id"):
        trades = await data_api.trades_by_event(info["event_id"], limit=500)
        for t in trades:
            addr = str(t.get("proxyWallet", "")).lower()
            if addr and addr in whales:
                side = str(t.get("side", "")).upper()
                if side == "BUY":
                    buys += 1
                elif side == "SELL":
                    sells += 1
    holders = []
    if info.get("condition_ids"):
        holders = await data_api.holders_by_conditions(info["condition_ids"])
    return {
        "event_id": info.get("event_id"),
        "condition_ids": info.get("condition_ids"),
        "whale_addresses": whales,
        "whale_trades": {"count": len(trades), "buys": buys, "sells": sells},
        "holders": holders
    }

class WhaleLearnRequest(BaseModel):
    slug: str
    top_n: Optional[int] = 10

@app.post("/whale/learn")
async def whale_learn(req: WhaleLearnRequest):
    data_api = PolymarketDataAPI()
    info = await data_api.event_info(req.slug)
    holders = []
    if info.get("condition_ids"):
        holders = await data_api.holders_by_conditions(info["condition_ids"])
    addrs: List[str] = []
    for h in holders:
        hs = h.get("holders", []) or []
        hs_sorted = sorted(hs, key=lambda x: float(x.get("amount", 0) or 0), reverse=True)
        for holder in hs_sorted[: int(req.top_n or 10)]:
            addr = str(holder.get("proxyWallet", "")).lower()
            if addr:
                addrs.append(addr)
    uniq = []
    seen = set()
    for a in addrs:
        if a not in seen:
            seen.add(a)
            uniq.append(a)
    update_learned_whales(uniq)
    return {"added": uniq, "total_learned": get_learned_whales()}

class PolyAnalyzeRequest(BaseModel):
    query: str
    category: Optional[str] = "crypto"
    date_filter: Optional[str] = "PAST_24_HOURS"
    limit: Optional[int] = 3

@app.post("/polycaster/analyze")
async def polycaster_analyze(req: PolyAnalyzeRequest, background_tasks: BackgroundTasks):
    tools = MCPTools()
    search = await tools.polymarket_search(req.query)
    markets = search.get("markets", []) if isinstance(search, dict) else []
    if not markets:
        return {"status": "no_markets", "query": req.query}
    picked = markets[0]
    slug = picked.get("slug") or picked.get("id") or req.query
    final = await run_vibe_reality(slug, use_manus=True)
    raw = await tools.desearch_multi(req.query, req.category or "crypto", req.date_filter or "PAST_24_HOURS")
    analyzer = SentimentAnalyzerTool()
    manu_res_str = await analyzer.execute(json.dumps(raw))
    try:
        manu_res = json.loads(manu_res_str)
        score = float(manu_res.get("overall_score", raw.get("sentiment_score", 0.0)))
    except Exception:
        raise HTTPException(status_code=500, detail="Manus sentiment failed")
    final["narrative_score"] = score
    signed = final["reality_odds"] * 2.0 - 1.0
    final["gap"] = score - signed
    briefing = (
        f"Briefing: Market {final['market_slug']} is priced at {final['reality_odds']:.2f}. "
        f"Sentiment score is {final['narrative_score']:.2f}, gap {final['gap']:.2f}. "
        f"Recommendation: {final['decision']} {final['direction']} with confidence {final['confidence']:.2f}."
    )
    audio_file = f"briefing_{final['market_slug']}_{int(time.time())}.mp3"
    background_tasks.add_task(generate_briefing, briefing, audio_file)
    audio_url = f"/polyflow/audio/{audio_file}"
    card = {
        "market_id": final["market_slug"],
        "strategy": "VIBE_REALITY",
        "confidence": final["confidence"],
        "direction": final["direction"],
        "reasoning": final["analysis"],
        "proof_link": f"https://polymarket.com/event/{final['market_slug']}",
    }
    uploader = ForeverlandClient()
    upload_res = await uploader.upload_trade_card(card)
    return {"picked": picked, "state": final, "card": card, "upload": upload_res, "audio_url": audio_url, "sentiment": raw}

class PolyAnalyzeSlugRequest(BaseModel):
    slug: str
    category: Optional[str] = "crypto"
    date_filter: Optional[str] = "PAST_24_HOURS"

@app.post("/polycaster/analyze/slug")
async def polycaster_analyze_slug(req: PolyAnalyzeSlugRequest, background_tasks: BackgroundTasks):
    tools = MCPTools()
    slug = req.slug
    final = await run_vibe_reality(slug, use_manus=True)
    raw = await tools.desearch_multi(slug, req.category or "crypto", req.date_filter or "PAST_24_HOURS")
    analyzer = SentimentAnalyzerTool()
    manu_res_str = await analyzer.execute(json.dumps(raw))
    try:
        manu_res = json.loads(manu_res_str)
        score = float(manu_res.get("overall_score", raw.get("sentiment_score", 0.0)))
    except Exception:
        score = raw.get("sentiment_score", 0.0)
    final["narrative_score"] = score
    signed = final["reality_odds"] * 2.0 - 1.0
    final["gap"] = score - signed
    briefing = (
        f"Briefing: Market {final['market_slug']} is priced at {final['reality_odds']:.2f}. "
        f"Sentiment score is {final['narrative_score']:.2f}, gap {final['gap']:.2f}. "
        f"Recommendation: {final['decision']} {final['direction']} with confidence {final['confidence']:.2f}."
    )
    audio_file = f"briefing_{final['market_slug']}_{int(time.time())}.mp3"
    background_tasks.add_task(generate_briefing, briefing, audio_file)
    audio_url = f"/polyflow/audio/{audio_file}"
    return {"slug": slug, "state": final, "audio_url": audio_url, "sentiment": raw}

@app.get("/polymarket/top")
async def polymarket_top(limit: int = 6, category: Optional[str] = None):
    try:
        async with httpx.AsyncClient() as client:
            url = "https://gamma-api.polymarket.com/markets?active=true&limit=200"
            res = await client.get(url, timeout=15.0)
            if res.status_code != 200:
                raise HTTPException(status_code=502, detail="Polymarket markets feed error")
            markets = res.json() if isinstance(res.json(), list) else res.json().get("markets", [])
            out = []
            for m in markets:
                if not isinstance(m, dict):
                    continue
                if m.get("closed", False) or not m.get("active", True):
                    continue
                prices = m.get("outcomePrices")
                if isinstance(prices, str):
                    try:
                        import json as _json
                        prices = _json.loads(prices)
                    except Exception:
                        prices = []
                prices = prices or []
                yes = 0.0
                try:
                    yes = float(prices[0]) if len(prices) > 0 else float(m.get("yesProbability", 0) or m.get("yes_probability", 0) or 0)
                except Exception:
                    yes = 0.0
                vol24 = float(m.get("volume24hr") or m.get("volume_24hr") or 0)
                cat = (m.get("category") or "").lower()
                if category:
                    ql = (m.get("question") or "").lower()
                    want = category.lower()
                    def match_cat() -> bool:
                        if want == "crypto":
                            return any(k in ql for k in ["btc","bitcoin","eth","ethereum","solana","crypto"]) or "crypto" in cat
                        if want == "politics":
                            return any(k in ql for k in ["election","vote","president","primary","trump","biden"]) or "polit" in cat
                        if want == "culture":
                            return any(k in ql for k in ["grammy","oscars","taylor","swift","celebrity"]) or "culture" in cat
                        if want == "sports":
                            return any(k in ql for k in ["nba","nfl","mlb","soccer","match","game","superbowl"]) or "sport" in cat
                        return True
                    if not match_cat():
                        continue
                # Allow zero odds; frontend will handle display
                out.append({
                    "id": m.get("id") or m.get("slug") or "",
                    "question": m.get("question") or "",
                    "outcomes": m.get("outcomes") or ["YES", "NO"],
                    "outcomePrices": [str(yes), str(max(0.0, 1.0 - yes))],
                    "volume": str(m.get("volume") or 0),
                    "volume24hr": str(vol24),
                    "liquidity": str(m.get("liquidity") or 0),
                    "tags": [m.get("category") or ""],
                    "slug": m.get("slug") or "",
                })
            if limit and isinstance(out, list):
                out = out[:limit]
            return {"status": "success", "count": len(out), "data": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/polymarket/curated")
async def polymarket_curated():
    return {
        "status": "success",
        "data": [
            {"id": "trump-2024", "title": "TRUMP 2024", "category": "politics", "query": "trump 2024 election", "slug": "will-donald-trump-win-the-2024-us-presidential-election"},
            {"id": "biden-approval", "title": "BIDEN APPROVAL", "category": "politics", "query": "biden approval rating", "slug": "will-joe-bidens-approval-rating-rise-this-quarter"},
            {"id": "uk-election", "title": "UK ELECTION", "category": "politics", "query": "uk election odds", "slug": "will-the-conservatives-win-the-next-uk-general-election"},
            {"id": "taylor-grammy", "title": "TAYLOR GRAMMY", "category": "culture", "query": "taylor swift grammy album of the year", "slug": "will-taylor-swift-win-album-of-the-year-at-the-grammys"},
            {"id": "oscars-best-picture", "title": "OSCARS BEST PIC", "category": "culture", "query": "oscars best picture odds", "slug": "will-oppneheimer-win-oscars-best-picture"},
            {"id": "tiktok-ban", "title": "TIKTOK BAN 2025", "category": "politics", "query": "tiktok ban 2025", "slug": "will-tiktok-be-banned-in-the-us-in-2025"},
            {"id": "btc-100k", "title": "BTC $100K", "category": "crypto", "query": "bitcoin price outlook", "slug": "will-bitcoin-reach-100k-by-year-end"},
            {"id": "eth-etf", "title": "ETH ETF", "category": "crypto", "query": "ethereum etf approval odds", "slug": "will-the-sec-approve-an-ethereum-etf"},
            {"id": "sol-200", "title": "SOL $200", "category": "crypto", "query": "solana price outlook", "slug": "will-solana-reach-200-by-year-end"},
            {"id": "fed-rate-cut", "title": "FED RATE CUT MAR", "category": "macro", "query": "fed rate cut march odds", "slug": "will-the-fed-cut-rates-in-march"},
            {"id": "cpi-below-3", "title": "CPI < 3%", "category": "macro", "query": "cpi inflation odds", "slug": "will-us-cpi-fall-below-3-percent-this-year"},
            {"id": "nfl-superbowl", "title": "NFL SUPERBOWL", "category": "sports", "query": "nfl superbowl odds", "slug": "will-the-49ers-win-the-super-bowl"},
            {"id": "nba-finals", "title": "NBA FINALS", "category": "sports", "query": "nba finals odds", "slug": "will-the-celtics-win-the-nba-finals"},
            {"id": "bitcoin-halving", "title": "BTC HALVING PUMP", "category": "crypto", "query": "bitcoin halving pump", "slug": "will-bitcoin-price-rise-10-percent-within-30-days-of-halving"},
            {"id": "ai-regulation", "title": "AI REGULATION", "category": "politics", "query": "ai regulation odds", "slug": "will-a-major-ai-regulation-pass-this-year"},
            {"id": "housing-rebound", "title": "HOUSING REBOUND", "category": "macro", "query": "housing market rebound odds", "slug": "will-us-housing-starts-increase-quarter-over-quarter"},
            {"id": "eth-staking", "title": "ETH STAKING RISE", "category": "crypto", "query": "ethereum staking odds", "slug": "will-ethereum-staking-participation-rise-10-percent"},
            {"id": "openai-ipo", "title": "OPENAI IPO", "category": "culture", "query": "openai ipo odds", "slug": "will-openai-file-for-an-ipo-this-year"},
            {"id": "btc-drawdown", "title": "BTC -20% DRAW", "category": "crypto", "query": "bitcoin drawdown odds", "slug": "will-bitcoin-drop-20-percent-from-its-peak-this-quarter"},
            {"id": "gold-2500", "title": "GOLD $2500", "category": "macro", "query": "gold price outlook", "slug": "will-gold-reach-2500-this-year"}
        ]
    }

@app.get("/polymarket/trending")
async def polymarket_trending(limit: int = 12, category: Optional[str] = None):
    try:
        async with httpx.AsyncClient() as client:
            url = "https://clob.polymarket.com/markets?limit=1000"
            res = await client.get(url, timeout=20.0)
            if res.status_code != 200:
                raise HTTPException(status_code=502, detail="Polymarket CLOB feed error")
            payload = res.json()
            markets = payload.get("data") or payload.get("markets") or payload
            out = []
            for m in markets:
                if not isinstance(m, dict):
                    continue
                q = m.get("question") or m.get("title") or ""
                cat = ",".join(m.get("tags") or [])
                if category:
                    want = category.lower()
                    ql = q.lower()
                    def match_cat() -> bool:
                        if want == "crypto":
                            return any(k in ql for k in ["btc","bitcoin","eth","ethereum","solana","crypto"]) or ("crypto" in cat.lower())
                        if want == "politics":
                            return any(k in ql for k in ["election","vote","president","primary","trump","biden"]) or ("polit" in cat.lower())
                        if want == "culture":
                            return any(k in ql for k in ["grammy","oscars","taylor","swift","celebrity"]) or ("culture" in cat.lower())
                        if want == "sports":
                            return any(k in ql for k in ["nba","nfl","mlb","soccer","match","game","superbowl"]) or ("sport" in cat.lower())
                        return True
                    if not match_cat():
                        continue
                # Compute odds from tokens (Yes outcome) or best bid/ask
                yes = 0.0
                tokens = m.get("tokens") or []
                try:
                    for t in tokens:
                        if (t.get("outcome") or "").lower() == "yes":
                            price = t.get("price")
                            if price is not None:
                                yes = float(price)
                                break
                    if yes == 0.0:
                        bb = m.get("bestBid")
                        if isinstance(bb, (int, float)):
                            yes = float(bb)
                except Exception:
                    yes = 0.0
                vol24 = 0.0
                try:
                    vol24 = float(m.get("volume24hr") or m.get("volume_24hr") or m.get("volumeNum") or m.get("volume") or 0)
                except Exception:
                    vol24 = 0.0
                out.append({
                    "id": m.get("id") or m.get("question_id") or m.get("slug") or m.get("market_slug") or "",
                    "question": q,
                    "outcomes": m.get("outcomes") or ["YES","NO"],
                    "outcomePrices": [str(yes), str(max(0.0, 1.0 - yes))],
                    "volume": str(m.get("volume") or m.get("volumeNum") or 0),
                    "volume24hr": str(vol24),
                    "liquidity": str(m.get("liquidity") or m.get("liquidityNum") or 0),
                    "tags": m.get("tags") or [],
                    "slug": m.get("market_slug") or m.get("slug") or "",
                })
            # Sort by 24h volume desc, then by odds
            out.sort(key=lambda x: (float(x.get("volume24hr") or 0), float(x["outcomePrices"][0])), reverse=True)
            if limit and isinstance(out, list):
                out = out[:limit]
            return {"status": "success", "count": len(out), "data": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/polymarket/examples")
async def polymarket_examples(limit: int = 8, category: Optional[str] = None):
    try:
        # Try trending first
        trending = await polymarket_trending(limit=limit, category=category)
        data = trending.get("data", []) if isinstance(trending, dict) else []
        if data:
            return {"status": "success", "count": len(data), "data": data}
        # Fallback to curated with fixed odds (0.5) to ensure non-empty demo list
        curated = await polymarket_curated()
        labels = curated.get("data", [])
        out = []
        for l in labels[:limit]:
            out.append({
                "id": l.get("id",""),
                "question": l.get("title",""),
                "outcomes": ["YES","NO"],
                "outcomePrices": ["0.5", "0.5"],
                "volume": "0",
                "volume24hr": "0",
                "liquidity": "0",
                "tags": [l.get("category","")],
                "slug": l.get("slug",""),
            })
        return {"status": "success", "count": len(out), "data": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/keys")
async def health_keys():
    return {
        "DESEARCH_API_KEY": bool(os.getenv("DESEARCH_API_KEY")),
        "MANUS_API_KEY": bool(os.getenv("MANUS_API_KEY")),
        "ELEVENLABS_API_KEY": bool(os.getenv("ELEVENLABS_API_KEY")),
    }

@app.get("/health")
async def health():
    return {"ok": True, "service": "Polycaster", "version": "v1"}

@app.get("/health/http")
async def health_http():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://gamma-api.polymarket.com/markets?limit=1", timeout=10.0)
            return {"internet_ok": True, "gamma_status": r.status_code}
    except Exception as e:
        return {"internet_ok": False, "error": str(e)}

@app.get("/health/manus")
async def health_manus():
    try:
        sample = {"key_content": {"tweets": [{"text": "Market panic"}], "posts": [], "news": []}}
        analyzer = SentimentAnalyzerTool()
        res = await analyzer.execute(json.dumps(sample))
        parsed = json.loads(res)
        ok = parsed.get("status") == "success"
        return {"ok": ok, "result": parsed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PodcastRequest(BaseModel):
    query: str
    category: Optional[str] = "crypto"
    duration: Optional[str] = "PAST_24_HOURS"
    variant: Optional[int] = 1
    target_duration_sec: Optional[int] = None

@app.post("/polycaster/podcast")
async def polycaster_podcast(req: PodcastRequest):
    """Generate a comprehensive podcast-style market briefing"""
    generator = PodcastBriefingGenerator()
    
    try:
        result = await generator.generate_podcast_briefing(
            query=req.query,
            category=req.category or "crypto",
            duration=req.duration or "PAST_24_HOURS"
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "query": result["query"],
            "audio_file": result["audio_file"],
            "audio_url": f"/polyflow/audio/{result['audio_file']}",
            "script_preview": result["script"][:500] + "..." if len(result["script"]) > 500 else result["script"],
            "sentiment_score": result["raw_data"].get("sentiment_score", 0),
            "data_sources": result["raw_data"].get("metrics", {}),
            "analysis_summary": result["analysis"][:300] + "..." if len(result["analysis"]) > 300 else result["analysis"],
            "variant": result.get("variant", 1),
            "target_duration_sec": result.get("target_duration_sec", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Podcast generation failed: {str(e)}")

# SPA fallback: serve index.html for non-API routes
API_PREFIXES = ("/polycaster", "/polyflow", "/sudo", "/spoon", "/health", "/trpc")

@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    try:
        if any(full_path.startswith(p.lstrip("/")) for p in API_PREFIXES):
            raise HTTPException(status_code=404, detail="Not Found")
        index_path = (mount_dir / "index.html") if mount_dir.exists() else None
        if index_path and index_path.exists():
            return FileResponse(str(index_path), media_type="text/html")
        raise HTTPException(status_code=404, detail="Index not found")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

class PodcastVariantsRequest(BaseModel):
    query: str
    category: Optional[str] = "crypto"
    duration: Optional[str] = "PAST_24_HOURS"

@app.post("/polycaster/podcast/variants")
async def polycaster_podcast_variants(req: PodcastVariantsRequest):
    generator = PodcastBriefingGenerator()
    try:
        # Version 1: full briefing
        v1 = await generator.generate_podcast_briefing(
            query=req.query,
            category=req.category or "crypto",
            duration=req.duration or "PAST_24_HOURS"
        )

        # Version 2: concise ~60s, alternate intro, remove repetitive lines
        script2 = v1["script"]
        paras = [p for p in script2.split("\n\n") if p.strip()]
        if paras:
            paras[0] = f"Quick briefing for prediction market traders on {req.query}. No fluff — just the signal."
        # Remove hot takes header if present
        paras = [p for p in paras if "catching fire in the timeline" not in p]

        # Fit to ~60 seconds (~2.3 words/sec → ~140 words)
        words = " ".join(paras).split()
        target_words = 140
        if len(words) > target_words:
            trimmed = " ".join(words[:target_words])
        else:
            trimmed = " ".join(words)
        script2_final = trimmed.strip()

        audio2_file = f"podcast_briefing_{req.query.replace(' ', '_')}_short_{int(time.time())}.mp3"
        audio2_path = generate_briefing(script2_final, audio2_file)

        return {
            "status": "success",
            "query": req.query,
            "versions": [
                {
                    "variant": 1,
                    "audio_file": v1["audio_file"],
                    "audio_url": f"/polyflow/audio/{v1['audio_file']}",
                    "script_preview": v1["script"][:400] + "..." if len(v1["script"]) > 400 else v1["script"],
                },
                {
                    "variant": 2,
                    "audio_file": audio2_file,
                    "audio_url": f"/polyflow/audio/{audio2_file}",
                    "script_preview": script2_final,
                    "target_duration_sec": 60
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Podcast variants failed: {str(e)}")

class LabelsRequest(BaseModel):
    questions: List[str]

@app.post("/labels/short")
async def labels_short(req: LabelsRequest):
    labels: List[str] = []
    # Try OpenAI to generate concise short-form labels
    if OPENAI_OK and os.getenv("OPENAI_API_KEY"):
        try:
            client = _AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            prompt = (
                "Create very short ticker-style labels (max 14 chars) for prediction markets. "
                "Use well-known abbreviations (BTC, ETH), event names (TRUMP 2024, TAYLOR GRAMMY, FED RATE), and avoid team acronyms unless famous. "
                "Return a JSON array of labels in order. Questions:\n" + "\n".join(f"- {q}" for q in req.questions)
            )
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You output only valid JSON array of strings."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=200,
            )
            import json as _json
            content = resp.choices[0].message.content.strip()
            labels = _json.loads(content)
        except Exception:
            labels = []
    if not labels:
        # Fallback heuristics
        for q in req.questions:
            qu = (q or "").upper()
            if "BITCOIN" in qu or "BTC" in qu:
                if "100K" in qu or "100,000" in qu:
                    labels.append("BTC $100K")
                else:
                    labels.append("BTC")
                continue
            if "ETH" in qu or "ETHEREUM" in qu:
                labels.append("ETH")
                continue
            if "TRUMP" in qu:
                labels.append("TRUMP 2024" if "2024" in qu else "TRUMP")
                continue
            if "TAYLOR" in qu and "GRAMMY" in qu:
                labels.append("TAYLOR GRAMMY")
                continue
            if "FED" in qu and "RATE" in qu:
                labels.append("FED RATE")
                continue
            if "TIKTOK" in qu and "BAN" in qu:
                labels.append("TIKTOK BAN")
                continue
            labels.append(qu[:14])
    return {"labels": labels}