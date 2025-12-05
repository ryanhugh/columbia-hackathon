import React, { useState } from 'react';
import { CheckCircle, XCircle, Heart, ExternalLink, Volume2 } from 'lucide-react';
import { TradeSignal } from '../services/api';
import { useSignalStore } from '../store/signals';

interface SignalCardProps {
  signal: TradeSignal;
  onPlayAudio?: () => void;
  showFooter?: boolean;
}

export default function SignalCard({
  signal,
  onPlayAudio,
  showFooter = true,
}: SignalCardProps) {
  const { isFavorite, toggleFavorite } = useSignalStore();
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  const isFav = isFavorite(signal.market_id);
  const confidenceColor =
    signal.confidence > 0.7
      ? 'text-green-400'
      : signal.confidence > 0.4
      ? 'text-yellow-400'
      : 'text-red-400';

  const handlePlayAudio = () => {
    if (onPlayAudio) {
      onPlayAudio();
      setIsAudioPlaying(true);
      setTimeout(() => setIsAudioPlaying(false), 3000);
    }
  };

  return (
    <div className="card hover:border-blue-500 cursor-pointer transform hover:scale-102 transition-all group">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-white group-hover:text-blue-400 truncate">
            {signal.market_id}
          </h3>
          <p className="text-xs text-gray-400 mt-1">
            {signal.timestamp
              ? new Date(signal.timestamp).toLocaleString()
              : 'Just now'}
          </p>
        </div>

        {/* Direction Badge */}
        <div className="flex items-center gap-2">
          {signal.direction === 'YES' ? (
            <CheckCircle className="text-green-400 flex-shrink-0" size={24} />
          ) : (
            <XCircle className="text-red-400 flex-shrink-0" size={24} />
          )}
          <button
            onClick={() => toggleFavorite(signal.market_id)}
            className="text-gray-400 hover:text-red-400 transition-colors"
          >
            <Heart
              size={20}
              fill={isFav ? 'currentColor' : 'none'}
              color={isFav ? '#f87171' : 'currentColor'}
            />
          </button>
        </div>
      </div>

      {/* Strategy Badge */}
      <div className="mb-3">
        <span className="inline-block bg-blue-900/50 text-blue-300 text-xs font-semibold px-3 py-1 rounded-full">
          {signal.strategy}
        </span>
      </div>

      {/* Confidence Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-400">Confidence Level</span>
          <span className={`font-bold text-sm ${confidenceColor}`}>
            {(signal.confidence * 100).toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2.5 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              signal.confidence > 0.7
                ? 'bg-green-400'
                : signal.confidence > 0.4
                ? 'bg-yellow-400'
                : 'bg-red-400'
            }`}
            style={{ width: `${signal.confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Reasoning */}
      <div className="bg-gray-900/50 rounded-lg p-3 mb-4 border border-gray-700">
        <p className="text-sm text-gray-300 line-clamp-3">
          {signal.reasoning || 'No reasoning provided'}
        </p>
      </div>

      {/* Footer Actions */}
      {showFooter && (
        <div className="flex gap-2 pt-4 border-t border-gray-700">
          <a
            href={signal.proof_link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 btn-secondary flex items-center justify-center gap-2 text-sm"
          >
            <ExternalLink size={16} />
            View Market
          </a>
          {onPlayAudio && (
            <button
              onClick={handlePlayAudio}
              disabled={isAudioPlaying}
              className="btn-secondary px-4 flex items-center justify-center gap-2 text-sm disabled:opacity-50"
            >
              <Volume2 size={16} />
              {isAudioPlaying ? 'Playing...' : 'Listen'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
