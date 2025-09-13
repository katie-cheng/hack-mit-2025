export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  endpoints: {
    users: '/users',
    register: '/register',
    alert: '/alert',
    health: '/health',
  }
} as const;

export const getApiUrl = (endpoint: keyof typeof API_CONFIG.endpoints) => {
  return `${API_CONFIG.baseURL}${API_CONFIG.endpoints[endpoint]}`;
};