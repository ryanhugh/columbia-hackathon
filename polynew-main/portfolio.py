"""
PolySignal - Portfolio Management
Allows users to connect their holdings and track personalized correlations
"""

from typing import Dict, List, Optional
from datetime import datetime
import json


class Portfolio:
    """Represents a user's portfolio of holdings"""
    
    def __init__(self, name: str, user_id: str = "default"):
        """
        Initialize portfolio
        
        Args:
            name: Portfolio name
            user_id: User identifier
        """
        self.name = name
        self.user_id = user_id
        self.holdings = {}  # {symbol: weight} e.g., {"BTC": 0.4, "ETH": 0.3, "SPY": 0.3}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_holding(self, symbol: str, weight: float = None, amount: float = None):
        """
        Add a holding to the portfolio
        
        Args:
            symbol: Asset symbol (BTC, ETH, SPY, etc.)
            weight: Weight as fraction (0.0-1.0) - if None, will normalize
            amount: Dollar amount - if provided, will calculate weight
        """
        if amount is not None:
            # Will normalize later
            self.holdings[symbol] = {"amount": amount, "weight": None}
        else:
            self.holdings[symbol] = {"weight": weight or 0.0, "amount": None}
        
        self.updated_at = datetime.now()
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Normalize weights to sum to 1.0"""
        if not self.holdings:
            return
        
        # If we have amounts, calculate total and convert to weights
        total_amount = sum(h.get("amount", 0) for h in self.holdings.values() if h.get("amount"))
        
        if total_amount > 0:
            for symbol, data in self.holdings.items():
                if data.get("amount"):
                    data["weight"] = data["amount"] / total_amount
                    data["amount"] = None  # Clear amount after calculating weight
        
        # Normalize weights to sum to 1.0
        total_weight = sum(h.get("weight", 0) for h in self.holdings.values())
        if total_weight > 0 and total_weight != 1.0:
            for symbol in self.holdings:
                self.holdings[symbol]["weight"] = self.holdings[symbol]["weight"] / total_weight
    
    def get_holdings(self) -> Dict[str, float]:
        """Get holdings as {symbol: weight}"""
        return {symbol: data.get("weight", 0) for symbol, data in self.holdings.items()}
    
    def get_symbols(self) -> List[str]:
        """Get list of asset symbols in portfolio"""
        return list(self.holdings.keys())
    
    def to_dict(self) -> Dict:
        """Convert portfolio to dictionary"""
        return {
            "name": self.name,
            "user_id": self.user_id,
            "holdings": self.holdings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create portfolio from dictionary"""
        portfolio = cls(data["name"], data.get("user_id", "default"))
        portfolio.holdings = data.get("holdings", {})
        portfolio.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        portfolio.updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        return portfolio


class PortfolioManager:
    """Manages multiple portfolios"""
    
    def __init__(self, db=None):
        """
        Initialize portfolio manager
        
        Args:
            db: Database instance (optional, for persistence)
        """
        self.db = db
        self.portfolios = {}  # {portfolio_id: Portfolio}
    
    def create_portfolio(self, name: str, user_id: str = "default") -> str:
        """Create a new portfolio and return its ID"""
        portfolio_id = f"{user_id}_{name}_{datetime.now().timestamp()}"
        portfolio = Portfolio(name, user_id)
        self.portfolios[portfolio_id] = portfolio
        
        if self.db:
            self._save_to_db(portfolio_id, portfolio)
        
        return portfolio_id
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        if portfolio_id in self.portfolios:
            return self.portfolios[portfolio_id]
        
        if self.db:
            return self._load_from_db(portfolio_id)
        
        return None
    
    def add_holdings_from_list(self, portfolio_id: str, holdings: List[Dict]):
        """
        Add holdings from a list
        
        Args:
            portfolio_id: Portfolio ID
            holdings: List of {symbol, weight} or {symbol, amount}
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        for holding in holdings:
            symbol = holding.get("symbol")
            weight = holding.get("weight")
            amount = holding.get("amount")
            portfolio.add_holding(symbol, weight=weight, amount=amount)
        
        if self.db:
            self._save_to_db(portfolio_id, portfolio)
    
    def add_holdings_from_addresses(self, portfolio_id: str, addresses: List[str]):
        """
        Add holdings from on-chain addresses (future: implement blockchain scanning)
        
        Args:
            portfolio_id: Portfolio ID
            addresses: List of wallet addresses
        """
        # TODO: Implement blockchain address scanning
        # For now, return placeholder
        raise NotImplementedError("On-chain address scanning not yet implemented")
    
    def _save_to_db(self, portfolio_id: str, portfolio: Portfolio):
        """Save portfolio to database"""
        if not self.db:
            return
        
        # This would be implemented in database.py
        pass
    
    def _load_from_db(self, portfolio_id: str) -> Optional[Portfolio]:
        """Load portfolio from database"""
        if not self.db:
            return None
        
        # This would be implemented in database.py
        return None
    
    def list_portfolios(self, user_id: str = None) -> List[Dict]:
        """List all portfolios, optionally filtered by user"""
        portfolios = []
        for portfolio_id, portfolio in self.portfolios.items():
            if user_id is None or portfolio.user_id == user_id:
                portfolios.append({
                    "id": portfolio_id,
                    **portfolio.to_dict()
                })
        return portfolios

