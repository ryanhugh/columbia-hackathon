import React, { useMemo } from 'react';
import { Clock, Trash2 } from 'lucide-react';
import SignalCard from '../components/SignalCard';
import { useSignalStore } from '../store/signals';

export default function History() {
  const { history, clearHistory } = useSignalStore();

  const stats = useMemo(() => {
    if (history.length === 0) return { wins: 0, losses: 0, winRate: 0 };
    const wins = history.filter((s) => s.direction === 'YES').length;
    const losses = history.filter((s) => s.direction === 'NO').length;
    return {
      wins,
      losses,
      winRate: ((wins / history.length) * 100).toFixed(1),
    };
  }, [history]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="bg-purple-600 p-3 rounded-lg">
              <Clock className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">Signal History</h2>
              <p className="text-gray-400">All past signals and analysis</p>
            </div>
          </div>
          {history.length > 0 && (
            <button
              onClick={clearHistory}
              className="btn-secondary flex items-center gap-2"
            >
              <Trash2 size={18} />
              Clear History
            </button>
          )}
        </div>

        {/* Stats Cards */}
        {history.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="card text-center">
              <p className="text-gray-400 text-sm">Total Signals</p>
              <p className="text-3xl font-bold text-white mt-2">
                {history.length}
              </p>
            </div>
            <div className="card text-center">
              <p className="text-gray-400 text-sm">Win Rate</p>
              <p className="text-3xl font-bold text-green-400 mt-2">
                {stats.winRate}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {stats.wins}W / {stats.losses}L
              </p>
            </div>
            <div className="card text-center">
              <p className="text-gray-400 text-sm">Date Range</p>
              <p className="text-sm text-white mt-2">
                {history.length > 0
                  ? `${new Date(history[history.length - 1].timestamp || '').toLocaleDateString()} - ${new Date(history[0].timestamp || '').toLocaleDateString()}`
                  : 'N/A'}
              </p>
            </div>
          </div>
        )}

        {/* History Grid */}
        {history.length > 0 ? (
          <div>
            <h3 className="text-lg font-bold text-white mb-6">All Signals</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {history.map((signal) => (
                <SignalCard
                  key={`${signal.market_id}-${signal.timestamp}`}
                  signal={signal}
                  showFooter={true}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="card text-center py-12 border-dashed">
            <Clock className="mx-auto text-gray-500 mb-4" size={48} />
            <p className="text-gray-400 text-lg">No signals in history yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
