// F1 HPC Racing - TypeScript Type Definitions

export interface TelemetryPoint {
  x: number;
  y: number;
  z: number;
  speed: number;
  throttle: number;
  brake: number | boolean;
  gear: number;
  rpm: number;
  time?: number;
  distance?: number;
  drs?: number;
  steering_angle?: number;
}

export interface DriverData {
  source: string;
  event: string;
  session: string;
  driver: string;
  driver_abbr: string;
  driver_number?: number;
  team: string;
  team_color: string;
  lap_time: number;
  telemetry_points: number;
  telemetry: TelemetryPoint[];
  sector1_time?: number;
  sector2_time?: number;
  sector3_time?: number;
  max_speed?: number;
  avg_speed?: number;
}

export interface DriverSummary {
  driver: string;
  driver_abbr: string;
  team: string;
  team_color: string;
  lap_time: number;
  telemetry_points: number;
}

export interface HPCStats {
  total_scenarios: number;
  database_size_mb: number;
  avg_lookup_time_ms: number;
  traditional_compute_time_s?: number;
  speedup_factor: number;
}

export interface DriversResponse {
  drivers: DriverSummary[];
}
