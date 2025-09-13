// Homeowner registration types
export interface HomeownerRegistration {
  name: string;
  phoneNumber: string;
}

export interface HomeownerRegistrationResponse {
  success: boolean;
  homeowner_id?: string;
  qr_code?: string;
  message?: string;
}

// Smart home status types
export interface HomeStatus {
  battery_level: number;
  thermostat_temp: number;
  market_status: 'monitoring' | 'executing_sale' | 'success' | 'idle';
  energy_sold: number;
  profit_generated: number;
  solar_charging: boolean;
  ac_running: boolean;
  last_updated: string;
}

export interface HomeStatusResponse {
  success: boolean;
  status: HomeStatus;
  message?: string;
}

// Homeowner types
export interface Homeowner {
  id: string;
  name: string;
  phone_number: string;
  qr_code: string;
  registered_at: string;
}

export interface HomeownersResponse {
  total_homeowners: number;
  homeowners: Homeowner[];
}

// Weather event types
export interface WeatherEvent {
  event_type: 'heatwave' | 'storm' | 'cold_snap' | 'normal';
  probability: number;
  severity: 'low' | 'medium' | 'high' | 'extreme';
  predicted_time: string;
  description: string;
}

// Simulation types
export interface SimulationResponse {
  success: boolean;
  message: string;
  call_initiated: boolean;
  call_id?: string;
}

// Common API response wrapper
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
