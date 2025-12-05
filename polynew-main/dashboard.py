"""
PolySignal - Web Dashboard
Shows signals, statistics, and correlations in a web interface
Uses mock data initially, switches to real data when available
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import json
import os
from database import Database
from portfolio import Portfolio, PortfolioManager
from portfolio_correlations import PortfolioCorrelationTracker
from edgescore import EdgeScoreCalculator
from semantic_matcher import SemanticMatcher
import asyncio

app = Flask(__name__)
db = Database()
portfolio_manager = PortfolioManager(db)

# Mock data (will be replaced with real data from database)
MOCK_DATA = {
    "signals": [
        {
            "id": 1,
            "market_question": "Will the Fed cut rates by 0.5% in Q1 2024?",
            "category": "fed_rates",
            "polymarket_change": "+12.3%",
            "signal_strength": "STRONG",
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "trade_suggestions": [
                {"asset": "SPY", "direction": "BUY", "expected_move": "+1.8%", "confidence": "85%", "data_source": "📊 Real Data"},
                {"asset": "BTC", "direction": "BUY", "expected_move": "+1.5%", "confidence": "70%", "data_source": "📊 Real Data"},
                {"asset": "TLT", "direction": "BUY", "expected_move": "+1.2%", "confidence": "65%", "data_source": "📈 Estimated"}
            ],
            "using_real_data": True
        },
        {
            "id": 2,
            "market_question": "Will Trump win the 2024 election?",
            "category": "politics_republican",
            "polymarket_change": "+8.5%",
            "signal_strength": "MEDIUM",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "trade_suggestions": [
                {"asset": "BTC", "direction": "BUY", "expected_move": "+1.2%", "confidence": "60%", "data_source": "📈 Estimated"},
                {"asset": "ETH", "direction": "BUY", "expected_move": "+1.0%", "confidence": "55%", "data_source": "📈 Estimated"}
            ],
            "using_real_data": False
        },
        {
            "id": 3,
            "market_question": "Will inflation exceed 3% in 2024?",
            "category": "inflation",
            "polymarket_change": "-6.2%",
            "signal_strength": "MEDIUM",
            "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
            "trade_suggestions": [
                {"asset": "GLD", "direction": "SELL/SHORT", "expected_move": "-0.8%", "confidence": "70%", "data_source": "📈 Estimated"},
                {"asset": "TLT", "direction": "BUY", "expected_move": "+0.6%", "confidence": "65%", "data_source": "📈 Estimated"}
            ],
            "using_real_data": False
        }
    ],
    "stats": {
        "market_data_points": 1240,
        "asset_data_points": 6200,
        "correlations": 47,
        "signals_generated": 18,
        "real_correlations": 23,
        "estimated_correlations": 24
    },
    "correlations": [
        {"category": "fed_rates", "asset": "SPY", "correlation": 0.731, "p_value": 0.002, "sample_size": 145, "is_significant": True},
        {"category": "fed_rates", "asset": "QQQ", "correlation": 0.689, "p_value": 0.004, "sample_size": 145, "is_significant": True},
        {"category": "fed_rates", "asset": "BTC", "correlation": 0.612, "p_value": 0.009, "sample_size": 145, "is_significant": True},
        {"category": "politics_republican", "asset": "BTC", "correlation": 0.584, "p_value": 0.012, "sample_size": 89, "is_significant": True},
        {"category": "inflation", "asset": "GLD", "correlation": 0.756, "p_value": 0.001, "sample_size": 112, "is_significant": True},
        {"category": "recession", "asset": "SPY", "correlation": -0.712, "p_value": 0.003, "sample_size": 67, "is_significant": True}
    ],
    "recent_activity": [
        {"type": "signal", "message": "New signal: Fed rate market +12.3%", "time": "15 min ago"},
        {"type": "data", "message": "Collected 45 market data points", "time": "1 hour ago"},
        {"type": "correlation", "message": "Calculated 3 new correlations", "time": "2 hours ago"},
        {"type": "signal", "message": "New signal: Trump election +8.5%", "time": "2 hours ago"}
    ],
    "portfolio": {
        "name": "My Crypto Portfolio",
        "user_id": "default",
        "holdings": {
            "BTC": {"weight": 0.5, "amount": None},
            "ETH": {"weight": 0.3, "amount": None},
            "SOL": {"weight": 0.2, "amount": None}
        },
        "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    "portfolio_analysis": {
        "correlations": {
            "BTC": [
                {
                    "market_id": "mock_btc_etf",
                    "market_question": "Will Bitcoin ETF be approved in Q1 2024?",
                    "category": "crypto",
                    "correlation": 0.731,
                    "p_value": 0.002,
                    "sample_size": 145,
                    "is_significant": True,
                    "relevance_score": 8.5
                },
                {
                    "market_id": "mock_btc_halving",
                    "market_question": "Will Bitcoin halving occur before May 2024?",
                    "category": "crypto",
                    "correlation": 0.612,
                    "p_value": 0.009,
                    "sample_size": 89,
                    "is_significant": True,
                    "relevance_score": 7.2
                },
                {
                    "market_id": "mock_btc_regulation",
                    "market_question": "Will SEC approve Bitcoin regulation by Q2 2024?",
                    "category": "crypto",
                    "correlation": None,
                    "relevance_score": 6.8,
                    "note": "No correlation data yet - collecting..."
                }
            ],
            "ETH": [
                {
                    "market_id": "mock_eth_upgrade",
                    "market_question": "Will Ethereum upgrade complete in Q2 2024?",
                    "category": "crypto",
                    "correlation": 0.689,
                    "p_value": 0.004,
                    "sample_size": 112,
                    "is_significant": True,
                    "relevance_score": 6.8
                },
                {
                    "market_id": "mock_eth_defi",
                    "market_question": "Will DeFi TVL exceed $100B in 2024?",
                    "category": "crypto",
                    "correlation": 0.545,
                    "p_value": 0.018,
                    "sample_size": 78,
                    "is_significant": True,
                    "relevance_score": 5.5
                }
            ],
            "SOL": [
                {
                    "market_id": "mock_sol_breakpoint",
                    "market_question": "Will Solana Breakpoint conference boost SOL price?",
                    "category": "crypto",
                    "correlation": 0.523,
                    "p_value": 0.025,
                    "sample_size": 45,
                    "is_significant": True,
                    "relevance_score": 5.2
                },
                {
                    "market_id": "mock_sol_network",
                    "market_question": "Will Solana network uptime exceed 99% in Q1?",
                    "category": "crypto",
                    "correlation": None,
                    "relevance_score": 4.8,
                    "note": "No correlation data yet - collecting..."
                }
            ]
        },
        "insights": [
            {
                "type": "high_impact_market",
                "market_id": "mock_btc_etf",
                "market_question": "Will Bitcoin ETF be approved in Q1 2024?",
                "affected_holdings": ["BTC"],
                "portfolio_weight": "50.0%",
                "avg_correlation": 0.731,
                "priority": "HIGH"
            },
            {
                "type": "high_impact_market",
                "market_id": "mock_eth_upgrade",
                "market_question": "Will Ethereum upgrade complete in Q2 2024?",
                "affected_holdings": ["ETH"],
                "portfolio_weight": "30.0%",
                "avg_correlation": 0.689,
                "priority": "MEDIUM"
            },
            {
                "type": "strongest_correlation",
                "data": {
                    "symbol": "BTC",
                    "market_question": "Will Bitcoin ETF be approved in Q1 2024?",
                    "correlation": 0.731,
                    "p_value": 0.002
                }
            }
        ]
    }
}


def get_real_data():
    """Get real data from database if available, otherwise return mock data"""
    try:
        db = Database()
        stats = db.get_stats()
        
        # Check if we have real data
        has_real_data = stats.get("market_data_points", 0) > 0
        
        if not has_real_data:
            return MOCK_DATA, False
        
        # Get real signals
        real_signals = db.get_recent_signals(limit=10)
        signals = []
        for sig in real_signals:
            signals.append({
                "id": sig["id"],
                "market_question": sig["market_question"],
                "category": sig["category"],
                "polymarket_change": f"{sig.get('polymarket_change', '0%')}",
                "signal_strength": sig.get("signal_strength", "WEAK"),
                "timestamp": sig["generated_at"],
                "trade_suggestions": sig.get("trade_suggestions", []),
                "using_real_data": True
            })
        
        # Get real correlations
        correlations = db.get_all_correlations()
        corr_list = []
        for corr in correlations[:20]:  # Top 20
            corr_list.append({
                "category": corr["market_category"],
                "asset": corr["asset_symbol"],
                "correlation": corr["correlation"],
                "p_value": corr.get("p_value"),
                "sample_size": corr.get("sample_size"),
                "is_significant": (corr.get("p_value") or 1.0) < 0.05
            })
        
        # Build real data structure
        real_data = {
            "signals": signals if signals else MOCK_DATA["signals"],
            "stats": stats,
            "correlations": corr_list if corr_list else MOCK_DATA["correlations"],
            "recent_activity": MOCK_DATA["recent_activity"]  # Keep mock for now
        }
        
        return real_data, True
    except Exception as e:
        print(f"Error getting real data: {e}")
        return MOCK_DATA, False


@app.route('/')
def index():
    """Main dashboard page - redirects to personalized view"""
    from flask import redirect
    return redirect('/personalized')

@app.route('/personalized')
def personalized_dashboard():
    """Personalized dashboard with Edge Map"""
    # Get portfolio
    portfolios = db.list_portfolios()
    
    if portfolios:
        portfolio_dict = portfolios[0]
        portfolio = Portfolio.from_dict(portfolio_dict)
    else:
        # Use mock portfolio
        portfolio = Portfolio.from_dict(MOCK_DATA.get("portfolio"))
    
    holdings = portfolio.get_holdings()
    
    # Calculate edge intensities
    edgescore_calc = EdgeScoreCalculator(db)
    edge_intensities = {}
    for symbol in holdings.keys():
        intensity = edgescore_calc.get_edge_intensity(symbol, holdings)
        edge_intensities[symbol] = intensity
    
    # Get markets that matter
    try:
        semantic_matcher = SemanticMatcher()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        markets_that_matter = loop.run_until_complete(
            semantic_matcher.find_markets_for_portfolio(holdings, min_edgescore=40.0)
        )
        loop.close()
        
        # Add alert status
        for market in markets_that_matter:
            if market["edgescore"] >= 75:
                market["alert_status"] = "live"
            elif market["edgescore"] >= 60:
                market["alert_status"] = "spike"
            else:
                market["alert_status"] = "elevated"
    except Exception as e:
        print(f"Error getting markets: {e}")
        # Use mock markets
        markets_that_matter = [
            {
                "market_id": "mock_1",
                "market_question": "Will ETH ETF be approved in Q1 2024?",
                "related_asset": "ETH",
                "edgescore": 86.0,
                "lead_time_hours": 8,
                "alert_status": "live"
            },
            {
                "market_id": "mock_2",
                "market_question": "Will Fed cut rates in September?",
                "related_asset": "SPY",
                "edgescore": 78.0,
                "lead_time_hours": 4,
                "alert_status": "spike"
            },
            {
                "market_id": "mock_3",
                "market_question": "Will Bitcoin hit $100k in 2024?",
                "related_asset": "BTC",
                "edgescore": 65.0,
                "lead_time_hours": 6,
                "alert_status": "elevated"
            }
        ]
    
    # Get upcoming events
    upcoming_events = [
        {"date": "2024-03-20", "name": "Federal Reserve Meeting", "markets": ["Fed Cut", "Rate Decision"], "impact": "high"},
        {"date": "2024-03-22", "name": "ETH ETF Decision", "markets": ["ETH ETF Approval"], "impact": "high"},
        {"date": "2024-04-15", "name": "CPI Release", "markets": ["Inflation Rate"], "impact": "medium"},
        {"date": "2024-04-20", "name": "Bitcoin Halving", "markets": ["BTC Halving"], "impact": "high"}
    ]
    
    return render_template('dashboard_personalized.html',
                         portfolio=portfolio,
                         edge_intensities=edge_intensities,
                         markets_that_matter=markets_that_matter,
                         upcoming_events=upcoming_events)

@app.route('/classic')
def classic_dashboard():
    """Classic dashboard page"""
    data, is_real = get_real_data()
    
    # Get portfolios for portfolio view
    portfolios = db.list_portfolios()
    portfolio_data = None
    
    if portfolios:
        # Use first portfolio for demo (in real app, would use user session)
        portfolio_dict = portfolios[0]
        portfolio = Portfolio.from_dict(portfolio_dict)
        
        # Get portfolio analysis (async, but simplified for now)
        try:
            tracker = PortfolioCorrelationTracker(db)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(tracker.analyze_portfolio(portfolio))
            portfolio_data = {
                "portfolio": portfolio.to_dict(),
                "analysis": analysis
            }
            loop.close()
        except Exception as e:
            print(f"Error analyzing portfolio: {e}")
            portfolio_data = {
                "portfolio": portfolio.to_dict(),
                "analysis": None
            }
    else:
        # Use mock portfolio data if no real portfolio exists
        if not is_real:
            portfolio_data = {
                "portfolio": MOCK_DATA.get("portfolio"),
                "analysis": {
                    "correlations": MOCK_DATA.get("portfolio_analysis", {}).get("correlations", {}),
                    "insights": MOCK_DATA.get("portfolio_analysis", {}).get("insights", [])
                }
            }
            
            # Add mock EdgeScore data
            portfolio_data["edge_intensities"] = [
                {"symbol": "BTC", "weight": 50.0, "edge_intensity": "High"},
                {"symbol": "ETH", "weight": 30.0, "edge_intensity": "Medium"},
                {"symbol": "SOL", "weight": 20.0, "edge_intensity": "Low"}
            ]
            
            portfolio_data["markets_that_matter"] = [
                {"rank": 1, "market": "ETH ETF Approval", "related_asset": "ETH", "edgescore": 86, "lead_time": "8 hrs", "alert": "🔥 Live"},
                {"rank": 2, "market": "Fed Cut in September", "related_asset": "SPY", "edgescore": 78, "lead_time": "4 hrs", "alert": "⚠️ Spike"},
                {"rank": 3, "market": "BTC to hit $100k", "related_asset": "BTC", "edgescore": 65, "lead_time": "6 hrs", "alert": ""},
                {"rank": 4, "market": "TikTok Ban Bill", "related_asset": "META", "edgescore": 54, "lead_time": "1 day", "alert": "🔍 Elevated"}
            ]
        else:
            # Calculate real EdgeScore data if portfolio exists
            if portfolio_data:
                portfolio = Portfolio.from_dict(portfolio_data["portfolio"])
                symbols = portfolio.get_symbols()
                
                try:
                    # Edge intensities
                    intensities = []
                    for symbol in symbols:
                        intensity = edgescore_calc.get_edge_intensity(symbol, symbols)
                        holdings = portfolio.get_holdings()
                        intensities.append({
                            "symbol": symbol,
                            "weight": holdings.get(symbol, 0) * 100,
                            "edge_intensity": intensity
                        })
                    portfolio_data["edge_intensities"] = intensities
                    
                    # Markets that matter (simplified - would use semantic matcher)
                    markets = []
                    # Would calculate markets that matter here
                    portfolio_data["markets_that_matter"] = []
                except Exception as e:
                    print(f"Error calculating EdgeScore data: {e}")
    
    return render_template('dashboard.html', 
                         data=data, 
                         is_real_data=is_real,
                         portfolio_data=portfolio_data)


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    data, is_real = get_real_data()
    return jsonify({
        "stats": data["stats"],
        "is_real_data": is_real
    })


@app.route('/api/signals')
def api_signals():
    """API endpoint for signals"""
    data, is_real = get_real_data()
    return jsonify({
        "signals": data["signals"],
        "is_real_data": is_real
    })


@app.route('/api/correlations')
def api_correlations():
    """API endpoint for correlations"""
    data, is_real = get_real_data()
    return jsonify({
        "correlations": data["correlations"],
        "is_real_data": is_real
    })


@app.route('/api/portfolios', methods=['GET', 'POST'])
def api_portfolios():
    """API endpoint for portfolios"""
    if request.method == 'POST':
        # Create new portfolio
        data = request.json
        portfolio_id = portfolio_manager.create_portfolio(
            data.get('name', 'My Portfolio'),
            data.get('user_id', 'default')
        )
        
        # Add holdings
        holdings = data.get('holdings', [])
        portfolio_manager.add_holdings_from_list(portfolio_id, holdings)
        
        return jsonify({"portfolio_id": portfolio_id, "status": "created"})
    else:
        # List portfolios
        portfolios = db.list_portfolios()
        return jsonify({"portfolios": portfolios})


@app.route('/api/portfolio/<portfolio_id>/analyze')
def api_portfolio_analyze(portfolio_id):
    """Analyze a portfolio"""
    portfolio_dict = db.get_portfolio(portfolio_id)
    if not portfolio_dict:
        return jsonify({"error": "Portfolio not found"}), 404
    
    portfolio = Portfolio.from_dict(portfolio_dict)
    tracker = PortfolioCorrelationTracker(db)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(tracker.analyze_portfolio(portfolio))
        loop.close()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/markets-that-matter')
def api_markets_that_matter():
    """Get markets that matter for default portfolio"""
    portfolios = db.list_portfolios()
    if not portfolios:
        return jsonify({"markets": []})
    
    portfolio = Portfolio.from_dict(portfolios[0])
    holdings = portfolio.get_holdings()
    
    try:
        semantic_matcher = SemanticMatcher()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        markets = loop.run_until_complete(
            semantic_matcher.find_markets_for_portfolio(holdings, min_edgescore=40.0)
        )
        loop.close()
        return jsonify({"markets": markets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/relationship/<market_id>/<asset>')
def api_relationship(market_id, asset):
    """Get relationship data for a market-asset pair"""
    from edgescore import EdgeScoreCalculator
    
    edgescore_calc = EdgeScoreCalculator(db)
    
    # Get correlation data
    # (Would need market category from market_id)
    # For now, return mock data structure
    return jsonify({
        "market_id": market_id,
        "asset": asset,
        "correlation": 0.73,
        "lead_time_hours": 8,
        "success_rate": 0.83,
        "sample_size": 145,
        "edgescore": 86.2,
        "historical_performance": "12 significant PM moves → 10 times asset followed within 12 hours"
    })


@app.route('/api/portfolio/<portfolio_id>/markets-that-matter')
def api_portfolio_markets_that_matter(portfolio_id):
    """Get ranked markets that matter for portfolio"""
    portfolio_dict = db.get_portfolio(portfolio_id)
    if not portfolio_dict:
        return jsonify({"error": "Portfolio not found"}), 404
    
    portfolio = Portfolio.from_dict(portfolio_dict)
    holdings = portfolio.get_holdings()
    
    # Get markets that matter using semantic matcher
    try:
        semantic_matcher = SemanticMatcher()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        markets = loop.run_until_complete(
            semantic_matcher.find_markets_for_portfolio(holdings, min_edgescore=40.0)
        )
        loop.close()
        return jsonify({"markets": markets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Format as "Markets That Matter" list
    markets = []
    for es in edgescores[:20]:  # Top 20
        # Get market question (would come from database in real implementation)
        market_question = es.get("market_question", f"{es['market_category']} market")
        
        # Determine alert status (mock for now)
        alert_status = "🔥 Live" if es["edgescore"] >= 80 else "⚠️ Spike" if es["edgescore"] >= 60 else "🔍 Elevated" if es["edgescore"] >= 40 else ""
        
        markets.append({
            "rank": len(markets) + 1,
            "market": market_question,
            "related_asset": es["asset"],
            "edgescore": es["edgescore"],
            "lead_time": f"{es.get('lag_hours', 12)} hrs",
            "alert": alert_status,
            "status": es["status"]
        })
    
    return jsonify({"markets": markets})


@app.route('/api/portfolio/<portfolio_id>/edge-intensity')
def api_edge_intensity(portfolio_id):
    """Get Edge Intensity for each holding"""
    portfolio_dict = db.get_portfolio(portfolio_id)
    if not portfolio_dict:
        return jsonify({"error": "Portfolio not found"}), 404
    
    portfolio = Portfolio.from_dict(portfolio_dict)
    symbols = portfolio.get_symbols()
    holdings = portfolio.get_holdings()
    
    intensities = []
    for symbol in symbols:
        intensity = edgescore_calc.get_edge_intensity(symbol, symbols)
        intensities.append({
            "symbol": symbol,
            "weight": holdings.get(symbol, 0) * 100,
            "edge_intensity": intensity
        })
    
    return jsonify({"intensities": intensities})


@app.route('/api/relationship/<market_category>/<asset_symbol>')
def api_relationship_explorer(market_category, asset_symbol):
    """Get relationship explorer data"""
    try:
        # Relationship explorer functionality (simplified)
        relationship = {
            "correlation": 0.73,
            "lead_time_hours": 8,
            "success_rate": 0.83
        }
        strategies = ["Buy dips when prob rises sharply", "Fade markets when prob drops too fast"]
        relationship["strategies"] = strategies
        return jsonify(relationship)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/portfolio/<portfolio_id>/events')
def api_portfolio_events(portfolio_id):
    """Get event calendar for portfolio"""
    portfolio_dict = db.get_portfolio(portfolio_id)
    if not portfolio_dict:
        return jsonify({"error": "Portfolio not found"}), 404
    
    portfolio = Portfolio.from_dict(portfolio_dict)
    # Event calendar (mock for now)
    events = [
        {"date": "2024-03-20", "name": "Federal Reserve Meeting", "markets": ["Fed Cut"], "impact": "high"},
        {"date": "2024-03-22", "name": "ETH ETF Decision", "markets": ["ETH ETF Approval"], "impact": "high"}
    ]
    events_by_date = {}
    
    return jsonify({
        "events": events,
        "events_by_date": events_by_date
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PolySignal Dashboard")
    print("=" * 60)
    print("📊 Starting web server...")
    print("🌐 Dashboard available at: http://localhost:8080")
    print("📡 API endpoints:")
    print("   - http://localhost:8080/api/stats")
    print("   - http://localhost:8080/api/signals")
    print("   - http://localhost:8080/api/correlations")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=8080)

