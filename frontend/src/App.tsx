import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import { AuthProvider, useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import DocumentsPage from './pages/DocumentsPage';
import TimelinePage from './pages/TimelinePage';
import ChartsPage from './pages/ChartsPage';
import ChatPage from './pages/ChatPage';

const queryClient = new QueryClient();

// TEMP DEV BYPASS - matches backend/app/core/deps.py's DISABLE_AUTH_FOR_DEV.
// Set back to true (and flip the backend flag back to False) to require
// login again.
const SKIP_LOGIN_FOR_DEV = true;

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  if (!token && !SKIP_LOGIN_FOR_DEV) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/upload" element={<PrivateRoute><UploadPage /></PrivateRoute>} />
      <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
      <Route path="/documents" element={<PrivateRoute><DocumentsPage /></PrivateRoute>} />
      <Route path="/timeline" element={<PrivateRoute><TimelinePage /></PrivateRoute>} />
      <Route path="/charts" element={<PrivateRoute><ChartsPage /></PrivateRoute>} />
      <Route path="/chat" element={<PrivateRoute><ChatPage /></PrivateRoute>} />
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
