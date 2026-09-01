import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { DriveData } from '../types';
import { ThemeConfig } from '../utils/theme';
import { sound } from '../utils/audio';

interface DriveTelemetryCardProps {
  drive: DriveData;
  theme: ThemeConfig;
  isSelected?: boolean;
  onSelect?: (drive: DriveData) => void;
  isRightSide?: boolean;
}

export const DriveTelemetryCard: React.FC<DriveTelemetryCardProps> = ({
  drive,
  theme,
  isSelected = false,
  onSelect,
  isRightSide = false,
}) => {
  const [rotation, setRotation] = useState(0);
  const [spectrumData, setSpectrumData] = useState<number[]>(drive.spectrum);
  const [readSpeed, setReadSpeed] = useState(drive.cacheRead);
  const [writeSpeed, setWriteSpeed] = useState(drive.cacheWrite);

  // Live fluctuating disk spectrum and access indicators
  useEffect(() => {
    const interval = setInterval(() => {
      setRotation((prev) => (prev + 3) % 360);
      setSpectrumData((prev) =>
        prev.map((val, idx) => {
          // Natural audio/disk spectrum decay & burst
          const decay = (prev.length - idx) / prev.length;
          const noise = Math.random() * 0.4 - 0.2;
          return Math.max(0.1, Math.min(1.0, decay * (0.8 + noise)));
        })
      );

      // Random speed fluctuations
      if (Math.random() > 0.6) {
        const rVal = Math.floor(parseInt(drive.cacheRead) + (Math.random() * 40 - 20));
        const wVal = Math.floor(parseInt(drive.cacheWrite) + (Math.random() * 40 - 20));
        setReadSpeed(`${Math.max(10, rVal)} KB`);
        setWriteSpeed(`${Math.max(10, wVal)} KB`);
      }
    }, 150);

    return () => clearInterval(interval);
  }, [drive]);

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      onClick={() => {
        sound.playClick();
        onSelect?.(drive);
      }}
      className={`group relative p-2 sm:p-2.5 rounded transition-all duration-300 cursor-pointer border ${
        isSelected
          ? 'border-cyan-400 bg-cyan-950/40 shadow-[0_0_20px_rgba(0,229,255,0.25)]'
          : 'border-cyan-500/30 bg-[#040c16]/75 hover:border-cyan-400/60 hover:bg-[#051424]/85'
      }`}
      style={{
        backdropFilter: 'blur(6px)',
      }}
    >
      {/* Corner Bracket Accents */}
      <div className="absolute -top-[1px] -left-[1px] w-2 h-2 border-t-2 border-l-2 border-cyan-400" />
      <div className="absolute -top-[1px] -right-[1px] w-2 h-2 border-t-2 border-r-2 border-cyan-400" />
      <div className="absolute -bottom-[1px] -left-[1px] w-2 h-2 border-b-2 border-l-2 border-cyan-400" />
      <div className="absolute -bottom-[1px] -right-[1px] w-2 h-2 border-b-2 border-r-2 border-cyan-400" />

      {/* Top Header: Rotating Disk Radar + Drive Specs */}
      <div className="flex items-start justify-between gap-2 mb-2">
        {/* Disk Radar Icon & Temperature */}
        <div className="relative flex items-center gap-2 p-1 rounded border border-cyan-500/40 bg-black/50">
          <div className="relative w-8 h-8 flex items-center justify-center">
            {/* Spinning Radar Platter */}
            <svg className="w-8 h-8" viewBox="0 0 36 36">
              <circle
                cx="18"
                cy="18"
                r="16"
                fill="none"
                stroke={theme.primaryHex}
                strokeWidth="1"
                strokeOpacity="0.4"
              />
              <circle
                cx="18"
                cy="18"
                r="10"
                fill="none"
                stroke={theme.primaryHex}
                strokeWidth="0.8"
                strokeDasharray="2,2"
                strokeOpacity="0.6"
              />
              <circle cx="18" cy="18" r="3" fill={theme.primaryHex} />

              {/* Rotating radar sweep arm */}
              <g transform={`rotate(${rotation} 180 180)`} transform-origin="18 18">
                <line
                  x1="18"
                  y1="18"
                  x2="18"
                  y2="2"
                  stroke={theme.primaryHex}
                  strokeWidth="1.5"
                  strokeOpacity="0.9"
                />
                <circle cx="18" cy="6" r="1.5" fill={theme.accentHex} />
              </g>
            </svg>
          </div>

          {/* Drive Temp readout */}
          <div className="flex flex-col">
            <span className="text-[8px] text-cyan-500/70 font-mono">TEMP</span>
            <span
              className={`text-xs font-bold font-mono ${
                drive.temp > 30 ? 'text-orange-400' : 'text-cyan-300'
              }`}
            >
              {drive.temp} °C
            </span>
          </div>
        </div>

        {/* Drive Info Specification Matrix */}
        <div className="flex-1 flex flex-col justify-between border border-cyan-500/40 rounded p-1 bg-black/40 text-[9px] font-mono">
          <div className="flex items-center justify-between border-b border-cyan-500/30 pb-0.5">
            <span className="font-bold text-cyan-300 tracking-wider">
              DRIVE {drive.letter}:\
            </span>
            <span className="text-cyan-400/60 text-[8px]">{drive.label}</span>
          </div>
          <div className="grid grid-cols-3 gap-1 pt-0.5 text-[8px]">
            <div>
              <span className="text-cyan-500/60 block">TOTAL</span>
              <span className="text-cyan-300 font-semibold">{drive.total}</span>
            </div>
            <div>
              <span className="text-orange-400/80 block">USED</span>
              <span className="text-orange-300 font-semibold">{drive.used}</span>
            </div>
            <div>
              <span className="text-cyan-400/80 block">FREE</span>
              <span className="text-cyan-200 font-semibold">{drive.free}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dual Segmented Percentage Bars */}
      <div className="relative mb-2 flex items-center gap-1.5">
        {/* Left Used Bar */}
        <div className="flex-1 relative h-5 rounded-sm bg-cyan-950/70 border border-cyan-500/50 overflow-hidden flex items-center px-1.5">
          <motion.div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-cyan-600/80 to-cyan-400/90 shadow-[0_0_10px_rgba(0,229,255,0.5)]"
            initial={{ width: 0 }}
            animate={{ width: `${drive.usedPercent}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
          <span className="relative z-10 text-[11px] font-black text-black tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>
            {drive.usedPercent.toFixed(1)} %
          </span>
        </div>

        {/* Right Free Bar */}
        <div className="w-16 sm:w-20 relative h-5 rounded-sm bg-cyan-950/70 border border-cyan-500/50 overflow-hidden flex items-center justify-end px-1.5">
          <motion.div
            className="absolute inset-y-0 right-0 bg-gradient-to-l from-orange-500/80 to-cyan-500/70"
            initial={{ width: 0 }}
            animate={{ width: `${drive.freePercent}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
          <span className="relative z-10 text-[10px] font-bold text-white font-mono tracking-tighter">
            {drive.freePercent.toFixed(1)} %
          </span>
        </div>
      </div>

      {/* Bottom Section: Cache Usage & Spectrum Equalizer */}
      <div className="flex items-end justify-between gap-2 border-t border-cyan-500/30 pt-1.5 text-[8px] font-mono">
        {/* Cache stats */}
        <div className="flex flex-col">
          <span className="text-[9px] font-bold text-cyan-300 tracking-wider flex items-center gap-1">
            <span className="w-1 h-1 bg-cyan-400 rounded-full animate-pulse" />
            CACHE USAGE
          </span>
          <div className="flex gap-2 text-cyan-500/80 mt-0.5">
            <span>TOTAL: <strong className="text-cyan-300">{drive.cacheTotal}</strong></span>
            <span>R: <strong className="text-cyan-200">{readSpeed}</strong></span>
            <span>W: <strong className="text-orange-300">{writeSpeed}</strong></span>
          </div>
        </div>

        {/* Visual Spectrum Bars */}
        <div className="flex flex-col items-end">
          <div className="flex items-end gap-[2px] h-4 mb-0.5">
            {spectrumData.map((val, i) => (
              <div
                key={i}
                className="w-[3px] rounded-t-sm transition-all duration-150"
                style={{
                  height: `${Math.max(2, val * 16)}px`,
                  backgroundColor: i > spectrumData.length - 4 ? theme.accentHex : theme.primaryHex,
                  opacity: 0.4 + val * 0.6,
                  boxShadow: val > 0.7 ? `0 0 4px ${theme.primaryHex}` : 'none',
                }}
              />
            ))}
          </div>
          <span className="text-[7px] tracking-widest text-cyan-500/60">
            HARD DRIVE ACCESS ...
          </span>
        </div>
      </div>
    </motion.div>
  );
};
