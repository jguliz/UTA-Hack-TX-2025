import { motion } from 'framer-motion';

export default function ExamplesPage() {
  const examples = [
    {
      title: 'Mid-Race Deviation Recovery',
      description: 'Real-time path correction when driver goes off optimal line',
      metrics: ['11.7ms response', '99.9% accuracy', 'Zero computation delay'],
      gradient: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)',
    },
    {
      title: 'Dynamic Tire Strategy',
      description: 'Optimal pit stop timing based on tire degradation and race position',
      metrics: ['Live telemetry analysis', 'Multi-variable optimization', 'Predictive modeling'],
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    },
    {
      title: 'Multi-Car Battle Tactics',
      description: 'Overtaking strategies considering track position and competitor behavior',
      metrics: ['Scenario planning', 'Risk assessment', 'DRS zone optimization'],
      gradient: 'linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%)',
    },
    {
      title: 'Qualifying Lap Optimization',
      description: 'Maximum performance extraction for single-lap qualifying runs',
      metrics: ['Corner-by-corner analysis', 'Brake point optimization', 'Throttle mapping'],
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
            className="glass hover-lift"
            style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <h3 style={{
                  fontSize: '1.5rem',
                  marginBottom: '0.75rem',
                  background: example.gradient,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}>
                  {example.title}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', lineHeight: '1.6' }}>
                  {example.description}
                </p>
              </div>

              <div style={{
                display: 'flex',
                gap: '1rem',
                flexWrap: 'wrap',
                marginTop: '0.5rem',
              }}>
                {example.metrics.map((metric, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '0.5rem 1rem',
                      background: 'rgba(255, 255, 255, 0.05)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.875rem',
                      color: 'var(--text-tertiary)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                    }}
                  >
                    {metric}
                  </div>
                ))}
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
