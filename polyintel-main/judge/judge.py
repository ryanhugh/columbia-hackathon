from typing import List
from core.models import AlphaSignal

class JudgeDecision(AlphaSignal):
    pass

class Judge:
    def decide(self, signals: List[AlphaSignal]) -> JudgeDecision:
        yes = [s for s in signals if s.direction == "YES"]
        no = [s for s in signals if s.direction == "NO"]
        yes_conf = sum(s.confidence for s in yes)
        no_conf = sum(s.confidence for s in no)
        if yes_conf >= no_conf:
            chosen = max(yes, key=lambda s: s.confidence) if yes else max(signals, key=lambda s: s.confidence)
        else:
            chosen = max(no, key=lambda s: s.confidence) if no else max(signals, key=lambda s: s.confidence)
        return JudgeDecision(
            market_id=chosen.market_id,
            strategy=chosen.strategy,
            confidence=max(yes_conf, no_conf) / max(len(signals), 1),
            direction=chosen.direction,
            reasoning=chosen.reasoning,
            proof_link=chosen.proof_link
        )