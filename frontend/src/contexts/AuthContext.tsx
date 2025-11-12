import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { LoginResponse } from '../api/auth';

interface User extends LoginResponse {
  id: string; // Alias for userId
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (userData: LoginResponse) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored user data on app load
    const userData = localStorage.getItem('user_data');
    
    if (userData) {
      try {
        const parsed = JSON.parse(userData);
        setUser({ ...parsed, id: parsed.userId });
      } catch (error) {
        console.error('Failed to parse user data:', error);
        localStorage.removeItem('user_data');
      }
    }
    setLoading(false);
  }, []);

  const login = (userData: LoginResponse) => {
    const userWithId = { ...userData, id: userData.userId };
    localStorage.setItem('user_data', JSON.stringify(userWithId));
    setUser(userWithId);
  };

  const logout = () => {
    localStorage.removeItem('user_data');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

