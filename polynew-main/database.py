"""
PolySignal - Database Module
Stores historical market data and calculated correlations
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import os


class Database:
    """SQLite database for storing market data and correlations"""
    
    def __init__(self, db_path: str = "polysignal.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Historical market data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_id TEXT NOT NULL,
                    market_question TEXT,
                    category TEXT,
                    price REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    volume_24h REAL,
                    UNIQUE(market_id, timestamp)
                )
            """)
            
            # Asset price data table (crypto, stocks, etc.)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_symbol TEXT NOT NULL,
                    asset_name TEXT,
                    price REAL NOT NULL,
                    change_24h REAL,
                    timestamp DATETIME NOT NULL,
                    UNIQUE(asset_symbol, timestamp)
                )
            """)
            
            # Calculated correlations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_category TEXT NOT NULL,
                    asset_symbol TEXT NOT NULL,
                    correlation REAL NOT NULL,
                    p_value REAL,
                    sample_size INTEGER,
                    last_updated DATETIME NOT NULL,
                    confidence_level REAL,
                    UNIQUE(market_category, asset_symbol)
                )
            """)
            
            # Signals history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_id TEXT,
                    market_question TEXT,
                    category TEXT,
                    signal_strength TEXT,
                    polymarket_change REAL,
                    generated_at DATETIME NOT NULL,
                    trade_suggestions TEXT,
                    signal_data TEXT
                )
            """)
            
            # Portfolios table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    holdings TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """)
            
            # Portfolio alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    symbol TEXT,
                    market_id TEXT,
                    message TEXT,
                    impact_data TEXT,
                    created_at DATETIME NOT NULL,
                    read BOOLEAN DEFAULT 0,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_data_market_id ON market_data(market_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_data_symbol ON asset_data(asset_symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_data_timestamp ON asset_data(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_correlations_category ON correlations(market_category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_generated_at ON signals(generated_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_alerts_portfolio_id ON portfolio_alerts(portfolio_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_alerts_created_at ON portfolio_alerts(created_at)")
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_market_data(self, market_id: str, price: float, market_question: str = None,
                        category: str = None, volume_24h: float = None):
        """Save Polymarket price data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO market_data 
                (market_id, market_question, category, price, timestamp, volume_24h)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (market_id, market_question, category, price, datetime.now(), volume_24h))
            conn.commit()
    
    def save_asset_data(self, asset_symbol: str, price: float, asset_name: str = None,
                       change_24h: float = None):
        """Save asset (crypto/stock) price data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO asset_data 
                (asset_symbol, asset_name, price, change_24h, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (asset_symbol, asset_name, price, change_24h, datetime.now()))
            conn.commit()
    
    def get_market_history(self, market_id: str, hours: int = 24) -> List[Dict]:
        """Get historical market data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM market_data
                WHERE market_id = ? AND timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp ASC
            """, (market_id, hours))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_asset_history(self, asset_symbol: str, hours: int = 24) -> List[Dict]:
        """Get historical asset data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM asset_data
                WHERE asset_symbol = ? AND timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp ASC
            """, (asset_symbol, hours))
            return [dict(row) for row in cursor.fetchall()]
    
    def save_correlation(self, market_category: str, asset_symbol: str, correlation: float,
                        p_value: float = None, sample_size: int = None, confidence_level: float = None):
        """Save calculated correlation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO correlations
                (market_category, asset_symbol, correlation, p_value, sample_size, 
                 last_updated, confidence_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (market_category, asset_symbol, correlation, p_value, sample_size,
                  datetime.now(), confidence_level))
            conn.commit()
    
    def get_correlation(self, market_category: str, asset_symbol: str) -> Optional[Dict]:
        """Get stored correlation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM correlations
                WHERE market_category = ? AND asset_symbol = ?
            """, (market_category, asset_symbol))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_correlations(self, market_category: str = None) -> List[Dict]:
        """Get all correlations, optionally filtered by category"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if market_category:
                cursor.execute("""
                    SELECT * FROM correlations
                    WHERE market_category = ?
                    ORDER BY abs(correlation) DESC
                """, (market_category,))
            else:
                cursor.execute("""
                    SELECT * FROM correlations
                    ORDER BY abs(correlation) DESC
                """)
            return [dict(row) for row in cursor.fetchall()]
    
    def save_signal(self, signal_data: Dict):
        """Save generated signal to history"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO signals
                (market_id, market_question, category, signal_strength, polymarket_change,
                 generated_at, trade_suggestions, signal_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal_data.get("market_id"),
                signal_data.get("market_question"),
                signal_data.get("category"),
                signal_data.get("signal_strength"),
                signal_data.get("polymarket_change"),
                datetime.now(),
                json.dumps(signal_data.get("trade_suggestions", [])),
                json.dumps(signal_data)
            ))
            conn.commit()
    
    def get_recent_signals(self, limit: int = 100) -> List[Dict]:
        """Get recent signals"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM signals
                ORDER BY generated_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result["trade_suggestions"] = json.loads(result["trade_suggestions"] or "[]")
                result["signal_data"] = json.loads(result["signal_data"] or "{}")
                results.append(result)
            return results
    
    def get_data_for_correlation(self, market_category: str, asset_symbol: str,
                                 days: int = 30) -> Tuple[List[float], List[float]]:
        """Get paired data for correlation calculation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get market prices for this category
            cursor.execute("""
                SELECT price, timestamp FROM market_data
                WHERE category = ? AND timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp ASC
            """, (market_category, days))
            market_rows = cursor.fetchall()
            
            # Get asset prices
            cursor.execute("""
                SELECT price, timestamp FROM asset_data
                WHERE asset_symbol = ? AND timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp ASC
            """, (asset_symbol, days))
            asset_rows = cursor.fetchall()
            
            # Match timestamps (within 1 hour window)
            market_prices = []
            asset_prices = []
            
            for m_row in market_rows:
                m_time = datetime.fromisoformat(m_row["timestamp"])
                for a_row in asset_rows:
                    a_time = datetime.fromisoformat(a_row["timestamp"])
                    time_diff = abs((m_time - a_time).total_seconds())
                    if time_diff < 3600:  # Within 1 hour
                        market_prices.append(m_row["price"])
                        asset_prices.append(a_row["price"])
                        break
            
            return market_prices, asset_prices
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records
            cursor.execute("SELECT COUNT(*) as count FROM market_data")
            stats["market_data_points"] = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM asset_data")
            stats["asset_data_points"] = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM correlations")
            stats["correlations"] = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM signals")
            stats["signals_generated"] = cursor.fetchone()["count"]
            
            # Date ranges
            cursor.execute("SELECT MIN(timestamp) as min, MAX(timestamp) as max FROM market_data")
            market_range = cursor.fetchone()
            if market_range["min"]:
                stats["market_data_range"] = {
                    "start": market_range["min"],
                    "end": market_range["max"]
                }
            
            return stats
    
    def save_portfolio(self, portfolio_id: str, name: str, user_id: str, holdings: Dict):
        """Save portfolio to database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO portfolios
                (id, name, user_id, holdings, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                portfolio_id,
                name,
                user_id,
                json.dumps(holdings),
                datetime.now(),
                datetime.now()
            ))
            conn.commit()
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """Get portfolio from database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM portfolios WHERE id = ?
            """, (portfolio_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result["holdings"] = json.loads(result["holdings"])
                return result
            return None
    
    def list_portfolios(self, user_id: str = None) -> List[Dict]:
        """List portfolios, optionally filtered by user"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("""
                    SELECT * FROM portfolios WHERE user_id = ? ORDER BY updated_at DESC
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT * FROM portfolios ORDER BY updated_at DESC
                """)
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result["holdings"] = json.loads(result["holdings"])
                results.append(result)
            return results
    
    def save_portfolio_alert(self, portfolio_id: str, alert_type: str, symbol: str = None,
                            market_id: str = None, message: str = None, impact_data: Dict = None):
        """Save portfolio alert"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO portfolio_alerts
                (portfolio_id, alert_type, symbol, market_id, message, impact_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                portfolio_id,
                alert_type,
                symbol,
                market_id,
                message,
                json.dumps(impact_data) if impact_data else None,
                datetime.now()
            ))
            conn.commit()
    
    def get_portfolio_alerts(self, portfolio_id: str, limit: int = 50, unread_only: bool = False) -> List[Dict]:
        """Get alerts for a portfolio"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if unread_only:
                cursor.execute("""
                    SELECT * FROM portfolio_alerts
                    WHERE portfolio_id = ? AND read = 0
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (portfolio_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM portfolio_alerts
                    WHERE portfolio_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (portfolio_id, limit))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                if result.get("impact_data"):
                    result["impact_data"] = json.loads(result["impact_data"])
                results.append(result)
            return results

