from typing import Dict
import asyncio
from spoon.graph import Graph
from spoon.mcp_tools import MCPTools
from integrations.manus import ManusClient
from integrations.aioz import AiozClient

async def run_vibe_reality(market_slug: str, use_manus: bool = False) -> Dict:
    tools = MCPTools()
    state: Dict = {
        "market_slug": market_slug,
        "polymarket_odds": 0.0,
        "kalshi_odds": None,
        "reality_odds": 0.0,
        "narrative_score": 0.0,
        "gap": 0.0,
        "decision": "PASS",
        "direction": "NO",
        "confidence": 0.0,
        "analysis": "",
    }

    async def node_fetch_core(s: Dict) -> Dict:
        pm_task = tools.market_odds(s["market_slug"])
        ka_task = tools.kalshi_odds(s["market_slug"])
        nar_task = tools.narrative(s["market_slug"])
        pm, ka, nar = await asyncio.gather(pm_task, ka_task, nar_task)
        s["polymarket_odds"] = float(pm)
        s["kalshi_odds"] = ka if ka is not None else None
        s["reality_odds"] = float(pm) if ka is None else float((float(pm) + float(ka)) / 2.0)
        s["narrative_score"] = float(nar)
        return s

    async def node_gap(s: Dict) -> Dict:
        reality01 = float(s["reality_odds"])  # [0,1]
        reality_signed = reality01 * 2.0 - 1.0
        s["gap"] = float(s["narrative_score"] - reality_signed)
        sp = (float(s["narrative_score"]) + 1.0) / 2.0
        s["divergence"] = abs(sp - reality01)
        return s

    async def node_decide(s: Dict) -> Dict:
        odds = float(s["reality_odds"])  # [0,1]
        sp = (float(s["narrative_score"]) + 1.0) / 2.0
        div = float(s.get("divergence", abs(sp - odds)))
        aligned = div < 0.15
        moderate = 0.15 <= div < 0.30
        major = div >= 0.30
        if aligned:
            s["decision"] = "PASS"
            s["direction"] = "NO"
        else:
            s["decision"] = "BUY"
            s["direction"] = "YES" if sp > odds else "NO"
        s["confidence"] = float(min(0.9, 0.6 + 0.5 * div))
        if use_manus:
            manus = ManusClient()
            adjust = await manus.codeact("VIBE_REALITY", {"gap": s["gap"], "odds": odds, "narrative": s["narrative_score"], "direction": s["direction"], "confidence": s["confidence"], "market_slug": s["market_slug"]})
            s["direction"] = str(adjust.get("direction", s["direction"]))
            s["confidence"] = float(adjust.get("confidence", s["confidence"]))
        return s

    g = Graph()
    g.add_node("core", node_fetch_core)
    g.add_node("gap", node_gap)
    g.add_node("decision", node_decide)
    g.add_edge("core", "gap")
    g.add_edge("gap", "decision")
    final = await g.run("core", state)

    aioz = AiozClient()
    reasoning = await aioz.generate_reasoning("VIBE_REALITY", {"market_slug": final["market_slug"], "polymarket_odds": final["polymarket_odds"], "kalshi_odds": final["kalshi_odds"], "reality_odds": final["reality_odds"], "narrative_score": final["narrative_score"], "gap": final["gap"], "decision": final["decision"], "direction": final["direction"], "confidence": final["confidence"]})
    if not reasoning:
        reasoning = f"gap={final['gap']} reality_odds={final['reality_odds']} narrative={final['narrative_score']} decision={final['decision']}"
    final["analysis"] = reasoning
    return final