import { motion } from 'framer-motion';

export default function ExamplesPage() {
  const examples = [
    {
      title: 'Example 1: Mid-Race Deviation Recovery',
      scenario: 'Lap 34, driver defends against overtake at Turn 6, goes 3.2m off optimal line',
      traditional: {
        steps: ['Detect deviation: +0.5s', 'Compute optimal recovery: +6.2s', 'Radio to driver: +1.1s'],
        total: '7.8 seconds',
        result: 'Driver already made instinctive decision',
      },
      hpc: {
        steps: ['Detect deviation: +0.5s', 'HPC database lookup: +0.011s (11ms!)', 'Radio to driver: +0.8s'],
        total: '1.3 seconds',
        strategy: 'Short-shift to 5th, apex 142 km/h, full throttle at curb exit',
        result: 'Time loss minimized: +0.14s instead of +0.6s → Saved 0.46 seconds',
      },
      gradient: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)',
    },
    {
      title: 'Example 2: Dynamic Tire Strategy',
      scenario: 'Lap 18, unexpected rain in Sector 2, need to decide pit strategy',
      traditional: {
        steps: ['Engineer: "We need to run scenarios..."', 'Driver: "I need an answer NOW!"'],
        total: '15+ seconds',
        result: 'Delayed pit decision, loses 2 positions',
      },
      hpc: {
        steps: ['Match: Scenario #23,487 (98.7% match)', 'Optimal: Pit lap 19 for intermediates', 'Expected: P3 → P5 (pit) → P2 (by lap 25)'],
        total: '8ms',
        strategy: 'Box this lap, intermediates, plus-2 fuel',
        result: 'Perfect pit timing, gains P2 by lap 25',
      },
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    },
    {
      title: 'Example 3: Multi-Car Battle Strategy',
      scenario: 'Lap 45, P4 chasing P3 (1.2s gap), P5 closing (0.8s behind)',
      traditional: {
        steps: ['Engineer analyzes: DRS zones, tire delta, fuel loads...', 'Time required: 15+ seconds'],
        total: '15+ seconds',
        result: 'Generic advice, missed optimal overtake window',
      },
      hpc: {
        steps: ['Match: Scenario #41,293', 'Defend from P5 for 2 laps (old tires will fade)', 'Attack P3 at Turn 6 lap 47 (tire advantage peaks)'],
        total: '12ms',
        strategy: 'Defend 2 laps, attack Turn 6 lap 47',
        result: 'Executes perfectly, finishes P3',
      },
      gradient: 'linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%)',
    },
    {
      title: 'Example 4: Qualifying Hot Lap Optimization',
      scenario: 'Final Q3 run, driver on provisional pole by 0.05s, one lap to improve',
      traditional: {
        steps: ['Engineer: "Just copy your previous lap"', 'Driver repeats same line'],
        total: 'N/A',
        result: 'Improves by 0.02s → P2 on grid',
      },
      hpc: {
        steps: ['53,847 pre-computed lines analyzed (scalable to millions)', 'Turn 1: +2m wider, apex 2 km/h faster', 'Turn 6: Sacrifice 0.1s for better exit', 'Turn 15: Late apex, +4 km/h to finish'],
        total: '<10ms',
        strategy: 'Turn 1 wider plus-two, hairpin late apex plus-four exit',
        result: 'Predicted: -0.18s → Actual: -0.16s → Secures pole position',
      },
      gradient: 'linear-gradient(135deg, #dc2626 0%, #7f1d1d 100%)',
    },
  ];

  return (
    <div className="container" style={{ padding: '4rem 2rem', maxWidth: '1200px' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: '3rem' }}
      >
        <h1 style={{ fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', marginBottom: '1rem' }}>
          Real-Time Decision Examples
        </h1>
        <p style={{ fontSize: '1.125rem', color: 'var(--text-tertiary)' }}>
          HPC-powered race strategy scenarios and live decision making
        </p>
      </motion.div>

      <div style={{ display: 'grid', gap: '2rem' }}>
        {examples.map((example, index) => (
          <motion.div
            key={example.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass"
            style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}
          >
            <h3 style={{
              fontSize: '1.5rem',
              marginBottom: '1rem',
              background: example.gradient,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              {example.title}
            </h3>

            <div style={{
              padding: '1rem',
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: '1.5rem',
              borderLeft: '3px solid rgba(220, 38, 38, 0.5)',
            }}>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem', fontWeight: '600' }}>
                Scenario:
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem' }}>
                {example.scenario}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
              <div style={{
                padding: '1.5rem',
                background: 'rgba(255, 100, 100, 0.05)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid rgba(255, 100, 100, 0.2)',
              }}>
                <div style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: 'rgba(255, 100, 100, 0.9)' }}>
                  Traditional System
                </div>
                <ul style={{ listStyle: 'none', padding: 0, fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '1rem' }}>
                  {example.traditional.steps.map((step, i) => (
                    <li key={i} style={{ marginBottom: '0.5rem' }}>• {step}</li>
                  ))}
                </ul>
                <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                  <strong style={{ color: 'var(--text-secondary)' }}>Total:</strong> {example.traditional.total}
                </div>
                <div style={{ fontSize: '0.875rem', color: 'rgba(255, 100, 100, 0.8)' }}>
                  <strong>Result:</strong> {example.traditional.result}
                </div>
              </div>

              <div style={{
                padding: '1.5rem',
                background: 'rgba(220, 38, 38, 0.1)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid rgba(220, 38, 38, 0.3)',
              }}>
                <div style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: 'rgba(220, 38, 38, 0.9)' }}>
                  HPC System
                </div>
                <ul style={{ listStyle: 'none', padding: 0, fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '1rem' }}>
                  {example.hpc.steps.map((step, i) => (
                    <li key={i} style={{ marginBottom: '0.5rem' }}>• {step}</li>
                  ))}
                </ul>
                <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                  <strong style={{ color: 'var(--text-secondary)' }}>Total:</strong> {example.hpc.total}
                </div>
                <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                  <strong>Strategy:</strong> "{example.hpc.strategy}"
                </div>
                <div style={{ fontSize: '0.875rem', color: '#22c55e' }}>
                  <strong>Result:</strong> {example.hpc.result}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass"
        style={{ padding: '3rem', borderRadius: 'var(--radius-lg)', marginTop: '3rem' }}
      >
        <h2 style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>Business Value</h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
          <div>
            <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              For F1 Teams
            </h3>
            <ul style={{ listStyle: 'none', padding: 0, color: 'var(--text-tertiary)', fontSize: '0.9375rem' }}>
              <li style={{ marginBottom: '0.5rem' }}>• Competitive advantage through faster decisions</li>
              <li style={{ marginBottom: '0.5rem' }}>• Real-time strategy optimization</li>
              <li style={{ marginBottom: '0.5rem' }}>• Reduced driver cognitive load</li>
              <li>• Data-driven performance gains</li>
            </ul>
          </div>

          <div>
            <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              For Racing Industry
            </h3>
            <ul style={{ listStyle: 'none', padding: 0, color: 'var(--text-tertiary)', fontSize: '0.9375rem' }}>
              <li style={{ marginBottom: '0.5rem' }}>• Scalable to other racing series</li>
              <li style={{ marginBottom: '0.5rem' }}>• Training tool for drivers</li>
              <li style={{ marginBottom: '0.5rem' }}>• Enhanced broadcast insights</li>
              <li>• Fan engagement opportunities</li>
            </ul>
          </div>

          <div>
            <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              Technology Impact
            </h3>
            <ul style={{ listStyle: 'none', padding: 0, color: 'var(--text-tertiary)', fontSize: '0.9375rem' }}>
              <li style={{ marginBottom: '0.5rem' }}>• Demonstrates HPC applications</li>
              <li style={{ marginBottom: '0.5rem' }}>• Real-time AI decision making</li>
              <li style={{ marginBottom: '0.5rem' }}>• Edge computing potential</li>
              <li>• Future autonomous racing</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
