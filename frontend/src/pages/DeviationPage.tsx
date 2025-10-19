import { motion } from 'framer-motion';
import { useState } from 'react';

export default function DeviationPage() {
  const [isSimulating, setIsSimulating] = useState(false);

  const handleSimulate = () => {
    setIsSimulating(true);
    setTimeout(() => setIsSimulating(false), 2000);
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
            <div style={{ textAlign: 'center' }}>
              <div className="loader-spinner" style={{ margin: '0 auto 1rem' }} />
              <p style={{ color: 'var(--text-tertiary)' }}>Computing optimal recovery path...</p>
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
