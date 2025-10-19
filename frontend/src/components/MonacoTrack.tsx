import { useEffect, useRef, useState } from 'react';
import type { DriverData } from '../types';

interface MonacoTrackProps {
  telemetryData: DriverData | null;
  width?: number;
  height?: number;
  showSpeed?: boolean;
}

export default function MonacoTrack({ telemetryData, width = 800, height = 500, showSpeed = true }: MonacoTrackProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!telemetryData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const telemetry = telemetryData.telemetry || [];
    if (telemetry.length === 0) return;

    // Find bounds
    const xCoords = telemetry.map(p => p.x);
    const yCoords = telemetry.map(p => p.y);
    const minX = Math.min(...xCoords);
    const maxX = Math.max(...xCoords);
    const minY = Math.min(...yCoords);
    const maxY = Math.max(...yCoords);

    // Scale to canvas
    const padding = 40;
    const scaleX = (width - 2 * padding) / (maxX - minX);
    const scaleY = (height - 2 * padding) / (maxY - minY);
    const scale = Math.min(scaleX, scaleY);

    const centerX = width / 2;
    const centerY = height / 2;
    const trackCenterX = (minX + maxX) / 2;
    const trackCenterY = (minY + maxY) / 2;

    const toCanvasX = (x: number) => centerX + (x - trackCenterX) * scale;
    const toCanvasY = (y: number) => centerY + (y - trackCenterY) * scale;

    let animationFrame: number;
    let currentProgress = 0;

    function animate() {
      if (!ctx) return;

      ctx.clearRect(0, 0, width, height);

      // Draw track surface
      ctx.strokeStyle = '#1a1a2a';
      ctx.lineWidth = 30;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.beginPath();
      telemetry.forEach((point, i) => {
        const x = toCanvasX(point.x);
        const y = toCanvasY(point.y);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      // Draw racing line (gradient based on speed)
      telemetry.forEach((point, i) => {
        if (i === 0 || i > currentProgress) return;

        const nextPoint = telemetry[i];
        const x1 = toCanvasX(telemetry[i - 1].x);
        const y1 = toCanvasY(telemetry[i - 1].y);
        const x2 = toCanvasX(nextPoint.x);
        const y2 = toCanvasY(nextPoint.y);

        // Color by speed
        const speed = point.speed;
        const speedPercent = speed / 300;
        const r = Math.floor(239 * (1 - speedPercent) + 34 * speedPercent);
        const g = Math.floor(68 * (1 - speedPercent) + 197 * speedPercent);
        const b = Math.floor(68 * (1 - speedPercent) + 94 * speedPercent);

        ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.9)`;
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      });

      // Draw current position marker
      if (currentProgress < telemetry.length) {
        const current = telemetry[Math.floor(currentProgress)];
        const x = toCanvasX(current.x);
        const y = toCanvasY(current.y);

        // Outer glow
        ctx.shadowColor = '#fbbf24';
        ctx.shadowBlur = 20;
        ctx.fillStyle = '#fbbf24';
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);
        ctx.fill();

        // Inner core
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();

        // Speed indicator
        if (showSpeed) {
          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 12px Orbitron';
          ctx.fillText(`${Math.round(current.speed)} km/h`, x + 15, y - 10);
        }
      }

      // Animate progress
      currentProgress += 0.5;
      if (currentProgress >= telemetry.length) {
        currentProgress = 0;
      }
      setProgress(Math.floor((currentProgress / telemetry.length) * 100));

      animationFrame = requestAnimationFrame(animate);
    }

    animate();

    return () => {
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [telemetryData, width, height, showSpeed]);

  return (
    <div style={{ position: 'relative' }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          width: '100%',
          height: 'auto',
          borderRadius: '16px',
          background: 'radial-gradient(circle at 30% 30%, rgba(59, 130, 246, 0.15) 0%, transparent 50%), radial-gradient(circle at 70% 70%, rgba(239, 68, 68, 0.15) 0%, transparent 50%), linear-gradient(135deg, #0a0a15 0%, #151520 100%)',
        }}
      />
      <div
        className="glass"
        style={{
          position: 'absolute',
          top: '1rem',
          right: '1rem',
          padding: '0.5rem 1rem',
          borderRadius: '8px',
        }}
      >
        <span style={{ fontFamily: 'Orbitron', fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
          LAP PROGRESS: {progress}%
        </span>
      </div>
    </div>
  );
}
