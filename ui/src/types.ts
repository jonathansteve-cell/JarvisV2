export interface DriveData {
  id: string;
  letter: string;
  label: string;
  total: string;
  used: string;
  free: string;
  usedPercent: number;
  freePercent: number;
  temp: number;
  cacheTotal: string;
  cacheRead: string;
  cacheWrite: string;
  spectrum: number[];
  color?: string;
}

export interface TaskItem {
  id: string;
  text: string;
  completed: boolean;
  priority?: 'HIGH' | 'MED' | 'LOW';
}

export interface ProcessItem {
  id: string;
  name: string;
  status: 'ACTIVE' | 'IDLE' | 'BUSY';
  cpu: number;
  memory: string;
}

export interface WeatherData {
  location: string;
  country: string;
  updatedTime: string;
  temp: number;
  tempUnit: 'C' | 'F';
  condition: string;
  humidity: number;
  feelsLike: number;
  precipitation: number;
  visibility: number;
  windSpeed: number;
  windDirection: string;
  pressure: number;
  sunrise: string;
  sunset: string;
}

export type HudTheme = 'classic-cyan' | 'matrix-green' | 'cyber-magenta' | 'solar-amber';
