from core.models import AlphaSignal
from integrations.apro_oracle import AproOracleClient
from integrations.aioz import AiozClient
from integrations.gata_protocol import GataClient
from integrations.manus import ManusClient
from agents.base import Agent

class FundamentalAgent(Agent):
    async def generate(self, market_id: str, identity: dict) -> AlphaSignal:
        oracle = AproOracleClient()
        data = await oracle.fetch_market_baseline(market_id)
        gata = GataClient()
        sim = await gata.run_monte_carlo({"market_id": market_id, "baseline": data})
        prob = float(sim.get("prob", 0.5))
        base_direction = "YES" if prob >= 0.5 else "NO"
        base_conf = abs(prob - 0.5) * 2.0
        manus = ManusClient()
        adjust = await manus.codeact("FUNDAMENTAL", {"direction": base_direction, "confidence": base_conf, "market_id": market_id})
        aioz = AiozClient()
        reasoning = await aioz.generate_reasoning("FUNDAMENTAL", {"baseline": data, "sim": sim, "adjust": adjust})
        return AlphaSignal(
            market_id=market_id,
            strategy="FUNDAMENTAL",
            confidence=float(adjust.get("confidence", base_conf)),
            direction=str(adjust.get("direction", base_direction)),
            reasoning=reasoning,
            proof_link=data.get("proof_link", "")
        )