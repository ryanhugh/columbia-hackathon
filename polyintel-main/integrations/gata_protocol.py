import os
import httpx

class GataClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("GATA_BASE_URL", "")
        self.api_key = os.getenv("GATA_API_KEY", "")

    async def run_monte_carlo(self, payload: dict) -> dict:
        if not self.base_url or not self.api_key:
            return {"prob": 0.5}
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/montecarlo",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=20.0,
                )
                if res.status_code != 200:
                    return {"prob": 0.5}
                return res.json()
        except Exception:
            return {"prob": 0.5}