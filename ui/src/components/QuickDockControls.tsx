import React from 'react';
import { motion } from 'motion/react';
import { Power, RotateCcw, Moon, Palette, Tv, Shield, Volume2, VolumeX, Maximize2 } from 'lucide-react';
import { HudTheme } from '../types';
import { ThemeConfig, HUD_THEMES } from '../utils/theme';
import { sound } from '../utils/audio';

interface QuickDockControlsProps {
  theme: ThemeConfig;
  currentTheme: HudTheme;
  onCycleTheme: () => void;
  showScanlines: boolean;
  onToggleScanlines: () => void;
  soundEnabled: boolean;
  onToggleSound: () => void;
  onTriggerDiagnostic: () => void;
  onTriggerOverload: () => void;
  isSleepMode: boolean;
  onToggleSleepMode: () => void;
}

export const QuickDockControls: React.FC<QuickDockControlsProps> = ({
  theme,
  currentTheme,
  onCycleTheme,
  showScanlines,
  onToggleScanlines,
  soundEnabled,
  onToggleSound,
  onTriggerDiagnostic,
  onTriggerOverload,
  isSleepMode,
  onToggleSleepMode,
}) => {
  const dockButtons = [
    {
      id: 'power',
      icon: Power,
      label: 'DIAG',
      sub: 'POWER',
      action: () => {
        sound.playScanSweep();
        onTriggerDiagnostic();
      },
      title: 'Run Diagnostic System Sweep',
      active: false,
    },
    {
      id: 'restart',
      icon: RotateCcw,
      label: 'RST',
      sub: 'BURST',
      action: () => {
        sound.playAlert();
        onTriggerOverload();
      },
      title: 'Reactor Overload Surge Test',
      active: false,
    },
    {
      id: 'sleep',
      icon: Moon,
      label: 'SLEEP',
      sub: 'STANDBY',
      action: () => {
        sound.playClick(600);
        onToggleSleepMode();
      },
      title: 'Toggle Standby Dim Mode',
      active: isSleepMode,
    },
    {
      id: 'theme',
      icon: Palette,
      label: 'THEME',
      sub: 'COLOR',
      action: () => {
        sound.playConfirm();
        onCycleTheme();
      },
      title: `Cycle Color Palette (${HUD_THEMES[currentTheme].name})`,
      active: true,
    },
    {
      id: 'crt',
      icon: Tv,
      label: 'CRT',
      sub: 'SCAN',
      action: () => {
        sound.playClick(1100);
        onToggleScanlines();
      },
      title: 'Toggle CRT Scanline Effect',
      active: showScanlines,
    },
    {
      id: 'audio',
      icon: soundEnabled ? Volume2 : VolumeX,
      label: soundEnabled ? 'AUDIO' : 'MUTED',
      sub: 'SFX',
      action: () => {
        onToggleSound();
      },
      title: 'Toggle Futuristic Synthesizer Audio',
      active: soundEnabled,
    },
  ];

  return (
    <div className="relative p-1.5 sm:p-2 rounded border border-cyan-500/40 bg-[#040c16]/80 backdrop-blur-sm flex items-center gap-1 sm:gap-1.5 font-mono">
      {/* Corner Bracket Accents */}
      <div className="absolute -top-[1px] -left-[1px] w-2 h-2 border-t-2 border-l-2 border-cyan-400" />
      <div className="absolute -top-[1px] -right-[1px] w-2 h-2 border-t-2 border-r-2 border-cyan-400" />
      <div className="absolute -bottom-[1px] -left-[1px] w-2 h-2 border-b-2 border-l-2 border-cyan-400" />
      <div className="absolute -bottom-[1px] -right-[1px] w-2 h-2 border-b-2 border-r-2 border-cyan-400" />

      {dockButtons.map((btn) => {
        const Icon = btn.icon;
        return (
          <motion.button
            key={btn.id}
            whileHover={{ scale: 1.06, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={btn.action}
            title={btn.title}
            className={`flex flex-col items-center justify-between p-1 sm:p-1.5 w-9 sm:w-11 h-12 sm:h-14 rounded border transition-all ${
              btn.active
                ? 'border-cyan-400 bg-cyan-950/80 text-cyan-200 shadow-[0_0_10px_rgba(0,229,255,0.4)]'
                : 'border-cyan-500/40 bg-black/60 text-cyan-400/80 hover:border-cyan-300 hover:text-cyan-200'
            }`}
          >
            {/* Upper LED status indicator */}
            <div className="flex gap-[2px] w-full justify-center">
              <span className="w-1 h-[2px] bg-cyan-500 rounded-full opacity-60" />
              <span
                className={`w-2 h-[2px] rounded-full ${
                  btn.active ? 'bg-cyan-300' : 'bg-cyan-700'
                }`}
              />
              <span className="w-1 h-[2px] bg-cyan-500 rounded-full opacity-60" />
            </div>

            {/* Icon */}
            <Icon className="w-3.5 sm:w-4 h-3.5 sm:h-4" />

            {/* Text labels */}
            <div className="flex flex-col items-center leading-none">
              <span className="text-[7px] sm:text-[8px] font-bold tracking-tight">
                {btn.label}
              </span>
              <span className="text-[5px] sm:text-[6px] text-cyan-500/70">
                {btn.sub}
              </span>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
};
