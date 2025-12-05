import os
import httpx
from typing import List, Dict, Optional

class SudoClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("SUDO_BASE_URL", "https://sudoapp.dev")
        self.api_key = os.getenv("SUDO_API_KEY", "")

    async def chat_completions(self, model: str, messages: List[Dict], store: bool = True, api_key: Optional[str] = None) -> Dict:
        key = api_key or self.api_key
        if not key:
            return {"error": "missing_api_key"}
        url = f"{self.base_url}/api/v1/chat/completions"
        payload = {"model": model, "messages": messages, "store": store}
        headers = {"Authorization": f"Bearer {key}"}
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers, timeout=20.0)
                if res.status_code != 200:
                    return {"error": "request_failed", "status": res.status_code, "body": res.text}
                return res.json()
        except Exception as e:
            return {"error": "exception", "message": str(e)}