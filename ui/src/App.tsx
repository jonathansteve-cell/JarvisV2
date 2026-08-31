import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { DriveData, TaskItem, ProcessItem, WeatherData, HudTheme } from './types';
import { HUD_THEMES, ThemeConfig } from './utils/theme';
import { sound } from './utils/audio';
import { BackgroundGrid } from './components/BackgroundGrid';
import { HeaderBar } from './components/HeaderBar';
import { DriveTelemetryCard } from './components/DriveTelemetryCard';
import { CenterCoreHUD } from './components/CenterCoreHUD';
import { RecycleBinWidget } from './components/RecycleBinWidget';
import { QuickDockControls } from './components/QuickDockControls';
import { Modals } from './components/Modals';

// Initial Mock Telemetry Data accurately matched to screenshot
const INITIAL_DRIVES: DriveData[] = [
  // Left side
  {
    id: 'drive-c',
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
    id: 'drive-d',
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
    id: 'drive-e',
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
  // Right side
  {
    id: 'drive-f',
    letter: 'F',
    label: 'SECONDARY BACKUP',
    total: '1.81 TB',
    used: '1.10 TB',
    free: '710.0 GB',
    usedPercent: 60.8,
    freePercent: 39.2,
    temp: 28,
    cacheTotal: '210 KB',
    cacheRead: '174 KB',
    cacheWrite: '194 KB',
    spectrum: [0.88, 0.82, 0.72, 0.64, 0.58, 0.48, 0.4, 0.32, 0.26, 0.2, 0.14, 0.1, 0.08, 0.05, 0.03],
  },
  {
    id: 'drive-g',
    letter: 'G',
    label: 'RENDER CACHE',
    total: '931.5 GB',
    used: '512.1 GB',
    free: '419.4 GB',
    usedPercent: 55.0,
    freePercent: 45.0,
    temp: 29,
    cacheTotal: '107 KB',
    cacheRead: '185 KB',
    cacheWrite: '353 KB',
    spectrum: [0.92, 0.84, 0.76, 0.66, 0.54, 0.46, 0.38, 0.3, 0.24, 0.18, 0.14, 0.09, 0.06, 0.04, 0.02],
  },
  {
    id: 'drive-h',
    letter: 'H',
    label: 'MEDIA STORAGE',
    total: '2.72 TB',
    used: '1.38 TB',
    free: '1.40 TB',
    usedPercent: 51.0,
    freePercent: 49.0,
    temp: 30,
    cacheTotal: '511 KB',
    cacheRead: '211 KB',
    cacheWrite: '251 KB',
    spectrum: [0.9, 0.85, 0.75, 0.68, 0.6, 0.52, 0.45, 0.38, 0.3, 0.25, 0.18, 0.12, 0.08, 0.05, 0.02],
  },
];

const INITIAL_TASKS: TaskItem[] = [
  { id: 't1', text: 'FINISH AFTER FX PROJECTS', completed: false },
  { id: 't2', text: 'CHECK NEW TUTORIAL', completed: false },
  { id: 't3', text: "GO TO JUSTIN'S PRD", completed: false },
  { id: 't4', text: 'MEET WITH FRIENDS', completed: false },
  { id: 't5', text: 'CALL MOM', completed: false },
];

const INITIAL_PROCESSES: ProcessItem[] = [
  { id: 'p1', name: 'MEDIA ENCODER', status: 'ACTIVE', cpu: 18, memory: '1.2 GB' },
  { id: 'p2', name: 'AFTER EFFECTS', status: 'ACTIVE', cpu: 32, memory: '4.8 GB' },
  { id: 'p3', name: 'PREMIERE PRO', status: 'ACTIVE', cpu: 24, memory: '3.1 GB' },
  { id: 'p4', name: 'CHARACTER ANIMATION', status: 'IDLE', cpu: 4, memory: '850 MB' },
  { id: 'p5', name: 'ILLUSTRATOR', status: 'ACTIVE', cpu: 12, memory: '1.6 GB' },
  { id: 'p6', name: 'PHOTOSHOP', status: 'ACTIVE', cpu: 15, memory: '2.4 GB' },
  { id: 'p7', name: 'CINEMA 4D', status: 'IDLE', cpu: 6, memory: '2.9 GB' },
];

const INITIAL_WEATHER: WeatherData = {
  location: 'OVIEDO/AVIL, UNITED STATES',
  country: 'US',
  updatedTime: '15:10:00 AM AT 17:00',
  temp: 15,
  tempUnit: 'C',
  condition: 'CLEAR',
  humidity: 72,
  feelsLike: 13,
  precipitation: 0,
  visibility: 10,
  windSpeed: 8,
  windDirection: 'SSW',
  pressure: 1017.3,
  sunrise: '07:11',
  sunset: '19:32',
};

export default function App() {
  const [currentThemeKey, setCurrentThemeKey] = useState<HudTheme>('classic-cyan');
  const theme: ThemeConfig = HUD_THEMES[currentThemeKey];

  const [drives, setDrives] = useState<DriveData[]>(INITIAL_DRIVES);
  const [tasks, setTasks] = useState<TaskItem[]>(INITIAL_TASKS);
  const [processes, setProcesses] = useState<ProcessItem[]>(INITIAL_PROCESSES);
  const [weather, setWeather] = useState<WeatherData>(INITIAL_WEATHER);

  const [selectedDrive, setSelectedDrive] = useState<DriveData | null>(null);
  const [showScanlines, setShowScanlines] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [isRealTime, setIsRealTime] = useState(false);
  const [isSleepMode, setIsSleepMode] = useState(false);

  // Modals
  const [isDiagnosticActive, setIsDiagnosticActive] = useState(false);
  const [isOverloadActive, setIsOverloadActive] = useState(false);
  const [isWeatherOpen, setIsWeatherOpen] = useState(false);
  const [activeAppModal, setActiveAppModal] = useState<string | null>(null);

  // Task Handlers
  const handleToggleTask = (id: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  };

  const handleAddTask = (text: string) => {
    const newTask: TaskItem = {
      id: `task-${Date.now()}`,
      text: text.toUpperCase(),
      completed: false,
    };
    setTasks((prev) => [newTask, ...prev]);
  };

  // Process Handlers
  const handleToggleProcess = (id: string) => {
    setProcesses((prev) =>
      prev.map((p) =>
        p.id === id
          ? {
              ...p,
              status: p.status === 'ACTIVE' ? 'IDLE' : 'ACTIVE',
              cpu: p.status === 'ACTIVE' ? 0 : Math.floor(Math.random() * 25 + 10),
            }
          : p
      )
    );
  };

  // Theme Cycler
  const handleCycleTheme = () => {
    const themeKeys: HudTheme[] = ['classic-cyan', 'matrix-green', 'cyber-magenta', 'solar-amber'];
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

  const leftDrives = drives.slice(0, 3);
  const rightDrives = drives.slice(3, 6);

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
          {/* LEFT 3 DRIVE MODULES */}
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
              onOpenAppLauncher={(name) => {
                setActiveAppModal(name);
                sound.playConfirm();
              }}
            />
          </div>

          {/* RIGHT 3 DRIVE MODULES */}
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

        {/* BOTTOM HUD DOCKS (Recycle Bin on Left, Quick Command Dock on Right) */}
        <footer className="relative w-full z-20 flex flex-col sm:flex-row items-center justify-between gap-3 pt-1 px-2 border-t border-cyan-500/20">
          {/* Bottom Left: Recycle Bin */}
          <RecycleBinWidget theme={theme} />

          {/* Center Subtle Status Readout */}
          <div className="hidden md:flex items-center gap-6 text-[9px] font-mono text-cyan-500/60 tracking-widest">
            <span>JARVIS CORE KERNEL: ONLINE</span>
            <span className="text-orange-400 font-bold">TELEMETRY FREQ: 60 FPS</span>
            <span>MEMORY ACCESS: DMA ENABLED</span>
          </div>

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
