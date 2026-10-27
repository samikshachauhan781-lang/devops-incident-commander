// Main application component for DevOps Incident Commander
import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MainLayout from './layouts/MainLayout';
import { IncidentProvider } from './contexts/IncidentContext';
import { AuthProvider } from './hooks/useAuth';
import { ToastProvider } from './components/ui/Toast';
import { ThemeProvider } from './contexts/ThemeContext';

const Dashboard = lazy(() => import('./components/Dashboard'));
const IncidentList = lazy(() => import('./components/incidents/IncidentList'));
const IncidentDetail = lazy(() => import('./components/incidents/IncidentDetail'));
const Analytics = lazy(() => import('./components/analytics/Analytics'));
const Timeline = lazy(() => import('./components/timeline/Timeline'));
const SimpleSettings = lazy(() => import('./components/settings/SimpleSettings'));

function RouteFallback() {
  return (
    <div className="loading-container" role="status" aria-label="Loading page">
      <div className="loading-spinner h-10 w-10" />
    </div>
  );
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <IncidentProvider>
            <ToastProvider>
            <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
              <Routes>
                <Route path="/" element={<MainLayout />}>
                  <Route
                    index
                    element={
                      <Suspense fallback={<RouteFallback />}>
                        <Dashboard />
                      </Suspense>
                    }
                  />
                  <Route
                    path="incidents"
                    element={
                      <Suspense fallback={<RouteFallback />}>
                        <IncidentList />
                      </Suspense>
                    }
                  />
                  <Route
                    path="incidents/:id"
                    element={
                      <Suspense fallback={<RouteFallback />}>
                        <IncidentDetail />
                      </Suspense>
                    }
                  />
                  <Route
                    path="analytics"
                    element={
                      <Suspense fallback={<RouteFallback />}>
                        <Analytics />
                      </Suspense>
                    }
                  />
                  <Route
                    path="timeline"
                    element={
                      <Suspense fallback={<RouteFallback />}>
                        <Timeline />
                      </Suspense>
                    }
                  />
                  <Route
                    path="settings"
                    element={
                      <Suspense fallback={<RouteFallback />}>
                        <SimpleSettings />
                      </Suspense>
                    }
                  />
                </Route>
              </Routes>
            </Router>
            </ToastProvider>
          </IncidentProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
