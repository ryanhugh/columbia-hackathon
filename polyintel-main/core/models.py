from pydantic import BaseModel, Field

class AlphaSignal(BaseModel):
    market_id: str = Field(...)
    strategy: str = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    direction: str = Field(...)
    reasoning: str = Field(...)
    proof_link: str = Field(...)