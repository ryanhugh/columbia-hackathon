import os
import httpx
from typing import Dict, Any, List

class PolymarketDataAPI:
    async def event_info(self, slug: str) -> Dict[str, Any]:
        base = os.getenv("POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com")
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{base}/events?slug={slug}", timeout=10.0)
            if r.status_code != 200:
                return {}
            data = r.json()
            ev = data[0] if isinstance(data, list) and data else {}
            event_id = ev.get("id")
            condition_ids: List[str] = []
            for m in ev.get("markets", []) if isinstance(ev.get("markets"), list) else []:
                cid = m.get("conditionId") or m.get("condition_id")
                if cid:
                    condition_ids.append(cid)
            return {"event_id": event_id, "condition_ids": condition_ids}

    async def trades_by_event(self, event_id: int, limit: int = 500) -> List[Dict[str, Any]]:
        url = "https://data-api.polymarket.com/trades"
        params = {"eventId": str(event_id), "limit": str(limit), "takerOnly": "true"}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, timeout=10.0)
            if r.status_code != 200:
                return []
            data = r.json()
            return data if isinstance(data, list) else []

    async def holders_by_conditions(self, condition_ids: List[str]) -> List[Dict[str, Any]]:
        if not condition_ids:
            return []
        url = "https://data-api.polymarket.com/holders"
        params = {"market": ",".join(condition_ids)}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, timeout=10.0)
            if r.status_code != 200:
                return []
            data = r.json()
            return data if isinstance(data, list) else []