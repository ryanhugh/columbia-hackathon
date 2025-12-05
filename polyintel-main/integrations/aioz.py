import os
import httpx

class AiozClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("AIOZ_BASE_URL", "")
        self.api_key = os.getenv("AIOZ_API_KEY", "")

    async def generate_reasoning(self, strategy: str, context: dict) -> str:
        if not self.base_url or not self.api_key:
            return ""
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={"model": os.getenv("AIOZ_MODEL", ""), "messages": [{"role": "system", "content": strategy}, {"role": "user", "content": str(context)}]},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=20.0,
                )
                if res.status_code != 200:
                    return ""
                data = res.json()
                c = data.get("choices", [])
                if not c:
                    return ""
                m = c[0].get("message", {})
                return m.get("content", "")
        except Exception:
            return ""