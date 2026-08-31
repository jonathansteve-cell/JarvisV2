import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { DriveData, ProcessItem, WeatherData } from '../types';
import { ThemeConfig } from '../utils/theme';
import { sound } from '../utils/audio';
import { Activity, Zap, Play, Terminal, CloudSun, Wind, Droplets, Compass } from 'lucide-react';

interface CenterCoreHUDProps {
  theme: ThemeConfig;
  drives: DriveData[];
  selectedDriveId?: string;
  onSelectDrive: (drive: DriveData) => void;
  processes: ProcessItem[];
  onToggleProcess: (id: string) => void;
  weather: WeatherData;
  onOpenWeatherModal: () => void;
  onOpenAppLauncher: (appName: string) => void;
}

export const CenterCoreHUD: React.FC<CenterCoreHUDProps> = ({
  theme,
  drives,
  selectedDriveId,
  onSelectDrive,
  processes,
  onToggleProcess,
  weather,
  onOpenWeatherModal,
  onOpenAppLauncher,
}) => {
  const [coreRotation, setCoreRotation] = useState(0);
  const [hazardRotation, setHazardRotation] = useState(0);
  const [outerRingRotation, setOuterRingRotation] = useState(0);
  const [isExtremeMode, setIsExtremeMode] = useState(false);
  const [is200kMode, setIs200kMode] = useState(false);

  // Core metrics animation
  const [cpuUsage, setCpuUsage] = useState(12);
  const [ramUsage, setRamUsage] = useState(48);
  const [gpuUsage, setGpuUsage] = useState(72);
  const [netUsage, setNetUsage] = useState(28);

  useEffect(() => {
    const interval = setInterval(() => {
      const speedMult迷 = isExtremeMode ? 2.5 : 1;
      setCoreRotation((prev) => (prev + 0.5 * speedMult迷) % 360);
      setHazardRotation((prev) => (prev - 0.7 * speedMult迷) % 360);
      setOuterRingRotation((prev) => (prev + 0.2 * speedMult迷) % 360);

      // Organic telemetry oscillation
      if (Math.random() > 0.4) {
        const baseCpu = isExtremeMode ? 85 : 12;
        const baseRam = isExtremeMode ? 92 : 48;
        const baseGpu = isExtremeMode ? 96 : 72;
        const baseNet = isExtremeMode ? 75 : 28;

        setCpuUsage(Math.min(99, Math.max(5, baseCpu + Math.floor(Math.random() * 8 - 4))));
        setRamUsage(Math.min(99, Math.max(10, baseRam + Math.floor(Math.random() * 6 - 3))));
        setGpuUsage(Math.min(99, Math.max(10, baseGpu + Math.floor(Math.random() * 6 - 3))));
        setNetUsage(Math.min(99, Math.max(5, baseNet + Math.floor(Math.random() * 10 - 5))));
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isExtremeMode]);

  // Sector buttons around the inner circle
  const sectorButtons = [
    { label: 'WP', name: 'Word Processor', angle: 160 },
    { label: 'COMP', name: 'Computer Explorer', angle: 180 },
    { label: 'DOCS', name: 'Document Vault', angle: 200 },
    { label: 'UTIL', name: 'System Utilities', angle: 220 },
    { label: 'XRM', name: 'Matrix Terminal', angle: 240 },
    { label: 'USER', name: 'User Profile', angle: 20 },
    { label: 'CHRM', name: 'Chrome Browser', angle: 0 },
    { label: 'GAME', name: 'Gaming Subsystem', angle: 340 },
    { label: 'CFG', name: 'Configuration', angle: 320 },
    { label: 'FFOX', name: 'Quantum Engine', angle: 300 },
  ];

  // Drive orbital badge coordinates mapped around the central ring
  const driveNodes = [
    { drive: drives[0], angle: 90, distance: 220, labelVal: '811.5 GB' }, // C (Top)
    { drive: drives[1], angle: 330, distance: 220, labelVal: '538.1 GB' }, // D
    { drive: drives[2], angle: 300, distance: 220, labelVal: '50.6 GB' }, // E
    { drive: drives[3], angle: 270, distance: 220, labelVal: '1.1 TB' }, // F (Bottom)
    { drive: drives[4], angle: 240, distance: 220, labelVal: '405.8 GB' }, // G
    { drive: drives[5], angle: 180, distance: 220, labelVal: '1.4 TB' }, // H (Left)
  ];

  return (
    <div className="relative flex items-center justify-center w-full max-w-[620px] lg:max-w-[700px] h-[520px] lg:h-[580px] select-none">
      {/* Top Center Mode Buttons */}
      <div className="absolute top-2 z-30 flex items-center gap-3">
        <button
          onClick={() => {
            sound.playClick(isExtremeMode ? 800 : 1600);
            setIsExtremeMode(!isExtremeMode);
            if (!isExtremeMode) sound.playAlert();
          }}
          className={`px-2.5 py-1 text-[10px] font-mono tracking-widest rounded border transition-all ${
            isExtremeMode
              ? 'bg-orange-500 text-black border-orange-400 font-bold shadow-[0_0_15px_rgba(255,84,0,0.8)] animate-pulse'
              : 'bg-black/60 text-cyan-400/80 border-cyan-500/40 hover:border-cyan-300 hover:text-cyan-200'
          }`}
        >
          XTRM MODE
        </button>

        <button
          onClick={() => {
            sound.playClick(1400);
            setIs200kMode(!is200kMode);
          }}
          className={`px-2.5 py-1 text-[10px] font-mono tracking-widest rounded border transition-all ${
            is200kMode
              ? 'bg-cyan-400 text-black border-cyan-300 font-bold shadow-[0_0_15px_rgba(0,229,255,0.8)]'
              : 'bg-black/60 text-cyan-400/80 border-cyan-500/40 hover:border-cyan-300 hover:text-cyan-200'
          }`}
        >
          200K MODE
        </button>
      </div>

      {/* LEFT Process List Readout */}
      <div className="absolute left-0 lg:-left-6 top-1/2 -translate-y-1/2 z-30 flex flex-col items-start min-w-[130px] sm:min-w-[150px] pointer-events-auto">
        <div className="text-[9px] font-bold tracking-widest text-cyan-500/80 border-b border-cyan-500/30 pb-0.5 mb-1 flex items-center gap-1 font-mono">
          <Activity className="w-2.5 h-2.5 text-cyan-400" />
          ACTIVE MODULES
        </div>
        <div className="flex flex-col gap-1 w-full font-mono text-[9px] sm:text-[10px]">
          {processes.map((proc) => (
            <motion.div
              key={proc.id}
              whileHover={{ x: 4 }}
              onClick={() => {
                sound.playClick();
                onToggleProcess(proc.id);
              }}
              className={`cursor-pointer px-1.5 py-0.5 rounded flex items-center justify-between transition-all border ${
                proc.status === 'ACTIVE'
                  ? 'border-cyan-500/60 bg-cyan-950/40 text-cyan-300 shadow-[0_0_8px_rgba(0,229,255,0.2)]'
                  : 'border-cyan-500/20 bg-black/40 text-cyan-500/50 hover:text-cyan-400'
              }`}
            >
              <div className="flex items-center gap-1 truncate">
                <span
                  className={`w-1 h-1 rounded-full ${
                    proc.status === 'ACTIVE' ? 'bg-cyan-400 animate-ping' : 'bg-cyan-700'
                  }`}
                />
                <span className="truncate">{proc.name}</span>
              </div>
              <span className="text-[8px] text-cyan-500/60 ml-1">{proc.cpu}%</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* RIGHT Weather Telemetry Readout */}
      <div
        onClick={() => {
          sound.playClick();
          onOpenWeatherModal();
        }}
        className="absolute right-0 lg:-right-6 top-1/2 -translate-y-1/2 z-30 flex flex-col items-start p-2 rounded border border-cyan-500/40 bg-[#040e1a]/85 backdrop-blur-sm cursor-pointer hover:border-cyan-300 transition-all font-mono text-[8px] sm:text-[9px] max-w-[145px] sm:max-w-[165px] shadow-[0_0_15px_rgba(0,229,255,0.15)]"
      >
        <div className="text-[8px] text-cyan-400/70 font-semibold tracking-wider truncate w-full border-b border-cyan-500/30 pb-0.5 mb-1">
          {weather.location}
        </div>

        <div className="text-[7px] text-cyan-500/50 mb-1">
          UPDATED AT {weather.updatedTime}
        </div>

        {/* Big Temperature Indicator */}
        <div className="flex items-center justify-between w-full mb-1">
          <span
            className="text-lg sm:text-xl font-black text-cyan-300 tracking-wider"
            style={{
              fontFamily: "'Orbitron', sans-serif",
              textShadow: `0 0 8px ${theme.primaryGlow}`,
            }}
          >
            {weather.temp} °{weather.tempUnit}
          </span>
          <span className="text-[8px] text-orange-400 font-bold px-1 py-0.5 rounded bg-orange-950/60 border border-orange-500/40">
            {weather.condition}
          </span>
        </div>

        {/* Detailed environmental telemetry grid */}
        <div className="flex flex-col gap-0.5 text-cyan-400/80 w-full text-[7px] sm:text-[8px]">
          <div className="flex justify-between">
            <span>HUMIDITY</span>
            <span className="text-cyan-200 font-semibold">{weather.humidity}%</span>
          </div>
          <div className="flex justify-between">
            <span>FEELS LIKE</span>
            <span className="text-cyan-200 font-semibold">{weather.feelsLike}°</span>
          </div>
          <div className="flex justify-between">
            <span>PRECIPITATION</span>
            <span className="text-cyan-200 font-semibold">{weather.precipitation}%</span>
          </div>
          <div className="flex justify-between">
            <span>VISIBILITY</span>
            <span className="text-cyan-200 font-semibold">{weather.visibility} KM</span>
          </div>
          <div className="flex justify-between">
            <span>WIND</span>
            <span className="text-cyan-200 font-semibold">
              {weather.windSpeed} KM/H [{weather.windDirection}]
            </span>
          </div>
          <div className="flex justify-between">
            <span>PRESSURE</span>
            <span className="text-cyan-200 font-semibold">{weather.pressure} HPA</span>
          </div>
          <div className="flex justify-between pt-0.5 border-t border-cyan-500/20 text-[7px] text-cyan-500/70">
            <span>SUN: {weather.sunrise}</span>
            <span>SET: {weather.sunset}</span>
          </div>
        </div>
      </div>

      {/* SVG Central Arc Reactor and Rotating Rings */}
      <svg
        className="w-full h-full max-w-[580px] max-h-[580px] overflow-visible"
        viewBox="0 0 600 600"
      >
        <defs>
          {/* Gradients */}
          <linearGradient id="cyanArcGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={theme.primaryHex} stopOpacity="1" />
            <stop offset="100%" stopColor="#00b4d8" stopOpacity="0.8" />
          </linearGradient>

          <linearGradient id="orangeArcGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={theme.accentHex} stopOpacity="1" />
            <stop offset="100%" stopColor="#ffb703" stopOpacity="0.9" />
          </linearGradient>

          <pattern
            id="diagonalStripes"
            width="8"
            height="8"
            patternTransform="rotate(45 0 0)"
            patternUnits="userSpaceOnUse"
          >
            <line x1="0" y1="0" x2="0" y2="8" stroke={theme.primaryHex} strokeWidth="3" />
          </pattern>

          {/* Glow filter */}
          <filter id="coreGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* 1. Outermost Orbital Ring with Tech Ticks */}
        <g transform={`rotate(${outerRingRotation} 300 300)`}>
          <circle
            cx="300"
            cy="300"
            r="240"
            fill="none"
            stroke={theme.primaryHex}
            strokeWidth="1.5"
            strokeDasharray="60 12 180 12 90 12"
            strokeOpacity="0.7"
          />
          <circle
            cx="300"
            cy="300"
            r="248"
            fill="none"
            stroke={theme.primaryHex}
            strokeWidth="0.8"
            strokeDasharray="4 6"
            strokeOpacity="0.4"
          />
        </g>

        {/* 2. Outer Segmented Notches Ring */}
        <g>
          {Array.from({ length: 36 }).map((_, i) => {
            const angle = (i * 10 * Math.PI) / 180;
            const x1 = 300 + Math.cos(angle) * 218;
            const y1 = 300 + Math.sin(angle) * 218;
            const x2 = 300 + Math.cos(angle) * (i % 3 === 0 ? 228 : 223);
            const y2 = 300 + Math.sin(angle) * (i % 3 === 0 ? 228 : 223);
            return (
              <line
                key={i}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={i % 6 === 0 ? theme.accentHex : theme.primaryHex}
                strokeWidth={i % 3 === 0 ? '2' : '1'}
                strokeOpacity={i % 3 === 0 ? '0.9' : '0.4'}
              />
            );
          })}
        </g>

        {/* 3. Segmented Reactor Block Ring (Trapezoid Sector Blocks) */}
        <g transform={`rotate(${coreRotation * 0.3} 300 300)`}>
          {Array.from({ length: 24 }).map((_, i) => {
            const startA = ((i * 15 + 2) * Math.PI) / 180;
            const endA = ((i * 15 + 13) * Math.PI) / 180;
            const rIn = 185;
            const rOut = 198;

            const p1x = 300 + Math.cos(startA) * rIn;
            const p1y = 300 + Math.sin(startA) * rIn;
            const p2x = 300 + Math.cos(startA) * rOut;
            const p2y = 300 + Math.sin(startA) * rOut;
            const p3x = 300 + Math.cos(endA) * rOut;
            const p3y = 300 + Math.sin(endA) * rOut;
            const p4x = 300 + Math.cos(endA) * rIn;
            const p4y = 300 + Math.sin(endA) * rIn;

            const isLit = (i + Math.floor(coreRotation / 15)) % 4 === 0;

            return (
              <polygon
                key={i}
                points={`${p1x},${p1y} ${p2x},${p2y} ${p3x},${p3y} ${p4x},${p4y}`}
                fill={isLit ? theme.primaryHex : 'transparent'}
                stroke={theme.primaryHex}
                strokeWidth="1"
                fillOpacity={isLit ? 0.8 : 0.05}
                strokeOpacity="0.6"
              />
            );
          })}
        </g>

        {/* 4. Hazard Striped Gear Ring */}
        <g transform={`rotate(${hazardRotation} 300 300)`}>
          <circle
            cx="300"
            cy="300"
            r="165"
            fill="none"
            stroke={theme.primaryHex}
            strokeWidth="12"
            strokeDasharray="6 6"
            strokeOpacity="0.8"
          />
        </g>

        {/* 5. Concentric Circular Progress Telemetry Gauges */}
        {/* Gauge 1: 48% (CPU Core) */}
        <circle
          cx="300"
          cy="300"
          r="140"
          fill="none"
          stroke={theme.primaryHex}
          strokeWidth="5"
          strokeDasharray={`${(ramUsage / 100) * (2 * Math.PI * 140)} ${(1 - ramUsage / 100) * (2 * Math.PI * 140)}`}
          strokeDashoffset="120"
          strokeLinecap="round"
          filter="url(#coreGlow)"
        />

        {/* Gauge 2: 72% (RAM / Core 2) */}
        <circle
          cx="300"
          cy="300"
          r="125"
          fill="none"
          stroke={theme.primaryHex}
          strokeWidth="4"
          strokeDasharray={`${(gpuUsage / 100) * (2 * Math.PI * 125)} ${(1 - gpuUsage / 100) * (2 * Math.PI * 125)}`}
          strokeDashoffset="60"
          strokeLinecap="round"
          strokeOpacity="0.9"
        />

        {/* Gauge 3: 28% (Orange Accent Arc) */}
        <circle
          cx="300"
          cy="300"
          r="110"
          fill="none"
          stroke={theme.accentHex}
          strokeWidth="5"
          strokeDasharray={`${(netUsage / 100) * (2 * Math.PI * 110)} ${(1 - netUsage / 100) * (2 * Math.PI * 110)}`}
          strokeDashoffset="240"
          strokeLinecap="round"
          filter="url(#coreGlow)"
        />

        {/* 6. Inner Core Reactor Circle */}
        <circle
          cx="300"
          cy="300"
          r="75"
          fill="#030b14"
          stroke={theme.primaryHex}
          strokeWidth="2"
          strokeOpacity="0.85"
        />
        <circle
          cx="300"
          cy="300"
          r="68"
          fill="none"
          stroke={theme.primaryHex}
          strokeWidth="1"
          strokeDasharray="4 4"
          strokeOpacity="0.6"
        />
        <circle
          cx="300"
          cy="300"
          r="58"
          fill="none"
          stroke={theme.accentHex}
          strokeWidth="1.5"
          strokeDasharray="20 40 10 40"
          strokeOpacity="0.8"
        />

        {/* Dynamic Telemetry Percentage Display inside arcs */}
        <g transform="translate(300, 260)">
          <text
            x="0"
            y="-18"
            textAnchor="middle"
            fill={theme.primaryHex}
            fontSize="10"
            fontWeight="bold"
            fontFamily="'Orbitron', monospace"
            letterSpacing="1"
          >
            {ramUsage}%
          </text>
          <text
            x="0"
            y="-6"
            textAnchor="middle"
            fill={theme.primaryHex}
            fontSize="10"
            fontWeight="bold"
            fontFamily="'Orbitron', monospace"
            letterSpacing="1"
          >
            {gpuUsage}%
          </text>
          <text
            x="0"
            y="6"
            textAnchor="middle"
            fill={theme.accentHex}
            fontSize="10"
            fontWeight="bold"
            fontFamily="'Orbitron', monospace"
            letterSpacing="1"
          >
            {netUsage}%
          </text>
        </g>

        {/* Core Center Text */}
        <g transform="translate(300, 305)">
          <text
            x="0"
            y="-6"
            textAnchor="middle"
            fill={theme.primaryHex}
            fontSize="11"
            fontWeight="900"
            fontFamily="'Orbitron', monospace"
            letterSpacing="2"
          >
            CPU
          </text>
          <text
            x="0"
            y="14"
            textAnchor="middle"
            fill="#ffffff"
            fontSize="18"
            fontWeight="900"
            fontFamily="'Orbitron', monospace"
            letterSpacing="1"
          >
            {cpuUsage}%
          </text>
        </g>
      </svg>

      {/* Radial Sector Shortcut Buttons */}
      {sectorButtons.map((btn, i) => {
        const rad = (btn.angle * Math.PI) / 180;
        const x = 300 + Math.cos(rad) * 155;
        const y = 300 + Math.sin(rad) * 155;

        return (
          <motion.button
            key={i}
            whileHover={{ scale: 1.15 }}
            onClick={() => {
              sound.playClick(1500);
              onOpenAppLauncher(btn.name);
            }}
            title={btn.name}
            className="absolute z-20 px-1 py-0.5 rounded text-[8px] font-mono font-bold border border-cyan-500/50 bg-[#030d1a]/90 text-cyan-300 hover:border-cyan-300 hover:bg-cyan-500 hover:text-black transition-all shadow-[0_0_8px_rgba(0,229,255,0.2)]"
            style={{
              left: `${(x / 600) * 100}%`,
              top: `${(y / 600) * 100}%`,
              transform: 'translate(-50%, -50%)',
            }}
          >
            {btn.label}
          </motion.button>
        );
      })}

      {/* Orbiting Drive Badges (C, D, E, F, G, H) */}
      {driveNodes.map((node, i) => {
        if (!node.drive) return null;
        const rad = (node.angle * Math.PI) / 180;
        const x = 300 + Math.cos(rad) * node.distance;
        const y = 300 + Math.sin(rad) * node.distance;
        const isSelected = selectedDriveId === node.drive.id;

        return (
          <motion.div
            key={i}
            whileHover={{ scale: 1.1 }}
            onClick={() => {
              sound.playClick();
              onSelectDrive(node.drive);
            }}
            className="absolute z-30 flex flex-col items-center cursor-pointer group"
            style={{
              left: `${(x / 600) * 100}%`,
              top: `${(y / 600) * 100}%`,
              transform: 'translate(-50%, -50%)',
            }}
          >
            {/* Top drive size badge */}
            <span
              className={`text-[8px] font-mono px-1 py-0.2 rounded border transition-colors ${
                isSelected
                  ? 'bg-orange-500 text-black border-orange-400 font-bold'
                  : 'bg-black/70 text-orange-400 border-orange-500/40 group-hover:border-orange-300'
              }`}
            >
              {node.labelVal}
            </span>

            {/* Circular Drive Letter Badge matching screenshot */}
            <div
              className={`w-6 h-6 rounded-full border-2 flex items-center justify-center font-bold text-xs transition-all ${
                isSelected
                  ? 'border-orange-400 bg-orange-950/80 text-orange-200 shadow-[0_0_12px_rgba(255,84,0,0.8)]'
                  : 'border-cyan-400/80 bg-black/80 text-cyan-300 group-hover:border-cyan-300 shadow-[0_0_8px_rgba(0,229,255,0.4)]'
              }`}
              style={{ fontFamily: "'Orbitron', sans-serif" }}
            >
              {node.drive.letter}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};
