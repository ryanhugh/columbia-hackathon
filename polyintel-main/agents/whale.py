import os
from core.models import AlphaSignal
from integrations.de_search import DeSearchClient
from integrations.polywhaler import PolywhalerClient
from integrations.polymarket_data import PolymarketDataAPI

LEARNED_WHALES: set[str] = set()

def update_learned_whales(addresses: list[str]) -> None:
    for a in addresses:
        if a:
            LEARNED_WHALES.add(a.strip().lower())

def get_learned_whales() -> list[str]:
    return sorted(list(LEARNED_WHALES))
from integrations.aioz import AiozClient
from integrations.manus import ManusClient
from agents.base import Agent

class WhaleAgent(Agent):
    async def generate(self, market_id: str, identity: dict) -> AlphaSignal:
        desearch = DeSearchClient()
        # Prefer Polywhaler if available for real-time whale bias
        poly = PolywhalerClient()
        bias = await poly.whale_bias()
        data_api = PolymarketDataAPI()
        info = await data_api.event_info(market_id)
        whale_addresses = [a.strip().lower() for a in (os.getenv("POLYMARKET_WHALE_WALLETS", "").split(",")) if a.strip()]
        whale_addresses.extend(get_learned_whales())
        cross_direction = ""
        cross_conf = 0.0
        if info.get("event_id"):
            trades = await data_api.trades_by_event(info["event_id"], limit=500)
            buys = 0
            sells = 0
            for t in trades:
                addr = str(t.get("proxyWallet", "")).lower()
                if addr and addr in whale_addresses:
                    side = str(t.get("side", "")).upper()
                    if side == "BUY":
                        buys += 1
                    elif side == "SELL":
                        sells += 1
            total = buys + sells
            if total > 0:
                cross_direction = "YES" if buys > sells else "NO"
                cross_conf = min(0.9, max(0.6, abs(buys - sells) / float(total)))
        if not cross_direction and info.get("condition_ids"):
            holders = await data_api.holders_by_conditions(info["condition_ids"])
            present = 0
            for h in holders:
                for holder in h.get("holders", []) or []:
                    addr = str(holder.get("proxyWallet", "")).lower()
                    if addr and addr in whale_addresses:
                        present += 1
            if present > 0:
                cross_direction = bias.get("direction") or "YES"
                cross_conf = max(float(bias.get("confidence") or 0.6), 0.7)
        whale = await desearch.query_whale_activity(market_id)
        aioz = AiozClient()
        direction = str(cross_direction or bias.get("direction") or whale.get("direction", "YES"))
        confidence = float((cross_conf or bias.get("confidence") or whale.get("confidence", 0.6)))
        manus = ManusClient()
        adjust = await manus.codeact("WHALE", {"direction": direction, "confidence": confidence, "market_id": market_id})
        reasoning = await aioz.generate_reasoning("WHALE", {"whale": whale, "adjust": adjust})
        return AlphaSignal(
            market_id=market_id,
            strategy="WHALE",
            confidence=float(adjust.get("confidence", confidence)),
            direction=str(adjust.get("direction", direction)),
            reasoning=reasoning,
            proof_link=bias.get("proof_link") or whale.get("proof_link", "")
        )