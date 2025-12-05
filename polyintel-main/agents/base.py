from abc import ABC, abstractmethod
from core.models import AlphaSignal

class Agent(ABC):
    @abstractmethod
    async def generate(self, market_id: str, identity: dict) -> AlphaSignal:
        raise NotImplementedError