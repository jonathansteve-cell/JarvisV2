import React, { useEffect, useRef } from 'react';
import { ThemeConfig } from '../utils/theme';

interface BackgroundGridProps {
  theme: ThemeConfig;
  showScanlines: boolean;
}

export const BackgroundGrid: React.FC<BackgroundGridProps> = ({ theme, showScanlines }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    // Floating particles
    const particles = Array.from({ length: 45 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 1.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2,
      alpha: Math.random() * 0.5 + 0.2,
    }));

    // Fixed crosshairs on grid coordinates
    const crosshairs: { x: number; y: number }[] = [];
    const step = 200;
    for (let x = 100; x < width; x += step) {
      for (let y = 100; y < height; y += step) {
        if (Math.random() > 0.4) {
          crosshairs.push({ x, y });
        }
      }
    }

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Dark background gradient
      const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 100, width / 2, height / 2, width * 0.75);
      bgGrad.addColorStop(0, theme.bgDark);
      bgGrad.addColorStop(1, '#000205');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Subtle cyber grid lines
      ctx.strokeStyle = theme.primaryHex;
      ctx.lineWidth = 0.5;
      ctx.globalAlpha = 0.04;

      const gridSize = 40;
      ctx.beginPath();
      for (let x = 0; x <= width; x += gridSize) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
      }
      for (let y = 0; y <= height; y += gridSize) {
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
      }
      ctx.stroke();

      // Technical crosshair marks (+)
      ctx.globalAlpha = 0.25;
      ctx.strokeStyle = theme.primaryHex;
      ctx.lineWidth = 1;
      crosshairs.forEach(({ x, y }) => {
        ctx.beginPath();
        ctx.moveTo(x - 5, y);
        ctx.lineTo(x + 5, y);
        ctx.moveTo(x, y - 5);
        ctx.lineTo(x, y + 5);
        ctx.stroke();
      });

      // Floating data particles
      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.globalAlpha = p.alpha * 0.7;
        ctx.fillStyle = theme.primaryHex;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      });

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animId);
    };
  }, [theme]);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <canvas ref={canvasRef} className="w-full h-full block" />
      
      {/* CRT Scanline Overlay */}
      {showScanlines && (
        <div 
          className="absolute inset-0 pointer-events-none opacity-40 mix-blend-overlay"
          style={{
            backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 0, 0, 0.6) 2px, rgba(0, 0, 0, 0.6) 4px)',
          }}
        />
      )}

      {/* Subtle Vignette */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at center, transparent 45%, rgba(0, 2, 8, 0.85) 100%)',
        }}
      />
    </div>
  );
};
