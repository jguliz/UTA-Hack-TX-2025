// F1 HPC Racing - API Service Layer
import type { DriverData, DriversResponse, HPCStats } from '../types';

const API_BASE_URL = 'http://localhost:8080/api';

class APIService {
  private async fetchJSON<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    return response.json();
  }

  async getLeclercTelemetry(): Promise<DriverData> {
    return this.fetchJSON<DriverData>('/telemetry/leclerc');
  }

  async getAIOptimalTelemetry(): Promise<DriverData> {
    return this.fetchJSON<DriverData>('/telemetry/ai_optimal');
  }

  async getAllDrivers(): Promise<DriversResponse> {
    return this.fetchJSON<DriversResponse>('/telemetry/all_drivers');
  }

  async getHPCStats(): Promise<HPCStats> {
    return this.fetchJSON<HPCStats>('/hpc/scenarios');
  }
}

export const apiService = new APIService();
