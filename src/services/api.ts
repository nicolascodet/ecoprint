import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const auth = {
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    const response = await api.post('/api/token', formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (email: string, password: string, full_name: string) => {
    const response = await api.post('/api/register', {
      email,
      password,
      full_name,
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/user/stats');
    return response.data;
  },
};

export interface Analysis {
  main_sources: string[];
  patterns: string[];
  comparison: string;
  projection: string;
}

export interface AIAnalysisResponse {
  analysis: Analysis;
  suggestions: string[];
  total_activities: number;
  total_impact: number;
}

export const activities = {
  create: async (activity: {
    activity_type: string;
    description: string;
    carbon_impact: number;
  }) => {
    const response = await api.post('/api/activities', activity);
    return response.data;
  },

  getAll: async () => {
    const response = await api.get('/api/activities');
    return response.data;
  },

  getAnalysis: async (): Promise<AIAnalysisResponse> => {
    const response = await api.get('/api/activities/analysis');
    return response.data;
  },

  calculateTransportImpact: async (distance: number, mode: string) => {
    const response = await api.post('/api/calculate/transport', null, {
      params: { distance, mode },
    });
    return response.data;
  },

  calculateHomeEnergyImpact: async (energy_kwh: number, energy_type: string) => {
    const response = await api.post('/api/calculate/home-energy', null, {
      params: { energy_kwh, energy_type },
    });
    return response.data;
  },
};

export default api; 