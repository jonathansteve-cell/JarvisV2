// Live bridge between the CyberHUD React shell and the Jarvis V2 Python backend.
//
//   GET  /api/state    -> full telemetry snapshot (polled)
//   POST /api/command  -> natural-language command through the Jarvis pipeline
//
// The Python API is snake_case; the HUD components are camelCase, so this module
// is the single place that translates between them.

import { useCallback, useEffect, useRef, useState } from 'react';
import { DriveData, ProcessItem, TaskItem, WeatherData } from '../types';

// ---------------------------------------------------------------------------
// Raw API shapes (snake_case, straight off dashboard/server.py)
// ---------------------------------------------------------------------------

export interface ApiSystem {
  cpu: number | null;
  mem: number | null;
  disk: number | null;
  battery: number | null;
}

export interface ApiDrive {
  id: string;
  letter: string;
  label: string;
  mountpoint: string;
  filesystem: string;
  total: string;
  used: string;
  free: string;
  used_percent: number;
  free_percent: number;
  temp: number | null;
  cache_total: string | null;
  cache_read: string | null;
  cache_write: string | null;
}

export interface ApiProcess {
  id: string;
  pid: number;
  name: string;
  status: 'ACTIVE' | 'IDLE' | 'BUSY';
  cpu: number;
  memory: string;
}

export interface ApiTask {
  id: string;
  text: string;
  done: boolean;
  time: string;
}

export interface ApiWeather {
  location: string;
  country: string;
  updated_time: string;
  temp: number;
  temp_unit: 'C' | 'F';
  condition: string;
  humidity: number;
  feels_like: number;
  precipitation: number;
  visibility: number;
  wind_speed: number;
  wind_direction: string;
  pressure: number;
  sunrise: string;
  sunset: string;
}

export interface ApiNet {
  percent: number;
  rate_mbps: number;
  sent: string;
  received: string;
}

export interface ApiGpu {
  name: string;
  percent: number;
  memory_percent: number;
  temp: number;
}

export interface JarvisState {
  time: string;
  assistant_name: string;
  system: ApiSystem;
  ai: { groq_ready: boolean; model: string };
  voice: { available: boolean };
  memory: { stats: Record<string, number>; facts: { key: string; value: string }[] };
  productivity: { tasks: ApiTask[]; notes: { text: string }[] };
  roblox: {
    session: { focus: string; minutes: number; remaining: number } | null;
    goals: { text: string; done: boolean }[];
    sessions_logged: number;
    total_minutes: number;
  };
  conversations: { command: string; response: string; time: string }[];
  drives: ApiDrive[];
  processes: ApiProcess[];
  net: ApiNet | null;
  gpu: ApiGpu | null;
  weather: ApiWeather | null;
  uptime: string;
}

export interface CommandResult {
  text?: string;
  success?: boolean;
  intent?: string;
  provider?: string;
  error?: string;
}

/** Everything the HUD renders, already in component-ready camelCase. */
export interface HudData {
  drives: DriveData[];
  tasks: TaskItem[];
  processes: ProcessItem[];
  weather: WeatherData | null;
  gauges: { cpu: number | null; ram: number | null; gpu: number | null; net: number | null };
}

// ---------------------------------------------------------------------------
// Transport
// ---------------------------------------------------------------------------

export class BackendOfflineError extends Error {
  constructor() {
    super('Jarvis backend is not reachable');
    this.name = 'BackendOfflineError';
  }
}

async function parseResponse(response: Response): Promise<unknown> {
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    // A 503 with the "build the UI" HTML page, or a proxy error page.
    throw new BackendOfflineError();
  }
}

export async function fetchState(): Promise<JarvisState> {
  let response: Response;
  try {
    response = await fetch('/api/state', { headers: { Accept: 'application/json' } });
  } catch {
    throw new BackendOfflineError();
  }
  if (!response.ok) throw new BackendOfflineError();
  const data = (await parseResponse(response)) as JarvisState;
  if (!data || typeof data !== 'object' || !('system' in data)) {
    throw new BackendOfflineError();
  }
  return data;
}

export async function postCommand(command: string): Promise<CommandResult> {
  const response = await fetch('/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command }),
  });
  return (await parseResponse(response)) as CommandResult;
}

// ---------------------------------------------------------------------------
// Mapping
// ---------------------------------------------------------------------------

const clamp = (value: number, low = 0, high = 100) =>
  Math.min(high, Math.max(low, value));

/**
 * The drive card draws a 15-bar spectrum. It is decorative, so it is derived
 * deterministically from the real fill level rather than shipped as fake data —
 * a fuller drive gets a taller, flatter curve.
 */
