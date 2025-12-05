import os
import httpx

class ManusClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("MANUS_BASE_URL", "")
        self.api_key = os.getenv("MANUS_API_KEY", "")

    async def codeact(self, strategy: str, context: dict) -> dict:
        if not self.base_url or not self.api_key:
            return {"direction": context.get("direction", "YES"), "confidence": context.get("confidence", 0.5)}
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/codeact",
                    json={"strategy": strategy, "context": context},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                if res.status_code != 200:
                    return {"direction": context.get("direction", "YES"), "confidence": context.get("confidence", 0.5)}
                return res.json()
        except Exception:
            return {"direction": context.get("direction", "YES"), "confidence": context.get("confidence", 0.5)}