import os
import httpx

class ForeverlandClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("FOREVERLAND_BASE_URL", "")
        self.api_key = os.getenv("FOREVERLAND_API_KEY", "")

    async def upload_trade_card(self, card: dict) -> dict:
        if not self.base_url or not self.api_key:
            return {"status": "stub", "cid": ""}
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/ipfs/upload",
                    json=card,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                if res.status_code != 200:
                    return {"status": "error"}
                return res.json()
        except Exception:
            return {"status": "error"}