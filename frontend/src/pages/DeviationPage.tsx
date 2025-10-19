import { motion } from 'framer-motion';
import { useState } from 'react';

interface SimulationResult {
  deviationDistance: number;
  timeLost: number;
  recoveryTime: number;
  optimalPath: string;
  status: 'analyzing' | 'complete';
}

export default function DeviationPage() {
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [progress, setProgress] = useState(0);

  const handleSimulate = () => {
    setIsSimulating(true);
    setSimulationResult({
      deviationDistance: 0,
      timeLost: 0,
      recoveryTime: 0,
      optimalPath: '',
      status: 'analyzing'
    });
    setProgress(0);

    // Simulate HPC computation with progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 10;
      });
    }, 100);

    // Simulate HPC lookup with realistic timing
    setTimeout(() => {
      clearInterval(progressInterval);
      setProgress(100);

      // Simulate HPC database lookup results
      setSimulationResult({
        deviationDistance: 2.0,
        timeLost: 0.142,
        recoveryTime: 11.7,
        optimalPath: 'Tight apex, gradual rejoin',
        status: 'complete'
      });

      setTimeout(() => {
        setIsSimulating(false);
      }, 500);
    }, 1200);
  };

  return (
    <div className="container" style={{ padding: '4rem 2rem', maxWidth: '1200px' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: '3rem' }}
      >
        <h1 style={{ fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', marginBottom: '1rem' }}>
          Interactive Deviation Recovery
        </h1>
        <p style={{ fontSize: '1.125rem', color: 'var(--text-tertiary)' }}>
          Simulate driver going off-line and watch HPC find optimal recovery
        </p>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}
        >
          <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>Traditional Method</h3>
          <div style={{
            fontSize: '3rem',
            fontWeight: '700',
            marginBottom: '0.5rem',
            color: 'rgba(255, 100, 100, 0.9)',
          }}>
            6-8s
          </div>
          <p style={{ color: 'var(--text-muted)' }}>
            Physics simulation delay
          </p>
          <ul style={{ marginTop: '1.5rem', listStyle: 'none', padding: 0, fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>
            <li style={{ marginBottom: '0.5rem' }}>❌ Slow computation</li>
            <li style={{ marginBottom: '0.5rem' }}>❌ Not real-time viable</li>
            <li>❌ Complex calculations</li>
          </ul>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass"
          style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', border: '1px solid rgba(220, 38, 38, 0.3)' }}
        >
          <h3 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>HPC Method</h3>
          <div style={{
            fontSize: '3rem',
            fontWeight: '700',
            marginBottom: '0.5rem',
            background: 'var(--primary-gradient)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            11.7ms
          </div>
          <p style={{ color: 'var(--text-muted)' }}>
            Database lookup time
          </p>
          <ul style={{ marginTop: '1.5rem', listStyle: 'none', padding: 0, fontSize: '0.875rem', color: 'rgba(220, 38, 38, 0.9)' }}>
            <li style={{ marginBottom: '0.5rem' }}>✓ Instant response</li>
            <li style={{ marginBottom: '0.5rem' }}>✓ Real-time decisions</li>
            <li>✓ Pre-computed paths</li>
          </ul>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass"
        style={{ padding: '3rem', borderRadius: 'var(--radius-lg)' }}
      >
        <h2 style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>Deviation Scenario: Turn 6</h2>

        <div style={{
          minHeight: '300px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(0, 0, 0, 0.2)',
          borderRadius: 'var(--radius-md)',
          padding: '2rem',
          marginBottom: '2rem',
        }}>
          <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', textAlign: 'center' }}>
            Driver goes 2 meters wide at Turn 6
          </p>

          {isSimulating ? (
            <div style={{ textAlign: 'center', width: '100%' }}>
              <div className="loader-spinner" style={{ margin: '0 auto 1rem' }} />
              <p style={{ color: 'var(--text-tertiary)', marginBottom: '1rem' }}>
                Computing optimal recovery path...
              </p>
              <div style={{
                width: '100%',
                maxWidth: '300px',
                height: '4px',
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '2px',
                margin: '0 auto',
                overflow: 'hidden',
              }}>
                <div style={{
                  width: `${progress}%`,
                  height: '100%',
                  background: 'var(--primary-gradient)',
                  borderRadius: '2px',
                  transition: 'width 0.1s linear',
                }} />
              </div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                {progress}% complete
              </p>
            </div>
          ) : simulationResult && simulationResult.status === 'complete' ? (
            <div style={{ width: '100%', textAlign: 'left' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1.5rem',
                marginBottom: '1.5rem'
              }}>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
                    Deviation Distance
                  </div>
                  <div style={{ fontSize: '2rem', fontWeight: '700', color: '#ffffff' }}>
                    {simulationResult.deviationDistance}m
                  </div>
                </div>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
                    Time Lost
                  </div>
                  <div style={{ fontSize: '2rem', fontWeight: '700', color: '#f59e0b' }}>
                    {simulationResult.timeLost.toFixed(3)}s
                  </div>
                </div>
                <div style={{ padding: '1rem', background: 'rgba(220, 38, 38, 0.1)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(220, 38, 38, 0.3)' }}>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
                    HPC Recovery Time
                  </div>
                  <div style={{
                    fontSize: '2rem',
                    fontWeight: '700',
                    background: 'var(--primary-gradient)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}>
                    {simulationResult.recoveryTime}ms
                  </div>
                </div>
              </div>
              <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
                  Optimal Recovery Path
                </div>
                <div style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>
                  {simulationResult.optimalPath}
                </div>
              </div>
              <div style={{
                marginTop: '1rem',
                padding: '1rem',
                background: 'rgba(34, 197, 94, 0.1)',
                border: '1px solid rgba(34, 197, 94, 0.3)',
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem'
              }}>
                <div style={{ fontSize: '1.5rem' }}>✓</div>
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#22c55e' }}>
                    HPC Advantage
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>
                    Traditional method: 6-8s delay • HPC method: 11.7ms (500x faster)
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🏎️</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                Click simulate to test HPC recovery
              </p>
            </div>
          )}
        </div>

        <button
          onClick={handleSimulate}
          disabled={isSimulating}
          style={{
            width: '100%',
            padding: '1rem 2rem',
            fontSize: '1rem',
            fontWeight: '600',
            color: '#ffffff',
            background: isSimulating ? 'rgba(220, 38, 38, 0.3)' : 'var(--primary-gradient)',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            cursor: isSimulating ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s ease',
          }}
          onMouseEnter={(e) => {
            if (!isSimulating) {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 10px 30px rgba(220, 38, 38, 0.3)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isSimulating) {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }
          }}
        >
          {isSimulating ? 'Simulating...' : 'Run Deviation Simulation'}
        </button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass"
        style={{ padding: '2rem', borderRadius: 'var(--radius-lg)', marginTop: '2rem' }}
      >
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Recovery Process</h3>
        <div style={{ display: 'grid', gap: '1rem' }}>
          {[
            { step: '1', title: 'Detect Deviation', desc: 'System identifies 2m deviation at Turn 6' },
            { step: '2', title: 'Query Database', desc: 'Lookup pre-computed scenarios in 11.7ms' },
            { step: '3', title: 'Optimal Path', desc: 'Retrieve best recovery trajectory' },
            { step: '4', title: 'Execute', desc: 'Guide driver back to racing line' },
          ].map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              style={{
                display: 'flex',
                gap: '1rem',
                padding: '1rem',
                background: 'rgba(255, 255, 255, 0.02)',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: 'var(--primary-gradient)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '700',
                flexShrink: 0,
              }}>
                {item.step}
              </div>
              <div>
                <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{item.title}</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>{item.desc}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
