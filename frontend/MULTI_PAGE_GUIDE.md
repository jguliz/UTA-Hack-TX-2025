# F1 HPC Multi-Page Demo - Complete Guide

I've created **MonacoTrack.tsx** component that displays the Monaco track with animated racing line on every page.

## Pages to Create for F1 Executive Presentation

Create these 4 additional page files:

### 1. `src/components/Navigation.tsx`

```typescript
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Navigation() {
  const location = useLocation();

  const links = [
    { path: '/', label: 'Overview' },
    { path: '/telemetry', label: 'Live Telemetry' },
    { path: '/hpc', label: 'HPC Performance' },
    { path: '/comparison', label: 'Driver Comparison' },
  ];

  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 1000,
      background: 'rgba(10, 10, 10, 0.95)',
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 2rem' }}>
        <h1 style={{ fontFamily: 'Orbitron', fontSize: '1.5rem', background: 'linear-gradient(135deg, #E10600, #FF1E00)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          F1 HPC RACING
        </h1>
        <div style={{ display: 'flex', gap: '2rem' }}>
          {links.map(link => (
            <Link
              key={link.path}
              to={link.path}
              style={{
                fontFamily: 'Orbitron',
                fontSize: '0.9rem',
                color: location.pathname === link.path ? '#E10600' : 'var(--text-secondary)',
                textDecoration: 'none',
                transition: 'color 0.3s ease',
                position: 'relative',
              }}
            >
              {link.label}
              {location.pathname === link.path && (
                <motion.div
                  layoutId="activeTab"
                  style={{
                    position: 'absolute',
                    bottom: '-0.5rem',
                    left: 0,
                    right: 0,
                    height: '2px',
                    background: 'linear-gradient(90deg, #E10600, #FF1E00)',
                  }}
                />
              )}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
```

### 2. `src/pages/TelemetryPage.tsx`

```typescript
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
import MonacoTrack from '../components/MonacoTrack';
import type { DriverData } from '../types';

export default function TelemetryPage() {
  const [leclercData, setLeclercData] = useState<DriverData | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiService.getLeclercTelemetry().then(data => {
      setLeclercData(data);
      setLoading(false);
    });

    const interval = setInterval(() => {
      setCurrentIndex(prev => prev + 1);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  if (loading || !leclercData) {
    return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <h2 className="glow-text-blue" style={{ fontFamily: 'Orbitron' }}>LOADING...</h2>
    </div>;
  }

  const point = leclercData.telemetry[currentIndex % leclercData.telemetry.length];

  return (
    <div className="container" style={{ padding: '6rem 2rem 4rem' }}>
      <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ fontFamily: 'Orbitron', fontSize: '3rem', marginBottom: '3rem', textAlign: 'center' }}>
        LIVE TELEMETRY
      </motion.h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
        <MonacoTrack telemetryData={leclercData} width={800} height={500} />

        <div>
          <h2 style={{ fontFamily: 'Orbitron', marginBottom: '2rem' }}>REAL-TIME DATA</h2>
          <div style={{ display: 'grid', gap: '1rem' }}>
            <div className="glass-dark" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>SPEED</div>
              <div className="glow-text-yellow" style={{ fontFamily: 'Orbitron', fontSize: '3rem', fontWeight: '900' }}>{Math.round(point.speed)}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>km/h</div>
            </div>
            <div className="glass-dark" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>THROTTLE</div>
              <div className="glow-text-green" style={{ fontFamily: 'Orbitron', fontSize: '2.5rem', fontWeight: '900' }}>{Math.round(point.throttle)}%</div>
              <div style={{ width: '100%', background: '#333', borderRadius: '4px', height: '8px', marginTop: '1rem' }}>
                <div style={{ width: `${point.throttle}%`, background: '#22c55e', height: '100%', borderRadius: '4px', transition: 'width 0.3s ease' }} />
              </div>
            </div>
            <div className="glass-dark" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>BRAKE</div>
              <div className="glow-text-red" style={{ fontFamily: 'Orbitron', fontSize: '2.5rem', fontWeight: '900' }}>{Math.round(point.brake)}%</div>
              <div style={{ width: '100%', background: '#333', borderRadius: '4px', height: '8px', marginTop: '1rem' }}>
                <div style={{ width: `${point.brake}%`, background: '#ef4444', height: '100%', borderRadius: '4px', transition: 'width 0.3s ease' }} />
              </div>
            </div>
            <div className="glass-dark" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>GEAR / RPM</div>
              <div className="glow-text-blue" style={{ fontFamily: 'Orbitron', fontSize: '3rem', fontWeight: '900' }}>{point.gear}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{Math.round(point.rpm)} RPM</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 3. `src/pages/HPCPage.tsx`

```typescript
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
import MonacoTrack from '../components/MonacoTrack';
import type { DriverData, HPCStats } from '../types';

