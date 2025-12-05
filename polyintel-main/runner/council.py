import asyncio
from typing import List
from core.models import AlphaSignal
from agents.fundamental import FundamentalAgent
from agents.sentiment import SentimentAgent
from agents.whale import WhaleAgent

async def run_council(market_id: str, identity: dict) -> List[AlphaSignal]:
    f = FundamentalAgent()
    s = SentimentAgent()
    w = WhaleAgent()
    results = await asyncio.gather(
        f.generate(market_id, identity),
        s.generate(market_id, identity),
        w.generate(market_id, identity),
    )
    return list(results)