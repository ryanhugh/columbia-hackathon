"""
PolySignal - Event Calendar
Tracks upcoming events relevant to portfolio holdings
"""

from typing import Dict, List
from datetime import datetime, timedelta
from portfolio import Portfolio


class EventCalendar:
    """Manages event calendar for portfolio holdings"""
    
    def __init__(self):
        """Initialize event calendar"""
        # Event templates (would be populated from external APIs in production)
        self.event_templates = {
            "fed_meeting": {
                "name": "Federal Reserve Meeting",
                "frequency": "monthly",
                "impact": "high",
                "affected_assets": ["SPY", "QQQ", "TLT", "BTC", "GLD"]
            },
            "cpi_release": {
                "name": "CPI Data Release",
                "frequency": "monthly",
                "impact": "high",
                "affected_assets": ["SPY", "TLT", "GLD", "BTC"]
            },
            "btc_halving": {
                "name": "Bitcoin Halving",
                "frequency": "every_4_years",
                "impact": "high",
                "affected_assets": ["BTC"]
            },
            "eth_upgrade": {
                "name": "Ethereum Protocol Upgrade",
                "frequency": "quarterly",
                "impact": "medium",
                "affected_assets": ["ETH"]
            },
            "etf_decision": {
                "name": "ETF Approval Decision",
                "frequency": "irregular",
                "impact": "high",
                "affected_assets": ["BTC", "ETH"]
            },
            "earnings": {
                "name": "Earnings Report",
                "frequency": "quarterly",
                "impact": "high",
                "affected_assets": ["NVDA", "META", "AAPL"]
            }
        }
    
    def get_upcoming_events(self, portfolio: Portfolio, days_ahead: int = 30) -> List[Dict]:
        """
        Get upcoming events relevant to portfolio
        
        Args:
            portfolio: Portfolio instance
            days_ahead: How many days ahead to look
        
        Returns:
            List of upcoming events
        """
        symbols = portfolio.get_symbols()
        events = []
        
        # Generate events for next N days
        today = datetime.now()
        for i in range(days_ahead):
            date = today + timedelta(days=i)
            
            # Fed meetings (first Wednesday of month)
            if date.weekday() == 2 and date.day <= 7:  # Wednesday, first week
                if any(s in ["SPY", "QQQ", "TLT", "BTC"] for s in symbols):
                    events.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "type": "fed_meeting",
                        "name": "Federal Reserve Meeting",
                        "impact": "high",
                        "relevant_markets": self._get_relevant_markets("fed_rates", symbols),
                        "affected_holdings": [s for s in symbols if s in ["SPY", "QQQ", "TLT", "BTC"]]
                    })
            
            # CPI release (second Tuesday of month)
            if date.weekday() == 1 and 8 <= date.day <= 14:
                if any(s in ["SPY", "TLT", "GLD", "BTC"] for s in symbols):
                    events.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "type": "cpi_release",
                        "name": "CPI Data Release",
                        "impact": "high",
                        "relevant_markets": self._get_relevant_markets("inflation", symbols),
                        "affected_holdings": [s for s in symbols if s in ["SPY", "TLT", "GLD", "BTC"]]
                    })
            
            # Example: Bitcoin halving (simplified - would use actual date)
            if "BTC" in symbols and date.month == 4 and date.day == 20:
                events.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "btc_halving",
                    "name": "Bitcoin Halving",
                    "impact": "high",
                    "relevant_markets": self._get_relevant_markets("crypto", symbols),
                    "affected_holdings": ["BTC"]
                })
            
            # Example: NVDA earnings (quarterly, simplified)
            if "NVDA" in symbols and date.month in [2, 5, 8, 11] and date.day == 15:
                events.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "earnings",
                    "name": "NVIDIA Earnings Report",
                    "impact": "high",
                    "relevant_markets": self._get_relevant_markets("earnings", symbols),
                    "affected_holdings": ["NVDA"]
                })
        
        return sorted(events, key=lambda x: x["date"])
    
    def _get_relevant_markets(self, category: str, symbols: List[str]) -> List[str]:
        """Get relevant prediction markets for event category"""
        # This would query actual markets
        # For now, return placeholder
        markets = {
            "fed_rates": [
                "Will the Fed cut rates in March?",
                "Will the Fed raise rates in Q2?"
            ],
            "inflation": [
                "Will inflation exceed 3%?",
                "Will CPI come in above expectations?"
            ],
            "crypto": [
                "Will Bitcoin hit $100k?",
                "Will BTC halving boost price?"
            ],
            "earnings": [
                "Will NVDA beat earnings?",
                "Will NVDA guidance be positive?"
            ]
        }
        return markets.get(category, [])
    
    def get_events_by_date(self, portfolio: Portfolio, start_date: datetime = None,
                          end_date: datetime = None) -> Dict[str, List[Dict]]:
        """
        Get events grouped by date
        
        Args:
            portfolio: Portfolio instance
            start_date: Start date (default: today)
            end_date: End date (default: 30 days ahead)
        
        Returns:
            Dict mapping date strings to events
        """
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        events = self.get_upcoming_events(
            portfolio,
            days_ahead=(end_date - start_date).days
        )
        
        # Filter by date range
        filtered = [
            e for e in events
            if start_date <= datetime.fromisoformat(e["date"]) <= end_date
        ]
        
        # Group by date
        grouped = {}
        for event in filtered:
            date = event["date"]
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(event)
        
        return grouped