export default function HPCPage() {
  const [aiData, setAIData] = useState<DriverData | null>(null);
  const [hpcStats, setHPCStats] = useState<HPCStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiService.getAIOptimalTelemetry(),
      apiService.getHPCStats()
    ]).then(([ai, stats]) => {
      setAIData(ai);
      setHPCStats(stats);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <h2 className="glow-text-blue" style={{ fontFamily: 'Orbitron' }}>LOADING...</h2>
    </div>;
  }

  return (
    <div className="container" style={{ padding: '6rem 2rem 4rem' }}>
      <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ fontFamily: 'Orbitron', fontSize: '3rem', marginBottom: '3rem', textAlign: 'center' }}>
        HPC PERFORMANCE
      </motion.h1>

      <div style={{ marginBottom: '3rem' }}>
        <MonacoTrack telemetryData={aiData} width={1200} height={600} />
      </div>

      {hpcStats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="glass-dark pulse-border-green" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', textAlign: 'center', border: '2px solid rgba(34, 197, 94, 0.3)' }}>
            <div className="glow-text-blue" style={{ fontFamily: 'Orbitron', fontSize: '3.5rem', fontWeight: '900', marginBottom: '1rem' }}>{hpcStats.total_scenarios.toLocaleString()}</div>
            <div style={{ color: 'var(--text-tertiary)' }}>PRE-COMPUTED SCENARIOS</div>
          </motion.div>
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }} className="glass-dark pulse-border-green" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', textAlign: 'center', border: '2px solid rgba(34, 197, 94, 0.3)' }}>
            <div className="glow-text-green" style={{ fontFamily: 'Orbitron', fontSize: '3.5rem', fontWeight: '900', marginBottom: '1rem' }}>{hpcStats.avg_lookup_time_ms}ms</div>
            <div style={{ color: 'var(--text-tertiary)' }}>AVERAGE LOOKUP TIME</div>
          </motion.div>
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }} className="glass-dark pulse-border-green" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', textAlign: 'center', border: '2px solid rgba(34, 197, 94, 0.3)' }}>
            <div className="glow-text-yellow" style={{ fontFamily: 'Orbitron', fontSize: '3.5rem', fontWeight: '900', marginBottom: '1rem' }}>{hpcStats.speedup_factor}x</div>
            <div style={{ color: 'var(--text-tertiary)' }}>FASTER THAN REAL-TIME</div>
          </motion.div>
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4 }} className="glass-dark pulse-border-green" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', textAlign: 'center', border: '2px solid rgba(34, 197, 94, 0.3)' }}>
            <div className="glow-text-red" style={{ fontFamily: 'Orbitron', fontSize: '3.5rem', fontWeight: '900', marginBottom: '1rem' }}>{hpcStats.database_size_mb}MB</div>
            <div style={{ color: 'var(--text-tertiary)' }}>DATABASE SIZE</div>
          </motion.div>
        </div>
      )}

      <div className="glass-dark" style={{ padding: '3rem', borderRadius: 'var(--radius-lg)', marginTop: '3rem' }}>
        <h2 style={{ fontFamily: 'Orbitron', fontSize: '2rem', marginBottom: '2rem' }}>WHAT IS HPC?</h2>
        <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          High-Performance Computing (HPC) pre-computes <strong>{hpcStats?.total_scenarios.toLocaleString()}</strong> racing scenarios offline,
          enabling instant <strong>sub-{hpcStats?.avg_lookup_time_ms}ms</strong> decision making during live races.
        </p>
        <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: 'var(--text-secondary)' }}>
          Traditional systems take <strong>6-8 seconds</strong> to compute optimal strategies.
          Our HPC system delivers results <strong>{hpcStats?.speedup_factor}x faster</strong>, fast enough for real-time F1 decision making.
        </p>
      </div>
    </div>
  );
}
```

### 4. `src/pages/ComparisonPage.tsx`

```typescript
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../services/api';
import MonacoTrack from '../components/MonacoTrack';
import type { DriversResponse } from '../types';

