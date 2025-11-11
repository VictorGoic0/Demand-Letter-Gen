import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { MainLayout } from './components/Layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Documents } from './pages/Documents';
import { Templates } from './pages/Templates';
import { CreateLetter } from './pages/CreateLetter';
import { Letters } from './pages/Letters';
import { FinalizeLetter } from './pages/FinalizeLetter';
import { EditLetter } from './pages/EditLetter';
import { NotFound } from './pages/NotFound';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/upload-assets" element={<Documents />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/create-letter" element={<CreateLetter />} />
            <Route path="/letters" element={<Letters />} />
            <Route path="/letters/:id/finalize" element={<FinalizeLetter />} />
            <Route path="/letters/:id/edit" element={<EditLetter />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </MainLayout>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
