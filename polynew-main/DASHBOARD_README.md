# 🎨 PolySignal Dashboard

Beautiful web dashboard for monitoring signals, correlations, and statistics.

## 🚀 Quick Start

### Start the Dashboard

```bash
python dashboard.py
```

Then open your browser to: **http://localhost:8080**

**Note:** Port 8080 is used (instead of 5000) because macOS uses port 5000 for AirPlay.

## 📊 Features

### Current View (Mock Data)
- **Signals**: Shows recent trading signals with trade suggestions
- **Statistics**: Database stats (data points, correlations, signals)
- **Correlations**: Top correlations with statistical significance
- **Activity Feed**: Recent system activity

### Auto-Switching to Real Data
The dashboard automatically switches from mock data to real data when:
- Database has collected data (`market_data_points > 0`)
- Real signals are available
- Real correlations have been calculated

**Indicator**: Look for the badge in the header:
- 🟢 **📊 Real Data** = Using real database data
- 🟡 **📈 Mock Data** = Using mock data (no real data yet)

## 🔌 API Endpoints

The dashboard also provides REST API endpoints:

### Get Statistics
```bash
curl http://localhost:8080/api/stats
```

### Get Signals
```bash
curl http://localhost:8080/api/signals
```

### Get Correlations
```bash
curl http://localhost:8080/api/correlations
```

## 🎨 Dashboard Sections

### 1. Statistics Cards
- **Market Data Points**: Total Polymarket price records
- **Asset Data Points**: Total crypto/asset price records
- **Correlations**: Number of calculated correlations
- **Signals Generated**: Total signals created

### 2. Recent Signals
Shows the latest trading signals with:
- Market question
- Price change percentage
- Signal strength (STRONG/MEDIUM/WEAK)
- Trade suggestions with confidence levels
- Data source indicator (Real vs Estimated)

### 3. Top Correlations
Displays calculated correlations with:
- Category → Asset pairs
- Correlation coefficient (r)
- P-value (statistical significance)
- Sample size (n)
- Significance badge

### 4. Recent Activity
Timeline of recent system events

## 🔄 Auto-Refresh

The dashboard automatically refreshes every 30 seconds to show new data.

## 🛠️ Customization

### Change Port
Edit `dashboard.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change port here
```

### Modify Mock Data
Edit the `MOCK_DATA` dictionary in `dashboard.py` to customize initial display.

### Styling
Edit `templates/dashboard.html` to change colors, layout, or add features.

## 📱 Mobile Responsive

The dashboard is responsive and works on:
- Desktop
- Tablet
- Mobile devices

## 🔍 Troubleshooting

### Dashboard won't start
```bash
# Check if port 8080 is in use
lsof -i :8080

# Install Flask if missing
pip install flask

# If port 8080 is taken, edit dashboard.py and change port=8080 to another port
```

### No data showing
- If using mock data: This is normal initially
- If expecting real data: Check database has data:
  ```bash
  python -c "from database import Database; db = Database(); print(db.get_stats())"
  ```

### Dashboard shows old data
- Refresh the page (auto-refresh is every 30 seconds)
- Check if monitor is running and collecting data

## 🎯 Next Steps

1. **Start collecting data**:
   ```bash
   python collect_data.py continuous 5 24
   ```

2. **Calculate correlations** (after 1-2 weeks):
   ```bash
   python calculate_correlations.py calculate 7
   ```

3. **Watch dashboard switch** from mock to real data automatically!

---

**Dashboard is ready! Open http://localhost:8080 in your browser** 🚀

