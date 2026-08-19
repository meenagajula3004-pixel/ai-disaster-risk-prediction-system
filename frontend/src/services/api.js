import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 12000,
});

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
    return null;
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

export default apiClient;
