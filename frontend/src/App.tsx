import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import { MainLayout } from '@/components/layout/MainLayout'
import { LandingPage } from '@/pages/LandingPage'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { ScannerPage } from '@/pages/ScannerPage'
import { SecurityPage } from '@/pages/SecurityPage'
import { RefactoringPage } from '@/pages/RefactoringPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { CompliancePage } from '@/pages/CompliancePage'
import { ReportsPage } from '@/pages/ReportsPage'
import { useAuthStore } from '@/store/authStore'
import { initializeAuth } from '@/store/authStore'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

export function App() {
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    initializeAuth()
  }, [])

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <LandingPage />} />
          <Route path="/landing" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Routes>
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/scanner" element={<ScannerPage />} />
                    <Route path="/security" element={<SecurityPage />} />
                    <Route path="/compliance" element={<CompliancePage />} />
                    <Route path="/reports" element={<ReportsPage />} />
                    <Route path="/refactoring" element={<RefactoringPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                  </Routes>
                </MainLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
