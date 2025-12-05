import React, { useState, useEffect } from 'react';
import { Waves, TrendingUp, TrendingDown } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import APIService from '../services/api';

interface WhaleActivity {
  market_id: string;
  trader: string;
  amount: number;
  direction: 'BUY' | 'SELL';
  timestamp: string;
  odds_before: number;
  odds_after: number;
  impact: number;
}

export default function WhaleTracker() {
  const [whaleActivity, setWhaleActivity] = useState<WhaleActivity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'ALL' | 'BUY' | 'SELL'>('ALL');

  useEffect(() => {
    loadWhaleActivity();
  }, []);

  const loadWhaleActivity = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await APIService.getWhaleActivity(30);
      setWhaleActivity(data);
    } catch (err) {
      setError(APIService.getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const filteredActivity = whaleActivity.filter((activity) => {
    if (filter === 'ALL') return true;
    return activity.direction === filter;
  });

  const totalVolume = whaleActivity.reduce((sum, a) => sum + a.amount, 0);
  const buyCount = whaleActivity.filter((a) => a.direction === 'BUY').length;
  const sellCount = whaleActivity.filter((a) => a.direction === 'SELL').length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="bg-orange-600 p-3 rounded-lg">
              <Waves className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">Whale Tracker</h2>
              <p className="text-gray-400">Monitor large holder activity</p>
            </div>
          </div>
          <button
            onClick={loadWhaleActivity}
            disabled={loading}
            className="btn-primary disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="card">
            <p className="text-gray-400 text-sm">Total Volume</p>
            <p className="text-2xl font-bold text-white mt-2">
              ${(totalVolume / 1e6).toFixed(2)}M
            </p>
          </div>
          <div className="card">
            <p className="text-gray-400 text-sm">Buy Orders</p>
            <p className="text-2xl font-bold text-green-400 mt-2">{buyCount}</p>
          </div>
          <div className="card">
            <p className="text-gray-400 text-sm">Sell Orders</p>
            <p className="text-2xl font-bold text-red-400 mt-2">{sellCount}</p>
          </div>
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2 mb-6">
          {(['ALL', 'BUY', 'SELL'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded font-semibold transition ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Loading State */}
        {loading && <LoadingSpinner message="Loading whale activity..." />}

        {/* Error Alert */}
        {error && (
          <ErrorAlert
            message={error}
            onClose={() => setError(null)}
            autoClose={5000}
          />
        )}

        {/* Activity List */}
        {!loading && filteredActivity.length > 0 && (
          <div className="space-y-3">
            {filteredActivity.map((activity, idx) => (
              <div
                key={idx}
                className="card flex items-center justify-between hover:border-blue-500 transition"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {activity.direction === 'BUY' ? (
                      <TrendingUp className="text-green-400" size={20} />
                    ) : (
                      <TrendingDown className="text-red-400" size={20} />
                    )}
                    <h4 className="font-bold text-white">{activity.market_id}</h4>
                  </div>
                  <div className="text-sm text-gray-400">
                    <p>Trader: {activity.trader}</p>
                    <p>Amount: ${(activity.amount / 1e6).toFixed(2)}M</p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="text-sm font-mono text-gray-300 mb-1">
                    {activity.odds_before.toFixed(2)} →{' '}
                    {activity.odds_after.toFixed(2)}
                  </p>
                  <p className={`text-xs font-semibold ${
                    activity.impact > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {activity.impact > 0 ? '+' : ''}{(activity.impact * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(activity.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredActivity.length === 0 && (
          <div className="card text-center py-12 border-dashed">
            <Waves className="mx-auto text-gray-500 mb-4" size={48} />
            <p className="text-gray-400">No whale activity found.</p>
          </div>
        )}
      </div>
    </div>
  );
}