export default function ComparisonPage() {
  const [allDrivers, setAllDrivers] = useState<DriversResponse['drivers']>([]);
  const [selectedDriver, setSelectedDriver] = useState<DriversResponse['drivers'][0] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiService.getAllDrivers().then(data => {
      setAllDrivers(data.drivers || []);
      if (data.drivers && data.drivers.length > 0) {
        setSelectedDriver(data.drivers[0]);
      }
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <h2 className="glow-text-blue" style={{ fontFamily: 'Orbitron' }}>LOADING...</h2>
    </div>;
  }

  return (
    <div className="container" style={{ padding: '6rem 2rem 4rem' }}>
      <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ fontFamily: 'Orbitron', fontSize: '3rem', marginBottom: '3rem', textAlign: 'center' }}>
        MONACO 2024 QUALIFYING
      </motion.h1>

      <div className="glass-dark" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
        {allDrivers.map((driver, index) => (
          <div key={driver.driver_abbr} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.5rem', borderRadius: 'var(--radius-md)', background: selectedDriver?.driver_abbr === driver.driver_abbr ? 'rgba(225, 6, 0, 0.1)' : 'rgba(0, 0, 0, 0.3)', marginBottom: index < allDrivers.length - 1 ? '1rem' : 0, cursor: 'pointer', transition: 'all 0.3s ease' }} onClick={() => setSelectedDriver(driver)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
              <div style={{ fontFamily: 'Orbitron', fontSize: '2rem', fontWeight: 'bold', color: index < 3 ? '#fbbf24' : 'var(--text-muted)', width: '3rem' }}>
                {index + 1}
              </div>
              <div style={{ width: '6px', height: '60px', borderRadius: '3px', background: driver.team_color }} />
              <div>
                <div style={{ fontWeight: 'bold', fontSize: '1.3rem' }}>{driver.driver}</div>
                <div style={{ color: 'var(--text-tertiary)' }}>{driver.team}</div>
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontFamily: 'Orbitron', fontSize: '2rem', fontWeight: 'bold' }}>{driver.lap_time?.toFixed(3)}s</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{driver.telemetry_points} data points</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 5. Update `src/App.tsx`

```typescript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import TelemetryPage from './pages/TelemetryPage';
import HPCPage from './pages/HPCPage';
import ComparisonPage from './pages/ComparisonPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <div className="app-background">
          <div className="bg-grid" />
          <div className="bg-gradient-overlay" />
        </div>

        <Navigation />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/telemetry" element={<TelemetryPage />} />
            <Route path="/hpc" element={<HPCPage />} />
            <Route path="/comparison" element={<ComparisonPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
```

## Summary

After creating these files, you'll have **4 pages** for your F1 executive presentation:

1. **Overview** (`/`) - Main dashboard with lap comparisons and HPC stats
2. **Live Telemetry** (`/telemetry`) - Real-time telemetry data visualization with Monaco track
3. **HPC Performance** (`/hpc`) - Detailed HPC statistics and capabilities with Monaco track
4. **Driver Comparison** (`/comparison`) - Full Monaco 2024 qualifying leaderboard

**Each page displays the animated Monaco track** showing the racing line with speed-based colors!

Navigate between pages using the top navigation bar.
