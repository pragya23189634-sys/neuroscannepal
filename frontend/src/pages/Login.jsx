import React, { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import {
  ArrowRightIcon,
  BeakerIcon,
  ChevronRightIcon,
  EnvelopeIcon,
  EyeIcon,
  EyeSlashIcon,
  KeyIcon,
  LockClosedIcon,
  UserIcon,
} from '@heroicons/react/24/outline'
import LoginBrandPanel from '../components/LoginBrandPanel'
import { useAuth } from '../context/AuthContext'
import { LOGIN } from '../content/siteCopy'

const DEMO_ACCOUNTS = [
  {
    role: 'Radiologist',
    email: 'radiologist@neuroscan.np',
    password: 'radiologist123',
    icon: BeakerIcon,
    color: 'bg-violet-100 text-violet-700',
  },
  {
    role: 'Doctor',
    email: 'doctor@neuroscan.np',
    password: 'doctor123',
    icon: UserIcon,
    color: 'bg-sky-100 text-sky-700',
  },
  {
    role: 'Patient',
    email: 'patient@neuroscan.np',
    password: 'patient123',
    icon: UserIcon,
    color: 'bg-emerald-100 text-emerald-700',
  },
]

export default function Login() {
  const { login, isAuthenticated, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (isAuthenticated) {
    const dest =
      user?.role === 'patient'
        ? '/my-records'
        : user?.role === 'doctor'
          ? '/doctor-review'
          : location.state?.from || '/'
    return <Navigate to={dest} replace />
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const loggedIn = await login(email, password)
      const dest =
        loggedIn.role === 'patient'
          ? '/my-records'
          : loggedIn.role === 'doctor'
            ? '/doctor-review'
            : location.state?.from || '/'
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
    setError('')
  }

  return (
    <div className="login-page">
      <LoginBrandPanel />

      <div className="login-panel-right">
        <div className="login-panel-right-inner">
          <h1 className="login-form-title">{LOGIN.formTitle}</h1>
          <p className="login-form-subtitle">{LOGIN.formHint}</p>

          <form onSubmit={handleSubmit} className="login-form">
            {error && (
              <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                {error}
              </div>
            )}

            <label className="login-label login-field-group">
              <span className="login-label-text">Email</span>
              <div className="relative">
                <EnvelopeIcon className="login-input-icon" />
                <input
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="you@neuroscan.np"
                  className="login-field pl-10"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </label>

            <label className="login-label login-field-group block">
              <span className="login-label-text">Password</span>
              <div className="relative">
                <LockClosedIcon className="login-input-icon" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  className="login-field pl-10 pr-10"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="login-password-toggle"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-[18px] w-[18px]" />
                  ) : (
                    <EyeIcon className="h-[18px] w-[18px]" />
                  )}
                </button>
              </div>
            </label>

            <button type="submit" className="login-submit-btn" disabled={submitting}>
              {submitting ? (
                'Signing in…'
              ) : (
                <>
                  Sign in
                  <ArrowRightIcon className="h-4 w-4" />
                </>
              )}
            </button>

            <p className="login-register-link">
              {LOGIN.registerPrompt}{' '}
              <Link to="/register">{LOGIN.registerLink}</Link>
            </p>
          </form>

          <div className="login-divider" />

          <div className="login-dev-card">
            <div className="flex items-center gap-2">
              <KeyIcon className="h-4 w-4 text-[#5D718A]" strokeWidth={1.5} />
              <p className="text-sm font-semibold text-[#10233D]">{LOGIN.demoTitle}</p>
            </div>
            <p className="mt-0.5 text-xs text-[#5D718A]">{LOGIN.demoSubtitle}</p>
            <div className="mt-2 divide-y divide-[#D8D2C8]/80">
              {DEMO_ACCOUNTS.map((account) => {
                const Icon = account.icon
                return (
                  <button
                    key={account.email}
                    type="button"
                    onClick={() => fillDemo(account)}
                    className="login-dev-row"
                  >
                    <span className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${account.color}`}>
                      <Icon className="h-3.5 w-3.5" strokeWidth={1.75} />
                    </span>
                    <div className="min-w-0 flex-1 text-left">
                      <p className="text-[13px] font-medium text-[#10233D]">{account.role}</p>
                      <p className="truncate font-mono text-[10px] text-[#5D718A]">{account.email}</p>
                    </div>
                    <ChevronRightIcon className="h-4 w-4 shrink-0 text-[#5D718A]/50" />
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
