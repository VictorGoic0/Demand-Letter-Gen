import api from '../lib/api';

export async function login(email, password) {
  try {
    const response = await api.post('/login', { email, password });
    return response.data;
  } catch (error) {
    throw new Error(error.message || 'Login failed');
  }
}

export function logout() {
  // Clear any stored auth data
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_data');
}

export async function getCurrentUser() {
  try {
    const response = await api.get('/auth/me');
    return response.data;
  } catch (error) {
    return null;
  }
}

