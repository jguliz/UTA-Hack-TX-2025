import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Navigation() {
  const location = useLocation();

  const links = [
    { path: '/', label: 'Overview' },
    { path: '/racing-line', label: 'Racing Line' },
    { path: '/hpc-stats', label: 'HPC Stats' },
    { path: '/deviation', label: 'Deviation Recovery' },
    { path: '/examples', label: 'Live Examples' },
  ];

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: '#0f0f0f',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1.25rem 2rem',
          maxWidth: '1200px',
          margin: '0 auto',
        }}
      >
        {/* Logo Section */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <h1
            style={{
              fontSize: '1.25rem',
              fontWeight: '800',
              background: 'linear-gradient(135deg, #ffffff, #888888)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              margin: 0,
            }}
          >
            F1 HPC Demo
          </h1>
        </Link>

        {/* Navigation Links */}
        <div style={{ display: 'flex', gap: '0.25rem', alignItems: 'center' }}>
          {links.map((link) => {
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                style={{
                  fontSize: '0.9rem',
                  fontWeight: '500',
                  color: isActive ? '#ffffff' : 'rgba(255, 255, 255, 0.6)',
                  textDecoration: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '8px',
                  background: 'transparent',
                  transition: 'all 0.3s ease',
                  position: 'relative',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = '#ffffff';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = 'rgba(255, 255, 255, 0.6)';
                  }
                }}
              >
                {link.label}
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    style={{
                      position: 'absolute',
                      bottom: '0',
                      left: '1rem',
                      right: '1rem',
                      height: '2px',
                      background: 'linear-gradient(90deg, #dc2626, #991b1b)',
                      borderRadius: '2px',
                    }}
                  />
                )}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
