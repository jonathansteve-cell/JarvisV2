import React, { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { DriveData, TaskItem, ProcessItem, WeatherData, HudTheme } from './types';
import { HUD_THEMES, ThemeConfig } from './utils/theme';
import { sound } from './utils/audio';
import { useJarvis } from './lib/api';
import { BackgroundGrid } from './components/BackgroundGrid';
import { HeaderBar } from './components/HeaderBar';
import { DriveTelemetryCard } from './components/DriveTelemetryCard';
import { CenterCoreHUD } from './components/CenterCoreHUD';
import { RecycleBinWidget } from './components/RecycleBinWidget';
import { QuickDockControls } from './components/QuickDockControls';
import { CommandConsole } from './components/CommandConsole';
import { Modals } from './components/Modals';

// ---------------------------------------------------------------------------
// Demo data. Rendered ONLY until the backend answers its first /api/state, so
// the HUD is never blank on a cold start or in a static preview. Once Jarvis is
// reachable, every panel is driven by real telemetry and none of this is used.
// ---------------------------------------------------------------------------
const DEMO_DRIVES: DriveData[] = [
  {
    id: 'demo-c',
    letter: 'C',
    label: 'SYSTEM PRIMARY',
    total: '931.5 GB',
    used: '749.7 GB',
    free: '181.8 GB',
    usedPercent: 81.0,
    freePercent: 19.0,
    temp: 27,
    cacheTotal: '355 KB',
    cacheRead: '261 KB',
    cacheWrite: '309 KB',
    spectrum: [0.9, 0.8, 0.7, 0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.08, 0.05],
  },
  {
    id: 'demo-d',
    letter: 'D',
    label: 'ARCHIVE VAULT',
    total: '1.81 TB',
    used: '1.35 TB',
    free: '466.0 GB',
    usedPercent: 74.9,
    freePercent: 25.1,
    temp: 29,
    cacheTotal: '228 KB',
    cacheRead: '120 KB',
    cacheWrite: '109 KB',
    spectrum: [0.85, 0.75, 0.7, 0.65, 0.55, 0.5, 0.42, 0.38, 0.3, 0.22, 0.18, 0.12, 0.1, 0.06, 0.04],
  },
  {
    id: 'demo-e',
    letter: 'E',
    label: 'QUANTUM WORKSPACE',
    total: '931.5 GB',
    used: '456.2 GB',
    free: '475.3 GB',
    usedPercent: 49.0,
    freePercent: 51.0,
    temp: 31,
    cacheTotal: '310 KB',
    cacheRead: '210 KB',
    cacheWrite: '261 KB',
    spectrum: [0.95, 0.88, 0.78, 0.68, 0.6, 0.5, 0.44, 0.35, 0.28, 0.22, 0.15, 0.12, 0.09, 0.05, 0.03],
  },
];

const DEMO_PROCESSES: ProcessItem[] = [
  { id: 'demo-p1', name: 'AWAITING UPLINK', status: 'IDLE', cpu: 0, memory: '—' },
];

const DEMO_TASKS: TaskItem[] = [
  { id: 'demo-t1', text: 'CONNECT THE JARVIS BACKEND', completed: false },
];

export default function App() {
  // Solar amber is the J.A.R.V.I.S V2 house style (black + orange).
  const [currentThemeKey, setCurrentThemeKey] = useState<HudTheme>('solar-amber');
  const theme: ThemeConfig = HUD_THEMES[currentThemeKey];

  const [selectedDrive, setSelectedDrive] = useState<DriveData | null>(null);
  const [showScanlines, setShowScanlines] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [isRealTime, setIsRealTime] = useState(true);
  const [isSleepMode, setIsSleepMode] = useState(false);

  // Modals
  const [isDiagnosticActive, setIsDiagnosticActive] = useState(false);
  const [isOverloadActive, setIsOverloadActive] = useState(false);
  const [isWeatherOpen, setIsWeatherOpen] = useState(false);
  const [activeAppModal, setActiveAppModal] = useState<string | null>(null);

  // Live backend. Sleep mode stops polling so the machine can idle.
  const { hud, state, connected, lastError, runCommand, sending } = useJarvis({
    paused: isSleepMode,
  });

  // Until the first successful poll we are in demo mode.
  const demoMode = state === null;

  const drives = useMemo<DriveData[]>(
    () => (demoMode ? DEMO_DRIVES : hud?.drives ?? []),
    [demoMode, hud]
  );
  const tasks = useMemo<TaskItem[]>(
    () => (demoMode ? DEMO_TASKS : hud?.tasks ?? []),
    [demoMode, hud]
  );
  const processes = useMemo<ProcessItem[]>(
    () => (demoMode ? DEMO_PROCESSES : hud?.processes ?? []),
    [demoMode, hud]
  );
  const weather: WeatherData | null = demoMode ? null : hud?.weather ?? null;

  // Split across the two side columns so a machine with 1-3 drives still
  // looks balanced instead of leaving the right column empty.
  const leftDrives = drives.filter((_, index) => index % 2 === 0).slice(0, 3);
  const rightDrives = drives.filter((_, index) => index % 2 === 1).slice(0, 3);

  // Task mutations go through the real Jarvis pipeline, so the HUD, the desktop
  // app and voice all see the same list.
  const handleToggleTask = (id: string) => {
    const task = tasks.find((item) => item.id === id);
    if (!task) return;
    sound.playClick();
    void runCommand(task.completed ? `reopen task ${task.text}` : `complete task ${task.text}`);
  };

  const handleAddTask = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    void runCommand(`add task ${trimmed}`);
  };

  // Process list is live telemetry — read-only. Killing a process by clicking a
  // HUD row is not something Jarvis should do on a mis-click.
  const handleToggleProcess = () => {
    sound.playClick(900);
  };

  // Theme Cycler
  const handleCycleTheme = () => {
    const themeKeys: HudTheme[] = ['solar-amber', 'classic-cyan', 'matrix-green', 'cyber-magenta'];
    const nextIdx = (themeKeys.indexOf(currentThemeKey) + 1) % themeKeys.length;
    setCurrentThemeKey(themeKeys[nextIdx]);
  };

  // Overload Shockwave
  const handleTriggerOverload = () => {
    setIsOverloadActive(true);
    setTimeout(() => {
      setIsOverloadActive(false);
    }, 1200);
  };

  const assistantName = state?.assistant_name ?? 'J.A.R.V.I.S';
  const coreStatus = demoMode
    ? 'CORE OFFLINE · DEMO TELEMETRY'
    : connected
      ? 'CORE ONLINE · LIVE TELEMETRY'
      : 'CORE UNREACHABLE · LAST KNOWN';

  return (
    <div
      className={`relative min-h-screen w-full select-none overflow-x-hidden flex flex-col justify-between transition-colors duration-700 ${
        isSleepMode ? 'opacity-40 brightness-50' : 'opacity-100'
      }`}
      style={{
        backgroundColor: theme.bgDark,
        color: theme.primaryHex,
      }}
    >
      {/* Background Starfield & Hologram Grid */}
      <BackgroundGrid theme={theme} showScanlines={showScanlines} />

      {/* Overload Surge Shockwave FX */}
      <AnimatePresence>
        {isOverloadActive && (
          <motion.div
            initial={{ opacity: 0.9, scale: 0.9 }}
            animate={{ opacity: 0, scale: 1.5 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
            className="fixed inset-0 pointer-events-none z-50 bg-gradient-radial from-orange-500/50 via-cyan-500/20 to-transparent"
          />
        )}
      </AnimatePresence>

      {/* Backend fault banner — only once we know the core is genuinely down */}
      <AnimatePresence>
        {!demoMode && !connected && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-0 left-0 right-0 z-[60] px-4 py-1.5 text-center text-[10px] font-mono tracking-widest bg-orange-600/90 text-black font-bold"
          >
            BACKEND UNREACHABLE — START IT WITH `python main.py --web`
            {lastError ? ` · ${lastError.toUpperCase()}` : ''}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Container Content */}
      <div className="relative z-10 flex flex-col justify-between min-h-screen w-full max-w-[1700px] mx-auto p-2 sm:p-4">
        {/* TOP HUD HEADER */}
        <HeaderBar
          theme={theme}
          tasks={tasks}
          onToggleTask={handleToggleTask}
          onAddTask={handleAddTask}
          isRealTime={isRealTime}
          onToggleRealTime={() => setIsRealTime(!isRealTime)}
          soundEnabled={soundEnabled}
          onToggleSound={() => {
            const next = !soundEnabled;
            setSoundEnabled(next);
            sound.setEnabled(next);
            if (next) sound.playConfirm();
          }}
        />

        {/* MIDDLE & MAIN TELEMETRY GRID */}
        <main className="flex-1 flex flex-col xl:flex-row items-center justify-between gap-4 sm:gap-6 my-2 sm:my-4 w-full">
          {/* LEFT DRIVE MODULES */}
          <div className="w-full xl:w-[320px] 2xl:w-[360px] flex flex-col gap-2.5 sm:gap-3 z-20">
            {leftDrives.map((drive) => (
              <DriveTelemetryCard
                key={drive.id}
                drive={drive}
                theme={theme}
                isSelected={selectedDrive?.id === drive.id}
                onSelect={(d) => setSelectedDrive(d)}
              />
            ))}
          </div>

          {/* CENTER CORE REACTOR HUD */}
          <div className="flex-1 flex items-center justify-center z-20 px-2">
            <CenterCoreHUD
              theme={theme}
              drives={drives}
              selectedDriveId={selectedDrive?.id}
              onSelectDrive={(d) => setSelectedDrive(d)}
              processes={processes}
              onToggleProcess={handleToggleProcess}
              weather={weather}
              onOpenWeatherModal={() => setIsWeatherOpen(true)}
              gauges={hud?.gauges}
              onOpenAppLauncher={(name) => {
                setActiveAppModal(name);
                sound.playConfirm();
              }}
            />
          </div>

          {/* RIGHT DRIVE MODULES */}
          <div className="w-full xl:w-[320px] 2xl:w-[360px] flex flex-col gap-2.5 sm:gap-3 z-20">
            {rightDrives.map((drive) => (
              <DriveTelemetryCard
                key={drive.id}
                drive={drive}
                theme={theme}
                isRightSide
                isSelected={selectedDrive?.id === drive.id}
                onSelect={(d) => setSelectedDrive(d)}
              />
            ))}
          </div>
        </main>

        {/* BOTTOM HUD DOCKS */}
        <footer className="relative w-full z-20 flex flex-col lg:flex-row items-center justify-between gap-3 pt-1 px-2 border-t border-cyan-500/20">
          {/* Bottom Left: Recycle Bin */}
          <RecycleBinWidget theme={theme} />

          {/* Center: live command console */}
          <CommandConsole
            theme={theme}
            connected={connected || demoMode}
            sending={sending}
            onSend={runCommand}
          />

          {/* Bottom Right: Quick Action Controls */}
          <QuickDockControls
            theme={theme}
            currentTheme={currentThemeKey}
            onCycleTheme={handleCycleTheme}
            showScanlines={showScanlines}
            onToggleScanlines={() => setShowScanlines(!showScanlines)}
            soundEnabled={soundEnabled}
            onToggleSound={() => {
              const next = !soundEnabled;
              setSoundEnabled(next);
              sound.setEnabled(next);
              if (next) sound.playConfirm();
            }}
            onTriggerDiagnostic={() => setIsDiagnosticActive(true)}
            onTriggerOverload={handleTriggerOverload}
            isSleepMode={isSleepMode}
            onToggleSleepMode={() => setIsSleepMode(!isSleepMode)}
          />
        </footer>

        {/* Status readout */}
        <div className="flex items-center justify-center gap-6 text-[9px] font-mono text-cyan-500/60 tracking-widest pt-1.5 pb-0.5">
          <span className={connected ? '' : 'text-orange-400 font-bold'}>{coreStatus}</span>
          <span>MODEL: {(state?.ai.model ?? 'unknown').toUpperCase()}</span>
          <span className="text-orange-400 font-bold">UPTIME: {state?.uptime ?? '--:--:--'}</span>
          <span>
            {assistantName.toUpperCase()} · {state?.ai.groq_ready ? 'AI READY' : 'AI KEY MISSING'}
          </span>
        </div>
      </div>

      {/* Interactive Modals & Overlays */}
      <Modals
        theme={theme}
        selectedDrive={selectedDrive}
        onCloseDrive={() => setSelectedDrive(null)}
        isDiagnosticActive={isDiagnosticActive}
        onCloseDiagnostic={() => setIsDiagnosticActive(false)}
        isWeatherOpen={isWeatherOpen}
        onCloseWeather={() => setIsWeatherOpen(false)}
        weather={weather}
        activeAppModal={activeAppModal}
        onCloseAppModal={() => setActiveAppModal(null)}
      />
    </div>
  );
}
