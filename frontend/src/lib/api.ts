import axios from 'axios';
import { API_BASE_URL } from './constants';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor - no token attachment needed (mock auth)
api.interceptors.request.use(
  (config) => {
    // No token attachment - using mock auth
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 401) {
        // Unauthorized - clear user data and redirect to login
        localStorage.removeItem('user_data');
        // Redirect to login if we're in the browser
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
      
      // Return error with message
      return Promise.reject({
        message: data?.detail || data?.message || 'An error occurred',
        status,
        data,
      });
    } else if (error.request) {
      // Request made but no response received
      return Promise.reject({
        message: 'Network error. Please check your connection.',
        status: 0,
      });
    } else {
      // Something else happened
      return Promise.reject({
        message: error.message || 'An unexpected error occurred',
        status: 0,
      });
    }
  }
);

export default api;

