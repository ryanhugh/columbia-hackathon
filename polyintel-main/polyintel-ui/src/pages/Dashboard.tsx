import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertCircle, Zap } from 'lucide-react';
import APIService from '../services/api';
import SignalCard from '../components/SignalCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import TrendingMarkets from '../components/TrendingMarkets';
import { useSignalStore } from '../store/signals';

export default function Dashboard() {
  const [marketSlug, setMarketSlug] = useState('');
  const [analysisType, setAnalysisType] = useState<'spoon' | 'polycaster'>('polycaster');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { signals, addSignal, addToHistory } = useSignalStore();

  const handleAnalyze = async (slug: string) => {
    if (!slug.trim()) {
      setError('Please enter a market slug');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let response;

      if (analysisType === 'spoon') {
        response = await APIService.analyzeWithSPOON(slug);
      } else {
        response = await APIService.analyzeWithPolycaster(
          slug,
          `What is the sentiment around ${slug}?`,
          'crypto',
          true
        );
      }

      const signal = {
        ...response.card,
        timestamp: new Date().toISOString(),
      };

      addSignal(signal);
      addToHistory(signal);
      setMarketSlug('');
    } catch (err) {
      setError(APIService.getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header Section */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-600 p-3 rounded-lg">
              <Zap className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">Market Analysis</h2>
              <p className="text-gray-400">
                AI-powered signals for prediction markets
              </p>
            </div>
          </div>
        </div>

        {/* Analysis Input Card */}
        <div className="card mb-8 border-blue-600/30">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Market Slug
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={marketSlug}
                  onChange={(e) => setMarketSlug(e.target.value)}
                  onKeyPress={(e) =>
                    e.key === 'Enter' && handleAnalyze(marketSlug)
                  }
                  placeholder="e.g., btc-100k, trump-win-2024"
                  className="input flex-1"
                />
                <button
                  onClick={() => handleAnalyze(marketSlug)}
                  disabled={loading}
                  className="btn-primary flex items-center gap-2 disabled:opacity-50"
                >
                  <TrendingUp size={20} />
                  {loading ? 'Analyzing...' : 'Analyze'}
                </button>
              </div>
            </div>

            {/* Analysis Type Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Strategy
              </label>
              <div className="flex gap-3">
                <button
                  onClick={() => setAnalysisType('spoon')}
                  className={`flex-1 py-2 px-4 rounded font-semibold transition ${
                    analysisType === 'spoon'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  SPOON (Multi-Factor)
                </button>
                <button
                  onClick={() => setAnalysisType('polycaster')}
                  className={`flex-1 py-2 px-4 rounded font-semibold transition ${
                    analysisType === 'polycaster'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  PolyCaster (Sentiment)
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && <LoadingSpinner />}

        {/* Error Alert */}
        {error && (
          <ErrorAlert
            message={error}
            onClose={() => setError(null)}
            autoClose={5000}
          />
        )}

        {/* Trending Markets Section */}
        <TrendingMarkets />

        {/* Signals Grid */}
        {!loading && signals.length > 0 && (
          <div>
            <h3 className="text-2xl font-bold text-white mb-6">Your Signals</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {signals.map((signal) => (
                <SignalCard key={signal.market_id} signal={signal} />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && signals.length === 0 && (
          <div className="card text-center py-12 border-dashed">
            <AlertCircle className="mx-auto text-gray-500 mb-4" size={48} />
            <p className="text-gray-400 text-lg">
              Explore trending markets above or enter a market slug to analyze.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
