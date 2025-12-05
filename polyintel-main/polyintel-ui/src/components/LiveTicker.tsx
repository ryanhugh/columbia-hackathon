import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface TickerItem {
  id: string;
  slug: string;
  title: string;
  odds: number;
  change24h?: number;
  volume24h?: number;
}

export default function LiveTicker() {
  const [tickers, setTickers] = useState<TickerItem[]>([
    { id: '1', slug: 'btc-100k', title: 'BTC > $100K', odds: 0.72, change24h: 5.2, volume24h: 5200000 },
    { id: '2', slug: 'eth-5k', title: 'ETH > $5K', odds: 0.45, change24h: -2.1, volume24h: 3100000 },
    { id: '3', slug: 'trump-2024', title: 'Trump Wins 2024', odds: 0.58, change24h: 3.5, volume24h: 8500000 },
    { id: '4', slug: 'fed-rate-cut', title: 'Fed Rate Cut Q4', odds: 0.68, change24h: 1.2, volume24h: 2300000 },
    { id: '5', slug: 'ai-breakthrough', title: 'AI Breakthrough 2024', odds: 0.82, change24h: 8.3, volume24h: 4100000 },
  ]);

  const [scrollPosition, setScrollPosition] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate live odds updates
      setTickers((prev) =>
        prev.map((ticker) => ({
          ...ticker,
          odds: Math.max(0.01, Math.min(0.99, ticker.odds + (Math.random() - 0.5) * 0.02)),
          change24h: (ticker.change24h || 0) + (Math.random() - 0.5) * 0.5,
        }))
      );
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // Auto-scroll ticker
  useEffect(() => {
    const scrollInterval = setInterval(() => {
      setScrollPosition((prev) => (prev + 1) % (tickers.length * 100));
    }, 30);

    return () => clearInterval(scrollInterval);
  }, [tickers.length]);

  return (
    <div className="bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600 overflow-hidden">
      <div className="relative flex items-center h-12 px-4">
        <div className="flex items-center gap-2 mr-4 flex-shrink-0">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs font-bold text-green-400">LIVE</span>
        </div>

        <div className="overflow-hidden flex-1">
          <div
            className="flex gap-6 transition-transform duration-100 ease-linear"
            style={{
              transform: `translateX(-${(scrollPosition / tickers.length) * 100}%)`,
            }}
          >
            {tickers.map((ticker, idx) => (
              <div
                key={`${ticker.id}-${idx}`}
                className="flex items-center gap-3 flex-shrink-0 px-2 py-1 rounded hover:bg-gray-600/30 cursor-pointer transition group"
              >
                <div className="min-w-max">
                  <p className="text-xs font-bold text-gray-300 group-hover:text-white transition">
                    {ticker.title}
                  </p>
                  <p className="text-xs text-gray-500">{ticker.slug}</p>
                </div>

                <div className="flex items-center gap-2 min-w-max">
                  <span className="text-sm font-bold text-white">
                    {(ticker.odds * 100).toFixed(0)}%
                  </span>
                  {ticker.change24h !== undefined && (
                    <div
                      className={`flex items-center gap-0.5 text-xs font-semibold ${
                        ticker.change24h >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {ticker.change24h >= 0 ? (
                        <TrendingUp size={12} />
                      ) : (
                        <TrendingDown size={12} />
                      )}
                      {Math.abs(ticker.change24h).toFixed(1)}%
                    </div>
                  )}
                </div>

                <div className="w-12 h-6 bg-gray-700/50 rounded relative overflow-hidden flex-shrink-0">
                  <div
                    className="h-full bg-blue-600/40"
                    style={{ width: `${ticker.odds * 100}%` }}
                  />
                </div>
              </div>
            ))}

            {/* Duplicate for seamless loop */}
            {tickers.map((ticker, idx) => (
              <div
                key={`${ticker.id}-dup-${idx}`}
                className="flex items-center gap-3 flex-shrink-0 px-2 py-1 rounded hover:bg-gray-600/30 cursor-pointer transition group"
              >
                <div className="min-w-max">
                  <p className="text-xs font-bold text-gray-300 group-hover:text-white transition">
                    {ticker.title}
                  </p>
                  <p className="text-xs text-gray-500">{ticker.slug}</p>
                </div>

                <div className="flex items-center gap-2 min-w-max">
                  <span className="text-sm font-bold text-white">
                    {(ticker.odds * 100).toFixed(0)}%
                  </span>
                  {ticker.change24h !== undefined && (
                    <div
                      className={`flex items-center gap-0.5 text-xs font-semibold ${
                        ticker.change24h >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {ticker.change24h >= 0 ? (
                        <TrendingUp size={12} />
                      ) : (
                        <TrendingDown size={12} />
                      )}
                      {Math.abs(ticker.change24h).toFixed(1)}%
                    </div>
                  )}
                </div>

                <div className="w-12 h-6 bg-gray-700/50 rounded relative overflow-hidden flex-shrink-0">
                  <div
                    className="h-full bg-blue-600/40"
                    style={{ width: `${ticker.odds * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
