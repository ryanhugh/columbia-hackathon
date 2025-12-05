"""
PolySignal - Portfolio Alerts
Generates personalized alerts for portfolio holders
"""

from typing import Dict, List
from database import Database
from portfolio import Portfolio
from portfolio_correlations import PortfolioCorrelationTracker
from datetime import datetime


class PortfolioAlertSystem:
    """Manages alerts for portfolio holders"""
    
    def __init__(self, db: Database):
        """
        Initialize alert system
        
        Args:
            db: Database instance
        """
        self.db = db
        self.tracker = PortfolioCorrelationTracker(db)
    
    async def check_and_alert(self, portfolio: Portfolio, recent_signals: List[Dict]):
        """
        Check recent signals and create alerts if they affect portfolio
        
        Args:
            portfolio: Portfolio instance
            recent_signals: Recent signals from monitor
        """
        alerts = self.tracker.get_portfolio_alerts(portfolio, recent_signals)
        
        # Get portfolio ID (would be stored with portfolio)
        portfolio_id = getattr(portfolio, 'portfolio_id', f"portfolio_{portfolio.name}")
        
        for alert in alerts:
            # Save alert to database
            self.db.save_portfolio_alert(
                portfolio_id=portfolio_id,
                alert_type=alert["type"],
                symbol=alert.get("symbol"),
                message=f"{alert['symbol']} ({alert['portfolio_weight']} of portfolio) may be affected by: {alert['market_question']}",
                impact_data={
                    "expected_impact": alert.get("expected_impact"),
                    "confidence": alert.get("confidence"),
                    "signal_strength": alert.get("signal_strength")
                }
            )
        
        return alerts
    
    def get_alerts_summary(self, portfolio_id: str) -> Dict:
        """Get summary of alerts for a portfolio"""
        alerts = self.db.get_portfolio_alerts(portfolio_id, limit=100)
        unread = self.db.get_portfolio_alerts(portfolio_id, limit=100, unread_only=True)
        
        return {
            "total_alerts": len(alerts),
            "unread_alerts": len(unread),
            "recent_alerts": alerts[:10],
            "high_priority": [a for a in alerts if a.get("alert_type") == "portfolio_impact"][:5]
        }
    
    async def generate_daily_summary(self, portfolio: Portfolio) -> Dict:
        """Generate daily summary of portfolio-relevant activity"""
        # Get recent signals (last 24 hours)
        recent_signals = self.db.get_recent_signals(limit=100)
        
        # Filter to last 24 hours
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=24)
        recent = [s for s in recent_signals if datetime.fromisoformat(s["generated_at"]) > cutoff]
        
        # Analyze portfolio impact
        alerts = await self.check_and_alert(portfolio, recent)
        
        # Get upcoming events
        # (Would integrate with event calendar)
        
        return {
            "date": datetime.now().isoformat(),
            "signals_checked": len(recent),
            "portfolio_alerts": len(alerts),
            "top_impacts": alerts[:5] if alerts else []
        }

