import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import TrackVisualization from '../components/TrackVisualization';
import type { DriverData } from '../types';

export default function RacingLinePage() {
  const [leclercData, setLeclercData] = useState<DriverData | null>(null);
  const [aiData, setAIData] = useState<DriverData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiService.getLeclercTelemetry(),
      apiService.getAIOptimalTelemetry(),
    ]).then(([leclerc, ai]) => {
      setLeclercData(leclerc);
      setAIData(ai);
      setLoading(false);
    }).catch(err => {
      console.error('Error loading data:', err);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="loader-spinner" />
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '4rem 2rem', maxWidth: '1200px' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: '3rem' }}
      >
        <h1 style={{ fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', marginBottom: '1rem' }}>
          Racing Line Comparison
        </h1>
        <p style={{ fontSize: '1.125rem', color: 'var(--text-tertiary)' }}>
          Visual side-by-side: Original (70.270s) vs HPC Optimized (69.450s)
        </p>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="glass"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}
        >
          <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>Original Line</h3>
          <div style={{
            fontSize: '3rem',
            fontWeight: '700',
            marginBottom: '0.5rem',
            background: 'linear-gradient(135deg, #ffffff, #888888)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            {leclercData?.lap_time.toFixed(3)}s
          </div>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
            {leclercData?.driver} • {leclercData?.team}
          </p>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>
            <div>{leclercData?.telemetry_points.toLocaleString()} telemetry points</div>
            <div>Monaco Grand Prix 2024 Qualifying</div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', border: '1px solid rgba(220, 38, 38, 0.3)' }}
        >
          <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>HPC Optimized</h3>
          <div style={{
            fontSize: '3rem',
            fontWeight: '700',
            marginBottom: '0.5rem',
            background: 'var(--primary-gradient)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            {aiData?.lap_time.toFixed(3)}s
          </div>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
            AI Racing Agent • HPC Optimization
          </p>
          <div style={{ fontSize: '0.875rem', color: 'rgba(220, 38, 38, 0.9)' }}>
            <div>⚡ {((leclercData?.lap_time || 0) - (aiData?.lap_time || 0)).toFixed(3)}s faster</div>
            <div>Computed from 53,847 scenarios</div>
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass"
        style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}
      >
        <h3 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Monaco Circuit - Racing Line Comparison</h3>
        {leclercData?.telemetry && aiData?.telemetry ? (
          <TrackVisualization
            leclercTelemetry={leclercData.telemetry}
            aiTelemetry={aiData.telemetry}
          />
        ) : (
          <div style={{
            minHeight: '400px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(0, 0, 0, 0.2)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-muted)',
          }}>
            <div style={{ textAlign: 'center' }}>
              <div className="loader-spinner" style={{ margin: '0 auto 1rem' }} />
              <p>Loading telemetry data...</p>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
