import React from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import Upload from './pages/Upload'
import Processing from './pages/Processing'
import Results from './pages/Results'
import ModelInfo from './pages/ModelInfo'
import About from './pages/About'
import Login from './pages/Login'
import Register from './pages/Register'
import DoctorReview from './pages/DoctorReview'
import PatientPortal from './pages/PatientPortal'

export default function App() {
  const { pathname } = useLocation()
  const isAuthScreen = pathname === '/login' || pathname === '/register'

  return (
    <div className={`flex min-h-screen flex-col bg-surface ${isAuthScreen ? 'h-screen overflow-hidden' : ''}`}>
      {!isAuthScreen && <Header />}
      <main className={`flex-1 ${isAuthScreen ? 'min-h-0 overflow-hidden' : 'container-app py-8'}`}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/" element={<ProtectedRoute roles={['radiologist']}><Home /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute roles={['radiologist']}><Upload /></ProtectedRoute>} />
          <Route path="/processing" element={<ProtectedRoute roles={['radiologist']}><Processing /></ProtectedRoute>} />
          <Route path="/results" element={<ProtectedRoute roles={['radiologist']}><Results /></ProtectedRoute>} />
          <Route path="/model" element={<ProtectedRoute roles={['radiologist']}><ModelInfo /></ProtectedRoute>} />
          <Route path="/about" element={<ProtectedRoute roles={['radiologist', 'doctor', 'patient']}><About /></ProtectedRoute>} />

          <Route path="/doctor-review" element={<ProtectedRoute roles={['doctor']}><DoctorReview /></ProtectedRoute>} />
          <Route path="/my-records" element={<ProtectedRoute roles={['patient']}><PatientPortal /></ProtectedRoute>} />

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </main>
      {!isAuthScreen && <Footer />}
    </div>
  )
}
