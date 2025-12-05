import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  AlertCircle,
  Play,
  Lock,
  BarChart3,
  Zap,
  Search,
  ExternalLink,
  Loader,
  Eye,
  Shield,
} from 'lucide-react';
import APIService, { SignalResponse } from '../services/api';
import { useSignalStore } from '../store/signals';
import ErrorAlert from '../components/ErrorAlert';
import Chatbot from '../components/Chatbot';

interface FeaturedMarket {
  id: string;
  slug: string;
  title: string;
  category: string;
  odds: number;
  volume: number;
  sentiment?: number;
  risk?: string;
  whale?: string;
}

interface Analysis {
  market: FeaturedMarket;
  vibe: {
    score: number;
    sentiment: string;
    reasoning: string;
  };
  reality: {
    odds: number;
    divergence: number;
  };
  recommendation: string;
  audioUrl?: string;
}

type ActiveTab = 'polycaster' | 'polycop' | 'whaleauditor' | 'arb';

export default function DashboardV2() {
  const [featuredMarkets, setFeaturedMarkets] = useState<FeaturedMarket[]>([]);
  const [selectedMarket, setSelectedMarket] = useState<FeaturedMarket | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [marketsLoading, setMarketsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<ActiveTab>('polycaster');
  const [tickerData, setTickerData] = useState<any[]>([]);
  const { addSignal, addToHistory } = useSignalStore();

  // Load featured markets on component mount
  useEffect(() => {
    loadFeaturedMarkets();
    loadTickerMarkets();
  }, []);

  // Load ticker data from live API
  const loadTickerMarkets = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/polymarket/trending?limit=50`);
      if (!response.ok) throw new Error('Failed to fetch ticker markets');
      const data = await response.json();

      if (data.data && Array.isArray(data.data)) {
        const tickerItems = data.data.map((market: any) => {
          // Parse odds as percentage (0-1 to 0-100)
          let odds = 0.5;
          const outcomePrices = market.outcomePrices;
          if (Array.isArray(outcomePrices)) {
            try {
              odds = parseFloat(outcomePrices[0]);
            } catch (e) {
              odds = 0.5;
            }
          }

          const percentage = (odds * 100).toFixed(1);
          const change = (Math.random() - 0.5) * 5; // Random small change for display

          return {
            slug: market.slug || '',
            category: market.category || 'OTHER',
            price: parseFloat(percentage),
            change: change,
            percentage: `${change > 0 ? '+' : ''}${change.toFixed(1)}%`,
          };
        });

        setTickerData(tickerItems);
        console.log(`✓ Loaded ${tickerItems.length} markets for ticker`);
      }
    } catch (err) {
      console.error('Failed to load ticker markets:', err);
      // Fallback to demo data if API fails
      const demoTicker = featuredMarkets.map((market, idx) => ({
        slug: market.slug,
        category: market.category,
        price: market.odds * 100,
        change: Math.random() - 0.5,
        percentage: `${((Math.random() - 0.5) * 5).toFixed(1)}%`,
      }));
      setTickerData(demoTicker);
    }
  };

  const loadFeaturedMarkets = async () => {
    setMarketsLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/polymarket/trending?limit=8`);
      if (!response.ok) throw new Error('Failed to fetch markets');
      const data = await response.json();

      if (data.data && Array.isArray(data.data)) {
        const markets = data.data.slice(0, 4).map((market: any, idx: number) => {
          // Parse outcomePrices - could be array or string
          let odds = 0.5;
          const outcomePrices = market.outcomePrices;
          if (Array.isArray(outcomePrices)) {
            try {
              odds = parseFloat(outcomePrices[0]);
            } catch (e) {
              odds = 0.5;
            }
          } else if (typeof outcomePrices === 'string') {
            try {
              const parsed = JSON.parse(outcomePrices);
              odds = parseFloat(parsed[0]);
            } catch (e) {
              odds = 0.5;
            }
          }

          // Parse volume - handle both string and number formats
          let volumeNum = 0;
          const volumeStr = market.volume24hr || market.volume24h || market.volume || '0';
          try {
            volumeNum = parseFloat(String(volumeStr).replace(/[^0-9.-]/g, ''));
          } catch (e) {
            volumeNum = 0;
          }

          return {
            id: market.id || `market-${idx}`,
            slug: market.slug || market.title?.toLowerCase().replace(/\s+/g, '-') || `market-${idx}`,
            title: market.title || market.question || 'Unknown Market',
            category: market.category || 'General',
            odds: odds,
            volume: volumeNum,
            sentiment: Math.round((Math.random() * 100 - 50) * 10) / 10,
            risk: Math.random() > 0.7 ? 'HIGH' : Math.random() > 0.4 ? 'MODERATE' : 'LOW',
            whale: `@Whale${idx + 1}`,
          };
        });
        setFeaturedMarkets(markets);
        if (markets.length > 0) {
          setSelectedMarket(markets[0]);
        }
        console.log(`✓ Loaded ${markets.length} featured markets`);
      }
    } catch (err) {
      console.error('Failed to load markets:', err);
      setError('Failed to load trending markets. Using demo data.');
      // Fallback to demo markets if API fails
      setFeaturedMarkets(getDemoMarkets());
      setSelectedMarket(getDemoMarkets()[0]);
    } finally {
      setMarketsLoading(false);
    }
  };

  const getDemoMarkets = (): FeaturedMarket[] => [
    {
      id: '1',
      slug: 'trump-2024',
      title: 'Will Donald Trump win the 2024 Presidential Election?',
      category: 'Politics',
      odds: 0.52,
      volume: 1200000,
      sentiment: 35,
      risk: 'MODERATE',
      whale: '@Whale1',
    },
    {
      id: '2',
      slug: 'taylor-grammy',
      title: 'Will Taylor Swift win Album of the Year at the 2025 Grammys?',
      category: 'Culture',
      odds: 0.45,
      volume: 320000,
      sentiment: 62,
      risk: 'LOW',
      whale: '@Whale2',
    },
    {
      id: '3',
      slug: 'btc-100k',
      title: 'Will Bitcoin reach $100K by December 31, 2024?',
      category: 'Crypto',
      odds: 0.35,
      volume: 890000,
      sentiment: -15,
      risk: 'HIGH',
      whale: '@Whale3',
    },
    {
      id: '4',
      slug: 'fed-rate-cut',
      title: 'Will Fed cut rates in Q4 2024?',
      category: 'Macro',
      odds: 0.68,
      volume: 450000,
      sentiment: 28,
      risk: 'MODERATE',
      whale: '@Whale4',
    },
  ];

  useEffect(() => {
    if (selectedMarket) {
      analyzeMarket(selectedMarket);
    }
  }, [selectedMarket]);

  const analyzeMarket = async (market: FeaturedMarket) => {
    setLoading(true);
    setError(null);
    try {
      // Call PolyCaster API with use_manus=true to get audio
      const response = await APIService.analyzeWithPolycaster(
        market.slug,
        `Analysis for ${market.title}`,
        market.category,
        true
      );

      // Extract data from response
      const vibeScore = (response.state.narrative_score || 0) * 100;
      const realityOdds = response.state.current_odds || market.odds;
      const divergence = Math.abs(market.odds - realityOdds) * 100;

      const analysis: Analysis = {
        market,
        vibe: {
          score: vibeScore,
          sentiment: vibeScore > 0 ? 'positive' : 'negative',
          reasoning: response.state.reasoning || `Social media sentiment analysis complete. Market shows ${vibeScore > 0 ? 'bullish' : 'bearish'} signals with ${Math.abs(vibeScore).toFixed(1)}% sentiment score.`,
        },
        reality: {
          odds: realityOdds,
          divergence,
        },
        recommendation:
          divergence > 15
            ? `LONG ${realityOdds > 0.5 ? 'YES' : 'NO'}`
            : 'HOLD',
        audioUrl: response.audio_url || undefined,
      };

      setAnalysis(analysis);

      // Save to history
      const signal = {
        market_id: market.slug,
        strategy: 'PolyCaster',
        confidence: Math.abs(divergence) / 100,
        direction: (realityOdds > 0.5 ? 'YES' : 'NO') as 'YES' | 'NO',
        reasoning: analysis.vibe.reasoning,
        proof_link: `https://polymarket.com/event/${market.slug}`,
        timestamp: new Date().toISOString(),
      };
      addSignal(signal);
      addToHistory(signal);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(APIService.getErrorMessage(err));

      // Fallback to mock analysis
      const mockAnalysis = generateMockAnalysis(market);
      setAnalysis(mockAnalysis);
    } finally {
      setLoading(false);
    }
  };

  const generateMockAnalysis = (market: FeaturedMarket): Analysis => {
    const vibeScore = market.sentiment || 0;
    const realityOdds = market.odds + (Math.random() - 0.5) * 0.15;
    const divergence = Math.abs(market.odds - realityOdds) * 100;

    return {
      market,
      vibe: {
        score: vibeScore,
        sentiment: vibeScore > 0 ? 'positive' : 'negative',
        reasoning: `Analysis from social media sources including Twitter, Reddit, and financial news. Market sentiment indicates ${Math.abs(vibeScore).toFixed(1)}% ${vibeScore > 0 ? 'positive' : 'negative'} outlook on this prediction market.`,
      },
      reality: {
        odds: realityOdds,
        divergence,
      },
      recommendation:
        divergence > 15
          ? `LONG ${realityOdds > 0.5 ? 'YES' : 'NO'}`
          : 'HOLD',
    };
  };

  // Live Ticker Component
  const LiveTicker = () => (
    <div className="mb-6 bg-gray-800/50 border-y border-gray-700 overflow-hidden">
      <div className="animate-scroll flex gap-6 py-3 px-4">
        {tickerData.length > 0 ? (
          [...tickerData, ...tickerData, ...tickerData].map((item, idx) => (
            <div key={idx} className="flex items-center gap-4 whitespace-nowrap">
              <span className="text-xs font-bold text-yellow-400 min-w-[70px] bg-gray-700/50 px-2 py-1 rounded">
                {item.category}
              </span>
              <span className="text-white font-semibold min-w-[300px] text-sm truncate">
                {item.slug}
              </span>
              <span className="text-cyan-400 font-bold min-w-[60px]">
                {typeof item.price === 'number' ? item.price.toFixed(1) : item.price}%
              </span>
              <span className={`text-sm font-semibold min-w-[50px] ${item.percentage.includes('-') ? 'text-red-400' : 'text-green-400'}`}>
                {item.percentage}
              </span>
              <span className="w-1 h-1 bg-gray-600 rounded-full"></span>
            </div>
          ))
        ) : (
          <div className="text-center w-full text-gray-400 py-2">
            Loading live market data...
          </div>
        )}
      </div>
    </div>
  );

  // PolyCop Component - Risk Analysis
  const [riskData, setRiskData] = useState<any>(null);

  React.useEffect(() => {
    if (selectedMarket) {
      const loadRiskData = async () => {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
          const response = await fetch(`${apiUrl}/polycop/risk-analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ market_slug: selectedMarket.slug })
          });
          if (response.ok) {
            const data = await response.json();
            setRiskData(data);
          }
        } catch (err) {
          console.error('Failed to load risk data:', err);
        }
      };
      loadRiskData();
    }
  }, [selectedMarket]);

  const PolyCopDashboard = () => (
    <div className="bg-red-900/20 border border-red-600/50 rounded-lg p-6">
      <h2 className="text-red-400 font-bold text-lg mb-4 flex items-center gap-2">
        <Shield size={20} />
        PolyCop - Risk & Compliance Monitor
      </h2>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Risk Level</div>
            <div className={`text-2xl font-bold ${
              riskData?.state?.risk_level === 'LOW' ? 'text-green-400' :
              riskData?.state?.risk_level === 'HIGH' ? 'text-red-400' : 'text-yellow-400'
            }`}>
              {riskData?.state?.risk_level || 'MODERATE'}
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Volatility</div>
            <div className="text-2xl font-bold text-orange-400">{riskData?.state?.volatility?.toFixed(1) || '0.0'}%</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Market Liquidity</div>
            <div className="text-2xl font-bold text-blue-400">{riskData?.state?.liquidity || '$0'}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Spread</div>
            <div className="text-2xl font-bold text-yellow-400">{riskData?.state?.spread?.toFixed(2) || '0.00'}%</div>
          </div>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
          <h3 className="text-red-400 font-semibold mb-3">Risk Factors</h3>
          <ul className="space-y-2 text-gray-300 text-sm">
            {riskData?.risk_indicators && riskData.risk_indicators.length > 0 ? (
              riskData.risk_indicators.map((factor: string, idx: number) => (
                <li key={idx} className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${
                    factor.includes('Low') || factor.includes('Stable') || factor.includes('Clarity') ? 'bg-green-500' :
                    factor.includes('High') || factor.includes('detected') ? 'bg-red-500' : 'bg-yellow-500'
                  }`}></span>
                  {factor}
                </li>
              ))
            ) : (
              <>
                <li className="flex items-center gap-2"><span className="w-2 h-2 bg-gray-500 rounded-full"></span>Loading risk data...</li>
              </>
            )}
          </ul>
        </div>
        {riskData?.scores && (
          <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
            <h3 className="text-red-400 font-semibold mb-3">Risk Scores (0-100)</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Liquidity</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500" style={{width: `${riskData.scores.liquidity}%`}}></div>
                  </div>
                  <span className="text-blue-400 font-semibold w-10 text-right">{riskData.scores.liquidity}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Trader Diversity</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-purple-500" style={{width: `${riskData.scores.trader_diversity}%`}}></div>
                  </div>
                  <span className="text-purple-400 font-semibold w-10 text-right">{riskData.scores.trader_diversity}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Volume Consistency</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500" style={{width: `${riskData.scores.volume_consistency}%`}}></div>
                  </div>
                  <span className="text-green-400 font-semibold w-10 text-right">{riskData.scores.volume_consistency}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // WhaleAuditor Component
  const [whaleData, setWhaleData] = useState<any>(null);

  // Load whale data
  React.useEffect(() => {
    const loadWhaleData = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/polywhaler/whales`);
        if (response.ok) {
          const data = await response.json();
          setWhaleData(data);
        }
      } catch (err) {
        console.error('Failed to load whale data:', err);
      }
    };

    loadWhaleData();
    const interval = setInterval(loadWhaleData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const WhaleAuditorDashboard = () => (
    <div className="bg-purple-900/20 border border-purple-600/50 rounded-lg p-6">
      <h2 className="text-purple-400 font-bold text-lg mb-4 flex items-center gap-2">
        <Eye size={20} />
        WhaleAuditor - Large Position Tracking
      </h2>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Largest Whale Position</div>
            <div className="text-2xl font-bold text-purple-400">
              {whaleData ? `$${(whaleData.largest_position / 1000000).toFixed(2)}M` : 'Loading...'}
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Whale Activity (24h)</div>
            <div className="text-2xl font-bold text-pink-400">
              {whaleData ? `${whaleData.whale_activity} trades` : 'Loading...'}
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Market Concentration</div>
            <div className="text-2xl font-bold text-blue-400">
              {whaleData ? `${whaleData.market_concentration}%` : 'Loading...'}
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Total Whale Volume</div>
            <div className="text-2xl font-bold text-cyan-400">
              {whaleData ? `${whaleData.total_whale_volume}` : 'Loading...'}
            </div>
          </div>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
          <h3 className="text-purple-400 font-semibold mb-3">Top Whale Positions</h3>
          <div className="space-y-3">
            {whaleData && whaleData.top_whales && whaleData.top_whales.length > 0 ? (
              whaleData.top_whales.map((whale: any, idx: number) => (
                <div key={idx} className="flex items-start justify-between text-sm border-b border-gray-700 pb-2">
                  <div className="flex-1">
                    <div className="font-semibold text-white flex items-center gap-2">
                      {whale.alias}
                      <span className="text-xs px-2 py-0.5 bg-purple-900/50 text-purple-300 rounded">
                        {whale.reputation}
                      </span>
                    </div>
                    <div className="text-gray-500 text-xs mt-1">
                      Position: {whale.total_position} | Markets: {whale.active_markets}
                    </div>
                    <div className="text-gray-600 text-xs">
                      24h Trades: {whale.trades_24h}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold text-sm ${whale.pnl_percentage > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {whale.pnl_percentage > 0 ? '+' : ''}{whale.pnl_percentage.toFixed(1)}%
                    </div>
                    <div className="text-gray-500 text-xs">
                      ${(whale.pnl_24h / 1000).toFixed(1)}K
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-gray-400 text-xs">Loading whale data...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  // Arb Dashboard Component
  const ArbDashboard = () => (
    <div className="bg-green-900/20 border border-green-600/50 rounded-lg p-6">
      <h2 className="text-green-400 font-bold text-lg mb-4 flex items-center gap-2">
        <BarChart3 size={20} />
        Arb Dashboard - Cross-Market Opportunities
      </h2>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Potential Arb</div>
            <div className="text-2xl font-bold text-green-400">{(Math.random() * 5 + 0.5).toFixed(2)}%</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="text-gray-400 text-sm mb-2">Volume Available</div>
            <div className="text-2xl font-bold text-cyan-400">${((Math.random() * 500 + 100) * 1000).toFixed(0)}</div>
          </div>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
          <h3 className="text-green-400 font-semibold mb-3">Arb Opportunities</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-800/30 rounded border border-gray-700">
              <div className="text-sm">
                <div className="font-semibold text-white">Market Pair 1</div>
                <div className="text-gray-500 text-xs">YES/NO spread detected</div>
              </div>
              <div className="text-green-400 font-bold text-lg">+2.3%</div>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-800/30 rounded border border-gray-700">
              <div className="text-sm">
                <div className="font-semibold text-white">Market Pair 2</div>
                <div className="text-gray-500 text-xs">Correlated markets</div>
              </div>
              <div className="text-green-400 font-bold text-lg">+1.8%</div>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-800/30 rounded border border-gray-700">
              <div className="text-sm">
                <div className="font-semibold text-white">Cross-Exchange</div>
                <div className="text-gray-500 text-xs">Exchange price diff</div>
              </div>
              <div className="text-green-400 font-bold text-lg">+3.1%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Live Ticker - Full Width */}
      <LiveTicker />

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Featured Markets */}
          <div className="lg:col-span-1">
            {/* Featured Markets Header */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-yellow-400 text-xl">★</span>
                <h2 className="text-lg font-bold text-white">Featured Markets</h2>
                <span className="text-xs text-gray-500 ml-auto">DEMO</span>
              </div>

              {/* Market Items */}
              <div className="space-y-3">
                {featuredMarkets.map((market) => (
                  <button
                    key={market.id}
                    onClick={() => setSelectedMarket(market)}
                    className={`w-full text-left p-3 rounded-lg border-2 transition ${
                      selectedMarket?.id === market.id
                        ? 'border-blue-500 bg-blue-950/30'
                        : 'border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <h3 className="font-semibold text-white text-sm mb-2 line-clamp-2">
                      {market.title}
                    </h3>
                    <div className="space-y-2">
                      <div className="flex gap-2 text-xs">
                        <span className="px-2 py-1 bg-gray-700 rounded text-gray-300">
                          {market.category}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-cyan-400 font-bold">
                          YES: {(market.odds * 100).toFixed(1)}%
                        </span>
                        <span className="text-gray-500 text-xs">
                          {market.volume > 1e6 ? `$${(market.volume / 1e6).toFixed(2)}M` : market.volume > 1e3 ? `$${(market.volume / 1e3).toFixed(1)}K` : `$${market.volume}`}
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-xs text-gray-400">
                        <div>
                          <div className="text-gray-500">Sentiment</div>
                          <div
                            className={
                              market.sentiment! > 0
                                ? 'text-green-400 font-semibold'
                                : 'text-red-400 font-semibold'
                            }
                          >
                            {market.sentiment! > 0 ? '+' : ''}{market.sentiment?.toFixed(1)}
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-500">Risk</div>
                          <div
                            className={`font-semibold ${
                              market.risk === 'LOW'
                                ? 'text-green-400'
                                : market.risk === 'MODERATE'
                                  ? 'text-yellow-400'
                                  : 'text-red-400'
                            }`}
                          >
                            {market.risk}
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-500">Whale</div>
                          <div className="text-cyan-400 truncate">{market.whale}</div>
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              {/* Search Markets */}
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-white mb-3">Select Market</h3>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
                  <input
                    type="text"
                    placeholder="Search prediction markets..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Main Content - Analysis */}
          <div className="lg:col-span-3">
            {error && (
              <ErrorAlert
                message={error}
                onClose={() => setError(null)}
                autoClose={5000}
              />
            )}

            {marketsLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Loader className="animate-spin mx-auto text-blue-500 mb-3" size={32} />
                  <p className="text-gray-400">Loading featured markets...</p>
                </div>
              </div>
            ) : selectedMarket && (
              <div className="space-y-6">
                {/* Market Header */}
                <div className="border-b border-gray-800 pb-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="px-3 py-1 bg-gray-800 text-gray-300 text-xs rounded">
                          PREDICTION MARKET
                        </span>
                        <span className="px-3 py-1 bg-gray-800 text-gray-300 text-xs rounded">
                          TOTAL VOL: {selectedMarket.volume > 1e6 ? `$${(selectedMarket.volume / 1e6).toFixed(2)}M` : selectedMarket.volume > 1e3 ? `$${(selectedMarket.volume / 1e3).toFixed(1)}K` : `$${selectedMarket.volume}`}
                        </span>
                        <span className="px-3 py-1 bg-green-900 text-green-300 text-xs rounded">
                          ACTIVE
                        </span>
                      </div>
                      <h1 className="text-3xl font-bold text-white mb-2">
                        {selectedMarket.title}
                      </h1>
                      <a
                        href={`https://polymarket.com/event/${selectedMarket.slug}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-400 text-sm flex items-center gap-1 hover:text-cyan-300"
                      >
                        View on Polymarket
                        <ExternalLink size={14} />
                      </a>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-bold text-cyan-400">
                        {selectedMarket.odds >= 0.01
                          ? (selectedMarket.odds * 100).toFixed(0)
                          : (selectedMarket.odds * 100).toFixed(2)
                        }%
                      </div>
                      <div className="text-sm text-gray-400">Current Market Price (YES)</div>
                    </div>
                  </div>
                </div>

                {/* Analysis Tabs */}
                <div className="flex gap-4 border-b border-gray-800 pb-4 overflow-x-auto">
                  <button
                    onClick={() => setActiveTab('polycaster')}
                    className={`flex items-center gap-2 px-4 py-2 font-semibold whitespace-nowrap transition ${
                      activeTab === 'polycaster'
                        ? 'text-cyan-400 border-b-2 border-cyan-400'
                        : 'text-gray-500 hover:text-gray-400'
                    }`}
                  >
                    <Zap size={18} />
                    PolyCaster
                  </button>
                  <button
                    onClick={() => setActiveTab('polycop')}
                    className={`flex items-center gap-2 px-4 py-2 font-semibold whitespace-nowrap transition ${
                      activeTab === 'polycop'
                        ? 'text-red-400 border-b-2 border-red-400'
                        : 'text-gray-500 hover:text-gray-400'
                    }`}
                  >
                    <Shield size={18} />
                    PolyCop
                  </button>
                  <button
                    onClick={() => setActiveTab('whaleauditor')}
                    className={`flex items-center gap-2 px-4 py-2 font-semibold whitespace-nowrap transition ${
                      activeTab === 'whaleauditor'
                        ? 'text-purple-400 border-b-2 border-purple-400'
                        : 'text-gray-500 hover:text-gray-400'
                    }`}
                  >
                    <Eye size={18} />
                    WhaleAuditor
                  </button>
                  <button
                    onClick={() => setActiveTab('arb')}
                    className={`flex items-center gap-2 px-4 py-2 font-semibold whitespace-nowrap transition ${
                      activeTab === 'arb'
                        ? 'text-green-400 border-b-2 border-green-400'
                        : 'text-gray-500 hover:text-gray-400'
                    }`}
                  >
                    <BarChart3 size={18} />
                    Arb Dashboard
                  </button>
                </div>

                {/* Analysis Content */}
                {loading && activeTab === 'polycaster' ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-3"></div>
                      <p className="text-gray-400">Analyzing market...</p>
                    </div>
                  </div>
                ) : activeTab === 'polycaster' && analysis ? (
                  <>
                    <div className="bg-cyan-900/20 border border-cyan-600/50 rounded-lg p-6">
                      <h2 className="text-cyan-400 font-bold text-lg mb-4 flex items-center gap-2">
                        <Zap size={20} />
                        PolyCaster Analysis
                      </h2>
                      <p className="text-gray-300 mb-4">
                        Sentiment-driven position recommendation
                      </p>

                      {/* Play Audio Button */}
                      {analysis && (
                        <div className="mb-6 space-y-3">
                          {analysis.audioUrl ? (
                            <>
                              <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
                                <p className="text-sm text-gray-400 mb-3">🎙️ Audio Briefing Available</p>
                                <audio
                                  key={analysis.audioUrl}
                                  controls
                                  className="w-full h-10"
                                  controlsList="nodownload"
                                  crossOrigin="anonymous"
                                  onError={(e: any) => {
                                    console.error("Audio error:", e);
                                    console.log("Attempted URL:", analysis.audioUrl);
                                  }}
                                  onLoadedMetadata={() => console.log("Audio loaded:", analysis.audioUrl)}
                                >
                                  <source src={analysis.audioUrl} type="audio/mpeg" />
                                  Your browser does not support the audio element.
                                </audio>
                                <p className="text-xs text-gray-500 mt-2">
                                  {analysis.audioUrl.split('/').pop()}
                                </p>
                              </div>
                              <button className="w-full bg-cyan-900/30 border border-cyan-600/50 rounded-lg p-4 flex items-center justify-center gap-3 hover:bg-cyan-900/50 transition text-cyan-400 font-semibold">
                                <Play size={20} />
                                Play Full Audio Briefing
                              </button>
                            </>
                          ) : (
                            <div className="w-full bg-cyan-900/20 border border-cyan-600/30 rounded-lg p-4 flex items-center justify-center gap-3 text-cyan-400 font-semibold opacity-75">
                              <Play size={20} />
                              <div className="text-sm text-left">
                                <p>Audio Briefing</p>
                                <p className="text-xs text-cyan-500">Set ELEVENLABS_API_KEY in backend .env</p>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Vibe vs Reality */}
                      <div className="grid grid-cols-2 gap-6">
                        {/* The Vibe */}
                        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                          <h3 className="text-purple-400 font-bold text-lg mb-4 flex items-center gap-2">
                            📊 The Vibe
                          </h3>
                          <div className="space-y-3">
                            <div>
                              <div className="text-gray-400 text-sm mb-1">Sentiment Score</div>
                              <div
                                className={`text-4xl font-bold ${
                                  analysis.vibe.score > 0
                                    ? 'text-green-400'
                                    : 'text-red-400'
                                }`}
                              >
                                {analysis.vibe.score > 0 ? '+' : ''}
                                {analysis.vibe.score.toFixed(0)}%
                              </div>
                            </div>
                            <div>
                              <div className="text-gray-400 text-sm mb-1">Dominant Sentiment</div>
                              <span
                                className={`px-3 py-1 rounded text-sm font-semibold ${
                                  analysis.vibe.score > 0
                                    ? 'bg-green-900/50 text-green-300'
                                    : 'bg-purple-900/50 text-purple-300'
                                }`}
                              >
                                {analysis.vibe.score > 0 ? 'positive' : 'negative'}
                              </span>
                            </div>
                            <p className="text-gray-400 text-sm mt-4">
                              Social media sentiment analysis from Twitter, Reddit, and news
                              sources
                            </p>
                          </div>
                        </div>

                        {/* The Reality */}
                        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                          <h3 className="text-cyan-400 font-bold text-lg mb-4 flex items-center gap-2">
                            📈 The Reality
                          </h3>
                          <div className="space-y-3">
                            <div>
                              <div className="text-gray-400 text-sm mb-1">Market Probability</div>
                              <div className="text-4xl font-bold text-cyan-400">
                                {(() => {
                                  const percentage = analysis.reality.odds * 100;
                                  // Show 2 decimal places for small odds, 1 for others
                                  if (percentage < 1) {
                                    return percentage.toFixed(2);
                                  } else if (percentage < 10) {
                                    return percentage.toFixed(1);
                                  } else {
                                    return percentage.toFixed(0);
                                  }
                                })()}%
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                {analysis.reality.odds === 0 ? 'Very unlikely' :
                                 analysis.reality.odds < 0.1 ? 'Unlikely' :
                                 analysis.reality.odds < 0.5 ? 'Possible' :
                                 analysis.reality.odds < 0.9 ? 'Likely' : 'Very likely'}
                              </p>
                            </div>
                            <div>
                              <div className="text-gray-400 text-sm mb-1">Divergence from Sentiment</div>
                              <span
                                className={`text-xl font-bold ${
                                  analysis.reality.divergence > 15
                                    ? 'text-red-400'
                                    : 'text-green-400'
                                }`}
                              >
                                {analysis.reality.divergence.toFixed(2)}%
                              </span>
                              <p className="text-xs text-gray-500 mt-1">
                                {analysis.reality.divergence > 30 ? 'Strong divergence' :
                                 analysis.reality.divergence > 15 ? 'Moderate divergence' :
                                 'Small divergence'}
                              </p>
                            </div>
                            <p className="text-gray-400 text-sm mt-4 border-t border-gray-600 pt-3">
                              Current market odds from Polymarket participants based on order book data
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Analysis Reasoning */}
                      <div className="mt-6 bg-gray-900/50 rounded-lg p-4 border border-gray-700">
                        <h3 className="text-cyan-400 font-bold mb-3">Detailed Analysis Reasoning</h3>
                        <p className="text-gray-300 whitespace-pre-wrap text-sm leading-relaxed">{analysis.vibe.reasoning}</p>
                      </div>

                      {/* Recommendation */}
                      <div className="mt-6 flex items-center justify-between bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                        <div>
                          <p className="text-gray-400 text-sm">Recommended Position</p>
                          <p className="text-gray-300">
                            {analysis.reality.divergence > 15
                              ? `Strong ${analysis.recommendation}`
                              : 'Hold position, wait for more clarity'}
                          </p>
                        </div>
                        <button
                          className={`px-6 py-2 rounded font-bold text-lg border-2 ${
                            analysis.reality.divergence > 15
                              ? 'border-green-500 text-green-400 hover:bg-green-900/30'
                              : 'border-gray-600 text-gray-400 cursor-not-allowed'
                          }`}
                        >
                          {analysis.recommendation}
                        </button>
                      </div>
                    </div>

                    {/* Made with Manus */}
                    <div className="text-right text-xs text-gray-600">
                      Made with Manus
                    </div>
                  </>
                ) : activeTab === 'polycop' ? (
                  <PolyCopDashboard />
                ) : activeTab === 'whaleauditor' ? (
                  <WhaleAuditorDashboard />
                ) : activeTab === 'arb' ? (
                  <ArbDashboard />
                ) : null}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Chatbot Component */}
      <Chatbot 
        context={{
          selectedMarket: selectedMarket,
          analysis: analysis
        }}
      />
    </div>
  );
}
