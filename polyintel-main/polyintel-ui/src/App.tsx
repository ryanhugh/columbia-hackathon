import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/DashboardV2';
import History from './pages/History';
import WhaleTracker from './pages/WhaleTracker';
import Settings from './pages/Settings';
import './styles/index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900">
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/history" element={<History />} />
            <Route path="/whales" element={<WhaleTracker />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-700 bg-gray-800/30 mt-16 py-8">
          <div className="max-w-7xl mx-auto px-6 text-center text-gray-500 text-sm">
            <p>
              PolyIntel © 2024 | AI-Powered Prediction Market Analysis
            </p>
            <p className="mt-2">
              Backend API: {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
