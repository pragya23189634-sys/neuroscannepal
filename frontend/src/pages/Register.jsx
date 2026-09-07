import React, { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import PageHeader from '../components/PageHeader'
import { PAGES } from '../content/siteCopy'

export default function Register() {
  const { register, isAuthenticated, user } = useAuth()
  const [form, setForm] = useState({ email: '', password: '', full_name: '', role: 'patient' })
  const [error, setError] = useState('')
  const [patientId, setPatientId] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (isAuthenticated) {
    return <Navigate to={user?.role === 'patient' ? '/my-records' : '/'} replace />
  }

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const created = await register(form)
      if (created.patient_unique_id) setPatientId(created.patient_unique_id)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (patientId) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface-card px-8 py-10">
        <div className="card-accent max-w-lg p-8 text-center">
          <p className="section-label">Done</p>
          <h2 className="page-title mt-2">Your patient ID</h2>
          <p className="mt-4 font-mono text-2xl font-semibold text-accent">{patientId}</p>
          <p className="mt-4 text-sm text-brand-600">Save this ID. Your radiologist needs it when uploading your scan.</p>
          <Link to="/my-records" className="btn-primary mt-6 inline-flex">Go to my records</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-card px-8 py-10">
      <div className="w-full max-w-lg space-y-6">
        <PageHeader
          eyebrow={PAGES.register.eyebrow}
          title={PAGES.register.title}
          description={PAGES.register.description}
        />

        <form onSubmit={handleSubmit} className="card space-y-4 p-6">
          {error && (
            <div className="rounded-md border border-red-300/50 bg-red-50 px-4 py-3 text-sm text-red-900">{error}</div>
          )}

          <label className="block text-sm">
            <span className="font-medium text-brand-800">Full name</span>
            <input name="full_name" required className="field-input" value={form.full_name} onChange={handleChange} />
          </label>

          <label className="block text-sm">
            <span className="font-medium text-brand-800">Email</span>
            <input name="email" type="email" required className="field-input" value={form.email} onChange={handleChange} />
          </label>

          <label className="block text-sm">
            <span className="font-medium text-brand-800">Password</span>
            <input name="password" type="password" required minLength={6} className="field-input" value={form.password} onChange={handleChange} />
          </label>

          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting ? 'Creating account…' : 'Register as patient'}
          </button>

          <p className="text-center text-sm text-brand-600">
            Already have an account? <Link to="/login" className="font-medium text-accent hover:underline">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
