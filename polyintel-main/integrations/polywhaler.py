import httpx
import re
from typing import Dict, Any

class PolywhalerClient:
    async def fetch_summary(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get("https://www.polywhaler.com/", timeout=10.0)
                html = res.text if res.status_code == 200 else ""
            def extract(label: str) -> float:
                m = re.search(rf"{label}\$?([0-9,.]+)", html, re.IGNORECASE)
                if not m:
                    m = re.search(rf"{label}\s*([0-9,.]+)", html, re.IGNORECASE)
                try:
                    return float((m.group(1) if m else "0").replace(",", ""))
                except Exception:
                    return 0.0
            total_volume = extract("Total Volume")
            buy_orders = extract("Buy Orders")
            sell_orders = extract("Sell Orders")
            avg_trade = extract("Avg Trade Size")
            return {
                "status": "success",
                "source": "polywhaler",
                "total_volume": total_volume,
                "buy_orders": buy_orders,
                "sell_orders": sell_orders,
                "avg_trade_size": avg_trade
            }
        except Exception:
            return {
                "status": "error",
                "source": "polywhaler",
                "total_volume": 0.0,
                "buy_orders": 0.0,
                "sell_orders": 0.0,
                "avg_trade_size": 0.0
            }

    async def whale_bias(self) -> Dict[str, Any]:
        s = await self.fetch_summary()
        buys = float(s.get("buy_orders", 0) or 0)
        sells = float(s.get("sell_orders", 0) or 0)
        total = buys + sells
        if total <= 0:
            return {"direction": "", "confidence": 0.0, "proof_link": "https://www.polywhaler.com/"}
        bias = (buys - sells) / total
        direction = "YES" if bias > 0 else "NO"
        confidence = min(0.9, max(0.5, abs(bias)))
        return {"direction": direction, "confidence": confidence, "proof_link": "https://www.polywhaler.com/"}