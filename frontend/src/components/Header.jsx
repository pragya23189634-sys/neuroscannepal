import React, { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import BackendStatus from './BackendStatus'
import { useAuth } from '../context/AuthContext'
import { BRAND } from '../content/siteCopy'

const navClass = ({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`

const ROLE_NAV = {
  radiologist: [
    ['/', 'Dashboard'],
    ['/upload', 'Upload'],
    ['/processing', 'Processing'],
    ['/results', 'Results'],
    ['/model', 'Model'],
  ],
  doctor: [
    ['/doctor-review', 'MRI Review'],
  ],
  patient: [
    ['/my-records', 'My Records'],
  ],
}

const ROLE_LABELS = {
  radiologist: 'Radiologist',
  doctor: 'Doctor',
  patient: 'Patient',
}

export default function Header() {
  const [open, setOpen] = useState(false)
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const navItems = user ? [...(ROLE_NAV[user.role] || []), ['/about', 'About']] : []

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const homeTo = isAuthenticated
    ? (user?.role === 'patient' ? '/my-records' : user?.role === 'doctor' ? '/doctor-review' : '/')
    : '/login'

  return (
    <header className="sticky top-0 z-40 border-b border-brand-900/20 bg-brand-900 text-white">
      <div className="container-app flex items-center justify-between py-3">
        <Link to={homeTo} className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center border border-white/20 bg-brand-800 font-display text-sm font-semibold">
            NS
          </div>
          <div>
            <div className="font-display text-base font-semibold leading-tight">{BRAND.name}</div>
            <div className="text-[11px] text-white/60">{BRAND.subtitle}</div>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          <BackendStatus />
          {isAuthenticated && (
            <div className="hidden text-right md:block">
              <p className="text-sm font-medium">{user.full_name}</p>
              <p className="text-[11px] text-white/60">
                {ROLE_LABELS[user.role]}
                {user.patient_unique_id ? ` · ${user.patient_unique_id}` : ''}
              </p>
            </div>
          )}
          {isAuthenticated && (
            <nav className="hidden items-center gap-0.5 md:flex">
              {navItems.map(([to, label]) => (
                <NavLink key={to} to={to} end={to === '/'} className={navClass}>{label}</NavLink>
              ))}
            </nav>
          )}
          {user?.role === 'radiologist' && (
            <Link to="/upload" className="btn-primary hidden md:inline-flex">New scan</Link>
          )}
          {isAuthenticated ? (
            <button type="button" className="hidden rounded-md border border-white/25 px-3 py-2 text-sm font-medium text-white transition hover:bg-white/10 md:inline-flex" onClick={handleLogout}>
              Sign out
            </button>
          ) : (
            <Link to="/login" className="btn-primary hidden md:inline-flex">Sign in</Link>
          )}
          <button type="button" className="rounded-md p-2 text-white/80 md:hidden" onClick={() => setOpen((v) => !v)} aria-label="Toggle menu">
            {open ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-white/10 bg-brand-800 px-4 py-3 md:hidden">
          {isAuthenticated && (
            <p className="mb-2 px-2 text-sm text-white/70">{user.full_name} · {ROLE_LABELS[user.role]}</p>
          )}
          <nav className="flex flex-col gap-1">
            {isAuthenticated ? (
              <>
                {navItems.map(([to, label]) => (
                  <NavLink key={to} to={to} end={to === '/'} className={navClass} onClick={() => setOpen(false)}>
                    {label}
                  </NavLink>
                ))}
                {user?.role === 'radiologist' && (
                  <Link to="/upload" className="btn-primary mt-2" onClick={() => setOpen(false)}>New scan</Link>
                )}
                <button type="button" className="mt-2 rounded-md border border-white/25 px-3 py-2 text-sm text-white" onClick={() => { setOpen(false); handleLogout() }}>
                  Sign out
                </button>
              </>
            ) : (
              <Link to="/login" className="btn-primary" onClick={() => setOpen(false)}>Sign in</Link>
            )}
          </nav>
        </div>
      )}
    </header>
  )
}
