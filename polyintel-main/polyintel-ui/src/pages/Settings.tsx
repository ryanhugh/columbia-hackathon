import React, { useState } from 'react';
import { Settings as SettingsIcon, Save, RotateCcw } from 'lucide-react';

interface AppSettings {
  apiUrl: string;
  autoRefresh: boolean;
  refreshInterval: number;
  theme: 'dark' | 'light';
  notifications: boolean;
}

export default function Settings() {
  const [settings, setSettings] = useState<AppSettings>({
    apiUrl: localStorage.getItem('polyintel_api_url') || 'http://localhost:8000',
    autoRefresh: JSON.parse(localStorage.getItem('polyintel_auto_refresh') || 'false'),
    refreshInterval: parseInt(localStorage.getItem('polyintel_refresh_interval') || '30'),
    theme: (localStorage.getItem('polyintel_theme') as any) || 'dark',
    notifications: JSON.parse(localStorage.getItem('polyintel_notifications') || 'true'),
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem('polyintel_api_url', settings.apiUrl);
    localStorage.setItem('polyintel_auto_refresh', JSON.stringify(settings.autoRefresh));
    localStorage.setItem('polyintel_refresh_interval', String(settings.refreshInterval));
    localStorage.setItem('polyintel_theme', settings.theme);
    localStorage.setItem('polyintel_notifications', JSON.stringify(settings.notifications));

    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    setSettings({
      apiUrl: 'http://localhost:8000',
      autoRefresh: false,
      refreshInterval: 30,
      theme: 'dark',
      notifications: true,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-green-600 p-3 rounded-lg">
            <SettingsIcon className="text-white" size={24} />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-white">Settings</h2>
            <p className="text-gray-400">Manage your preferences</p>
          </div>
        </div>

        {/* Settings Form */}
        <div className="card space-y-6">
          {/* API Configuration */}
          <div>
            <h3 className="text-lg font-bold text-white mb-4">API Configuration</h3>
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Backend API URL
              </label>
              <input
                type="text"
                value={settings.apiUrl}
                onChange={(e) =>
                  setSettings({ ...settings, apiUrl: e.target.value })
                }
                className="input w-full"
              />
              <p className="text-xs text-gray-500 mt-2">
                The URL where your PolyIntel backend is running
              </p>
            </div>
          </div>

          {/* Auto Refresh */}
          <div className="border-t border-gray-700 pt-6">
            <h3 className="text-lg font-bold text-white mb-4">Refresh Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="autoRefresh"
                  checked={settings.autoRefresh}
                  onChange={(e) =>
                    setSettings({ ...settings, autoRefresh: e.target.checked })
                  }
                  className="w-4 h-4 rounded border-gray-600 bg-gray-700 cursor-pointer"
                />
                <label
                  htmlFor="autoRefresh"
                  className="ml-3 text-sm font-semibold text-gray-300 cursor-pointer"
                >
                  Auto-refresh signals
                </label>
              </div>

              {settings.autoRefresh && (
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    Refresh Interval (seconds)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="300"
                    value={settings.refreshInterval}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        refreshInterval: parseInt(e.target.value),
                      })
                    }
                    className="input w-full"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Display Settings */}
          <div className="border-t border-gray-700 pt-6">
            <h3 className="text-lg font-bold text-white mb-4">Display</h3>
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Theme
              </label>
              <select
                value={settings.theme}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    theme: e.target.value as 'dark' | 'light',
                  })
                }
                className="input w-full"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
              </select>
            </div>
          </div>

          {/* Notifications */}
          <div className="border-t border-gray-700 pt-6">
            <h3 className="text-lg font-bold text-white mb-4">Notifications</h3>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="notifications"
                checked={settings.notifications}
                onChange={(e) =>
                  setSettings({ ...settings, notifications: e.target.checked })
                }
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 cursor-pointer"
              />
              <label
                htmlFor="notifications"
                className="ml-3 text-sm font-semibold text-gray-300 cursor-pointer"
              >
                Enable desktop notifications for new signals
              </label>
            </div>
          </div>

          {/* Buttons */}
          <div className="border-t border-gray-700 pt-6 flex gap-3">
            <button onClick={handleSave} className="btn-primary flex items-center gap-2">
              <Save size={18} />
              Save Settings
            </button>
            <button
              onClick={handleReset}
              className="btn-secondary flex items-center gap-2"
            >
              <RotateCcw size={18} />
              Reset to Default
            </button>
          </div>

          {/* Success Message */}
          {saved && (
            <div className="bg-green-900/20 border border-green-600 rounded p-3 text-green-300 text-sm">
              ✓ Settings saved successfully
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
