import { HudTheme } from '../types';

export interface ThemeConfig {
  name: string;
  primary: string; // e.g. text-cyan-400
  primaryHex: string;
  primaryGlow: string;
  primaryBorder: string;
  accent: string; // e.g. text-orange-500
  accentHex: string;
  accentGlow: string;
  accentBorder: string;
  bgDark: string;
  panelBg: string;
}

export const HUD_THEMES: Record<HudTheme, ThemeConfig> = {
  'classic-cyan': {
    name: 'Classic Sci-Fi Cyan',
    primary: 'text-cyan-400',
    primaryHex: '#00e5ff',
    primaryGlow: 'rgba(0, 229, 255, 0.4)',
    primaryBorder: 'border-cyan-500/40',
    accent: 'text-orange-500',
    accentHex: '#ff5400',
    accentGlow: 'rgba(255, 84, 0, 0.4)',
    accentBorder: 'border-orange-500/60',
    bgDark: '#03070d',
    panelBg: 'rgba(5, 18, 30, 0.65)',
  },
  'matrix-green': {
    name: 'Matrix Emerald',
    primary: 'text-emerald-400',
    primaryHex: '#00ff88',
    primaryGlow: 'rgba(0, 255, 136, 0.4)',
    primaryBorder: 'border-emerald-500/40',
    accent: 'text-amber-400',
    accentHex: '#ffb703',
    accentGlow: 'rgba(255, 183, 3, 0.4)',
    accentBorder: 'border-amber-500/60',
    bgDark: '#030d06',
    panelBg: 'rgba(5, 30, 14, 0.65)',
  },
  'cyber-magenta': {
    name: 'Cyberpunk Neon',
    primary: 'text-fuchsia-400',
    primaryHex: '#e056fd',
    primaryGlow: 'rgba(224, 86, 253, 0.4)',
    primaryBorder: 'border-fuchsia-500/40',
    accent: 'text-yellow-400',
    accentHex: '#f9ca24',
    accentGlow: 'rgba(249, 202, 36, 0.4)',
    accentBorder: 'border-yellow-500/60',
    bgDark: '#0b040e',
    panelBg: 'rgba(28, 8, 32, 0.65)',
  },
  'solar-amber': {
    name: 'Solar Tactical Gold',
    primary: 'text-amber-400',
    primaryHex: '#f59e0b',
    primaryGlow: 'rgba(245, 158, 11, 0.4)',
    primaryBorder: 'border-amber-500/40',
    accent: 'text-cyan-400',
    accentHex: '#06b6d4',
    accentGlow: 'rgba(6, 182, 212, 0.4)',
    accentBorder: 'border-cyan-500/60',
    bgDark: '#0d0a03',
    panelBg: 'rgba(28, 20, 5, 0.65)',
  },
};
