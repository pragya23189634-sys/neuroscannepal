import React, { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import BackendStatus from './BackendStatus'

const navClass = ({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`

export default function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
      <div className="container-app flex items-center justify-between py-4">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-blue-700 text-sm font-bold text-white shadow-sm">
            NS
          </div>
          <div>
            <div className="text-base font-semibold text-slate-900">NeuroScan Nepal</div>
            <div className="text-xs text-slate-500">Brain MRI screening & clinical support</div>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          <BackendStatus />
          <nav className="hidden items-center gap-1 md:flex">
            <NavLink to="/" end className={navClass}>Dashboard</NavLink>
            <NavLink to="/upload" className={navClass}>Upload</NavLink>
            <NavLink to="/processing" className={navClass}>Processing</NavLink>
            <NavLink to="/results" className={navClass}>Results</NavLink>
            <NavLink to="/model" className={navClass}>Model</NavLink>
            <NavLink to="/about" className={navClass}>About</NavLink>
          </nav>
          <Link to="/upload" className="btn-primary hidden md:inline-flex">New scan</Link>
          <button type="button" className="rounded-lg p-2 text-slate-600 md:hidden" onClick={() => setOpen((v) => !v)} aria-label="Toggle menu">
            {open ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-slate-200 bg-white px-4 py-3 md:hidden">
          <nav className="flex flex-col gap-1">
            {[
              ['/', 'Dashboard'],
              ['/upload', 'Upload'],
              ['/processing', 'Processing'],
              ['/results', 'Results'],
              ['/model', 'Model'],
              ['/about', 'About'],
            ].map(([to, label]) => (
              <NavLink key={to} to={to} end={to === '/'} className={navClass} onClick={() => setOpen(false)}>
                {label}
              </NavLink>
            ))}
            <Link to="/upload" className="btn-primary mt-2" onClick={() => setOpen(false)}>New scan</Link>
          </nav>
        </div>
      )}
    </header>
  )
}
