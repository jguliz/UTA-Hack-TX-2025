# F1 HPC Racing - React App Setup Guide

## Current Status

✅ **COMPLETED:**
- Vite + React + TypeScript project initialized
- Dependencies installed (framer-motion, react-router-dom)
- TypeScript types defined (`src/types/index.ts`)
- API service layer created (`src/services/api.ts`)
- Global styles ready (`src/styles/globals.css`)

⏳ **REMAINING WORK:**

### 1. Update Vite Config (`vite.config.ts`)

Replace the content with:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      }
    }
  }
})
```

### 2. Update `index.html`

Add Google Fonts for F1 aesthetic:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>F1 HPC Racing Line Optimizer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### 3. Update `src/main.tsx`

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles/globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### 4. Create `src/App.tsx`

```typescript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import HomePage from './pages/HomePage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        {/* Background effects */}
        <div className="app-background">
          <div className="bg-grid" />
          <div className="bg-gradient-overlay" />
        </div>

        {/* Main content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
```

### 5. Create `src/App.css`

```css
.app {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  position: relative;
}

.app-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.01) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.5;
}

.bg-gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at 50% 50%,
    transparent 0%,
    rgba(10, 10, 10, 0.4) 100%
  );
}

.main-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
}
```

### 6. Create `src/pages/HomePage.tsx`

```typescript
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
import type { DriverData, HPCStats, DriversResponse } from '../types';

export default function HomePage() {
  const [leclercData, setLeclercData] = useState<DriverData | null>(null);
  const [aiData, setAIData] = useState<DriverData | null>(null);
  const [hpcStats, setHPCStats] = useState<HPCStats | null>(null);
  const [allDrivers, setAllDrivers] = useState<DriversResponse['drivers']>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiService.getLeclercTelemetry(),
      apiService.getAIOptimalTelemetry(),
      apiService.getHPCStats(),
      apiService.getAllDrivers()
    ]).then(([leclerc, ai, hpc, drivers]) => {
      setLeclercData(leclerc);
      setAIData(ai);
      setHPCStats(hpc);
      setAllDrivers(drivers.drivers || []);
      setLoading(false);
    }).catch(err => {
      console.error('Error loading data:', err);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{ textAlign: 'center' }}
        >
          <h1 className="glow-text-blue" style={{ fontFamily: 'Orbitron', fontSize: '3rem' }}>LOADING</h1>
          <div style={{ marginTop: '2rem', height: '3px', width: '200px', background: '#333', borderRadius: '3px', overflow: 'hidden', margin: '2rem auto' }}>
            <motion.div
              style={{ height: '100%', background: 'linear-gradient(90deg, #E10600, #FF1E00)', width: '100%' }}
              animate={{ x: ['-100%', '100%'] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
            />
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '4rem 2rem' }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        style={{ textAlign: 'center', marginBottom: '4rem' }}
      >
        <h1 className="gradient-text" style={{ fontSize: 'clamp(3rem, 8vw, 6rem)', fontFamily: 'Orbitron', marginBottom: '1rem' }}>
          F1 HPC RACING
        </h1>
        <p style={{ fontSize: 'clamp(1.2rem, 2vw, 1.5rem)', color: 'var(--text-tertiary)', marginBottom: '1rem' }}>
          Real-Time Line Optimization • Monaco Grand Prix 2024
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          POWERED BY FASTF1 API • HACKTX 2025
        </p>
      </motion.div>

      {/* Lap Time Comparison */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '4rem' }}>
        {/* Leclerc */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="glass-dark pulse-border"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', border: '2px solid rgba(225, 6, 0, 0.3)' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: leclercData?.team_color || '#E80020' }} />
            <div>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>{leclercData?.driver}</div>
              <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{leclercData?.team}</div>
            </div>
          </div>
          <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>ACTUAL QUALIFYING LAP</div>
          <div className="glow-text-red" style={{ fontFamily: 'Orbitron', fontSize: 'clamp(2.5rem, 5vw, 4rem)', fontWeight: '900', marginBottom: '0.5rem' }}>
            {leclercData?.lap_time.toFixed(3)}s
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            Monaco 2024 • {leclercData?.telemetry_points} data points
          </div>
        </motion.div>

        {/* HPC Optimized */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="glass-dark pulse-border-green"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', border: '2px solid rgba(34, 197, 94, 0.5)' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'linear-gradient(135deg, #22c55e, #3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>
              🤖
            </div>
            <div>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>AI AGENT</div>
              <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>HPC Racing Intelligence</div>
            </div>
          </div>
          <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>HPC-OPTIMIZED LAP</div>
          <div className="glow-text-green" style={{ fontFamily: 'Orbitron', fontSize: 'clamp(2.5rem, 5vw, 4rem)', fontWeight: '900', marginBottom: '0.5rem' }}>
            {aiData?.lap_time.toFixed(3)}s
          </div>
          <div style={{ color: '#22c55e', fontSize: '0.8rem' }}>
            ✓ {((leclercData?.lap_time || 0) - (aiData?.lap_time || 0)).toFixed(3)}s faster • {hpcStats?.total_scenarios.toLocaleString()} scenarios
          </div>
        </motion.div>
      </div>

      {/* HPC Statistics */}
      {hpcStats && (
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          style={{ marginBottom: '4rem' }}
        >
          <h2 style={{ fontFamily: 'Orbitron', fontSize: '2rem', marginBottom: '2rem' }}>HPC PERFORMANCE</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
            <div className="glass-dark" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div className="glow-text-blue" style={{ fontFamily: 'Orbitron', fontSize: '2.5rem', fontWeight: '900', marginBottom: '0.5rem' }}>
                {hpcStats.total_scenarios.toLocaleString()}
              </div>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>PRE-COMPUTED SCENARIOS</div>
            </div>
            <div className="glass-dark" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div className="glow-text-green" style={{ fontFamily: 'Orbitron', fontSize: '2.5rem', fontWeight: '900', marginBottom: '0.5rem' }}>
                {hpcStats.avg_lookup_time_ms}ms
              </div>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>AVERAGE LOOKUP TIME</div>
            </div>
            <div className="glass-dark" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div className="glow-text-yellow" style={{ fontFamily: 'Orbitron', fontSize: '2.5rem', fontWeight: '900', marginBottom: '0.5rem' }}>
                {hpcStats.speedup_factor}x
              </div>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>FASTER THAN REAL-TIME</div>
            </div>
            <div className="glass-dark" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div className="glow-text-red" style={{ fontFamily: 'Orbitron', fontSize: '2.5rem', fontWeight: '900', marginBottom: '0.5rem' }}>
                {hpcStats.database_size_mb}MB
              </div>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>HPC DATABASE SIZE</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Driver Leaderboard */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.5 }}
      >
        <h2 style={{ fontFamily: 'Orbitron', fontSize: '2rem', marginBottom: '2rem' }}>2024 MONACO QUALIFYING</h2>
        <div className="glass-dark" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
          {allDrivers.slice(0, 10).map((driver, index) => (
            <div
              key={driver.driver_abbr}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1rem',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(0, 0, 0, 0.3)',
                marginBottom: index < 9 ? '0.75rem' : 0,
                transition: 'all 0.3s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ fontFamily: 'Orbitron', fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--text-muted)', width: '2rem' }}>
                  {index + 1}
                </div>
                <div style={{ width: '4px', height: '48px', borderRadius: '2px', background: driver.team_color }} />
                <div>
                  <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{driver.driver}</div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>{driver.team}</div>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontFamily: 'Orbitron', fontSize: '1.5rem', fontWeight: 'bold' }}>
                  {driver.lap_time?.toFixed(3)}s
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                  {driver.telemetry_points} points
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
```

## Running the App

### Terminal 1 - Start Flask Backend:
```bash
cd /Users/joshuagulizia/Documents/GitHub/UTA-Hack-TX-2025
source .venv/bin/activate
python3 app.py
```

### Terminal 2 - Start React Frontend:
```bash
cd /Users/joshuagulizia/Documents/GitHub/UTA-Hack-TX-2025/frontend
npm run dev
```

The app will be available at `http://localhost:3000` and will proxy API requests to Flask on port 8080.

## Next Steps (Optional Enhancements)

1. Add Monaco Track Canvas visualization component
2. Add real-time telemetry dashboard with speed/throttle/brake
3. Add more pages with React Router (Track Analysis, Statistics, etc.)
4. Add more Framer Motion animations
5. Build production bundle with `npm run build`

## For F1 Executive Presentation

The current setup provides a clean, professional demo with:
- Real FastF1 Monaco 2024 data
- Premium F1 aesthetic (Orbitron font, glowing effects)
- Smooth Framer Motion animations
- HPC performance statistics
- Driver leaderboard

This is ready to present!
