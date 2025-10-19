import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface TelemetryPoint {
  x: number;
  y: number;
  speed: number;
  brake?: number | boolean;
  throttle: number;
}

interface TrackVisualizationProps {
  leclercTelemetry: TelemetryPoint[];
  aiTelemetry: TelemetryPoint[];
  isAnimating?: boolean;
}

export default function TrackVisualization({
  leclercTelemetry,
  aiTelemetry,
  isAnimating = false
}: TrackVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [animationFrame, setAnimationFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // Normalize coordinates to fit canvas
  const normalizeCoordinates = (points: TelemetryPoint[], width: number, height: number) => {
    const allX = points.map(p => p.x);
    const allY = points.map(p => p.y);

    const minX = Math.min(...allX);
    const maxX = Math.max(...allX);
    const minY = Math.min(...allY);
    const maxY = Math.max(...allY);

    const rangeX = maxX - minX;
    const rangeY = maxY - minY;
    const scale = Math.min(width / rangeX, height / rangeY) * 0.85;

    const offsetX = (width - rangeX * scale) / 2;
    const offsetY = (height - rangeY * scale) / 2;

    return points.map(p => ({
      x: (p.x - minX) * scale + offsetX,
      y: (p.y - minY) * scale + offsetY,
      speed: p.speed,
      brake: p.brake,
      throttle: p.throttle,
    }));
  };

  // Draw the track
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !leclercTelemetry.length || !aiTelemetry.length) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, width, height);

    // Normalize both telemetry sets
    const normalizedLeclerc = normalizeCoordinates(leclercTelemetry, width, height);
    const normalizedAI = normalizeCoordinates(aiTelemetry, width, height);

    // Draw Leclerc's line (gray)
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = 3;
    normalizedLeclerc.forEach((point, i) => {
      if (i === 0) {
        ctx.moveTo(point.x, point.y);
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.stroke();

    // Draw AI optimal line (red gradient)
    ctx.beginPath();
    ctx.strokeStyle = '#dc2626';
    ctx.lineWidth = 4;
    normalizedAI.forEach((point, i) => {
      if (i === 0) {
        ctx.moveTo(point.x, point.y);
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.stroke();

    // Draw speed-based coloring for AI line
    normalizedAI.forEach((point, i) => {
      if (i === 0) return;

      const speedRatio = point.speed / 300; // Normalize speed (max ~300 km/h)
      const color = speedRatio > 0.8
        ? `rgba(220, 38, 38, ${0.8 + speedRatio * 0.2})` // Fast = bright red
        : `rgba(245, 158, 11, ${0.6 + speedRatio * 0.4})`; // Slow = amber

      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.moveTo(normalizedAI[i - 1].x, normalizedAI[i - 1].y);
      ctx.lineTo(point.x, point.y);
      ctx.stroke();
    });

    // Draw start/finish line
    if (normalizedLeclerc.length > 0) {
      const start = normalizedLeclerc[0];
      ctx.fillStyle = '#22c55e';
      ctx.beginPath();
      ctx.arc(start.x, start.y, 8, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 12px Inter';
      ctx.fillText('START', start.x + 12, start.y + 5);
    }

    // Draw animated cars if playing
    if (isPlaying && animationFrame < normalizedAI.length) {
      const leclercPos = normalizedLeclerc[Math.min(animationFrame, normalizedLeclerc.length - 1)];
      const aiPos = normalizedAI[animationFrame];

      // Leclerc car (gray)
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.beginPath();
      ctx.arc(leclercPos.x, leclercPos.y, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // AI car (red)
      ctx.fillStyle = '#dc2626';
      ctx.beginPath();
      ctx.arc(aiPos.x, aiPos.y, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  }, [leclercTelemetry, aiTelemetry, animationFrame, isPlaying]);

  // Animation loop
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setAnimationFrame(prev => {
        if (prev >= Math.min(leclercTelemetry.length, aiTelemetry.length) - 1) {
          setIsPlaying(false);
          return 0;
        }
        return prev + 1;
      });
    }, 30); // ~30fps

    return () => clearInterval(interval);
  }, [isPlaying, leclercTelemetry.length, aiTelemetry.length]);

  const handlePlayPause = () => {
    if (animationFrame >= Math.min(leclercTelemetry.length, aiTelemetry.length) - 1) {
      setAnimationFrame(0);
    }
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setAnimationFrame(0);
  };

  return (
    <div style={{ width: '100%' }}>
      <canvas
        ref={canvasRef}
        width={1000}
        height={600}
        style={{
          width: '100%',
          height: 'auto',
          borderRadius: 'var(--radius-md)',
          background: '#0a0a0a',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      />

      <div style={{
        display: 'flex',
        gap: '1rem',
        marginTop: '1.5rem',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button
            onClick={handlePlayPause}
            style={{
              padding: '0.75rem 2rem',
              fontSize: '0.9375rem',
              fontWeight: '600',
              color: '#ffffff',
              background: 'var(--primary-gradient)',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 10px 30px rgba(220, 38, 38, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            {isPlaying ? '⏸ Pause' : '▶ Play Animation'}
          </button>

          <button
            onClick={handleReset}
            style={{
              padding: '0.75rem 1.5rem',
              fontSize: '0.9375rem',
              fontWeight: '600',
              color: 'var(--text-primary)',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
            }}
          >
            ↺ Reset
          </button>
        </div>

        <div style={{ display: 'flex', gap: '2rem', fontSize: '0.875rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '20px',
              height: '3px',
              background: 'rgba(255, 255, 255, 0.4)',
              borderRadius: '2px',
            }} />
            <span style={{ color: 'var(--text-tertiary)' }}>Leclerc (70.270s)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '20px',
              height: '3px',
              background: '#dc2626',
              borderRadius: '2px',
            }} />
            <span style={{ color: 'var(--text-tertiary)' }}>AI Optimal (69.450s)</span>
          </div>
        </div>
      </div>

      {isPlaying && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.03)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.25rem' }}>
              Progress
            </div>
            <div style={{ fontSize: '1.125rem', fontWeight: '600' }}>
              {Math.round((animationFrame / Math.min(leclercTelemetry.length, aiTelemetry.length)) * 100)}%
            </div>
          </div>
          <div style={{
            flex: 1,
            height: '4px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '2px',
            margin: '0 1rem',
            overflow: 'hidden',
          }}>
            <div style={{
              width: `${(animationFrame / Math.min(leclercTelemetry.length, aiTelemetry.length)) * 100}%`,
              height: '100%',
              background: 'var(--primary-gradient)',
              borderRadius: '2px',
              transition: 'width 0.1s linear',
            }} />
          </div>
        </div>
      )}
    </div>
  );
}
