import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Check, Plus, Calendar, Clock, Sparkles, Volume2, VolumeX, ShieldCheck } from 'lucide-react';
import { TaskItem } from '../types';
import { ThemeConfig } from '../utils/theme';
import { sound } from '../utils/audio';

interface HeaderBarProps {
  theme: ThemeConfig;
  tasks: TaskItem[];
  onToggleTask: (id: string) => void;
  onAddTask: (text: string) => void;
  isRealTime: boolean;
  onToggleRealTime: () => void;
  soundEnabled: boolean;
  onToggleSound: () => void;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({
  theme,
  tasks,
  onToggleTask,
  onAddTask,
  isRealTime,
  onToggleRealTime,
  soundEnabled,
  onToggleSound,
}) => {
  const [time, setTime] = useState({
    month: 'MARCH',
    year: '2017',
    day: '25',
    timeStr: '15:10:24',
    dayOfWeek: 'SATURDAY',
  });
  const [isAddingTask, setIsAddingTask] = useState(false);
  const [newTaskText, setNewTaskText] = useState('');

  useEffect(() => {
    if (!isRealTime) {
      setTime({
        month: 'MARCH',
        year: '2017',
        day: '25',
        timeStr: '15:10:24',
        dayOfWeek: 'SATURDAY',
      });
      return;
    }

    const updateRealTime = () => {
      const now = new Date();
      const monthNames = [
        'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
        'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'
      ];
      const dayNames = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
      
      setTime({
        month: monthNames[now.getMonth()],
        year: now.getFullYear().toString(),
        day: String(now.getDate()).padStart(2, '0'),
        timeStr: now.toTimeString().split(' ')[0],
        dayOfWeek: dayNames[now.getDay()],
      });
    };

    updateRealTime();
    const interval = setInterval(updateRealTime, 1000);
    return () => clearInterval(interval);
  }, [isRealTime]);

  const handleTaskSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTaskText.trim()) {
      onAddTask(newTaskText.trim());
      setNewTaskText('');
      setIsAddingTask(false);
      sound.playConfirm();
    }
  };

  return (
    <header className="relative w-full z-20 flex flex-col items-center pt-2 px-3 sm:px-6">
      {/* Top Telemetry Small Status Strip */}
      <div className="w-full max-w-7xl flex items-center justify-between text-[10px] tracking-widest text-cyan-500/70 font-mono mb-1 px-4">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
            <ShieldCheck className="w-3 h-3 text-cyan-400" />
            SYSTEM INTEGRITY: 99.4%
          </span>
          <span className="hidden sm:inline-block text-cyan-500/40">|</span>
          <span className="hidden sm:inline-block text-cyan-400/80">CORE STATUS: ONLINE</span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              sound.playClick();
              onToggleRealTime();
            }}
            className="flex items-center gap-1 hover:text-cyan-300 transition-colors px-2 py-0.5 rounded border border-cyan-500/30 bg-cyan-950/40"
            title="Toggle between Screenshot Mode (March 2017) and Live Local Time"
          >
            <Clock className="w-3 h-3 text-cyan-400" />
            <span>MODE: {isRealTime ? 'LIVE CLOCK' : 'ARCHIVE 2017'}</span>
          </button>

          <button
            onClick={() => {
              onToggleSound();
            }}
            className="flex items-center gap-1 hover:text-cyan-300 transition-colors px-2 py-0.5 rounded border border-cyan-500/30 bg-cyan-950/40"
            title="Toggle Web Audio Synthesizer SFX"
          >
            {soundEnabled ? (
              <Volume2 className="w-3 h-3 text-cyan-400" />
            ) : (
              <VolumeX className="w-3 h-3 text-red-400" />
            )}
            <span className="hidden sm:inline">{soundEnabled ? 'SFX: ON' : 'SFX: MUTED'}</span>
          </button>
        </div>
      </div>

      {/* Main Slanted Sci-Fi HUD Bracket Frame */}
      <div className="relative w-full max-w-5xl">
        {/* SVG Slanted Sci-Fi Border & Background */}
        <svg
          className="w-full h-24 sm:h-28 overflow-visible"
          viewBox="0 0 1000 110"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="hudHeaderGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={theme.primaryHex} stopOpacity="0.12" />
              <stop offset="100%" stopColor={theme.primaryHex} stopOpacity="0.02" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background Polygon */}
          <polygon
            points="20,0 980,0 930,105 70,105"
            fill="url(#hudHeaderGrad)"
            stroke={theme.primaryHex}
            strokeWidth="1.5"
            strokeOpacity="0.8"
          />

          {/* Top Notch Accents */}
          <line x1="120" y1="0" x2="880" y2="0" stroke={theme.primaryHex} strokeWidth="3" strokeOpacity="0.9" />
          <line x1="250" y1="0" x2="750" y2="0" stroke={theme.accentHex} strokeWidth="2" strokeOpacity="0.8" />

          {/* Corner Tech Ticks */}
          <line x1="15" y1="0" x2="5" y2="20" stroke={theme.primaryHex} strokeWidth="2" />
          <line x1="985" y1="0" x2="995" y2="20" stroke={theme.primaryHex} strokeWidth="2" />
          <line x1="65" y1="105" x2="55" y2="90" stroke={theme.primaryHex} strokeWidth="2" />
          <line x1="935" y1="105" x2="945" y2="90" stroke={theme.primaryHex} strokeWidth="2" />

          {/* Diagonal Corner Cuts */}
          <path d="M 68 105 L 75 90 L 925 90 L 932 105" fill="none" stroke={theme.primaryHex} strokeWidth="1" strokeOpacity="0.4" />
        </svg>

        {/* Header Inner Content Overlay */}
        <div className="absolute inset-0 flex items-center justify-between px-6 sm:px-14 pb-2">
          {/* Left Corner Mini Readout */}
          <div className="hidden lg:flex flex-col text-[10px] text-cyan-400/70 font-mono leading-tight">
            <span className="tracking-widest font-semibold text-cyan-300">GEO-STATION: ALPHA</span>
            <span className="text-cyan-500/60">LAT: 43.3603° N</span>
            <span className="text-cyan-500/60">LON: 5.8448° W</span>
            <span className="text-orange-400 font-bold mt-0.5 tracking-wider">{time.dayOfWeek}</span>
          </div>

          {/* Center Date & Big Orange Day Box */}
          <div className="flex items-center gap-3 sm:gap-5 mx-auto lg:mx-0">
            {/* Month & Year */}
            <div className="flex flex-col items-end text-right">
              <span
                className="text-xl sm:text-2xl font-black tracking-[0.25em] text-cyan-300"
                style={{
                  fontFamily: "'Orbitron', 'Chakra Petch', sans-serif",
                  textShadow: `0 0 12px ${theme.primaryGlow}`,
                }}
              >
                {time.month}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-cyan-400/60 font-mono tracking-widest">{time.timeStr}</span>
                <span
                  className="text-sm sm:text-base font-bold tracking-[0.2em] text-cyan-400"
                  style={{ fontFamily: "'Orbitron', sans-serif" }}
                >
                  {time.year}
                </span>
              </div>
            </div>

            {/* Giant Orange Day Block matching the screenshot */}
            <div
              className="relative px-3 sm:px-4 py-0.5 sm:py-1 rounded bg-orange-600/90 text-black border-2 border-orange-400 font-black shadow-[0_0_20px_rgba(255,84,0,0.6)] flex items-center justify-center min-w-[52px] sm:min-w-[64px]"
              style={{
                clipPath: 'polygon(0 0, 100% 0, 100% 85%, 85% 100%, 0 100%)',
              }}
            >
              <span
                className="text-2xl sm:text-4xl leading-none text-black font-black tracking-tight"
                style={{ fontFamily: "'Orbitron', sans-serif" }}
              >
                {time.day}
              </span>
              {/* Little corner cut accent */}
              <div className="absolute bottom-0 right-0 w-2 h-2 bg-black border-l border-t border-orange-300" />
            </div>
          </div>

          {/* Right Task For Today List */}
          <div className="flex flex-col items-start min-w-[200px] sm:min-w-[260px] max-w-[320px]">
            <div className="flex items-center justify-between w-full border-b border-cyan-500/40 pb-0.5 mb-1">
              <span
                className="text-[11px] sm:text-xs font-bold tracking-widest text-cyan-300 flex items-center gap-1.5"
                style={{ fontFamily: "'Orbitron', sans-serif" }}
              >
                <span className="w-1.5 h-1.5 bg-orange-500 rounded-sm" />
                TASK FOR TODAY:
              </span>
              <button
                onClick={() => {
                  sound.playClick();
                  setIsAddingTask(!isAddingTask);
                }}
                className="text-[10px] text-cyan-400 hover:text-cyan-200 flex items-center gap-0.5 bg-cyan-950/60 px-1.5 py-0.2 rounded border border-cyan-500/40"
              >
                <Plus className="w-2.5 h-2.5" />
                <span>ADD</span>
              </button>
            </div>

            {/* Tasks list */}
            <div className="flex flex-col gap-0.5 max-h-[58px] overflow-y-auto w-full pr-1 scrollbar-thin scrollbar-thumb-cyan-500/40">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  onClick={() => {
                    sound.playClick(task.completed ? 900 : 1400);
                    onToggleTask(task.id);
                  }}
                  className={`group cursor-pointer flex items-center gap-1.5 text-[9px] sm:text-[10px] font-mono tracking-wider transition-colors py-0.5 px-1 rounded hover:bg-cyan-950/50 ${
                    task.completed
                      ? 'text-cyan-500/40 line-through'
                      : 'text-cyan-300/90 hover:text-cyan-100'
                  }`}
                >
                  <span
                    className={`w-2.5 h-2.5 flex items-center justify-center rounded-[2px] border text-[8px] transition-colors ${
                      task.completed
                        ? 'border-cyan-500/40 bg-cyan-900/60 text-cyan-300'
                        : 'border-cyan-400/60 group-hover:border-cyan-300'
                    }`}
                  >
                    {task.completed && <Check className="w-2 h-2" />}
                  </span>
                  <span className="truncate">{task.text}</span>
                </div>
              ))}
            </div>

            {/* Quick Add Task Popover */}
            <AnimatePresence>
              {isAddingTask && (
                <motion.form
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  onSubmit={handleTaskSubmit}
                  className="absolute top-full right-4 sm:right-14 mt-2 p-2 bg-[#040e1a] border border-cyan-500/70 rounded shadow-xl flex gap-1 z-50 backdrop-blur-md"
                >
                  <input
                    type="text"
                    value={newTaskText}
                    onChange={(e) => setNewTaskText(e.target.value)}
                    placeholder="ENTER HUD TASK..."
                    autoFocus
                    className="bg-black/80 border border-cyan-500/50 text-cyan-300 text-xs px-2 py-1 rounded focus:outline-none focus:border-cyan-400 w-48 font-mono placeholder:text-cyan-700"
                  />
                  <button
                    type="submit"
                    className="bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-bold px-2 py-1 rounded transition-colors font-mono"
                  >
                    ADD
                  </button>
                </motion.form>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  );
};