function spectrumFor(usedPercent: number): number[] {
  const fill = clamp(usedPercent) / 100;
  return Array.from({ length: 15 }, (_, i) => {
    const decay = 1 - i / 15;
    return Number((fill * 0.55 + decay * 0.45).toFixed(2));
  });
}

export function mapDrives(drives: ApiDrive[] | undefined): DriveData[] {
  return (drives ?? []).map((drive) => ({
    id: drive.id,
    letter: drive.letter,
    label: drive.label,
    total: drive.total,
    used: drive.used,
    free: drive.free,
    usedPercent: clamp(drive.used_percent),
    freePercent: clamp(drive.free_percent),
    temp: drive.temp ?? 0,
    cacheTotal: drive.cache_total ?? '—',
    cacheRead: drive.cache_read ?? '—',
    cacheWrite: drive.cache_write ?? '—',
    spectrum: spectrumFor(drive.used_percent),
  }));
}

export function mapTasks(tasks: ApiTask[] | undefined): TaskItem[] {
  return (tasks ?? []).map((task, index) => ({
    id: task.id || `task-${index}`,
    text: (task.text || '').toUpperCase(),
    completed: task.done,
  }));
}

export function mapProcesses(processes: ApiProcess[] | undefined): ProcessItem[] {
  return (processes ?? []).map((proc) => ({
    id: proc.id,
    name: proc.name,
    status: proc.status,
    cpu: Math.round(proc.cpu),
    memory: proc.memory,
  }));
}

export function mapWeather(weather: ApiWeather | null | undefined): WeatherData | null {
  if (!weather) return null;
  return {
    location: weather.location,
    country: weather.country,
    updatedTime: weather.updated_time,
    temp: weather.temp,
    tempUnit: weather.temp_unit,
    condition: weather.condition,
    humidity: weather.humidity,
    feelsLike: weather.feels_like,
    precipitation: weather.precipitation,
    visibility: weather.visibility,
    windSpeed: weather.wind_speed,
    windDirection: weather.wind_direction,
    pressure: weather.pressure,
    sunrise: weather.sunrise,
    sunset: weather.sunset,
  };
}

export function mapState(state: JarvisState): HudData {
  return {
    drives: mapDrives(state.drives),
    tasks: mapTasks(state.productivity?.tasks),
    processes: mapProcesses(state.processes),
    weather: mapWeather(state.weather),
    gauges: {
      cpu: state.system?.cpu ?? null,
      ram: state.system?.mem ?? null,
      gpu: state.gpu ? clamp(state.gpu.percent) : null,
      net: state.net ? clamp(state.net.percent) : null,
    },
  };
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export interface UseJarvisOptions {
  /** Poll interval in ms. Default 2000 — matches the desktop HUD's refresh. */
  pollMs?: number;
  /** Stop polling entirely (sleep mode). */
  paused?: boolean;
}

export interface UseJarvisResult {
  hud: HudData | null;
  state: JarvisState | null;
  connected: boolean;
  lastError: string | null;
  lastUpdated: Date | null;
  refresh: () => void;
  runCommand: (command: string) => Promise<CommandResult | null>;
  sending: boolean;
}

export function useJarvis(options: UseJarvisOptions = {}): UseJarvisResult {
  const { pollMs = 2000, paused = false } = options;

  const [state, setState] = useState<JarvisState | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [sending, setSending] = useState(false);
  const [tick, setTick] = useState(0);

  // Keep an in-flight guard so a slow response cannot pile up behind the poller.
  const inFlight = useRef(false);

  const load = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    try {
      const next = await fetchState();
      setState(next);
      setConnected(true);
      setLastError(null);
      setLastUpdated(new Date());
    } catch (error) {
      setConnected(false);
      setLastError(error instanceof Error ? error.message : 'unknown error');
    } finally {
      inFlight.current = false;
    }
  }, []);

  useEffect(() => {
    if (paused) return;
    load();
    const timer = window.setInterval(load, pollMs);
    return () => window.clearInterval(timer);
  }, [load, pollMs, paused]);

  const runCommand = useCallback(async (command: string) => {
    const trimmed = command.trim();
    if (!trimmed) return null;
    setSending(true);
    try {
      const result = await postCommand(trimmed);
      await load(); // reflect the side effect immediately
      return result;
    } catch (error) {
      setConnected(false);
      setLastError(error instanceof Error ? error.message : 'command failed');
      return null;
    } finally {
      setSending(false);
    }
  }, [load]);

  return {
    hud: state ? mapState(state) : null,
    state,
    connected,
    lastError,
    lastUpdated,
    refresh: () => {
      setTick((value) => value + 1);
      void load();
    },
    runCommand,
    sending,
  };
  // `tick` intentionally forces a manual refresh identity change.
  // eslint-disable-next-line react-hooks/exhaustive-deps
}
