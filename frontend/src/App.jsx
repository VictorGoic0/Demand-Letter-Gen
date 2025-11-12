import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import { MainLayout } from './components/Layout/MainLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Documents } from './pages/Documents';
import { Templates } from './pages/Templates';
import { TemplateView } from './pages/TemplateView';
import { TemplateEdit } from './pages/TemplateEdit';
import { CreateLetter } from './pages/CreateLetter';
import { Letters } from './pages/Letters';
import { LetterView } from './pages/LetterView';
import { FinalizeLetter } from './pages/FinalizeLetter';
import { EditLetter } from './pages/EditLetter';
import { NotFound } from './pages/NotFound';
import { PageLoader } from './components/ui/PageLoader';
import './App.css';

function LoginRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <PageLoader message="Loading..." />;
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
        path="/templates/new"
        element={
          <ProtectedRoute>
            <MainLayout>
              <TemplateEdit />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/templates/:templateId/view"
        element={
          <ProtectedRoute>
            <MainLayout>
              <TemplateView />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/templates/:templateId/edit"
        element={
          <ProtectedRoute>
            <MainLayout>
              <TemplateEdit />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/letters/new"
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
        path="/letters/:id/view"
        element={
          <ProtectedRoute>
            <MainLayout>
              <LetterView />
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
  // AuthProvider handles localStorage check on mount via useEffect
  // This ensures user data persists across page reloads
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
