import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored user data on app load (page reload)
    const loadUserFromStorage = () => {
      try {
        const userData = localStorage.getItem('user_data');
        
        if (userData) {
          const parsed = JSON.parse(userData);
          // Ensure we have all required fields
          if (parsed.email && parsed.userId && parsed.firmId && parsed.firmName) {
            setUser({ ...parsed, id: parsed.userId });
          } else {
            // Invalid user data - clear it
            console.warn('Invalid user data in localStorage, clearing...');
            localStorage.removeItem('user_data');
          }
        }
      } catch (error) {
        console.error('Failed to parse user data from localStorage:', error);
        localStorage.removeItem('user_data');
      } finally {
        setLoading(false);
      }
    };

    loadUserFromStorage();
  }, []);

  const login = (userData) => {
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
