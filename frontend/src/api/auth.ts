import api from '../lib/api';

export interface LoginResponse {
  email: string;
  userId: string;
  firmId: string;
  firmName: string;
}

export async function login(email: string): Promise<LoginResponse> {
  try {
    const response = await api.post<LoginResponse>('/login', { email });
    return response.data;
  } catch (error: any) {
    throw new Error(error.message || 'Login failed');
  }
}

export function logout(): void {
  // Clear any stored auth data
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_data');
}

export async function getCurrentUser(): Promise<LoginResponse | null> {
  try {
    const response = await api.get<LoginResponse>('/auth/me');
    return response.data;
  } catch (error) {
    return null;
  }
}

