import React from 'react'

const styles = {
  completed: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  running: 'bg-sky-100 text-sky-800 ring-sky-200',
  pending: 'bg-slate-100 text-slate-600 ring-slate-200',
  failed: 'bg-red-100 text-red-800 ring-red-200',
  OK: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  WARNING: 'bg-amber-100 text-amber-800 ring-amber-200',
  FAILED: 'bg-red-100 text-red-800 ring-red-200',
  RUNNING: 'bg-sky-100 text-sky-800 ring-sky-200',
}

export default function StatusBadge({ status, className = '' }) {
  const key = (status || 'pending').toLowerCase()
  const tone = styles[status] || styles[key] || styles.pending
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${tone} ${className}`}>
      {status || 'pending'}
    </span>
  )
}
