from core.models import AlphaSignal
from integrations.de_search import DeSearchClient
from integrations.aioz import AiozClient
from integrations.manus import ManusClient
from agents.base import Agent

class SentimentAgent(Agent):
    async def generate(self, market_id: str, identity: dict) -> AlphaSignal:
        desearch = DeSearchClient()
        sentiment = await desearch.query_sentiment(market_id)
        aioz = AiozClient()
        score = float(sentiment.get("score", 0.0))
        direction = "YES" if score >= 0 else "NO"
        confidence = min(abs(score), 1.0)
        manus = ManusClient()
        adjust = await manus.codeact("SENTIMENT", {"direction": direction, "confidence": confidence, "market_id": market_id, "score": score})
        reasoning = await aioz.generate_reasoning("SENTIMENT", {"sentiment": sentiment, "adjust": adjust})
        return AlphaSignal(
            market_id=market_id,
            strategy="SENTIMENT",
            confidence=float(adjust.get("confidence", confidence)),
            direction=str(adjust.get("direction", direction)),
            reasoning=reasoning,
            proof_link=sentiment.get("proof_link", "")
        )