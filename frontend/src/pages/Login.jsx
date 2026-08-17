import React, { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import PageHeader from '../components/PageHeader'

const DEMO_ACCOUNTS = [
  { role: 'Radiologist', email: 'radiologist@neuroscan.np', password: 'radiologist123' },
  { role: 'Doctor', email: 'doctor@neuroscan.np', password: 'doctor123' },
  { role: 'Patient', email: 'patient@neuroscan.np', password: 'patient123' },
]

export default function Login() {
  const { login, isAuthenticated, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (isAuthenticated) {
    const dest = user?.role === 'patient' ? '/my-records' : user?.role === 'doctor' ? '/doctor-review' : location.state?.from || '/'
    return <Navigate to={dest} replace />
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const loggedIn = await login(email, password)
      const dest =
        loggedIn.role === 'patient' ? '/my-records' :
        loggedIn.role === 'doctor' ? '/doctor-review' :
        location.state?.from || '/'
      navigate(dest, { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const fillDemo = (account) => {
    setEmail(account.email)
    setPassword(account.password)
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <PageHeader
        eyebrow="Secure access"
        title="Sign in to NeuroScan"
        description="Radiologists upload scans and run AI analysis. Doctors review images and add clinical recommendations. Patients view their reports."
      />

      <form onSubmit={handleSubmit} className="card space-y-4 p-6">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
        )}

        <label className="block text-sm">
          <span className="font-medium text-slate-700">Email</span>
          <input
            type="email"
            required
            className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label className="block text-sm">
          <span className="font-medium text-slate-700">Password</span>
          <input
            type="password"
            required
            className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        <button type="submit" className="btn-primary w-full" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>

        <p className="text-center text-sm text-slate-600">
          New patient? <Link to="/register" className="font-medium text-primary hover:underline">Register here</Link>
        </p>
      </form>

      <section className="card p-6">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Demo accounts</h3>
        <div className="mt-3 space-y-2">
          {DEMO_ACCOUNTS.map((account) => (
            <button
              key={account.email}
              type="button"
              onClick={() => fillDemo(account)}
              className="flex w-full items-center justify-between rounded-xl border border-slate-200 px-4 py-3 text-left text-sm transition hover:border-primary/30 hover:bg-blue-50/40"
            >
              <span className="font-medium text-slate-900">{account.role}</span>
              <span className="text-slate-500">{account.email}</span>
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
