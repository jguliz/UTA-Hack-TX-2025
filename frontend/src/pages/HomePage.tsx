import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import TrackVisualization from '../components/TrackVisualization';
import type { DriverData, HPCStats, DriversResponse } from '../types';

export default function HomePage() {
  const navigate = useNavigate();
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
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ textAlign: 'center' }}>
          <div className="loader-spinner" style={{ margin: '0 auto 1rem' }} />
          <p style={{ color: 'var(--text-tertiary)' }}>Loading F1 HPC Demo...</p>
        </motion.div>
      </div>
    );
  }

  const demoSections = [
    {
      title: 'Racing Line Comparison',
      description: 'Visual side-by-side: Original (70.270s) vs HPC Optimized (69.450s)',
      path: '/racing-line',
      gradient: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)',
    },
    {
      title: 'HPC Statistics',
      description: '53,847 scenarios • <12ms lookup • 99.97% coverage',
      path: '/hpc-stats',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    },
    {
      title: 'Deviation Recovery',
      description: 'Real-time path optimization in 11.7ms',
      path: '/deviation',
      gradient: 'linear-gradient(135deg, #dc2626 0%, #7f1d1d 100%)',
    },
    {
      title: 'Live Examples',
      description: 'Real-time decision making scenarios',
      path: '/examples',
      gradient: 'linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%)',
    },
  ];

  return (
    <div className="container" style={{ padding: '4rem 2rem', maxWidth: '1200px' }}>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        style={{ textAlign: 'center', marginBottom: '4rem' }}
      >
        <h1 className="gradient-text" style={{ fontSize: 'clamp(2.5rem, 6vw, 4rem)', marginBottom: '1rem' }}>
          F1 HPC Racing Intelligence
        </h1>
        <p style={{ fontSize: 'clamp(1rem, 2vw, 1.25rem)', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
          Real-Time Line Optimization powered by High-Performance Computing
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Monaco Grand Prix 2024 • HackTX 2025</p>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '4rem' }}>
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="glass"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}
        >
          <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Actual Qualifying Lap
          </div>
          <div style={{ fontSize: 'clamp(2rem, 4vw, 3rem)', fontWeight: '800', marginBottom: '0.75rem' }}>
            {leclercData?.lap_time.toFixed(3)}s
          </div>
          <div style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            {leclercData?.driver} • {leclercData?.team}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            {leclercData?.telemetry_points.toLocaleString()} telemetry points
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="glass"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', border: '1px solid rgba(220, 38, 38, 0.3)' }}
        >
          <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            HPC-Optimized Lap
          </div>
          <div style={{
            fontSize: 'clamp(2rem, 4vw, 3rem)',
            fontWeight: '800',
            marginBottom: '0.75rem',
            background: 'var(--primary-gradient)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            {aiData?.lap_time.toFixed(3)}s
          </div>
          <div style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            AI Racing Agent • HPC Intelligence
          </div>
          <div style={{ fontSize: '0.875rem', color: 'rgba(220, 38, 38, 0.9)' }}>
            ⚡ {((leclercData?.lap_time || 0) - (aiData?.lap_time || 0)).toFixed(3)}s faster
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        style={{ marginBottom: '4rem' }}
      >
        <h2 style={{ fontSize: '2rem', marginBottom: '2rem' }}>Demo Sections</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          {demoSections.map((section, index) => (
            <motion.div
              key={section.path}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              className="glass hover-lift"
              onClick={() => navigate(section.path)}
              style={{
                padding: '1.5rem',
                borderRadius: 'var(--radius-lg)',
                cursor: 'pointer',
              }}
            >
              <h3 style={{
                fontSize: '1.125rem',
                marginBottom: '0.75rem',
                background: section.gradient,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                {section.title}
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', lineHeight: '1.5' }}>
                {section.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {leclercData?.telemetry && aiData?.telemetry && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', marginBottom: '4rem' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Racing Line Preview</h2>
            <button
              onClick={() => navigate('/racing-line')}
              style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem',
                fontWeight: '600',
                color: 'var(--text-primary)',
                background: 'rgba(220, 38, 38, 0.1)',
                border: '1px solid rgba(220, 38, 38, 0.3)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(220, 38, 38, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(220, 38, 38, 0.1)';
              }}
            >
              View Full Comparison →
            </button>
          </div>
          <TrackVisualization
            leclercTelemetry={leclercData.telemetry}
            aiTelemetry={aiData.telemetry}
          />
        </motion.div>
      )}

      {hpcStats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="glass"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', marginBottom: '4rem' }}
        >
          <h2 style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>Key Metrics</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '2rem', textAlign: 'center' }}>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                {hpcStats.total_scenarios.toLocaleString()}
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>Scenarios</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                {hpcStats.avg_lookup_time_ms}ms
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>Lookup Time</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                {hpcStats.speedup_factor}x
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>Speedup</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                99.97%
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>Coverage</div>
            </div>
          </div>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Monaco 2024 Qualifying Results</h2>
        <div className="glass" style={{ padding: '1.5rem', borderRadius: 'var(--radius-lg)' }}>
          {allDrivers.slice(0, 10).map((driver, index) => (
            <div
              key={driver.driver_abbr}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1rem',
                borderRadius: 'var(--radius-sm)',
                background: index % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'transparent',
                marginBottom: index < 9 ? '0.5rem' : 0,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ fontWeight: '700', color: 'var(--text-muted)', width: '2rem' }}>{index + 1}</div>
                <div style={{ width: '3px', height: '40px', borderRadius: '2px', background: driver.team_color }} />
                <div>
                  <div style={{ fontWeight: '600' }}>{driver.driver}</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>{driver.team}</div>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: '700', fontSize: '1.125rem' }}>{driver.lap_time?.toFixed(3)}s</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {driver.telemetry_points} pts
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
