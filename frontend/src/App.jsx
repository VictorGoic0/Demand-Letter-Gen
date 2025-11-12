import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { MainLayout } from './components/Layout/MainLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Documents } from './pages/Documents';
import { Templates } from './pages/Templates';
import { CreateLetter } from './pages/CreateLetter';
import { Letters } from './pages/Letters';
import { FinalizeLetter } from './pages/FinalizeLetter';
import { EditLetter } from './pages/EditLetter';
import { NotFound } from './pages/NotFound';
import './App.css';

function LoginRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Login />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Navigate to="/dashboard" replace />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Dashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/upload-assets"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Documents />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/templates"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Templates />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/create-letter"
        element={
          <ProtectedRoute>
            <MainLayout>
              <CreateLetter />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/letters"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Letters />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/letters/:id/finalize"
        element={
          <ProtectedRoute>
            <MainLayout>
              <FinalizeLetter />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/letters/:id/edit"
        element={
          <ProtectedRoute>
            <MainLayout>
              <EditLetter />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <NotFound />
            </MainLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
