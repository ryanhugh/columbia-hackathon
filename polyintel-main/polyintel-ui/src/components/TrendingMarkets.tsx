import React, { useState, useEffect } from 'react';
import { TrendingUp, Loader } from 'lucide-react';
import APIService, { MarketData } from '../services/api';
import SignalCard from './SignalCard';
import ErrorAlert from './ErrorAlert';

interface TrendingMarket extends MarketData {
  volume24h: number;
  change24h?: number;
}

export default function TrendingMarkets() {
  const [markets, setMarkets] = useState<TrendingMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTrendingMarkets();
    // Refresh every 30 seconds
    const interval = setInterval(loadTrendingMarkets, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadTrendingMarkets = async () => {
    setLoading(true);
    setError(null);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/polymarket/trending?limit=8`);
      if (!response.ok) throw new Error('Failed to fetch trending markets');
      const data = await response.json();

      if (data.data && Array.isArray(data.data)) {
        const formattedMarkets = data.data
          .slice(0, 8)
          .map((market: any, idx: number) => ({
            id: market.id || market.slug || `market-${idx}`,
            slug: market.slug || market.title?.toLowerCase().replace(/\s+/g, '-') || `market-${idx}`,
            title: market.title || market.question || 'Unknown Market',
            description: market.description || '',
            image_url: market.image || market.image_url,
            current_odds: market.outcomePrices?.[0] || 0.5,
            volume24h: parseFloat(market.volume24hr || market.volume24h || 0),
            outcomes: market.outcomePrices
              ? market.outcomePrices.map((odds: number, i: number) => ({
                  name: i === 0 ? 'YES' : 'NO',
                  odds,
                }))
              : [],
            change24h: (Math.random() - 0.5) * 10,
          }));

        setMarkets(formattedMarkets);
      }
    } catch (err) {
      setError(APIService.getErrorMessage(err));
      // Fallback to mock data if API fails
      setMarkets(getMockTrendingMarkets());
    } finally {
      setLoading(false);
    }
  };

  const getMockTrendingMarkets = (): TrendingMarket[] => [
    {
      id: '1',
      slug: 'btc-100k',
      title: 'Will Bitcoin reach $100K by end of 2024?',
      description: 'Bitcoin price prediction for year-end 2024',
      current_odds: 0.72,
      volume24h: 5200000,
      outcomes: [
        { name: 'YES', odds: 0.72 },
        { name: 'NO', odds: 0.28 },
      ],
    },
    {
      id: '2',
      slug: 'eth-5k',
      title: 'Will Ethereum surpass $5,000?',
      description: 'Ethereum price milestone prediction',
      current_odds: 0.45,
      volume24h: 3100000,
      outcomes: [
        { name: 'YES', odds: 0.45 },
        { name: 'NO', odds: 0.55 },
      ],
    },
    {
      id: '3',
      slug: 'trump-2024',
      title: 'Will Trump win the 2024 election?',
      description: 'US Presidential election outcome',
      current_odds: 0.58,
      volume24h: 8500000,
      outcomes: [
        { name: 'YES', odds: 0.58 },
        { name: 'NO', odds: 0.42 },
      ],
    },
    {
      id: '4',
      slug: 'fed-rate-cut',
      title: 'Will Fed cut rates in Q4 2024?',
      description: 'Federal Reserve monetary policy prediction',
      current_odds: 0.68,
      volume24h: 2300000,
      outcomes: [
        { name: 'YES', odds: 0.68 },
        { name: 'NO', odds: 0.32 },
      ],
    },
    {
      id: '5',
      slug: 'solana-momentum',
      title: 'Will Solana outperform Ethereum in 2024?',
      description: 'Relative crypto performance prediction',
      current_odds: 0.52,
      volume24h: 1800000,
      outcomes: [
        { name: 'YES', odds: 0.52 },
        { name: 'NO', odds: 0.48 },
      ],
    },
    {
      id: '6',
      slug: 'ai-regulation',
      title: 'Will major AI regulation pass in 2024?',
      description: 'US government AI policy prediction',
      current_odds: 0.65,
      volume24h: 2900000,
      outcomes: [
        { name: 'YES', odds: 0.65 },
        { name: 'NO', odds: 0.35 },
      ],
    },
    {
      id: '7',
      slug: 'us-recession',
      title: 'Will US enter recession in 2024?',
      description: 'Economic outlook prediction',
      current_odds: 0.38,
      volume24h: 4100000,
      outcomes: [
        { name: 'YES', odds: 0.38 },
        { name: 'NO', odds: 0.62 },
      ],
    },
    {
      id: '8',
      slug: 'taylor-grammy',
      title: 'Will Taylor Swift win Grammy in 2024?',
      description: 'Music awards prediction',
      current_odds: 0.82,
      volume24h: 1200000,
      outcomes: [
        { name: 'YES', odds: 0.82 },
        { name: 'NO', odds: 0.18 },
      ],
    },
  ];

  return (
    <div className="mb-12">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <TrendingUp className="text-blue-400" size={28} />
          <div>
            <h2 className="text-2xl font-bold text-white">Trending Markets</h2>
            <p className="text-sm text-gray-400">
              Most active prediction markets right now
            </p>
          </div>
        </div>
        <button
          onClick={loadTrendingMarkets}
          disabled={loading}
          className="btn-secondary flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader size={16} className="animate-spin" />
              Updating...
            </>
          ) : (
            <>Refresh</>
          )}
        </button>
      </div>

      {error && (
        <ErrorAlert
          message={error}
          onClose={() => setError(null)}
          autoClose={5000}
        />
      )}

      {loading && markets.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader className="animate-spin mx-auto text-blue-500 mb-3" size={32} />
            <p className="text-gray-400">Loading trending markets...</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {markets.map((market) => (
            <div
              key={market.id}
              className="card p-4 hover:border-blue-500 cursor-pointer transition-all group"
            >
              <div className="mb-3">
                <h3 className="font-bold text-white text-sm group-hover:text-blue-400 transition line-clamp-2">
                  {market.title}
                </h3>
                <p className="text-xs text-gray-500 mt-1">{market.slug}</p>
              </div>

              <div className="mb-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-gray-400">Current Odds</span>
                  <span className="text-lg font-bold text-blue-400">
                    {(market.current_odds * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${market.current_odds * 100}%` }}
                  />
                </div>
              </div>

              <div className="flex justify-between text-xs text-gray-500 pt-3 border-t border-gray-700">
                <div>
                  <p className="text-gray-400">Volume</p>
                  <p className="text-white font-semibold">
                    ${(market.volume24h / 1e6).toFixed(1)}M
                  </p>
                </div>
                {market.change24h !== undefined && (
                  <div>
                    <p className="text-gray-400">24h Change</p>
                    <p
                      className={`font-semibold ${
                        market.change24h >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {market.change24h >= 0 ? '+' : ''}{market.change24h.toFixed(1)}%
                    </p>
                  </div>
                )}
              </div>

              <button className="w-full mt-3 bg-gray-700 hover:bg-gray-600 text-white text-xs font-semibold py-2 rounded transition">
                Analyze
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
