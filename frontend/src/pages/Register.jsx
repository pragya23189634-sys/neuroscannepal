import React, { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import PageHeader from '../components/PageHeader'

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
      <div className="mx-auto max-w-lg space-y-6">
        <div className="card p-8 text-center">
          <p className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Registration complete</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Your patient ID</h2>
          <p className="mt-4 font-mono text-2xl font-bold text-primary">{patientId}</p>
          <p className="mt-4 text-sm text-slate-600">
            Save this ID — your radiologist will use it when uploading your MRI scans.
          </p>
          <Link to="/my-records" className="btn-primary mt-6 inline-flex">Go to my records</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <PageHeader
        eyebrow="Patient registration"
        title="Create patient account"
        description="Register to receive a unique patient ID and access your MRI reports and doctor recommendations."
      />

      <form onSubmit={handleSubmit} className="card space-y-4 p-6">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
        )}

        <label className="block text-sm">
          <span className="font-medium text-slate-700">Full name</span>
          <input name="full_name" required className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm" value={form.full_name} onChange={handleChange} />
        </label>

        <label className="block text-sm">
          <span className="font-medium text-slate-700">Email</span>
          <input name="email" type="email" required className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm" value={form.email} onChange={handleChange} />
        </label>

        <label className="block text-sm">
          <span className="font-medium text-slate-700">Password</span>
          <input name="password" type="password" required minLength={6} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm" value={form.password} onChange={handleChange} />
        </label>

        <button type="submit" className="btn-primary w-full" disabled={submitting}>
          {submitting ? 'Creating account…' : 'Register as patient'}
        </button>

        <p className="text-center text-sm text-slate-600">
          Already have an account? <Link to="/login" className="font-medium text-primary hover:underline">Sign in</Link>
        </p>
      </form>
    </div>
  )
}
