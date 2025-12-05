import React from 'react';
import { TrendingUp, Settings } from 'lucide-react';
import { Link } from 'react-router-dom';
import LiveTicker from './LiveTicker';

export default function Header() {
  return (
    <header className="sticky top-0 z-50">
      <div className="border-b border-gray-700 bg-gray-800/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition">
            <div className="bg-blue-600 p-2 rounded-lg">
              <TrendingUp size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">PolyIntel</h1>
              <p className="text-xs text-gray-400">AI Market Analysis</p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            <Link
              to="/"
              className="text-gray-300 hover:text-white transition font-medium"
            >
              Dashboard
            </Link>
            <Link
              to="/analysis"
              className="text-gray-300 hover:text-white transition font-medium"
            >
              Analysis
            </Link>
            <Link
              to="/whales"
              className="text-gray-300 hover:text-white transition font-medium"
            >
              Whale Tracker
            </Link>
            <Link
              to="/history"
              className="text-gray-300 hover:text-white transition font-medium"
            >
              History
            </Link>
          </nav>

          <Link
            to="/settings"
            className="btn-secondary p-2 rounded-lg hover:bg-gray-700 transition"
          >
            <Settings size={20} />
          </Link>
        </div>
      </div>
      <LiveTicker />
    </header>
  );
}
