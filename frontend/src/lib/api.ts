import axios from 'axios';
import { API_BASE_URL } from './constants';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor - add user context (firmId, userId) to requests
api.interceptors.request.use(
  (config) => {
    // Get user data from localStorage for request context
    // This ensures firmId and userId are available even if AuthContext hasn't loaded yet
    try {
      const userData = localStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        
        // Add firmId and userId as headers for backend to use if needed
        // Backend can read these headers for logging, auditing, or validation
        if (user.firmId) {
          config.headers['X-Firm-Id'] = user.firmId;
        }
        if (user.userId) {
          config.headers['X-User-Id'] = user.userId;
        }
      }
    } catch (error) {
      // Silently fail - don't break requests if localStorage is unavailable
      console.warn('Failed to read user data from localStorage in interceptor:', error);
    }
    
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
        // This handles cases where the session is invalid or user is not authenticated
        localStorage.removeItem('user_data');
        // Redirect to login if we're in the browser
        // This ensures unauthenticated users are redirected on page reload if session expired
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
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

