import os
import httpx

class SoduClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("SODU_BASE_URL", "")
        self.api_key = os.getenv("SODU_API_KEY", "")

    async def get_ephemeral_identity(self) -> dict:
        if not self.base_url or not self.api_key:
            return {"token": "", "id": "ephemeral"}
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/ephemeral",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                if res.status_code != 200:
                    return {"token": "", "id": "ephemeral"}
                return res.json()
        except Exception:
            return {"token": "", "id": "ephemeral"}