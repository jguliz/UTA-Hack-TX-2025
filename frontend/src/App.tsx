import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import RacingLinePage from './pages/RacingLinePage';
import HPCStatsPage from './pages/HPCStatsPage';
import DeviationPage from './pages/DeviationPage';
import ExamplesPage from './pages/ExamplesPage';
import './App.css';
import './styles/globals.css';

function App() {
  return (
    <Router>
      <div className="app">
        {/* Background effects */}
        <div className="app-background">
          <div className="bg-grid" />
          <div className="bg-gradient-overlay" />
        </div>

        {/* Navigation */}
        <Navigation />

        {/* Main content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/racing-line" element={<RacingLinePage />} />
            <Route path="/hpc-stats" element={<HPCStatsPage />} />
            <Route path="/deviation" element={<DeviationPage />} />
            <Route path="/examples" element={<ExamplesPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="app-footer">
          <div className="footer-content">
            <div className="footer-section">
              <h4>F1 HPC Demo</h4>
              <p>Real-Time Racing Intelligence</p>
            </div>
            <div className="footer-section">
              <h5>Demo Sections</h5>
              <a href="/racing-line">Racing Line</a>
              <a href="/hpc-stats">HPC Stats</a>
              <a href="/deviation">Deviation Recovery</a>
              <a href="/examples">Live Examples</a>
            </div>
            <div className="footer-section">
              <h5>Technology</h5>
              <p style={{ fontSize: '0.875rem', lineHeight: '1.6' }}>
                Built with React, TypeScript, FastF1 API, and High-Performance Computing
              </p>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 HackTX Demo. Monaco Grand Prix 2024 Data.</p>
            <p>Powered by FastF1 API</p>
          </div>
        </footer>

        {/* Global styles */}
        <style>{`
          .loader-spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top-color: #dc2626;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }

          .app-footer {
            position: relative;
            z-index: 1;
            background: #0f0f0f;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding: 3rem 0 2rem;
            margin-top: 4rem;
          }

          .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
          }

          .footer-section h4 {
            font-size: 1.25rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #ffffff, #888888);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
          }

          .footer-section h5 {
            font-size: 1rem;
            margin-bottom: 1rem;
            color: rgba(255, 255, 255, 0.9);
          }

          .footer-section p {
            color: rgba(255, 255, 255, 0.6);
            line-height: 1.6;
          }

          .footer-section a {
            display: block;
            color: rgba(255, 255, 255, 0.6);
            text-decoration: none;
            padding: 0.25rem 0;
            transition: color 0.3s ease;
          }

          .footer-section a:hover {
            color: #ffffff;
          }

          .footer-bottom {
            text-align: center;
            padding: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 2rem;
            color: rgba(255, 255, 255, 0.4);
          }

          .footer-bottom p {
            margin: 0.25rem 0;
            font-size: 0.875rem;
          }

          @media (max-width: 768px) {
            .main-content {
              padding-top: 70px;
            }

            .footer-content {
              grid-template-columns: 1fr;
              text-align: center;
            }
          }
        `}</style>
      </div>
    </Router>
  );
}

export default App;
