"""
PolySignal - Portfolio Management CLI
Command-line interface for managing portfolios
"""

import asyncio
import json
from database import Database
from portfolio import Portfolio, PortfolioManager
from portfolio_correlations import PortfolioCorrelationTracker
from market_matcher import MarketMatcher


async def create_portfolio_interactive():
    """Interactive portfolio creation"""
    db = Database()
    manager = PortfolioManager(db)
    
    print("=" * 60)
    print("📊 Create New Portfolio")
    print("=" * 60)
    
    name = input("Portfolio name: ").strip()
    if not name:
        print("❌ Name required")
        return
    
    portfolio_id = manager.create_portfolio(name)
    portfolio = manager.get_portfolio(portfolio_id)
    
    print(f"\n✅ Portfolio '{name}' created!")
    print(f"Portfolio ID: {portfolio_id}\n")
    
    print("Add holdings (enter 'done' when finished):")
    print("Format: SYMBOL WEIGHT (e.g., BTC 0.4) or SYMBOL AMOUNT (e.g., BTC 1000)")
    
    while True:
        entry = input("\nHolding: ").strip()
        if entry.lower() == 'done':
            break
        
        parts = entry.split()
        if len(parts) < 2:
            print("⚠️  Format: SYMBOL WEIGHT/AMOUNT")
            continue
        
        symbol = parts[0].upper()
        try:
            value = float(parts[1])
            
            # Determine if it's weight or amount
            if value <= 1.0:
                portfolio.add_holding(symbol, weight=value)
                print(f"✅ Added {symbol} with weight {value}")
            else:
                portfolio.add_holding(symbol, amount=value)
                print(f"✅ Added {symbol} with amount ${value:,.2f}")
        except ValueError:
            print("⚠️  Invalid number")
    
    # Save to database
    manager.portfolios[portfolio_id] = portfolio
    db.save_portfolio(portfolio_id, portfolio.name, portfolio.user_id, portfolio.holdings)
    
    print("\n" + "=" * 60)
    print("✅ Portfolio saved!")
    print("=" * 60)
    print(f"\nHoldings:")
    for symbol, data in portfolio.holdings.items():
        weight = data.get("weight", 0)
        print(f"  {symbol}: {weight*100:.1f}%")
    
    return portfolio_id


async def analyze_portfolio(portfolio_id: str):
    """Analyze a portfolio and show relevant markets"""
    db = Database()
    manager = PortfolioManager(db)
    
    portfolio = manager.get_portfolio(portfolio_id)
    if not portfolio:
        # Try loading from database
        portfolio_data = db.get_portfolio(portfolio_id)
        if portfolio_data:
            portfolio = Portfolio.from_dict(portfolio_data)
        else:
            print(f"❌ Portfolio {portfolio_id} not found")
            return
    
    print("=" * 60)
    print(f"📊 Analyzing Portfolio: {portfolio.name}")
    print("=" * 60)
    
    print(f"\nHoldings:")
    for symbol, data in portfolio.holdings.items():
        weight = data.get("weight", 0)
        print(f"  {symbol}: {weight*100:.1f}%")
    
    print("\n🔍 Finding relevant prediction markets...")
    
    tracker = PortfolioCorrelationTracker(db)
    analysis = await tracker.analyze_portfolio(portfolio)
    
    print("\n📈 Relevant Markets by Holding:")
    print("-" * 60)
    
    for symbol, markets in analysis["correlations"].items():
        if markets:
            print(f"\n{symbol}:")
            for i, market in enumerate(markets[:5], 1):  # Top 5
                corr = market.get("correlation")
                if corr:
                    sig = "✅" if market.get("is_significant") else "⚠️"
                    print(f"  {i}. {sig} {market['market_question'][:60]}")
                    print(f"     Correlation: {corr:.3f} | Relevance: {market['relevance_score']:.1f}")
                else:
                    print(f"  {i}. 📊 {market['market_question'][:60]}")
                    print(f"     {market.get('note', 'Collecting data...')}")
    
    print("\n💡 Portfolio Insights:")
    print("-" * 60)
    for insight in analysis["insights"]:
        if insight["type"] == "high_impact_market":
            print(f"\n🎯 High Impact Market:")
            print(f"   {insight['market_question']}")
            print(f"   Affects: {', '.join(insight['affected_holdings'])}")
            print(f"   Portfolio weight: {insight['portfolio_weight']}")
            print(f"   Priority: {insight['priority']}")
        elif insight["type"] == "strongest_correlation":
            data = insight["data"]
            print(f"\n🔗 Strongest Correlation:")
            print(f"   {data['symbol']} ↔ {data['market_question'][:50]}")
            print(f"   Correlation: {data['correlation']:.3f} (p={data['p_value']:.4f})")
    
    await tracker.close()


async def list_portfolios():
    """List all portfolios"""
    db = Database()
    portfolios = db.list_portfolios()
    
    if not portfolios:
        print("No portfolios found. Create one with: python manage_portfolio.py create")
        return
    
    print("=" * 60)
    print("📊 Your Portfolios")
    print("=" * 60)
    
    for i, portfolio in enumerate(portfolios, 1):
        print(f"\n{i}. {portfolio['name']} (ID: {portfolio['id']})")
        print(f"   Holdings: {len(portfolio['holdings'])} assets")
        for symbol, data in portfolio['holdings'].items():
            weight = data.get("weight", 0)
            print(f"     {symbol}: {weight*100:.1f}%")


async def main():
    """Main CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_portfolio.py create          # Create new portfolio")
        print("  python manage_portfolio.py list            # List portfolios")
        print("  python manage_portfolio.py analyze <id>    # Analyze portfolio")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        await create_portfolio_interactive()
    elif command == "list":
        await list_portfolios()
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Please provide portfolio ID")
            print("   Use 'python manage_portfolio.py list' to see IDs")
            return
        await analyze_portfolio(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())

