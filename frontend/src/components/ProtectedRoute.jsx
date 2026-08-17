import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="card flex min-h-[240px] items-center justify-center p-8 text-sm text-slate-500">
        Checking session…
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (roles && !roles.includes(user.role)) {
    const fallback = user.role === 'patient' ? '/my-records' : user.role === 'doctor' ? '/doctor-review' : '/'
    return <Navigate to={fallback} replace />
  }

  return children
}
