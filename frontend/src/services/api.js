import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor to attach JWT token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Location & Weather APIs
export const searchLocationsAPI = async (query) => {
  try {
    const response = await apiClient.get('/api/v1/location/search', {
      params: { query },
    });
    return response.data;
  } catch (error) {
    console.error('Location search error:', error);
    return [];
  }
};

export const fetchLiveWeatherAPI = async (latitude, longitude) => {
  try {
    const response = await apiClient.get('/api/v1/weather/live', {
      params: { latitude, longitude },
    });
    return response.data;
  } catch (error) {
    console.error('Weather fetch error:', error);
    return null;
  }
};

export const predictDisasterRiskAPI = async (latitude, longitude, locationName) => {
  try {
    const response = await apiClient.post('/api/v1/predict', {
      latitude,
      longitude,
      location_name: locationName,
    });
    return response.data;
  } catch (error) {
    console.error('Prediction API error:', error);
    throw error;
  }
};

export const simulateWhatIfAPI = async (payload) => {
  try {
    const response = await apiClient.post('/api/v1/predict/what-if', payload);
    return response.data;
  } catch (error) {
    console.error('What-If simulation error:', error);
    throw error;
  }
};

export const fetchAdminStatsAPI = async () => {
  try {
    const response = await apiClient.get('/api/v1/admin/stats');
    return response.data;
  } catch (error) {
    console.error('Admin stats fetch error:', error);
    throw error;
  }
};

export const fetchHistoryAPI = async (locationName) => {
  try {
    const response = await apiClient.get('/api/v1/history/location', {
      params: { location_name: locationName },
    });
    return response.data;
  } catch (error) {
    console.error('History fetch error:', error);
    return [];
  }
};

// --- AUTHENTICATION & USER MANAGEMENT APIS ---

export const registerUserAPI = async (payload) => {
  const response = await apiClient.post('/api/v1/auth/register', payload);
  return response.data;
};

export const verifyOtpAPI = async (payload) => {
  const response = await apiClient.post('/api/v1/auth/verify-otp', payload);
  return response.data;
};

export const resendOtpAPI = async (payload) => {
  const response = await apiClient.post('/api/v1/auth/resend-otp', payload);
  return response.data;
};

export const loginUserAPI = async (payload) => {
  const response = await apiClient.post('/api/v1/auth/login', payload);
  return response.data;
};

export const forgotPasswordAPI = async (payload) => {
  const response = await apiClient.post('/api/v1/auth/forgot-password', payload);
  return response.data;
};

export const resetPasswordAPI = async (payload) => {
  const response = await apiClient.post('/api/v1/auth/reset-password', payload);
  return response.data;
};

export const fetchUserProfileAPI = async () => {
  const response = await apiClient.get('/api/v1/auth/me');
  return response.data;
};

export const fetchUserHistoryAPI = async () => {
  const response = await apiClient.get('/api/v1/history/user');
  return response.data;
};

export default apiClient;
