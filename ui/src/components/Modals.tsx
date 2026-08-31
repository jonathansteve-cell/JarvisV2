import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, HardDrive, ShieldAlert, CloudRain, Cpu, Radio, CheckCircle, Terminal } from 'lucide-react';
import { DriveData, WeatherData } from '../types';
import { ThemeConfig } from '../utils/theme';
import { sound } from '../utils/audio';

interface ModalsProps {
  theme: ThemeConfig;
  selectedDrive: DriveData | null;
  onCloseDrive: () => void;
  isDiagnosticActive: boolean;
  onCloseDiagnostic: () => void;
  isWeatherOpen: boolean;
  onCloseWeather: () => void;
  weather: WeatherData;
  activeAppModal: string | null;
  onCloseAppModal: () => void;
}

export const Modals: React.FC<ModalsProps> = ({
  theme,
  selectedDrive,
  onCloseDrive,
  isDiagnosticActive,
  onCloseDiagnostic,
  isWeatherOpen,
  onCloseWeather,
  weather,
  activeAppModal,
  onCloseAppModal,
}) => {
  return (
    <AnimatePresence>
      {/* 1. Drive Details Modal */}
      {selectedDrive && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md font-mono"
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            className="relative w-full max-w-lg p-5 rounded border border-cyan-400 bg-[#040e1a] shadow-[0_0_30px_rgba(0,229,255,0.3)] text-cyan-300"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-cyan-500/40 pb-2 mb-4">
              <div className="flex items-center gap-2">
                <HardDrive className="w-5 h-5 text-cyan-400" />
                <span className="text-sm font-bold tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                  VOLUME TELEMETRY: DRIVE [{selectedDrive.letter}:\]
                </span>
              </div>
              <button
                onClick={() => {
                  sound.playClick();
                  onCloseDrive();
                }}
                className="p-1 rounded hover:bg-cyan-950/60 text-cyan-400 hover:text-cyan-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <div className="p-2 rounded bg-black/50 border border-cyan-500/30">
                  <div className="text-[10px] text-cyan-500/70">TOTAL CAPACITY</div>
                  <div className="text-base font-bold text-cyan-300">{selectedDrive.total}</div>
                </div>
                <div className="p-2 rounded bg-black/50 border border-orange-500/30">
                  <div className="text-[10px] text-orange-500/70">ALLOCATED</div>
                  <div className="text-base font-bold text-orange-400">{selectedDrive.used}</div>
                </div>
                <div className="p-2 rounded bg-black/50 border border-cyan-500/30">
                  <div className="text-[10px] text-cyan-500/70">UNALLOCATED</div>
                  <div className="text-base font-bold text-cyan-200">{selectedDrive.free}</div>
                </div>
                <div className="p-2 rounded bg-black/50 border border-cyan-500/30">
                  <div className="text-[10px] text-cyan-500/70">TEMPERATURE</div>
                  <div className="text-base font-bold text-cyan-300">{selectedDrive.temp} °C</div>
                </div>
              </div>

              {/* Progress bar */}
              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span>STORAGE OCCUPANCY</span>
                  <span className="font-bold">{selectedDrive.usedPercent.toFixed(1)}%</span>
                </div>
                <div className="w-full h-4 rounded bg-cyan-950/80 border border-cyan-500/50 overflow-hidden flex">
                  <div
                    className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(0,229,255,0.6)]"
                    style={{ width: `${selectedDrive.usedPercent}%` }}
                  />
                  <div
                    className="h-full bg-orange-500/60"
                    style={{ width: `${selectedDrive.freePercent}%` }}
                  />
                </div>
              </div>

              {/* Simulated Sector Health */}
              <div className="p-3 rounded bg-black/40 border border-cyan-500/30 space-y-1.5">
                <div className="font-bold text-cyan-400 flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-cyan-400" />
                  S.M.A.R.T. SECTOR INTEGRITY: 100% HEALTHY
                </div>
                <div className="text-[10px] text-cyan-500/70 flex justify-between">
                  <span>FILE SYSTEM: NTFS SECURE ENCRYPTED</span>
                  <span>CACHE: {selectedDrive.cacheTotal} ACTIVE</span>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* 2. Diagnostic Sweep Modal */}
      {isDiagnosticActive && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-lg font-mono"
        >
          <div className="relative w-full max-w-md p-6 rounded border-2 border-cyan-400 bg-[#020b14] text-cyan-300 shadow-[0_0_40px_rgba(0,229,255,0.5)]">
            <div className="flex items-center justify-between border-b border-cyan-500/40 pb-2 mb-4">
              <span className="font-black text-sm tracking-widest text-cyan-300 flex items-center gap-2" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                <ShieldAlert className="w-5 h-5 text-orange-400 animate-pulse" />
                SYSTEM DIAGNOSTIC SWEEP
              </span>
              <button
                onClick={onCloseDiagnostic}
                className="text-cyan-400 hover:text-cyan-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="relative h-2 bg-cyan-950 border border-cyan-500/60 rounded overflow-hidden">
                <motion.div
                  className="h-full bg-cyan-400"
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{ duration: 1.8, ease: 'easeInOut' }}
                />
              </div>

              <div className="p-3 bg-black/60 rounded border border-cyan-500/30 text-[10px] space-y-1">
                <div className="text-cyan-400">» CHECKING NEURAL CORE VOLTAGES ... [OK]</div>
                <div className="text-cyan-400">» VERIFYING PARTITIONS C:\\ - H:\\ ... [6 MOUNTED]</div>
                <div className="text-cyan-400">» SCANNING QUANTUM BUS BANDWIDTH ... [128.4 GB/s]</div>
                <div className="text-orange-400 font-bold">» STATUS: ALL SUB-SYSTEMS NOMINAL</div>
              </div>

              <button
                onClick={onCloseDiagnostic}
                className="w-full py-2 bg-cyan-500 hover:bg-cyan-400 text-black font-black text-xs rounded transition-colors tracking-widest"
                style={{ fontFamily: "'Orbitron', sans-serif" }}
              >
                CONFIRM & RETURN
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* 3. Weather Modal */}
      {isWeatherOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md font-mono"
        >
          <div className="relative w-full max-w-md p-5 rounded border border-cyan-400 bg-[#040e1a] text-cyan-300 shadow-[0_0_30px_rgba(0,229,255,0.3)]">
            <div className="flex items-center justify-between border-b border-cyan-500/40 pb-2 mb-3">
              <span className="font-bold text-sm tracking-wider" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                METEOROLOGICAL SATELLITE HUD
              </span>
              <button onClick={onCloseWeather} className="text-cyan-400 hover:text-cyan-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-3 rounded bg-black/50 border border-cyan-500/30">
                <div>
                  <div className="text-base font-bold text-cyan-200">{weather.location}</div>
                  <div className="text-[10px] text-cyan-500/70">RADAR FREQUENCY: 5.4 GHZ</div>
                </div>
                <div className="text-2xl font-black text-cyan-300" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                  {weather.temp}°{weather.tempUnit}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div className="p-2 bg-black/40 rounded border border-cyan-500/30">
                  <span className="text-cyan-500/60">CONDITIONS:</span>
                  <span className="text-orange-400 font-bold block">{weather.condition}</span>
                </div>
                <div className="p-2 bg-black/40 rounded border border-cyan-500/30">
                  <span className="text-cyan-500/60">HUMIDITY:</span>
                  <span className="text-cyan-200 font-bold block">{weather.humidity}%</span>
                </div>
                <div className="p-2 bg-black/40 rounded border border-cyan-500/30">
                  <span className="text-cyan-500/60">WIND:</span>
                  <span className="text-cyan-200 font-bold block">{weather.windSpeed} KM/H {weather.windDirection}</span>
                </div>
                <div className="p-2 bg-black/40 rounded border border-cyan-500/30">
                  <span className="text-cyan-500/60">BAROMETRIC PRESSURE:</span>
                  <span className="text-cyan-200 font-bold block">{weather.pressure} HPA</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* 4. App Launcher Modal */}
      {activeAppModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md font-mono"
        >
          <div className="relative w-full max-w-md p-5 rounded border border-cyan-400 bg-[#040e1a] text-cyan-300 shadow-[0_0_30px_rgba(0,229,255,0.3)]">
            <div className="flex items-center justify-between border-b border-cyan-500/40 pb-2 mb-3">
              <span className="font-bold text-sm tracking-wider flex items-center gap-2" style={{ fontFamily: "'Orbitron', sans-serif" }}>
                <Terminal className="w-4 h-4 text-cyan-400" />
                EXECUTE MODULE: {activeAppModal}
              </span>
              <button onClick={onCloseAppModal} className="text-cyan-400 hover:text-cyan-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <p className="text-cyan-400/80 text-[11px]">
                Subsystem binary initialized in quantum container sandbox. Process PID allocated.
              </p>
              <div className="p-2.5 rounded bg-black/60 border border-cyan-500/30 text-[10px] text-cyan-300">
                STATUS: READY [THREAD PRIORITY: REALTIME]
              </div>
              <button
                onClick={onCloseAppModal}
                className="w-full py-1.5 bg-cyan-500 hover:bg-cyan-400 text-black font-bold rounded text-xs transition-colors font-mono"
              >
                DISMISS
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
