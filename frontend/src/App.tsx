import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { Login } from './pages/Login';
import { Overview } from './pages/Overview';
import { RealtimeLogs } from './pages/RealtimeLogs';
import Topology from './pages/Topology';
import { ErrorMonitoring } from './pages/ErrorMonitoring';
import { SlowRequestMonitoring } from './pages/SlowRequestMonitoring';
import { Alerts } from './pages/Alerts';
import { Users } from './pages/Users';
import { DashboardLayout } from './layouts/DashboardLayout';
import { useAuthStore } from './store/authStore';
import { LanguageProvider } from './i18n/LanguageContext';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <LanguageProvider>
      <ConfigProvider theme={{ token: { colorPrimary: '#1890ff' } }}>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route 
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Overview />} />
              <Route path="/realtime" element={<RealtimeLogs />} />
              <Route path="/topology" element={<Topology />} />
              <Route path="/errors" element={<ErrorMonitoring />} />
              <Route path="/slow-requests" element={<SlowRequestMonitoring />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/users" element={<Users />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </LanguageProvider>
  );
};

export default App;
